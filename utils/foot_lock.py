"""
Foot locking / anti-slide system
Detect foot contact and prevent sliding during stance phase
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional


class FootLocker:
    """Prevent foot sliding by stabilizing ankles during contact"""
    
    def __init__(
        self, 
        velocity_threshold: float = 2.0,  # pixels per frame
        contact_height_threshold: float = 0.85  # relative to frame height
    ):
        self.velocity_threshold = velocity_threshold
        self.contact_height_threshold = contact_height_threshold
    
    def detect_foot_contacts(
        self, 
        pose_keypoints: List[np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect when feet are in contact with ground
        
        Args:
            pose_keypoints: List of pose keypoint arrays per frame
                           Expected: [..., left_ankle, right_ankle, ...]
                           
        Returns:
            left_contacts: Boolean array of left foot contacts
            right_contacts: Boolean array of right foot contacts
        """
        n_frames = len(pose_keypoints)
        left_contacts = np.zeros(n_frames, dtype=bool)
        right_contacts = np.zeros(n_frames, dtype=bool)
        
        # Extract ankle positions (assuming standard COCO format)
        # Left ankle = index 15, Right ankle = index 16
        left_ankle_idx = 15
        right_ankle_idx = 16
        
        left_ankles = []
        right_ankles = []
        
        for kpts in pose_keypoints:
            if kpts is not None and len(kpts) > right_ankle_idx:
                left_ankles.append(kpts[left_ankle_idx][:2])
                right_ankles.append(kpts[right_ankle_idx][:2])
            else:
                left_ankles.append(None)
                right_ankles.append(None)
        
        # Detect contacts based on velocity and height
        for i in range(1, n_frames):
            # Left foot
            if left_ankles[i] is not None and left_ankles[i-1] is not None:
                velocity = np.linalg.norm(left_ankles[i] - left_ankles[i-1])
                height_relative = left_ankles[i][1]  # y coordinate
                
                if velocity < self.velocity_threshold:
                    left_contacts[i] = True
            
            # Right foot
            if right_ankles[i] is not None and right_ankles[i-1] is not None:
                velocity = np.linalg.norm(right_ankles[i] - right_ankles[i-1])
                height_relative = right_ankles[i][1]
                
                if velocity < self.velocity_threshold:
                    right_contacts[i] = True
        
        # Extend contact zones (if in contact for 3+ frames, keep it)
        left_contacts = self._extend_contacts(left_contacts, min_length=3)
        right_contacts = self._extend_contacts(right_contacts, min_length=3)
        
        return left_contacts, right_contacts
    
    def apply_foot_lock(
        self, 
        frames: List[np.ndarray],
        pose_keypoints: List[np.ndarray],
        left_contacts: np.ndarray,
        right_contacts: np.ndarray
    ) -> List[np.ndarray]:
        """
        Apply foot locking to prevent sliding
        
        Stabilizes foot position during contact by warping the frame
        """
        locked_frames = []
        
        # Extract ankle positions
        left_ankle_idx = 15
        right_ankle_idx = 16
        
        for i, frame in enumerate(frames):
            if i == 0:
                locked_frames.append(frame.copy())
                continue
            
            kpts = pose_keypoints[i]
            prev_kpts = pose_keypoints[i-1]
            
            if kpts is None or prev_kpts is None:
                locked_frames.append(frame.copy())
                continue
            
            # Check if any foot is in contact
            left_contact = left_contacts[i]
            right_contact = right_contacts[i]
            
            if not left_contact and not right_contact:
                locked_frames.append(frame.copy())
                continue
            
            # Calculate stabilization transform
            src_points = []
            dst_points = []
            
            if left_contact and len(kpts) > left_ankle_idx:
                curr_ankle = kpts[left_ankle_idx][:2]
                prev_ankle = prev_kpts[left_ankle_idx][:2]
                src_points.append(curr_ankle)
                dst_points.append(prev_ankle)
            
            if right_contact and len(kpts) > right_ankle_idx:
                curr_ankle = kpts[right_ankle_idx][:2]
                prev_ankle = prev_kpts[right_ankle_idx][:2]
                src_points.append(curr_ankle)
                dst_points.append(prev_ankle)
            
            if len(src_points) == 0:
                locked_frames.append(frame.copy())
                continue
            
            # Apply minimal warp to stabilize feet
            locked_frame = self._stabilize_region(
                frame,
                locked_frames[-1],
                np.array(src_points),
                np.array(dst_points)
            )
            
            locked_frames.append(locked_frame)
        
        return locked_frames
    
    def _stabilize_region(
        self,
        current_frame: np.ndarray,
        previous_frame: np.ndarray,
        src_points: np.ndarray,
        dst_points: np.ndarray
    ) -> np.ndarray:
        """
        Apply subtle warp to stabilize specific points
        Uses weighted blend to avoid harsh warping
        """
        if len(src_points) < 2:
            # Simple translation
            offset = dst_points[0] - src_points[0]
            M = np.float32([[1, 0, offset[0]], [0, 1, offset[1]]])
        else:
            # Affine transform for 2+ points
            M = cv2.estimateAffinePartial2D(src_points.reshape(-1, 1, 2), 
                                           dst_points.reshape(-1, 1, 2))[0]
            
            if M is None:
                return current_frame.copy()
        
        h, w = current_frame.shape[:2]
        warped = cv2.warpAffine(current_frame, M, (w, h), 
                               borderMode=cv2.BORDER_REPLICATE)
        
        # Blend 70% warped + 30% original to keep natural motion
        result = cv2.addWeighted(warped, 0.7, current_frame, 0.3, 0)
        
        return result
    
    def _extend_contacts(self, contacts: np.ndarray, min_length: int = 3) -> np.ndarray:
        """Extend contact zones to avoid flickering"""
        extended = contacts.copy()
        
        # Find contact runs
        i = 0
        while i < len(extended):
            if extended[i]:
                # Start of contact run
                run_start = i
                while i < len(extended) and extended[i]:
                    i += 1
                run_end = i
                
                # Extend if long enough
                if run_end - run_start >= min_length:
                    # Extend by 1 frame on each side
                    if run_start > 0:
                        extended[run_start - 1] = True
                    if run_end < len(extended):
                        extended[run_end] = True
            else:
                i += 1
        
        return extended
