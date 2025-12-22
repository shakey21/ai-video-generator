"""
Background plate extraction
Remove person from video to create clean background plate
"""

import cv2
import numpy as np
from typing import List
import torch


class BackgroundExtractor:
    """Extract clean background plate by inpainting person region"""
    
    def __init__(self):
        self.inpaint_radius = 3
    
    def extract_background_plate(
        self,
        frames: List[np.ndarray],
        person_masks: List[np.ndarray],
        method: str = 'telea'
    ) -> List[np.ndarray]:
        """
        Create background plate by inpainting person regions
        
        Args:
            frames: List of video frames
            person_masks: Binary masks of person (white = person, black = background)
            method: 'telea' or 'ns' (Navier-Stokes)
            
        Returns:
            List of background frames with person removed
        """
        bg_frames = []
        
        inpaint_flag = cv2.INPAINT_TELEA if method == 'telea' else cv2.INPAINT_NS
        
        for frame, mask in zip(frames, person_masks):
            # Dilate mask slightly to ensure full removal
            kernel = np.ones((5, 5), np.uint8)
            mask_dilated = cv2.dilate(mask, kernel, iterations=2)
            
            # Inpaint
            bg_frame = cv2.inpaint(
                frame,
                mask_dilated,
                self.inpaint_radius,
                inpaint_flag
            )
            
            bg_frames.append(bg_frame)
        
        # Temporal smoothing to reduce flickering
        bg_frames = self._temporal_smooth(bg_frames, person_masks)
        
        return bg_frames
    
    def extract_median_background(
        self,
        frames: List[np.ndarray],
        person_masks: List[np.ndarray],
        sample_rate: int = 5
    ) -> np.ndarray:
        """
        Extract static background using temporal median
        Works best for videos with camera motion but static background
        
        Args:
            frames: List of video frames
            person_masks: Binary masks of person
            sample_rate: Sample every Nth frame for efficiency
            
        Returns:
            Single background plate image
        """
        # Sample frames
        sampled_frames = frames[::sample_rate]
        sampled_masks = person_masks[::sample_rate]
        
        h, w = frames[0].shape[:2]
        bg_accumulator = np.zeros((h, w, 3), dtype=np.float64)
        weight_accumulator = np.zeros((h, w), dtype=np.float64)
        
        for frame, mask in zip(sampled_frames, sampled_masks):
            # Inverse mask (1 where background, 0 where person)
            bg_mask = (mask == 0).astype(float)
            
            # Accumulate background pixels
            for c in range(3):
                bg_accumulator[:, :, c] += frame[:, :, c] * bg_mask
            
            weight_accumulator += bg_mask
        
        # Avoid division by zero
        weight_accumulator = np.maximum(weight_accumulator, 1.0)
        
        # Compute median background
        bg_plate = bg_accumulator / weight_accumulator[:, :, np.newaxis]
        bg_plate = bg_plate.astype(np.uint8)
        
        # Inpaint any remaining person regions
        person_region = (weight_accumulator < len(sampled_frames) * 0.3).astype(np.uint8) * 255
        bg_plate = cv2.inpaint(bg_plate, person_region, 10, cv2.INPAINT_TELEA)
        
        return bg_plate
    
    def _temporal_smooth(
        self,
        frames: List[np.ndarray],
        masks: List[np.ndarray],
        window: int = 3
    ) -> List[np.ndarray]:
        """
        Apply temporal smoothing to background to reduce flickering
        Only smooth background regions (not person)
        """
        smoothed = []
        
        for i, (frame, mask) in enumerate(zip(frames, masks)):
            # Collect window of frames
            start = max(0, i - window // 2)
            end = min(len(frames), i + window // 2 + 1)
            
            window_frames = frames[start:end]
            window_masks = masks[start:end]
            
            # Average background regions only
            bg_sum = np.zeros_like(frame, dtype=np.float32)
            bg_count = np.zeros(frame.shape[:2], dtype=np.float32)
            
            for wf, wm in zip(window_frames, window_masks):
                bg_mask = (wm == 0).astype(float)
                bg_sum += wf * bg_mask[:, :, np.newaxis]
                bg_count += bg_mask
            
            bg_count = np.maximum(bg_count, 1.0)
            bg_avg = (bg_sum / bg_count[:, :, np.newaxis]).astype(np.uint8)
            
            # Blend: use averaged background where mask is 0
            bg_mask_3ch = (mask == 0)[:, :, np.newaxis]
            result = np.where(bg_mask_3ch, bg_avg, frame)
            
            smoothed.append(result.astype(np.uint8))
        
        return smoothed
