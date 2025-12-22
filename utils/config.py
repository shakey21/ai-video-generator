import torch

class Config:
    # Device - hardcoded for Apple Silicon (MPS)
    DEVICE = "mps"
    
    # Model settings
    MODEL_NAME = "runwayml/stable-diffusion-v1-5"
    CONTROLNET_NAME = "lllyasviel/control_v11p_sd15_openpose"
    
    # Processing
    DEFAULT_STRENGTH = 0.75
    INFERENCE_STEPS = 20
    
    # Video
    OUTPUT_DIR = "outputs"
    MAX_VIDEO_LENGTH = 300  # seconds (5 minutes)
