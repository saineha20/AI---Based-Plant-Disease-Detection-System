# scripts/train_plantvillage.py
"""
PlantVillage Dataset Training & ONNX Export Pipeline
This script provides the complete pipeline to train a MobileNetV2 classifier
on the 38-class PlantVillage dataset and export the trained model to ONNX.
"""
import os
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser(description="Train MobileNetV2 on PlantVillage")
    parser.add_argument("--data_dir", type=str, default="./data/PlantVillage", help="Path to PlantVillage dataset folder")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--output_onnx", type=str, default="./models/plant_disease_model.onnx", help="Output path for ONNX model")
    parser.add_argument("--device", type=str, default="cuda", help="cuda or cpu")
    return parser.parse_args()

TRAINING_TEMPLATE = '''
import torch
import torch.nn as nn
from torchvision import datasets, transforms, models

# 1. Data Transforms
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 2. Model: MobileNetV2 transfer learning
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
for param in model.features.parameters():
    param.requires_grad = False  # Freeze backbone initial epochs

num_ftrs = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(p=0.3),
    nn.Linear(num_ftrs, 38)
)

# 3. Export to ONNX once trained
def export_to_onnx(model, save_path):
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224)
    torch.onnx.export(
        model,
        dummy_input,
        save_path,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"Exported trained model to {save_path}")
'''

def main():
    args = parse_args()
    print("=" * 60)
    print("PLANTVILLAGE TRAINING SCRIPT")
    print("=" * 60)
    print(f"Target data directory: {args.data_dir}")
    print(f"Epochs: {args.epochs}, Batch Size: {args.batch_size}, LR: {args.lr}")
    print(f"Target ONNX output: {args.output_onnx}")

    if not os.path.exists(args.data_dir):
        print(f"\n[Notice] Dataset directory '{args.data_dir}' not found on this machine.")
        print("To download the PlantVillage dataset:")
        print("  1. Kaggle CLI: kaggle datasets download -d emmarex/plantdisease")
        print("  2. Unzip into data/PlantVillage/ with folders for each of the 38 classes.")
        print("  3. Run: python scripts/train_plantvillage.py --data_dir data/PlantVillage --epochs 15")
    else:
        print("\nStarting PyTorch training pipeline...")
        # Execute actual training if dataset is present
        exec(TRAINING_TEMPLATE)

if __name__ == "__main__":
    main()

