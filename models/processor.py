import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
from .detector import PersonDetector
from .generator import ModelGenerator
from utils.video_utils import VideoReader, VideoWriter

class VideoProcessor:
    def __init__(self):
        self.detector = PersonDetector()
        self.generator = ModelGenerator()
        self.frame_cache = []  # For temporal smoothing
        self.cache_size = 3  # Number of frames to blend
    
    def replace_model(
        self,
        video_path: str,
        model_description: str,
        progress_callback=None
    ) -> str:
        """
        High-quality video processing with temporal consistency
        """
        video_path = Path(video_path)
        output_path = Path("outputs") / f"replaced_{video_path.stem}.mp4"
        
        # Open video
        reader = VideoReader(str(video_path))
        
        # Use high-quality codec
        writer = VideoWriter(
            str(output_path),
            fps=reader.fps,
            width=reader.width,
            height=reader.height,
            quality='high'
        )
        
        total_frames = reader.frame_count
        print(f"Processing {total_frames} frames at {reader.width}x{reader.height}")
        
        try:
            for i, frame in enumerate(tqdm(reader, total=total_frames, desc="Processing")):
                print(f"[Frame {i+1}/{total_frames}] Generating AI model...")
                
                if progress_callback:
                    progress_callback(
                        (i + 1) / total_frames,
                        desc=f"Frame {i+1}/{total_frames} - Generating..."
                    )
                
                # Detect person and pose
                mask, person_region = self.detector.detect_and_segment(frame)
                pose_image = self.detector.extract_pose(frame)
                
                if pose_image is not None and person_region is not None:
                    # Generate replacement (uses JSON config)
                    generated = self.generator.generate_replacement(pose_image)
                    
                    # Resize to match frame
                    if generated.shape[:2] != frame.shape[:2]:
                        generated = cv2.resize(
                            generated,
                            (frame.shape[1], frame.shape[0]),
                            interpolation=cv2.INTER_LANCZOS4  # High-quality resize
                        )
                    
                    # Create smooth mask
                    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(float) / 255.0
                    
                    # Feather edges for seamless blend
                    mask_3ch = cv2.GaussianBlur(mask_3ch, (21, 21), 0)
                    
                    # Composite with feathered edges
                    result = (
                        generated * mask_3ch + 
                        frame * (1 - mask_3ch)
                    ).astype(np.uint8)
                    
                    # Temporal smoothing for consistency
                    result = self._temporal_smooth(result)
                    
                else:
                    # No person detected
                    result = frame
                
                writer.write(result)
            
        finally:
            reader.release()
            writer.release()
            self.detector.cleanup()
            print(f"Output saved: {output_path}")
        
        return str(output_path)
    
    def _temporal_smooth(self, frame: np.ndarray) -> np.ndarray:
        """Apply temporal smoothing for frame consistency"""
        self.frame_cache.append(frame.copy())
        
        if len(self.frame_cache) > self.cache_size:
            self.frame_cache.pop(0)
        
        if len(self.frame_cache) == 1:
            return frame
        
        # Weighted average of recent frames
        weights = np.array([0.2, 0.3, 0.5])[:len(self.frame_cache)]
        weights = weights / weights.sum()
        
        smoothed = np.zeros_like(frame, dtype=float)
        for weight, cached_frame in zip(weights, self.frame_cache):
            smoothed += cached_frame * weight
        
        return smoothed.astype(np.uint8)
