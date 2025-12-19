"""
Provider Adapters - Integration Layer

This module provides a clean adapter layer for image, video, and audio providers.
The core pipeline (Phase 1-5.5) uses these adapters instead of calling providers directly.

Architecture:
- Interfaces define the contract (interfaces.py)
- Mock providers provide offline functionality (mock_providers.py)
- Factory functions select providers based on configuration (get_*_provider)
- Real providers will be added in future EPs without touching core pipeline

Usage:
    from adapters import get_image_provider, get_video_provider, get_audio_provider
    
    image_provider = get_image_provider()
    image_url = image_provider.generate_image(prompt="A cat")
    
    video_provider = get_video_provider()
    result = video_provider.generate_video_segment(
        prompt="...",
        duration=8.0
    )
"""

from typing import Optional
import os
import warnings

from .interfaces import ImageProvider, VideoProvider, AudioProvider
from .mock_providers import MockImageProvider, MockVideoProvider, MockAudioProvider

# Provider selection via environment variables
# Default: "mock" (works offline)
# Future: "google", "veo", "openai", etc.
IMAGE_PROVIDER_TYPE = os.getenv("IMAGE_PROVIDER", "mock").lower()
VIDEO_PROVIDER_TYPE = os.getenv("VIDEO_PROVIDER", "mock").lower()
AUDIO_PROVIDER_TYPE = os.getenv("AUDIO_PROVIDER", "mock").lower()


def get_image_provider() -> ImageProvider:
    """
    Get the configured image provider.
    
    Returns:
        ImageProvider instance (default: MockImageProvider)
    
    Configuration:
        Set IMAGE_PROVIDER environment variable:
        - "mock" (default): Offline mock provider
        - "google": Google Vertex AI Imagen (requires VERTEX_API_KEY, VERTEX_PROJECT_ID)
        - Unknown values: Falls back to mock
    
    Fallback Behavior:
        If real provider fails to initialize (missing credentials, etc.),
        automatically falls back to MockImageProvider.
    """
    if IMAGE_PROVIDER_TYPE == "mock":
        return MockImageProvider()
    elif IMAGE_PROVIDER_TYPE == "google":
        try:
            from .google_providers import GoogleImageProvider
            return GoogleImageProvider()
        except ImportError as e:
            warnings.warn(
                f"Failed to import GoogleImageProvider: {e}. Falling back to mock.",
                UserWarning
            )
            return MockImageProvider()
        except Exception as e:
            # Catch ProviderAuthenticationError or any other initialization errors
            warnings.warn(
                f"Failed to initialize GoogleImageProvider: {e}. Falling back to mock.",
                UserWarning
            )
            return MockImageProvider()
    else:
        # Unknown provider type - fallback to mock
        warnings.warn(
            f"Unknown IMAGE_PROVIDER value: '{IMAGE_PROVIDER_TYPE}'. Falling back to mock.",
            UserWarning
        )
        return MockImageProvider()


def get_video_provider() -> VideoProvider:
    """
    Get the configured video provider.
    
    Returns:
        VideoProvider instance (default: MockVideoProvider)
    
    Configuration:
        Set VIDEO_PROVIDER environment variable:
        - "mock" (default): Offline mock provider
        - Future: "google", "veo", "runway", "pika", etc.
    """
    if VIDEO_PROVIDER_TYPE == "mock":
        return MockVideoProvider()
    else:
        # Future: Add real providers here
        # For now, fallback to mock if unknown provider
        return MockVideoProvider()


def get_audio_provider() -> AudioProvider:
    """
    Get the configured audio provider.
    
    Returns:
        AudioProvider instance (default: MockAudioProvider)
    
    Configuration:
        Set AUDIO_PROVIDER environment variable:
        - "mock" (default): Offline mock provider
        - Future: "google", "elevenlabs", "openai", etc.
    """
    if AUDIO_PROVIDER_TYPE == "mock":
        return MockAudioProvider()
    else:
        # Future: Add real providers here
        # For now, fallback to mock if unknown provider
        return MockAudioProvider()


__all__ = [
    "ImageProvider",
    "VideoProvider", 
    "AudioProvider",
    "get_image_provider",
    "get_video_provider",
    "get_audio_provider",
    "MockImageProvider",
    "MockVideoProvider",
    "MockAudioProvider",
    # Real providers (optional imports)
    # "GoogleImageProvider",  # Imported conditionally in get_image_provider()
]
