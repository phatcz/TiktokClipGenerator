"""
Mock Providers - Offline Implementations

Mock implementations of all provider interfaces.
These work offline and return mock data for development and testing.

These are the default providers and will be used when:
- IMAGE_PROVIDER=mock (or not set)
- VIDEO_PROVIDER=mock (or not set)
- AUDIO_PROVIDER=mock (or not set)
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from .interfaces import (
    ImageProvider,
    ImageGenerationRequest,
    ImageGenerationResult,
    VideoProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    AudioProvider,
    AudioGenerationRequest,
    AudioGenerationResult,
)


class MockImageProvider(ImageProvider):
    """
    Mock image provider that works offline.
    
    Returns mock image URLs/paths without calling any real API.
    Used for development, testing, and as fallback.
    """
    
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate a mock image URL/path.
        
        In real implementation, this would:
        1. Call provider API (Google Imagen, DALL-E, etc.)
        2. Download image bytes
        3. Save to local file
        4. Return file path
        
        For now, returns a mock URL or creates placeholder file.
        """
        # Create mock image ID from prompt hash
        image_id = abs(hash(request.prompt)) % 1000000
        
        # Option 1: Return mock URL (for display purposes)
        mock_url = f"https://mock-images.example.com/generated/{image_id}.jpg"
        
        # Option 2: Create placeholder file (if output directory exists)
        output_dir = "output/images"
        if os.path.exists(output_dir) or os.path.exists("output"):
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"mock_image_{image_id}_{timestamp}_{unique_id}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # Create empty placeholder file (real implementation would save image bytes)
            with open(filepath, "w") as f:
                f.write("# Mock image placeholder\n")
            
            return ImageGenerationResult(
                success=True,
                image_url=mock_url,
                image_path=filepath,
                metadata={
                    "provider": "mock",
                    "prompt": request.prompt,
                    "width": request.width,
                    "height": request.height,
                    "generated_at": timestamp,
                }
            )
        
        # Return URL only if output directory doesn't exist
        return ImageGenerationResult(
            success=True,
            image_url=mock_url,
            metadata={
                "provider": "mock",
                "prompt": request.prompt,
                "width": request.width,
                "height": request.height,
            }
        )


class MockVideoProvider(VideoProvider):
    """
    Mock video provider that works offline.
    
    Returns mock video paths without calling any real API.
    Used for development, testing, and as fallback.
    """
    
    def generate_video_segment(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """
        Generate a mock video path.
        
        In real implementation, this would:
        1. Call provider API (Google Veo, RunwayML, etc.)
        2. Send prompt, keyframes, parameters
        3. Wait for video generation (can take minutes)
        4. Download video file
        5. Return file path
        
        For now, returns a mock file path.
        """
        # Create mock video ID from prompt hash
        video_id = abs(hash(request.prompt)) % 1000000
        
        # Create output directory
        output_dir = "output/segments"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"mock_segment_{video_id}_{timestamp}_{unique_id}.mp4"
        filepath = os.path.join(output_dir, filename)
        
        # Create empty placeholder file (real implementation would save video bytes)
        with open(filepath, "w") as f:
            f.write("# Mock video segment placeholder\n")
        
        return VideoGenerationResult(
            success=True,
            video_path=filepath,
            duration=request.duration,  # Return requested duration
            metadata={
                "provider": "mock",
                "prompt": request.prompt,
                "duration": request.duration,
                "resolution": request.resolution,
                "start_keyframe": request.start_keyframe_path,
                "end_keyframe": request.end_keyframe_path,
                "motion_type": request.motion_type,
                "camera_movement": request.camera_movement,
                "generated_at": timestamp,
            }
        )


class MockAudioProvider(AudioProvider):
    """
    Mock audio provider that works offline.
    
    Returns mock audio paths without calling any real API.
    Used for development, testing, and as fallback.
    """
    
    def generate_voiceover(self, request: AudioGenerationRequest) -> AudioGenerationResult:
        """
        Generate a mock voiceover path.
        
        In real implementation, this would:
        1. Call provider API (Google TTS, ElevenLabs, OpenAI TTS, etc.)
        2. Send text, voice, language parameters
        3. Receive audio bytes
        4. Save to file
        5. Return file path
        
        For now, returns a mock file path.
        """
        # Create mock audio ID from text hash
        audio_id = abs(hash(request.text)) % 1000000
        
        # Create output directory
        output_dir = "output/audio"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"mock_voiceover_{audio_id}_{timestamp}_{unique_id}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        # Create empty placeholder file (real implementation would save audio bytes)
        with open(filepath, "w") as f:
            f.write("# Mock voiceover placeholder\n")
        
        # Estimate duration (rough: ~150 words per minute)
        word_count = len(request.text.split())
        estimated_duration = (word_count / 150) * 60 / request.speed
        
        return AudioGenerationResult(
            success=True,
            audio_path=filepath,
            duration=estimated_duration,
            metadata={
                "provider": "mock",
                "text": request.text,
                "voice_id": request.voice_id,
                "language": request.language,
                "speed": request.speed,
                "emotion": request.emotion,
                "generated_at": timestamp,
            }
        )
    
    def generate_sfx(self, description: str, duration: float = 2.0) -> AudioGenerationResult:
        """
        Generate mock sound effect.
        
        Returns mock result (SFX generation not implemented in mock mode).
        """
        return AudioGenerationResult(
            success=False,
            error="SFX generation not implemented in mock mode",
            metadata={
                "provider": "mock",
                "description": description,
                "duration": duration,
            }
        )


__all__ = [
    "MockImageProvider",
    "MockVideoProvider",
    "MockAudioProvider",
]
