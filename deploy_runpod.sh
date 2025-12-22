#!/bin/bash
# RunPod A100 Automated Deployment Script
# Run this script on your RunPod instance after connecting via SSH

set -e

echo "🚀 Setting up AI Video Generator on RunPod"

# Update system
echo "📦 Updating system packages..."
apt-get update -qq
apt-get install -y git ffmpeg libsm6 libxext6 libx264-dev \
    libavcodec-dev libavformat-dev libswscale-dev -qq

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install -q -r requirements-runpod.txt

# Install opencv with FFmpeg support
echo "🎥 Installing OpenCV with H264 encoder support..."
pip uninstall -y opencv-python opencv-python-headless 2>/dev/null || true
pip install opencv-contrib-python==4.10.0.84

# Download models (to avoid download time during processing)
echo "⬇️  Pre-downloading AI models (this takes ~10 minutes, only happens once)..."
python3 << EOF
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

print("Downloading ControlNet Pose...")
controlnet_pose = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_openpose",
    torch_dtype=torch.float16
)

print("Downloading ControlNet Depth...")
controlnet_depth = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11f1p_sd15_depth",
    torch_dtype=torch.float16
)

print("Downloading ControlNet Canny...")
controlnet_canny = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_canny",
    torch_dtype=torch.float16
)

print("Downloading Realistic Vision v5.1...")
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "stablediffusionapi/realistic-vision-v51",
    controlnet=[controlnet_pose, controlnet_depth, controlnet_canny],
    torch_dtype=torch.float16,
    safety_checker=None,
    use_safetensors=True
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

# Download MiDaS depth estimator
echo "⬇️  Downloading MiDaS depth estimator..."
python3 << EOF
from controlnet_aux import MidasDetector
depth_estimator = MidasDetector.from_pretrained("lllyasviel/Annotators")
print("✓ MiDaS cached")
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting app in detached screen session..."
screen -dmS ai-video python app.py
sleep 3
echo "✅ App is running in background!"
echo ""
echo "📱 Useful commands:"
echo "   screen -r ai-video    # Reattach to see logs"
echo "   screen -ls            # List all screen sessions"
echo "   Ctrl+A then D         # Detach from screen (keep running)"
echo "   Ctrl+C                # Stop the app"
echo ""
echo "💡 The app will keep running even if you disconnect!"
echo "   Access via RunPod's HTTP proxy URL (port 7860)"
