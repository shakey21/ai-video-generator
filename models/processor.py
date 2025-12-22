import cv2
import numpy as np
import torch
import gc
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Optional
from .detector import PersonDetector
from .generator import ModelGenerator
from utils.video_utils import VideoReader, VideoWriter
from utils.stabilization import VideoStabilizer
from utils.segmentation import VideoSegmenter
from utils.foot_lock import FootLocker
from utils.background import BackgroundExtractor

class VideoProcessor:
    def __init__(self, use_stabilization: bool = True, use_segments: bool = True):
        self.detector = PersonDetector()
        self.generator = ModelGenerator()
        self.stabilizer = VideoStabilizer() if use_stabilization else None
        self.segmenter = VideoSegmenter(num_segments=3) if use_segments else None
        self.foot_locker = FootLocker()
        self.bg_extractor = BackgroundExtractor()
        self.prev_frame = None  # For optical flow
        self.prev_generated = None  # For temporal blending
    
    def replace_model(
        self,
        video_path: str,
        model_description: str,
        progress_callback=None,
        use_background_plate: bool = False
    ) -> str:
        """
        Photorealistic video processing with:
        - Camera stabilization
        - Segment-based generation
        - Foot locking
        - Temporal consistency
        - Background plate extraction
        """
        video_path = Path(video_path)
        output_path = Path("outputs") / f"replaced_{video_path.stem}.mp4"
        
        # Reset temporal state
        self.generator.reset_temporal_state()
        self.prev_frame = None
        self.prev_generated = None
        
        print(f"🎬 Loading video: {video_path}")
        
        # Load all frames for stabilization and segmentation
        reader = VideoReader(str(video_path))
        all_frames = []
        for frame in reader:
            all_frames.append(frame)
        reader.release()
        
        total_frames = len(all_frames)
        fps = reader.fps
        width, height = reader.width, reader.height
        
        print(f"📹 Loaded {total_frames} frames at {width}x{height} @ {fps}fps")
        
        # Step 1: Stabilize video if enabled
        camera_transforms = None
        if self.stabilizer:
            print("🔧 Stabilizing video...")
            all_frames, camera_transforms = self.stabilizer.stabilize_video(all_frames)
            print("✅ Video stabilized")
        
        # Step 2: Create segments if enabled
        if self.segmenter:
            print("✂️  Planning segments...")
            segments = self.segmenter.segment_video(total_frames)
            print(f"📊 Created {len(segments)} segments")
        else:
            segments = [{'segment_id': 0, 'start_frame': 0, 'end_frame': total_frames, 'type': 'full'}]
        
        # Step 3: Extract background plate if requested
        bg_plate = None
        if use_background_plate:
            print("🖼️  Extracting background plate...")
            # Quick mask extraction for background
            masks = []
            for frame in tqdm(all_frames[::5], desc="Extracting masks"):  # Sample every 5th frame
                mask, _ = self.detector.detect_and_segment(frame)
                masks.append(mask)
            bg_plate = self.bg_extractor.extract_median_background(all_frames[::5], masks)
            print("✅ Background plate extracted")
        
        print(f"🎨 Using multi-ControlNet (pose + depth + canny edges)")
        
        # Step 4: Process each segment
        all_processed_frames = [None] * total_frames
        
        for seg_idx, segment in enumerate(segments):
            start_frame = segment['start_frame']
            end_frame = segment['end_frame']
            seg_type = segment['type']
            
            print(f"\n🎬 Processing segment {seg_idx + 1}/{len(segments)}: {seg_type} (frames {start_frame}-{end_frame})")
            
            # Get segment frames
            segment_frames = all_frames[start_frame:end_frame]
            
            # Extract pose keypoints for segment (for foot locking)
            print("🦴 Extracting poses...")
            pose_keypoints = []
            for frame in segment_frames:
                _, keypoints = self.detector.extract_pose(frame, return_keypoints=True)
                pose_keypoints.append(keypoints)
            
            # Process segment frames
            processed_segment = self._process_segment(
                segment_frames,
                pose_keypoints,
                model_description,
                bg_plate,
                segment_id=seg_idx,
                progress_callback=progress_callback
            )
            
            # Store processed frames
            for i, processed_frame in enumerate(processed_segment):
                frame_idx = start_frame + i
                all_processed_frames[frame_idx] = processed_frame
        
        # Step 5: Handle overlaps (blend overlapping regions)
        final_frames = self._blend_segment_overlaps(all_processed_frames, segments)
        
        # Step 6: Reapply camera motion if stabilized
        if camera_transforms is not None:
            print("\n🎥 Reapplying camera motion...")
            final_frames = self.stabilizer.reapply_motion(final_frames, camera_transforms)
            print("✅ Camera motion reapplied")
        
        # Step 7: Write output video
        print("\n💾 Writing output video...")
        writer = VideoWriter(
            str(output_path),
            fps=fps,
            width=width,
            height=height,
            quality='high'
        )
        
        try:
            for frame in tqdm(final_frames, desc="Writing"):
                writer.write(frame)
        finally:
            writer.release()
            self.detector.cleanup()
            print(f"✅ Output saved: {output_path}")
        
        return str(output_path)
    
    def _process_segment(
        self,
        frames: List[np.ndarray],
        pose_keypoints: List[np.ndarray],
        model_description: str,
        bg_plate: np.ndarray,
        segment_id: int,
        progress_callback=None
    ) -> List[np.ndarray]:
        """Process a single segment of video"""
        processed_frames = []
        
        # Reset temporal state for new segment
        self.prev_frame = None
        self.prev_generated = None
        
        for i, frame in enumerate(tqdm(frames, desc=f"Segment {segment_id + 1}")):
            # Extract control signals
            mask, person_region = self.detector.detect_and_segment(frame)
            pose_image = self.detector.extract_pose(frame)
            depth_image = self.detector.extract_depth(frame)
            canny_image = self.detector.extract_canny(frame)
            
            if pose_image is not None and person_region is not None:
                # Generate replacement
                generated = self.generator.generate_replacement(
                    pose_image=pose_image,
                    depth_image=depth_image,
                    canny_image=canny_image,
                    original_frame=frame
                )
                
                # Apply temporal consistency
                if self.prev_frame is not None and self.prev_generated is not None:
                    generated = self._apply_optical_flow_consistency(
                        frame, self.prev_frame, generated, self.prev_generated
                    )
                
                # Composite
                if bg_plate is not None:
                    # Use background plate
                    result = self._composite_with_background(generated, bg_plate, mask)
                else:
                    # Use original background
                    result = self._composite_with_background(generated, frame, mask)
                
                self.prev_generated = generated.copy()
            else:
                result = frame
            
            self.prev_frame = frame.copy()
            processed_frames.append(result)
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
        
        # Apply foot locking to entire segment
        if pose_keypoints and all(kp is not None for kp in pose_keypoints):
            print("👣 Applying foot locking...")
            left_contacts, right_contacts = self.foot_locker.detect_foot_contacts(pose_keypoints)
            processed_frames = self.foot_locker.apply_foot_lock(
                processed_frames,
                pose_keypoints,
                left_contacts,
                right_contacts
            )
        
        return processed_frames
    
    def _blend_segment_overlaps(
        self,
        frames: List[np.ndarray],
        segments: List[Dict]
    ) -> List[np.ndarray]:
        """Blend overlapping regions between segments"""
        if len(segments) == 1:
            return frames
        
        blended = frames.copy()
        
        for i in range(len(segments) - 1):
            seg1 = segments[i]
            seg2 = segments[i + 1]
            
            # Find overlap region
            overlap_start = seg2['start_frame']
            overlap_end = min(seg1['end_frame'], seg2['start_frame'] + 5)  # 5 frame blend
            
            if overlap_start >= overlap_end:
                continue
            
            # Blend frames in overlap
            for frame_idx in range(overlap_start, overlap_end):
                if frames[frame_idx] is not None:
                    # Simple linear blend based on position in overlap
                    alpha = (frame_idx - overlap_start) / (overlap_end - overlap_start)
                    # Keep the later segment's frame (simpler approach)
                    # In production, could do actual blending
                    pass
        
        return blended

    
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
        
        # Create coordinate grids
        x_coords, y_coords = np.meshgrid(np.arange(w), np.arange(h))
        
        # Apply flow to get warped coordinates
        flow_map_x = (x_coords + flow[:, :, 0]).astype(np.float32)
        flow_map_y = (y_coords + flow[:, :, 1]).astype(np.float32)
        
        warped_prev = cv2.remap(
            prev_generated,
            flow_map_x,
            flow_map_y,
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        # Blend current with warped previous for temporal consistency
        # Use 70% current, 30% warped previous
        result = cv2.addWeighted(curr_generated, 0.7, warped_prev, 0.3, 0)
        
        return result
