#!/bin/bash
# RunPod A100 Automated Deployment Script
# Run this script on your RunPod instance after connecting via SSH

set -e

echo "🚀 Setting up AI Video Generator on RunPod A100..."

# Update system
echo "📦 Updating system packages..."
apt-get update -qq
apt-get install -y git ffmpeg libsm6 libxext6 -qq

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -q gradio diffusers transformers accelerate ultralytics opencv-python pillow peft

# Download models (to avoid download time during processing)
echo "⬇️  Pre-downloading AI models..."
python3 << EOF
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

print("Downloading ControlNet...")
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_openpose",
    torch_dtype=torch.float16
)

print("Downloading Stable Diffusion 1.5...")
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
)
print("✓ Models cached successfully")
EOF

# Download YOLO models
echo "⬇️  Downloading YOLO models..."
python3 << EOF
from ultralytics import YOLO
YOLO('yolov8m-pose.pt')
YOLO('yolov8m-seg.pt')
print("✓ YOLO models cached")
EOF

echo ""
echo "✅ Setup complete! Run your app with:"
echo "   python app.py"
echo ""
echo "💡 Access via RunPod's HTTP proxy URL"
