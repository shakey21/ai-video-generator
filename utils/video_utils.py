import cv2
from typing import Iterator

class VideoReader:
    def __init__(self, video_path: str):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
            
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def __iter__(self) -> Iterator:
        return self
    
    def __next__(self):
        ret, frame = self.cap.read()
        if not ret:
            raise StopIteration
        return frame
    
    def release(self):
        self.cap.release()

class VideoWriter:
    def __init__(self, output_path: str, fps: int, width: int, height: int, quality='high'):
        """
        High-quality video writer
        
        Args:
            quality: 'high' for H.264 high quality, 'medium' for faster encoding
        """
        if quality == 'high':
            # H.264 codec with high quality
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not self.writer.isOpened():
            raise ValueError(f"Cannot create video writer: {output_path}")
    
    def write(self, frame):
        self.writer.write(frame)
    
    def release(self):
        self.writer.release()
