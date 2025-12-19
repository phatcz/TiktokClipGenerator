"""
Provider Interfaces - Abstract Base Classes

Defines the contract that all providers (mock and real) must implement.
This ensures the core pipeline can work with any provider without modification.

All providers must implement these interfaces to be compatible with the pipeline.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


# ==================== Error Types ====================

class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class ProviderTimeoutError(ProviderError):
    """Provider request timed out"""
    pass


class ProviderQuotaExceededError(ProviderError):
    """Provider quota/rate limit exceeded"""
    pass


class ProviderAuthenticationError(ProviderError):
    """Provider authentication failed"""
    pass


class ProviderValidationError(ProviderError):
    """Provider input validation failed"""
    pass


# ==================== Image Provider ====================

@dataclass
class ImageGenerationRequest:
    """Request for image generation"""
    prompt: str
    width: int = 1024
    height: int = 1024
    aspect_ratio: str = "1:1"  # "1:1", "16:9", "9:16", etc.
    style: Optional[str] = None
    quality: str = "standard"  # "standard", "hd"
    num_images: int = 1  # For batch generation


@dataclass
class ImageGenerationResult:
    """Result from image generation"""
    success: bool
    image_url: Optional[str] = None  # URL or file path
    image_path: Optional[str] = None  # Local file path (if downloaded)
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ImageProvider(ABC):
    """
    Interface for image generation providers.
    
    All image providers must implement:
    - generate_image(): Single image generation
    - generate_images(): Batch image generation (optional, can call generate_image multiple times)
    """
    
    @abstractmethod
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate a single image.
        
        Args:
            request: Image generation request with prompt and parameters
            
        Returns:
            ImageGenerationResult with success status and image URL/path
            
        Raises:
            ProviderError: For provider-specific errors
            ProviderTimeoutError: If request times out
            ProviderQuotaExceededError: If quota exceeded
            ProviderAuthenticationError: If authentication fails
        """
        pass
    
    def generate_images(self, requests: List[ImageGenerationRequest]) -> List[ImageGenerationResult]:
        """
        Generate multiple images (batch).
        
        Default implementation calls generate_image() for each request.
        Providers can override for optimized batch processing.
        
        Args:
            requests: List of image generation requests
            
        Returns:
            List of ImageGenerationResult (one per request)
        """
        return [self.generate_image(req) for req in requests]


# ==================== Video Provider ====================

@dataclass
class VideoGenerationRequest:
    """Request for video segment generation"""
    prompt: str
    duration: float = 8.0  # Duration in seconds (Phase 5 contract: always 8.0)
    start_keyframe_path: Optional[str] = None  # Path to start keyframe image
    end_keyframe_path: Optional[str] = None  # Path to end keyframe image
    resolution: str = "720p"  # "480p", "720p", "1080p"
    fps: int = 30
    style: Optional[str] = None
    motion_type: str = "smooth"  # "smooth", "dynamic", "static"
    camera_movement: str = "none"  # "none", "zoom_in", "zoom_out", "pan_left", etc.


@dataclass
class VideoGenerationResult:
    """Result from video generation"""
    success: bool
    video_path: Optional[str] = None  # Path to generated video file
    duration: float = 8.0  # Actual duration (should match request)
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VideoProvider(ABC):
    """
    Interface for video generation providers.
    
    All video providers must implement:
    - generate_video_segment(): Generate a single video segment (8 seconds)
    """
    
    @abstractmethod
    def generate_video_segment(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """
        Generate a single video segment.
        
        Args:
            request: Video generation request with prompt, duration, keyframes, etc.
            
        Returns:
            VideoGenerationResult with success status and video path
            
        Raises:
            ProviderError: For provider-specific errors
            ProviderTimeoutError: If request times out (video generation can be slow)
            ProviderQuotaExceededError: If quota exceeded
            ProviderAuthenticationError: If authentication fails
        """
        pass


# ==================== Audio Provider ====================

@dataclass
class AudioGenerationRequest:
    """Request for audio generation"""
    text: str  # Text for voiceover
    voice_id: Optional[str] = None  # Voice identifier (provider-specific)
    language: str = "th"  # Language code
    speed: float = 1.0  # Speech speed multiplier
    emotion: Optional[str] = None  # "neutral", "happy", "excited", etc.
    audio_type: str = "voiceover"  # "voiceover", "sfx", "music"


@dataclass
class AudioGenerationResult:
    """Result from audio generation"""
    success: bool
    audio_path: Optional[str] = None  # Path to generated audio file
    duration: Optional[float] = None  # Audio duration in seconds
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AudioProvider(ABC):
    """
    Interface for audio generation providers.
    
    All audio providers must implement:
    - generate_voiceover(): Generate voiceover from text
    - generate_sfx(): Generate sound effects (optional, can return mock)
    """
    
    @abstractmethod
    def generate_voiceover(self, request: AudioGenerationRequest) -> AudioGenerationResult:
        """
        Generate voiceover from text.
        
        Args:
            request: Audio generation request with text, voice, language, etc.
            
        Returns:
            AudioGenerationResult with success status and audio path
            
        Raises:
            ProviderError: For provider-specific errors
            ProviderTimeoutError: If request times out
            ProviderQuotaExceededError: If quota exceeded
            ProviderAuthenticationError: If authentication fails
        """
        pass
    
    def generate_sfx(self, description: str, duration: float = 2.0) -> AudioGenerationResult:
        """
        Generate sound effect.
        
        Default implementation returns mock result.
        Providers can override for real SFX generation.
        
        Args:
            description: Description of the sound effect
            duration: Duration in seconds
            
        Returns:
            AudioGenerationResult (mock by default)
        """
        # Default: return mock result
        return AudioGenerationResult(
            success=False,
            error="SFX generation not implemented (mock mode)"
        )


__all__ = [
    "ProviderError",
    "ProviderTimeoutError",
    "ProviderQuotaExceededError",
    "ProviderAuthenticationError",
    "ProviderValidationError",
    "ImageProvider",
    "ImageGenerationRequest",
    "ImageGenerationResult",
    "VideoProvider",
    "VideoGenerationRequest",
    "VideoGenerationResult",
    "AudioProvider",
    "AudioGenerationRequest",
    "AudioGenerationResult",
]
