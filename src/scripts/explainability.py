import torch
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from torch.nn import functional as F
from transformers import (
    AutoFeatureExtractor,
    AutoModel,
    AutoTokenizer,
)

vision_attn_probs = []
text_attn_probs = []

def vision_hook(module, input, output):
    
    hidden_states, attn_weights = output
    
    attn_weights = attn_weights.requires_grad_(True)
    vision_attn_probs.append(attn_weights)
    
def text_hook(module, input, output):
    
    hidden_states, attn_weights = output
    
    attn_weights = attn_weights.requires_grad_(True)
    text_attn_probs.append(attn_weights)
    
def register_hooks(model):
    
    vision_attn_probs.clear()
    text_attn_probs.clear()
    
    for layer in model.vision_model.encoder.layers:
        layer.self_attn.register_forward_hook(vision_hook)
    for layer in model.text_model.encoder.layers:
        layer.self_attn.register_forward_hook(text_hook)


def interpret(image, text, model, device, tokenizer, start_layer, start_layer_text):
    
    model.eval()
    model.to(device)
    
    text_inputs = tokenizer(text, return_tensors = 'pt', padding = True, truncation = True).to(device)
    
    register_hooks(model)
    
    inputs = {
        "pixel_values": image,
        "input_ids": text_inputs["input_ids"],
        "attention_mask": text_inputs["attention_mask"]
        
    }
    
    outputs = model(**inputs, output_attentions = True)
    logits_per_image = outputs.logits_per_image
    logits_per_text = outputs.logits_per_text
    
    batch_size = text_inputs["input_ids"].shape[0]
    index = torch.arange(batch_size).to(device)
    
    one_hot = torch.zeros_like(logits_per_image).to(device)
    one_hot[0, index] = 1.0
    one_hot = (one_hot * logits_per_image).sum()
    model.zero_grad()
    
    vision_layers = model.vision_model.encoder.layers
    text_layers = model.text_model.encoder.layers
    
    if start_layer == -1:
        start_layer = len(vision_layers) - 1
    if start_layer_text == -1:
        start_layer_text = len(text_layers) - 1
    
    batch_size_img = image.shape[0]
    num_tokens_vision = vision_attn_probs[0].shape[-1]
    
    R = torch.eye(num_tokens_vision, num_tokens_vision, dtype = vision_attn_probs[0].dtype, device = device)
    R = R.unsqueeze(0).expand(batch_size_img * batch_size, num_tokens_vision, num_tokens_vision)
    
    for i in range(len(vision_attn_probs) - 1, start_layer - 1, -1):
        attn = vision_attn_probs[i]
        grad = torch.autograd.grad(one_hot, [attn], retain_graph = True)[0]
        
        cam = grad * attn
        cam = cam.clamp(min = 0).mean(dim = 1)
        R = R + torch.bmm(cam, R)
    
    image_relevance = R[:, 0, 1:]
    
    num_tokens_text = text_attn_probs[0].shape[-1]
    R_text = torch.eye(num_tokens_text, num_tokens_text, dtype = text_attn_probs[0].dtype, device = device)
    R_text = R_text.unsqueeze(0).expand(batch_size, num_tokens_text, num_tokens_text)
    
    for i in range(len(text_attn_probs)-1, start_layer_text - 1, -1):
        attn = text_attn_probs[i]
        grad = torch.autograd.grad(one_hot, [attn], retain_graph = True)[0]
        cam = grad * attn
        cam = cam.clamp(min = 0).mean(dim = 1)
        R_text = R_text + torch.bmm(cam, R_text)
    text_relevance = R_text
    
    return text_relevance, image_relevance

def show_relevance(image_relevance, image, orig_image):
    def show_cam_on_image(img, mask):
        heatmap = cv2.applyColorMap(np.uint8(255 * mask), cv2.COLORMAP_JET)
        heatmap = np.float32(heatmap) / 255
        cam = heatmap + np.float32(img)
        cam = cam / np.max(cam)
        return cam
    fig, axs = plt.subplots(1, 2)
    
    axs[0].imshow(orig_image)
    axs[0].axis('off')
    
    dim = int(image_relevance.numel() ** .5)
    image_relevance = image_relevance.reshape(1, 1, dim, dim)
    image_relevance = F.interpolate(image_relevance, size = 224, mode = 'bilinear')
    image_relevance = image_relevance.detach().reshape(224, 224).cpu().numpy()
    
    image_relevance = (image_relevance - image_relevance.min())/ (image_relevance.max() - image_relevance.min())
    image = image[0].permute(1, 2, 0).cpu().numpy()
    
    image = (image - image.min()) / (image.max() - image.min())
    vis = show_cam_on_image(image, image_relevance)
    vis = np.uint8(255 * vis)
    vis = cv2.cvtColor(np.array(vis), cv2.COLOR_RGB2BGR)
    axs[1].imshow(vis)
    axs[1].axis('off')
    plt.show()

if '__name__' == '__main__':
    model = AutoModel.from_pretrained("wise-ft-large-clip-.7")
    processor = AutoFeatureExtractor.from_pretrained("laion/CLIP-ViT-H-14-laion2B-s32B-b79K")
    tokenizer = AutoTokenizer.from_pretrained("laion/CLIP-ViT-H-14-laion2B-s32B-b79K")
    image_path = 'path/to/image'

    orig_image = Image.open(image_path).convert('RGB')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    image_inputs = processor(images = orig_image, return_tensors = 'pt').to(device)

    pixel_values = image_inputs['pixel_values']

    texts = ['An image representing (country)']
    text_relevance, image_relevance = interpret(
        image = pixel_values,
        text = texts,
        model = model,
        device = device,
        tokenizer = tokenizer,
        start_layer = -1,
        start_layer_text = -1
    )

    show_relevance(image_relevance, pixel_values, orig_image)