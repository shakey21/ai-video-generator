# AI Video Model Replacer

Replace people in videos with AI-generated human models while preserving their exact movements and poses. All processing is done locally on your machine.

## What It Does

Takes a video containing a person and replaces them with an AI-generated model based on a text description. The original person's movements, poses, and actions are preserved exactly. The background remains unchanged.

## Requirements

- Python 3.10 or higher
- 16GB+ RAM recommended (8GB minimum)
- GPU recommended: Apple Silicon (M1/M2/M3/M4) or NVIDIA with 8GB+ VRAM
- 10GB free disk space

## Installation

```bash
# Navigate to project directory
cd /tmp/video-model-replacer

# Create virtual environment
python3 -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Start the application:

```bash
/tmp/video-model-replacer/venv/bin/python /tmp/video-model-replacer/app.py
```

Open browser to: http://127.0.0.1:7860

1. Upload a video file containing a person
2. Enter a text description of the desired replacement model (e.g., "woman in red dress", "athlete in sportswear")
3. Adjust strength slider (default 1.0 for maximum pose preservation)
4. Click "Replace Model"
5. Wait for processing to complete
6. Download the result

Processed videos are saved to `outputs/replaced_[filename].mp4`

## First Run

On first use, the application downloads AI models (~5GB) from HuggingFace. This takes 5-15 minutes and only happens once. Models are cached in `~/.cache/huggingface/`

## Performance

Processing times on Apple M4 Pro (1080p video):
- 10 seconds of video: ~2-5 minutes
- 30 seconds of video: ~6-15 minutes
- 1 minute of video: ~12-30 minutes

CPU-only processing is 5-10x slower than GPU.

## Privacy

All processing is local. Your videos never leave your computer. No cloud services, API keys, or accounts required. Works offline after initial model download.

## Project Structure

```
video-model-replacer/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── models/
│   ├── detector.py       # Person detection
│   ├── generator.py      # AI generation
│   └── processor.py      # Video pipeline
├── utils/
│   ├── video_utils.py    # Video I/O
│   └── config.py         # Settings
└── outputs/              # Processed videos
```

## AI Models

- Stable Diffusion v1.5 (runwayml/stable-diffusion-v1-5)
- ControlNet OpenPose (lllyasviel/control_v11p_sd15_openpose)
- MediaPipe 0.10

## Limitations

- Single person per video (best results)
- Some frame-to-frame flicker may occur
- Not real-time processing
- Audio is preserved but not modified

## Troubleshooting

**"Command not found: pip"** - Use `pip3` on macOS/Linux

**"externally-managed-environment"** - Must use virtual environment

**Very slow processing** - Confirm GPU is being used (check terminal for "Using device: mps" or "cuda")

**Poor quality** - Use 1080p input video, good lighting, detailed text descriptions
