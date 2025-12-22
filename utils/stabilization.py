"""
Video stabilization and camera motion extraction
Stabilize video before processing, then reapply motion at the end
"""

import cv2
import numpy as np
from typing import Tuple, List
import json


class VideoStabilizer:
    """Stabilize video using optical flow and motion smoothing"""
    
    def __init__(self):
        self.transforms = []
        self.smoothing_radius = 30  # frames to smooth over
        
    def stabilize_video(
        self, 
        frames: List[np.ndarray]
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Stabilize video and extract camera motion
        
        Returns:
            stabilized_frames: List of stabilized frames
            transforms: List of transform matrices to reapply motion later
        """
        if len(frames) < 2:
            return frames, [np.eye(3, dtype=np.float32) for _ in frames]
        
        # Extract transforms between consecutive frames
        transforms = self._extract_transforms(frames)
        
        # Smooth the trajectory
        smoothed_transforms = self._smooth_trajectory(transforms)
        
        # Apply smoothed transforms to stabilize
        stabilized_frames = self._apply_transforms(frames, smoothed_transforms)
        
        return stabilized_frames, transforms
    
    def _extract_transforms(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Extract transformation between consecutive frames"""
        transforms = [np.eye(3, dtype=np.float32)]  # First frame = identity
        
        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        
        for i in range(1, len(frames)):
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Detect feature points
            prev_pts = cv2.goodFeaturesToTrack(
                prev_gray,
                maxCorners=200,
                qualityLevel=0.01,
                minDistance=30,
                blockSize=3
            )
            
            if prev_pts is None:
                transforms.append(np.eye(3, dtype=np.float32))
                prev_gray = curr_gray
                continue
            
            # Calculate optical flow
            curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(
                prev_gray, curr_gray, prev_pts, None
            )
            
            # Filter good points
            idx = np.where(status == 1)[0]
            prev_pts = prev_pts[idx]
            curr_pts = curr_pts[idx]
            
            if len(prev_pts) < 10:
                transforms.append(np.eye(3, dtype=np.float32))
                prev_gray = curr_gray
                continue
            
            # Estimate affine transform
            transform = cv2.estimateAffinePartial2D(prev_pts, curr_pts)[0]
            
            if transform is None:
                transform = np.eye(2, 3, dtype=np.float32)
            
            # Convert to 3x3
            transform_3x3 = np.vstack([transform, [0, 0, 1]])
            transforms.append(transform_3x3)
            
            prev_gray = curr_gray
        
        return transforms
    
    def _smooth_trajectory(self, transforms: List[np.ndarray]) -> List[np.ndarray]:
        """Smooth camera trajectory using moving average"""
        # Convert transforms to trajectory (cumulative)
        trajectory = []
        cumulative = np.eye(3, dtype=np.float32)
        
        for transform in transforms:
            cumulative = cumulative @ transform
            trajectory.append(cumulative.copy())
        
        # Smooth trajectory
        smoothed_trajectory = []
        
        for i in range(len(trajectory)):
            start = max(0, i - self.smoothing_radius)
            end = min(len(trajectory), i + self.smoothing_radius + 1)
            
            # Average transforms in window
            window = trajectory[start:end]
            avg_transform = np.mean(window, axis=0)
            smoothed_trajectory.append(avg_transform)
        
        # Convert back to frame-to-frame transforms
        smoothed_transforms = [np.eye(3, dtype=np.float32)]
        
        for i in range(1, len(smoothed_trajectory)):
            # Transform from smoothed[i-1] to smoothed[i]
            transform = np.linalg.inv(smoothed_trajectory[i-1]) @ smoothed_trajectory[i]
            smoothed_transforms.append(transform)
        
        return smoothed_transforms
    
    def _apply_transforms(
        self, 
        frames: List[np.ndarray], 
        transforms: List[np.ndarray]
    ) -> List[np.ndarray]:
        """Apply transforms to stabilize frames"""
        stabilized = []
        h, w = frames[0].shape[:2]
        
        cumulative = np.eye(3, dtype=np.float32)
        
        for frame, transform in zip(frames, transforms):
            cumulative = cumulative @ transform
            
            # Apply inverse of cumulative transform
            transform_2x3 = np.linalg.inv(cumulative)[:2]
            
            stabilized_frame = cv2.warpAffine(
                frame,
                transform_2x3,
                (w, h),
                borderMode=cv2.BORDER_REPLICATE
            )
            
            stabilized.append(stabilized_frame)
        
        return stabilized
    
    def reapply_motion(
        self, 
        frames: List[np.ndarray], 
        transforms: List[np.ndarray]
    ) -> List[np.ndarray]:
        """Reapply original camera motion to stabilized frames"""
        unstabilized = []
        h, w = frames[0].shape[:2]
        
        for frame, transform in zip(frames, transforms):
            transform_2x3 = transform[:2]
            
            unstabilized_frame = cv2.warpAffine(
                frame,
                transform_2x3,
                (w, h),
                borderMode=cv2.BORDER_REPLICATE
            )
            
            unstabilized.append(unstabilized_frame)
        
        return unstabilized
    
    def save_transforms(self, transforms: List[np.ndarray], path: str):
        """Save transforms to JSON for later use"""
        transforms_list = [t.tolist() for t in transforms]
        with open(path, 'w') as f:
            json.dump(transforms_list, f)
    
    def load_transforms(self, path: str) -> List[np.ndarray]:
        """Load transforms from JSON"""
        with open(path, 'r') as f:
            transforms_list = json.load(f)
        return [np.array(t, dtype=np.float32) for t in transforms_list]
