"""
Video segmentation for segment-based processing
Split video into approach → hold → exit segments
"""

import numpy as np
from typing import List, Tuple, Dict


class VideoSegmenter:
    """Split video into segments based on motion analysis"""
    
    def __init__(self, num_segments: int = 3, overlap_frames: int = 5):
        self.num_segments = num_segments
        self.overlap_frames = overlap_frames
    
    def segment_video(
        self, 
        total_frames: int,
        pose_velocities: np.ndarray = None
    ) -> List[Dict]:
        """
        Create segment plan for video processing
        
        Args:
            total_frames: Total number of frames
            pose_velocities: Optional pose velocity data to find natural cuts
            
        Returns:
            List of segment dictionaries with start/end frames
        """
        if pose_velocities is not None:
            return self._segment_by_motion(total_frames, pose_velocities)
        else:
            return self._segment_uniform(total_frames)
    
    def _segment_uniform(self, total_frames: int) -> List[Dict]:
        """Simple uniform segmentation"""
        segment_length = total_frames // self.num_segments
        segments = []
        
        for i in range(self.num_segments):
            start = i * segment_length
            end = (i + 1) * segment_length if i < self.num_segments - 1 else total_frames
            
            # Add overlap
            if i > 0:
                start = max(0, start - self.overlap_frames)
            if i < self.num_segments - 1:
                end = min(total_frames, end + self.overlap_frames)
            
            segments.append({
                'segment_id': i,
                'start_frame': start,
                'end_frame': end,
                'type': ['approach', 'hold', 'exit'][i] if self.num_segments == 3 else f'seg_{i}'
            })
        
        return segments
    
    def _segment_by_motion(
        self, 
        total_frames: int, 
        pose_velocities: np.ndarray
    ) -> List[Dict]:
        """
        Segment based on motion patterns
        Find natural cut points at low-motion moments
        """
        # Find low-motion frames as potential cut points
        velocity_smoothed = self._smooth_signal(pose_velocities, window=15)
        
        # Divide into rough thirds
        third = total_frames // 3
        
        # Find best cut point in each third (excluding edges)
        cut_points = []
        for i in range(1, self.num_segments):
            search_start = i * third - third // 4
            search_end = i * third + third // 4
            search_start = max(0, min(search_start, total_frames - 1))
            search_end = max(0, min(search_end, total_frames - 1))
            
            if search_start < search_end:
                search_region = velocity_smoothed[search_start:search_end]
                local_min_idx = np.argmin(search_region)
                cut_frame = search_start + local_min_idx
                cut_points.append(cut_frame)
        
        # Build segments
        segments = []
        boundaries = [0] + cut_points + [total_frames]
        
        for i in range(self.num_segments):
            start = boundaries[i]
            end = boundaries[i + 1]
            
            # Add overlap
            if i > 0:
                start = max(0, start - self.overlap_frames)
            if i < self.num_segments - 1:
                end = min(total_frames, end + self.overlap_frames)
            
            segments.append({
                'segment_id': i,
                'start_frame': start,
                'end_frame': end,
                'type': ['approach', 'hold', 'exit'][i] if self.num_segments == 3 else f'seg_{i}',
                'cut_quality': 'motion_based'
            })
        
        return segments
    
    def _smooth_signal(self, signal: np.ndarray, window: int = 15) -> np.ndarray:
        """Smooth signal using moving average"""
        if len(signal) < window:
            return signal
        
        kernel = np.ones(window) / window
        return np.convolve(signal, kernel, mode='same')
    
    def get_segment_frames(
        self, 
        frames: List[np.ndarray], 
        segment: Dict
    ) -> List[np.ndarray]:
        """Extract frames for a specific segment"""
        start = segment['start_frame']
        end = segment['end_frame']
        return frames[start:end]
