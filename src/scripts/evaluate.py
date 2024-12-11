from datasets import load_dataset
import json
from torchvision.io import ImageReadMode, read_image
import torch
from torchvision.transforms.functional import InterpolationMode
from torchvision.transforms import CenterCrop, ConvertImageDtype, Normalize, Resize
from transformers import (
    AutoFeatureExtractor,
    AutoModel,
    AutoTokenizer
)

def evaluate_clip_retrieval(model_path, config, captions):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModel.from_pretrained(model_path).to(device)
    tokenizer = AutoTokenizer.from_pretrained(config.model_name, use_fast=True)
    feature_extractor = AutoFeatureExtractor.from_pretrained(config.model_name)
    
    image_transform = torch.nn.Sequential(
        Resize([model.config.vision_config.image_size], interpolation = InterpolationMode.BICUBIC),
        CenterCrop([model.config.vision_config.image_size]),
        ConvertImageDtype(torch.float),
        Normalize(feature_extractor.image_mean, feature_extractor.image_std)
    ).to(device)
    
    with open("split_dataset_test.json", "r") as f:
        data = [json.loads(line) for line in f]
    
    total_samples = 0
    top1_correct = 0
    top5_correct = 0
    
    all_captions = captions
    
    all_text_inputs = tokenizer(
        all_captions,
        max_length = config.max_seq_length,
        padding = 'max_length',
        truncation = True,
        return_tensors= 'pt'
    )
    all_text_inputs = {k: v.to(device) for k, v in all_text_inputs.items()}
    
    with torch.no_grad():
        text_embeddings = model.get_text_features(
            input_ids = all_text_inputs['input_ids'],
            attention_mask = all_text_inputs['attention_mask']
        )
        text_embeddings = text_embeddings / text_embeddings.norm(dim = -1, keepdim = True)
    for i in data:
        for j in i:
            
            try:
                image = read_image(j['image_path'], mode = ImageReadMode.RGB)
                transformed_image = image_transform(image).unsqueeze(0).to(device)
            except Exception as e:
                print(f"Error processing image: {j['image_path']} ")
                continue
            
            
            with torch.no_grad():
                image_embeds = model.get_image_features(transformed_image)
                image_embeds = image_embeds / image_embeds.norm(dim = -1, keepdim = True)
            
            similarities = torch.nn.functional.cosine_similarity(image_embeds, text_embeddings)
            
            top_similarities, top_indices = torch.topk(similarities, k = 5)
            
            original_caption = j['caption']
            top1_caption = all_captions[top_indices[0].item()]
            
            total_samples += 1
            
            if top1_caption == original_caption:
                top1_correct += 1
            
            if original_caption in [all_captions[idx] for idx in top_indices]:
                top5_correct += 1
                
    print("Retrieval Evaluation Results:")
    print(f"Total Samples: {total_samples}")
    print(f"top-1 accuracy: {top1_correct / total_samples}")
    print(f"top-5 accuracy: {top5_correct / total_samples}")

class Config:
    model_name: str = 'laion/CLIP-ViT-H-14-laion2B-s32B-b79K'
    dataset: str = 'dataset_final.json'
    image_column: str = 'image_path'
    caption_column: str = 'caption'
    max_seq_length: int = 77
    output_dir: str = './large-clip-scheduler'
    train_batch_size: int = 32
    eval_batch_size: int = 32
    epochs: int = 1
    logging_steps: int = 10
    save_steps: int = 100
    evaluation_strategy: str = 'steps'

if '__name__' == '__main__':
    cfg = Config()
    dataset = load_dataset("json", data_files = 'dataset_final.json')
    captions = set()
    for row in dataset['train']:
        captions.add(row['caption'])
    model_path = 'model_folder'

    evaluate_clip_retrieval(model_path, cfg, list(captions))

