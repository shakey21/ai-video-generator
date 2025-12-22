import warnings
warnings.filterwarnings("ignore", message=".*CUDA.*")

import cv2
import numpy as np
from typing import Tuple, Optional
from ultralytics import YOLO
import torch

class PersonDetector:
    def __init__(self):
        """Initialize YOLOv8 for accurate person detection"""
        print("Loading YOLOv8 person detector...")
        self.yolo = YOLO('yolov8m-seg.pt')  # Medium model for accuracy
        self.yolo.to('mps' if torch.backends.mps.is_available() else 'cpu')
        print("Person detector loaded")
        
        # Track previous frames for consistency
        self.prev_mask = None
        self.prev_bbox = None
    
    def detect_and_segment(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[Tuple]]:
        """
        Detect person and create high-quality segmentation mask
        
        Returns:
            mask: Binary mask of person (0-255)
            person_region: Bounding box (x, y, w, h) or None
        """
        h, w = frame.shape[:2]
        
        # Run YOLO detection
        results = self.yolo(frame, classes=[0], verbose=False)  # class 0 = person
        
        if len(results) > 0 and results[0].masks is not None:
            # Get the largest person (main subject)
            masks = results[0].masks.data.cpu()
            boxes = results[0].boxes.data.cpu()
            
            if len(masks) > 0:
                # Find largest person by bounding box area
                areas = [(boxes[i][2] - boxes[i][0]) * (boxes[i][3] - boxes[i][1]) 
                        for i in range(len(boxes))]
                largest_idx = np.argmax(areas)
                
                # Get mask and bbox
                mask_tensor = masks[largest_idx]
                mask = mask_tensor.numpy()
                
                # Resize mask to original frame size
                mask = cv2.resize(mask, (w, h))
                mask = (mask > 0.5).astype(np.uint8) * 255
                
                # Temporal smoothing for consistency
                if self.prev_mask is not None:
                    # Blend with previous frame
                    mask = cv2.addWeighted(mask, 0.7, self.prev_mask, 0.3, 0)
                    mask = (mask > 127).astype(np.uint8) * 255
                
                self.prev_mask = mask.copy()
                
                # Get bounding box
                box = boxes[largest_idx][:4].numpy()
                x, y, x2, y2 = map(int, box)
                person_region = (x, y, x2 - x, y2 - y)
                self.prev_bbox = person_region
                
                return mask, person_region
        
        # No person detected - use previous if available
        if self.prev_mask is not None:
            return self.prev_mask, self.prev_bbox
        
        # Fallback: empty mask
        return np.zeros((h, w), dtype=np.uint8), None
    
    def extract_pose(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract pose using YOLO pose estimation
        """
        # Use YOLO pose model
        pose_model = YOLO('yolov8m-pose.pt')
        pose_model.to('mps' if torch.backends.mps.is_available() else 'cpu')
        
        results = pose_model(frame, verbose=False)
        
        if len(results) > 0 and results[0].keypoints is not None:
            h, w = frame.shape[:2]
            pose_img = np.zeros((h, w, 3), dtype=np.uint8)
            
            # Get keypoints
            keypoints = results[0].keypoints.data[0].cpu().numpy()
            
            # Draw skeleton
            # COCO pose connections
            connections = [
                (0, 1), (0, 2), (1, 3), (2, 4),  # Head
                (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
                (5, 11), (6, 12), (11, 12),  # Torso
                (11, 13), (13, 15), (12, 14), (14, 16)  # Legs
            ]
            
            # Draw connections
            for conn in connections:
                if conn[0] < len(keypoints) and conn[1] < len(keypoints):
                    pt1 = tuple(map(int, keypoints[conn[0]][:2]))
                    pt2 = tuple(map(int, keypoints[conn[1]][:2]))
                    
                    if keypoints[conn[0]][2] > 0.5 and keypoints[conn[1]][2] > 0.5:
                        cv2.line(pose_img, pt1, pt2, (255, 255, 255), 3)
            
            # Draw joints
            for kp in keypoints:
                if kp[2] > 0.5:  # confidence threshold
                    cv2.circle(pose_img, tuple(map(int, kp[:2])), 5, (255, 255, 255), -1)
            
            return pose_img
        
        return None
    
    def cleanup(self):
        """Cleanup resources"""
        self.prev_mask = None
        self.prev_bbox = None
