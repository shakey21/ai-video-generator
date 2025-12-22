import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from PIL import Image
import numpy as np
import cv2
from typing import List, Optional, Tuple
from .config_loader import ModelConfig

class ModelGenerator:
    def __init__(self):
        """Auto-detects best device with multi-ControlNet support"""
        # Auto-detect device
        if torch.cuda.is_available():
            self.device = "cuda"
            device_name = torch.cuda.get_device_name(0)
        elif torch.backends.mps.is_available():
            self.device = "mps"
            device_name = "Apple Silicon"
        else:
            self.device = "cpu"
            device_name = "CPU (slow)"
        
        self.pipe = None
        self.config = ModelConfig()
        self.model_name = "default_model"
        self.prev_seed = self.config.get_seed(self.model_name)
        self.prev_image = None  # For temporal consistency
        
        print(f"🚀 Using device: {self.device} ({device_name})")
        print(f"📦 Model: {self.config.get_model(self.model_name)['name']}")
    
    def load_model(self):
        """Load photorealistic SD + Multi-ControlNet"""
        if self.pipe is not None:
            return
        
        print("🔄 Loading photorealistic AI models...")
        print("   This will download ~7GB on first run")
        
        # Use fp16 for CUDA, fp32 for MPS
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        # Load multiple ControlNets for better guidance
        controlnet_pose = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_openpose",
            torch_dtype=dtype
        )
        controlnet_depth = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11f1p_sd15_depth",
            torch_dtype=dtype
        )
        controlnet_canny = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_canny",
            torch_dtype=dtype
        )
        
        controlnets = [controlnet_pose, controlnet_depth, controlnet_canny]
        
        # Get base model from config (Realistic Vision or custom)
        base_model = self.config.get_base_model(self.model_name)
        
        print(f"   Base model: {base_model}")
        
        # Load Stable Diffusion with multi-ControlNet
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='.*torch_dtype.*')
            warnings.filterwarnings('ignore', message='.*CLIPFeatureExtractor.*')
            self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
                base_model,
                controlnet=controlnets,
                torch_dtype=dtype,
                safety_checker=None
            )
        
        # Use high-quality scheduler for photorealism
        self.pipe.scheduler = UniPCMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )
        
        self.pipe.to(self.device)
        
        # Enable memory optimizations
        self.pipe.enable_attention_slicing()
        if hasattr(self.pipe.vae, 'enable_slicing'):
            self.pipe.vae.enable_slicing()
        elif hasattr(self.pipe, 'enable_vae_slicing'):
            self.pipe.enable_vae_slicing()
        
        # Device-specific optimizations
        if self.device == "mps":
            torch.mps.set_per_process_memory_fraction(0.85)
        elif self.device == "cuda":
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            if hasattr(self.pipe, 'enable_xformers_memory_efficient_attention'):
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                    print("   ✅ xFormers enabled for faster generation")
                except:
                    pass
        
        print("✅ Models loaded successfully")
    
    def generate_replacement(
        self,
        pose_image: np.ndarray,
        depth_image: np.ndarray,
        canny_image: np.ndarray,
        original_frame: Optional[np.ndarray] = None,
        prompt: str = None,
        num_inference_steps: int = None
    ) -> np.ndarray:
        """
        Generate photorealistic replacement using multi-ControlNet
        
        Args:
            pose_image: OpenPose skeleton
            depth_image: Depth map
            canny_image: Edge detection map
            original_frame: Original frame for temporal reference
            prompt: Optional override for model description
            num_inference_steps: Optional override for quality steps
        """
        self.load_model()
        
        # Get frame dimensions
        h, w = pose_image.shape[:2]
        
        # Prepare control images
        control_images = self._prepare_control_images(
            pose_image, depth_image, canny_image, h, w
        )
        
        # Get config values
        full_prompt = self.config.get_full_prompt(self.model_name)
        negative_prompt = self.config.get_negative_prompt(self.model_name)
        steps = num_inference_steps if num_inference_steps else self.config.get_inference_steps(self.model_name)
        guidance = self.config.get_guidance_scale(self.model_name)
        controlnet_scales = self.config.get_controlnet_scales(self.model_name)
        
        # Prepare conditioning scales
        scales = [
            controlnet_scales.get('pose', 0.8),
            controlnet_scales.get('depth', 0.6),
            controlnet_scales.get('canny', 0.5)
        ]
        
        # Generate dimensions (match video resolution)
        gen_h, gen_w = self._get_generation_size(h, w)
        
        # Use consistent seed for temporal consistency
        generator = torch.Generator(device=self.device).manual_seed(self.prev_seed)
        
        # Generate with multi-ControlNet
        with torch.inference_mode():
            result = self.pipe(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                image=control_images,
                num_inference_steps=steps,
                controlnet_conditioning_scale=scales,
                generator=generator,
                guidance_scale=guidance,
                height=gen_h,
                width=gen_w
            ).images[0]
        
        # Store for temporal consistency
        self.prev_image = result
        
        # Convert to OpenCV format
        result_cv = cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
        
        # Resize to match original if needed
        if result_cv.shape[:2] != (h, w):
            result_cv = cv2.resize(result_cv, (w, h), interpolation=cv2.INTER_LANCZOS4)
        
        return result_cv
    
    def _prepare_control_images(
        self, 
        pose: np.ndarray, 
        depth: np.ndarray, 
        canny: np.ndarray,
        target_h: int,
        target_w: int
    ) -> List[Image.Image]:
        """Prepare control images for pipeline"""
        images = []
        
        for img in [pose, depth, canny]:
            # Ensure correct size
            if img.shape[:2] != (target_h, target_w):
                img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            # Convert to PIL
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            pil_img = Image.fromarray(img)
            images.append(pil_img)
        
        return images
    
    def _get_generation_size(self, h: int, w: int) -> Tuple[int, int]:
        """Get optimal generation size (must be divisible by 8)"""
        # Keep original aspect ratio, round to nearest 64 for quality
        target = 768  # Good balance between quality and speed
        
        aspect = w / h
        if w > h:
            gen_w = target
            gen_h = int(target / aspect)
        else:
            gen_h = target
            gen_w = int(target * aspect)
        
        # Round to nearest 64 (SD works best with this)
        gen_h = (gen_h // 64) * 64
        gen_w = (gen_w // 64) * 64
        
        # Ensure minimum size
        gen_h = max(gen_h, 512)
        gen_w = max(gen_w, 512)
        
        return gen_h, gen_w
    
    def reset_temporal_state(self):
        """Reset temporal consistency between videos"""
        self.prev_image = None
