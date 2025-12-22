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
        High-quality video writer with H.264 codec
        
        Args:
            quality: 'high' for maximum quality
        """
        # Use FFmpeg via OpenCV for better quality control
        # Try H.264 codecs in order of preference
        codecs = [
            ('avc1', 'H.264 AVC'),
            ('H264', 'H.264'),
            ('X264', 'x264'),
            ('mp4v', 'MPEG-4 fallback')
        ]
        
        self.writer = None
        self.output_path = output_path
        
        for codec, name in codecs:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            # Higher quality parameters
            writer = cv2.VideoWriter(
                output_path, 
                fourcc, 
                fps, 
                (width, height),
                params=[
                    cv2.VIDEOWRITER_PROP_QUALITY, 100,  # Maximum quality
                ]
            )
            if writer.isOpened():
                self.writer = writer
                print(f"Using {name} codec for high-quality output")
                break
            writer.release()
        
        if self.writer is None or not self.writer.isOpened():
            raise ValueError(f"Cannot create video writer: {output_path}")
    
    def write(self, frame):
        self.writer.write(frame)
    
    def release(self):
        self.writer.release()
