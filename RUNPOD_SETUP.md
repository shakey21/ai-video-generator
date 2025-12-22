# RunPod A100 Deployment Guide

Complete guide to running your AI video generator on RunPod A100 GPU (~10-15x faster than M4 Pro).

---

## 🚀 Quick Start (5 minutes)

### Step 1: Create RunPod Account
1. Go to [runpod.io](https://runpod.io)
2. Sign up and add $10-20 credit (enough for 10-20 videos)

### Step 2: Deploy GPU Instance
1. Click **"Deploy"** → **"GPU Pods"**
2. Select **GPU Type:**
   - **A100 40GB** ($1.09/hr) - Recommended
   - **A100 80GB SXM** ($1.89/hr) - If you need extra VRAM
3. Select **Template:** 
   - Choose **"RunPod PyTorch"** (pre-installed CUDA, Python, PyTorch)
4. Configure:
   - **Container Disk:** 30 GB minimum
   - **Volume Disk:** Not needed (optional for persistence)
5. Click **"Deploy On-Demand"**

### Step 3: Connect to Instance
1. Wait for instance to be **"Running"** (~30 seconds)
2. Click **"Connect"** → **"Start Web Terminal"**
3. Or use SSH: Copy SSH command and run in your terminal

### Step 4: Upload Your Code

**Option A: Git Clone (Recommended)**
```bash
git clone <your-repo-url>
cd ai-video-generator
```

**Option B: Direct Upload**
1. In RunPod terminal, create directory: `mkdir ai-video-generator && cd ai-video-generator`
2. Use RunPod's file upload feature (upload icon in web terminal)
3. Upload all files from your local project

### Step 5: Run Automated Setup
```bash
chmod +x deploy_runpod.sh
./deploy_runpod.sh
```

This will:
- Install all dependencies
- Pre-download AI models (SD 1.5, ControlNet, YOLO)
- Cache everything for faster processing

### Step 6: Start the App
```bash
python app.py
```

### Step 7: Access the UI
1. In RunPod dashboard, click **"Connect"** → **"HTTP Service [Port 7860]"**
2. Or use the proxy URL shown in terminal output
3. Upload your video and process!

### Step 8: Download Results
1. Processed videos save to `outputs/` folder
2. Download via web terminal file browser
3. Or use: `scp` to copy to your local machine

### Step 9: Stop Instance (Important!)
1. When done, click **"Stop Pod"** in RunPod dashboard
2. This stops billing immediately
3. Or **"Terminate Pod"** to delete everything

---

## 📊 Cost Breakdown

**A100 40GB at $1.09/hr:**
- 10-second video (300 frames): ~15-20 min = **$0.27-0.36**
- 30-second video (900 frames): ~45-60 min = **$0.82-1.09**
- 60-second video (1800 frames): ~90-120 min = **$1.64-2.18**

**Processing Speed:**
- ~2-3 seconds per frame (vs 120s on M4 Pro)
- **10-15x faster** than local Mac

---

## 🔧 Manual Setup (Alternative)

If you don't want to use the automated script:

### Install System Dependencies
```bash
apt-get update
apt-get install -y ffmpeg libsm6 libxext6
```

### Install Python Packages
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install gradio diffusers transformers accelerate ultralytics opencv-python pillow peft
```

### Download Models Manually
```bash
python -c "from diffusers import StableDiffusionControlNetPipeline, ControlNetModel; import torch; controlnet = ControlNetModel.from_pretrained('lllyasviel/control_v11p_sd15_openpose', torch_dtype=torch.float16); pipe = StableDiffusionControlNetPipeline.from_pretrained('runwayml/stable-diffusion-v1-5', controlnet=controlnet, torch_dtype=torch.float16)"
```

### Run App
```bash
python app.py
```

---

## 💡 Tips & Tricks

### Use Spot Instances (Save 70%)
- Select **"Community Cloud"** instead of **"Secure Cloud"**
- A100 spot: ~$0.30/hr (vs $1.09/hr)
- May be interrupted, but great for batch processing

### Batch Processing Multiple Videos
1. Upload all videos to `inputs/` folder
2. Modify script to loop through all files
3. Let it run overnight

### Persistent Storage
- Add a **Volume** (10GB = $2/month) to save models between sessions
- Models won't need to re-download each time
- Saves 5-10 minutes per session

### SSH File Transfer
```bash
# Download processed video
scp root@<runpod-ip>:/workspace/ai-video-generator/outputs/video.mp4 ~/Downloads/

# Upload input video
scp ~/Videos/input.mp4 root@<runpod-ip>:/workspace/ai-video-generator/
```

### Monitor GPU Usage
```bash
watch nvidia-smi
```

---

## 🐛 Troubleshooting

**"CUDA out of memory"**
- Reduce video resolution
- Use A100 80GB instead of 40GB
- Process fewer frames

**"Models downloading slowly"**
- Use pre-cache script: `./deploy_runpod.sh`
- Or download models locally and upload to RunPod

**"Can't access web UI"**
- Make sure app is running: `python app.py`
- Use RunPod's HTTP proxy link (not localhost)
- Check port 7860 is exposed

**"Instance costs too much"**
- Remember to **Stop** or **Terminate** when done
- Use Spot instances for 70% savings
- Process during off-peak hours (cheaper spot prices)

---

## 📈 Performance Comparison

| Hardware | Time/Frame | 10s Video (300 frames) | Cost |
|----------|-----------|------------------------|------|
| M4 Pro (Local) | 120s | ~10 hours | Free |
| A100 40GB | 2-3s | 15-20 min | $0.30 |
| A100 80GB | 1.5-2s | 10-15 min | $0.35 |

**Speedup: 10-15x faster on A100**

---

## 🔐 Security Notes

- Don't commit API keys or model configs with private data
- Use environment variables for sensitive info
- Terminate instances when not in use
- Enable 2FA on RunPod account

---

## 📞 Support

**RunPod Issues:**
- Discord: discord.gg/runpod
- Docs: docs.runpod.io

**Project Issues:**
- Check logs: `cat logs.txt`
- GPU status: `nvidia-smi`
- Python errors: Add `--debug` flag

---

Happy processing! 🎥✨
