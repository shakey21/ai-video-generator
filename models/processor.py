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
        self.prev_frame = None  # For optical flow
        self.prev_generated = None  # For temporal blending
    
    def replace_model(
        self,
        video_path: str,
        model_description: str,
        progress_callback=None
    ) -> str:
        """
        Photorealistic video processing with multi-ControlNet and temporal consistency
        """
        video_path = Path(video_path)
        output_path = Path("outputs") / f"replaced_{video_path.stem}.mp4"
        
        # Reset temporal state
        self.generator.reset_temporal_state()
        self.prev_frame = None
        self.prev_generated = None
        
        # Open video
        reader = VideoReader(str(video_path))
        
        # Output at original video resolution with high quality codec
        writer = VideoWriter(
            str(output_path),
            fps=reader.fps,
            width=reader.width,
            height=reader.height,
            quality='high'
        )
        
        total_frames = reader.frame_count
        print(f"🎬 Processing {total_frames} frames at {reader.width}x{reader.height}")
        print(f"🎨 Using multi-ControlNet (pose + depth + canny edges)")
        
        try:
            for i, frame in enumerate(tqdm(reader, total=total_frames, desc="Processing")):
                
                if progress_callback:
                    progress_callback(
                        (i + 1) / total_frames,
                        desc=f"Frame {i+1}/{total_frames} - AI Generation..."
                    )
                
                # Extract all control signals
                mask, person_region = self.detector.detect_and_segment(frame)
                pose_image = self.detector.extract_pose(frame)
                depth_image = self.detector.extract_depth(frame)
                canny_image = self.detector.extract_canny(frame)
                
                if pose_image is not None and person_region is not None:
                    # Generate replacement with multi-ControlNet
                    generated = self.generator.generate_replacement(
                        pose_image=pose_image,
                        depth_image=depth_image,
                        canny_image=canny_image,
                        original_frame=frame
                    )
                    
                    # Apply temporal consistency with optical flow
                    if self.prev_frame is not None and self.prev_generated is not None:
                        generated = self._apply_optical_flow_consistency(
                            frame, self.prev_frame, generated, self.prev_generated
                        )
                    
                    # High-quality compositing
                    result = self._composite_with_background(
                        generated, frame, mask
                    )
                    
                    # Store for next frame
                    self.prev_generated = generated.copy()
                    
                else:
                    # No person detected
                    result = frame
                
                self.prev_frame = frame.copy()
                writer.write(result)
            
        finally:
            reader.release()
            writer.release()
            self.detector.cleanup()
            print(f"✅ Output saved: {output_path}")
        
        return str(output_path)
    
    def _composite_with_background(
        self, 
        generated: np.ndarray, 
        original: np.ndarray, 
        mask: np.ndarray
    ) -> np.ndarray:
        """High-quality compositing with feathered edges"""
        # Convert mask to 3-channel float
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(float) / 255.0
        
        # Apply heavy feathering for seamless blend
        mask_3ch = cv2.GaussianBlur(mask_3ch, (31, 31), 0)
        
        # Composite
        result = (
            generated * mask_3ch + 
            original * (1 - mask_3ch)
        ).astype(np.uint8)
        
        return result
    
    def _apply_optical_flow_consistency(
        self,
        curr_frame: np.ndarray,
        prev_frame: np.ndarray,
        curr_generated: np.ndarray,
        prev_generated: np.ndarray
    ) -> np.ndarray:
        """Apply optical flow to ensure temporal consistency"""
        
        # Calculate optical flow between frames
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
        # Dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray,
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Warp previous generated frame using flow
        h, w = flow.shape[:2]
        flow_map = np.column_stack([
            (np.arange(w) + flow[:, :, 0].flatten()).astype(np.float32),
            (np.arange(h).repeat(w) + flow[:, :, 1].flatten()).astype(np.float32)
        ]).reshape(h, w, 2)
        
        warped_prev = cv2.remap(
            prev_generated,
            flow_map,
            None,
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        # Blend current with warped previous for temporal consistency
        # Use 70% current, 30% warped previous
        result = cv2.addWeighted(curr_generated, 0.7, warped_prev, 0.3, 0)
        
        return result
