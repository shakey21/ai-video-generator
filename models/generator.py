import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers import DPMSolverMultistepScheduler
from PIL import Image
import numpy as np
import cv2
from .config_loader import ModelConfig

class ModelGenerator:
    def __init__(self):
        """Auto-detects best device (CUDA for cloud GPUs, MPS for Mac)"""
        # Auto-detect device
        if torch.cuda.is_available():
            self.device = "cuda"
            device_name = torch.cuda.get_device_name(0)
        elif torch.backends.mps.is_available():
            self.device = "mps"
            device_name = "Apple M4 Pro"
        else:
            self.device = "cpu"
            device_name = "CPU (slow)"
        
        self.pipe = None
        self.config = ModelConfig()
        self.model_name = "default_model"
        self.prev_seed = self.config.get_seed(self.model_name)
        print(f"Using device: {self.device} ({device_name})")
        print(f"Loaded model config: {self.config.get_model(self.model_name)['name']}")
    
    def load_model(self):
        """Load high-quality SD 1.5 + ControlNet"""
        if self.pipe is not None:
            return
        
        print("Loading AI models (first run: ~5GB download)...")
        
        # Use fp16 for CUDA (A100), fp32 for MPS (stability)
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        # Load ControlNet for pose guidance
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_openpose",
            torch_dtype=dtype
        )
        
        # Load Stable Diffusion pipeline
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=dtype,
            safety_checker=None
        )
        
        # Use high-quality scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )
        
        self.pipe.to(self.device)
        self.pipe.enable_attention_slicing()
        
        # Device-specific optimizations
        if self.device == "mps":
            torch.mps.set_per_process_memory_fraction(0.85)
        elif self.device == "cuda":
            # Enable TF32 for A100 speedup
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
        
        print("Models loaded successfully")
    
    def generate_replacement(
        self,
        pose_image: np.ndarray,
        prompt: str = None,
        num_inference_steps: int = None
    ) -> np.ndarray:
        """
        Generate high-quality replacement model using JSON config
        
        Args:
            pose_image: Pose skeleton image
            prompt: Optional override for model description (uses config if None)
            num_inference_steps: Optional override for quality steps (uses config if None)
        """
        self.load_model()
        
        # Convert to PIL
        pose_pil = Image.fromarray(cv2.cvtColor(pose_image, cv2.COLOR_BGR2RGB))
        
        # Use config values
        full_prompt = self.config.get_full_prompt(self.model_name)
        negative_prompt = self.config.get_negative_prompt(self.model_name)
        steps = num_inference_steps if num_inference_steps else self.config.get_inference_steps(self.model_name)
        guidance = self.config.get_guidance_scale(self.model_name)
        
        # Generate with consistent seed for same character at high resolution
        with torch.inference_mode():
            result = self.pipe(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                image=pose_pil,
                num_inference_steps=steps,
                controlnet_conditioning_scale=1.0,  # Full pose control
                generator=torch.Generator(device=self.device).manual_seed(self.prev_seed),
                guidance_scale=guidance,
                height=768,  # Higher resolution than default 512
                width=768
            ).images[0]
        
        # Convert back to OpenCV format
        result_cv = cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
        return result_cv
