"""
Video processing service for P&ID analysis.
Extracts frames from video uploads and processes them through the analysis pipeline.
"""

import cv2
import os
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from PIL import Image
import tempfile
import uuid

class VideoProcessor:
    """
    Video processing service for extracting and analyzing frames from P&ID videos.
    """
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif']
        self.min_frame_quality = 0.3  # Minimum quality threshold for frame selection
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if the video format is supported."""
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.supported_formats
    
    def extract_frames(self, video_path: str, max_frames: int = 10) -> List[Dict[str, Any]]:
        """
        Extract key frames from a video file.
        
        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of frame information dictionaries
        """
        frames = []
        
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            # Calculate frame sampling interval
            if total_frames <= max_frames:
                frame_indices = list(range(total_frames))
            else:
                # Sample frames evenly across the video
                frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
            
            # Extract frames
            for i, frame_idx in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Calculate frame quality (blur detection)
                    quality = self._calculate_frame_quality(frame)
                    
                    # Save frame to temporary file
                    frame_filename = f"frame_{uuid.uuid4().hex}.png"
                    frame_path = os.path.join(tempfile.gettempdir(), frame_filename)
                    
                    # Convert BGR to RGB and save
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_pil.save(frame_path)
                    
                    frames.append({
                        'frame_index': frame_idx,
                        'timestamp': frame_idx / fps if fps > 0 else 0,
                        'quality_score': quality,
                        'file_path': frame_path,
                        'filename': frame_filename,
                        'width': frame.shape[1],
                        'height': frame.shape[0]
                    })
            
            cap.release()
            
            # Sort frames by quality and return the best ones
            frames.sort(key=lambda x: x['quality_score'], reverse=True)
            
            return frames
            
        except Exception as e:
            print(f"Error extracting frames from video: {e}")
            return []
    
    def _calculate_frame_quality(self, frame: np.ndarray) -> float:
        """
        Calculate frame quality using Laplacian variance (blur detection).
        Higher values indicate sharper images.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 range (empirically determined thresholds)
            quality = min(laplacian_var / 1000.0, 1.0)
            
            return quality
            
        except Exception:
            return 0.0
    
    def select_best_frame(self, frames: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Select the best frame from a list of extracted frames.
        
        Args:
            frames: List of frame information dictionaries
            
        Returns:
            Best frame information or None
        """
        if not frames:
            return None
        
        # Filter frames by minimum quality
        good_frames = [f for f in frames if f['quality_score'] >= self.min_frame_quality]
        
        if not good_frames:
            # If no frames meet quality threshold, return the best available
            good_frames = frames
        
        # Return the frame with highest quality
        return max(good_frames, key=lambda x: x['quality_score'])
    
    def extract_key_frames(self, video_path: str, num_frames: int = 3) -> List[Dict[str, Any]]:
        """
        Extract multiple key frames for analysis.
        
        Args:
            video_path: Path to the video file
            num_frames: Number of key frames to extract
            
        Returns:
            List of key frame information dictionaries
        """
        frames = self.extract_frames(video_path, max_frames=num_frames * 3)
        
        if not frames:
            return []
        
        # Select the best frames
        key_frames = []
        for frame in frames[:num_frames]:
            if frame['quality_score'] >= self.min_frame_quality:
                key_frames.append(frame)
        
        return key_frames
    
    def cleanup_temp_files(self, frames: List[Dict[str, Any]]):
        """Clean up temporary frame files."""
        for frame in frames:
            try:
                if os.path.exists(frame['file_path']):
                    os.remove(frame['file_path'])
            except Exception as e:
                print(f"Error cleaning up temp file {frame['file_path']}: {e}")
    
    def process_video_for_analysis(self, video_path: str) -> Dict[str, Any]:
        """
        Process a video file and extract the best frame for P&ID analysis.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract frames
            frames = self.extract_frames(video_path, max_frames=15)
            
            if not frames:
                return {
                    'success': False,
                    'error': 'No frames could be extracted from the video',
                    'frame_path': None
                }
            
            # Select best frame
            best_frame = self.select_best_frame(frames)
            
            if not best_frame:
                return {
                    'success': False,
                    'error': 'No suitable frame found in the video',
                    'frame_path': None
                }
            
            return {
                'success': True,
                'frame_path': best_frame['file_path'],
                'frame_info': best_frame,
                'total_frames_extracted': len(frames),
                'quality_score': best_frame['quality_score']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing video: {str(e)}',
                'frame_path': None
            }

# Global video processor instance
video_processor = VideoProcessor()

def process_video_upload(video_path: str) -> Dict[str, Any]:
    """
    Convenience function to process a video upload.
    
    Args:
        video_path: Path to the uploaded video file
        
    Returns:
        Processing results dictionary
    """
    return video_processor.process_video_for_analysis(video_path)
