import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

import torch
from datasets import load_dataset
from PIL import Image
from torchvision.io import ImageReadMode, read_image
from torchvision.transforms import CenterCrop, ConvertImageDtype, Normalize, Resize
from torchvision.transforms.functional import InterpolationMode

import transformers
from transformers import (
    AutoFeatureExtractor,
    AutoModel,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed,
)

@dataclass
class Config:
    model_name: str = 'laion/CLIP-ViT-H-14-laion2B-s32B-b79K' #specify pretrained clip from hugging face
    dataset: str = 'dataset_final.json'
    image_column: str = 'image_path'
    caption_column: str = 'caption'
    max_seq_length: int = 77
    output_dir: str = './output-dir'
    train_batch_size: int = 32
    eval_batch_size: int = 32
    epochs: int = 1
    logging_steps: int = 10
    save_steps: int = 100
    evaluation_strategy: str = 'steps'

class Transform(torch.nn.Module):
    def __init__(self, image_size, mean, std):
        super().__init__()
        self.transforms = torch.nn.Sequential(
            Resize([image_size], interpolation = InterpolationMode.BICUBIC),
            CenterCrop(image_size),
            ConvertImageDtype(torch.float),
            Normalize(mean, std)
        )
    def forward(self, x):
        with torch.no_grad():
            x = self.transforms(x)
        return x
    

def collate_fn(samples):
    pixel_values = torch.stack([sample["pixel_values"] for sample in samples])
    input_ids = torch.tensor([sample['input_ids'] for sample in samples], dtype = torch.long)
    attention_mask = torch.tensor([sample["attention_mask"] for sample in samples], dtype = torch.long)
    return {
        "pixel_values": pixel_values,
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "return_loss": True,
    }

cfg = Config()
training_args = TrainingArguments(
        output_dir = cfg.output_dir,
        do_train = True,
        do_eval = True,
        per_device_train_batch_size = cfg.train_batch_size,
        per_device_eval_batch_size = cfg.eval_batch_size,
        num_train_epochs = cfg.epochs,
        logging_steps = cfg.logging_steps,
        evaluation_strategy = cfg.evaluation_strategy,
        overwrite_output_dir = True,
        learning_rate = 1e-5,
        remove_unused_columns = False,
        weight_decay = 0.01,
        lr_scheduler_type = 'linear',
        warmup_steps = 500,
        fp16 = True,
    
    )
dataset = load_dataset("json", data_files = cfg.dataset)

tokenizer = AutoTokenizer.from_pretrained(cfg.model_name, use_fast= True)
feature_extractor = AutoFeatureExtractor.from_pretrained(cfg.model_name)
model = AutoModel.from_pretrained(cfg.model_name)

for parameter in model.text_model.parameters():
    parameter.requires_grad = False

with_split = dataset['train'].train_test_split(test_size = .1)

set_seed(42)
image_column = cfg.image_column
caption_column = cfg.caption_column
config = model.config

image_transformations = Transform(
    config.vision_config.image_size, feature_extractor.image_mean, feature_extractor.image_std
)
image_transformations = torch.jit.script(image_transformations)

def tokenize_captions(samples):
    captions = [c for c in samples[caption_column]]
    text_inputs = tokenizer(captions, max_length = cfg.max_seq_length, padding = 'max_length', truncation = True)
    samples['input_ids'] = text_inputs['input_ids']
    samples['attention_mask'] = text_inputs['attention_mask']
    return samples

def transform_images(samples):
    images = [read_image(img_path, mode = ImageReadMode.RGB) for img_path in samples[image_column]]
    samples['pixel_values'] = [image_transformations(image) for image in images]
    return samples
    
def filter_images(samples):
    valid = []

    for image_file in samples[image_column]:
        try:
            Image.open(image_file)
            valid.append(True)
        except:
            valid.append(False)
    return valid
train_dataset = with_split['train']

train_dataset = train_dataset.filter(filter_images, batched = True)
train_dataset = train_dataset.map(
    tokenize_captions,
    batched = True,
)
print(train_dataset[0].keys())
train_dataset.set_transform(transform_images)
print(train_dataset[0].keys())
eval_dataset = with_split['test']

eval_dataset = eval_dataset.filter(filter_images, batched = True)
eval_dataset = eval_dataset.map(
    tokenize_captions,
    batched = True,
)
eval_dataset.set_transform(transform_images)
trainer = Trainer(
        model = model,
        args = training_args,
        train_dataset= train_dataset,
        eval_dataset = eval_dataset,
        data_collator = collate_fn,
    )

trainer.train()
trainer.save_model()
trainer.evaluate()