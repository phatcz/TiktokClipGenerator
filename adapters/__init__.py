"""
Provider Adapters - Integration Layer

This module provides a clean adapter layer for image, video, and audio providers.
The core pipeline (Phase 1-5.5) uses these adapters instead of calling providers directly.

Architecture:
- Interfaces define the contract (interfaces.py)
- Mock providers provide offline functionality (mock_providers.py)
- Real providers implement interfaces (google_providers.py, stub_providers.py)
- Strategy module handles multi-provider selection and fallback (strategy.py)
- Factory functions select providers based on configuration (get_*_provider)

Usage:
    from adapters import get_image_provider, get_video_provider, get_audio_provider
    
    # Explicit provider
    image_provider = get_image_provider()  # Uses IMAGE_PROVIDER env var
    
    # Auto strategy (tries providers in priority order)
    # Set IMAGE_PROVIDER=auto
    image_provider = get_image_provider()
"""

from typing import Optional, Tuple
import os
import warnings

from .interfaces import ImageProvider, VideoProvider, AudioProvider
from .mock_providers import MockImageProvider, MockVideoProvider, MockAudioProvider
from .strategy import (
    register_provider_factory,
    get_provider_with_fallback,
    get_auto_provider,
)

# Provider selection via environment variables
# Default: "mock" (works offline)
# Options: "mock", "google", "stub", "auto"
#   - "mock": Use mock provider (default, works offline)
#   - "google": Use Google Vertex AI Imagen (requires credentials)
#   - "stub": Use stub provider (placeholder, always fails gracefully)
#   - "auto": Try providers in priority order (google → stub → mock)
IMAGE_PROVIDER_TYPE = os.getenv("IMAGE_PROVIDER", "mock").lower()
VIDEO_PROVIDER_TYPE = os.getenv("VIDEO_PROVIDER", "mock").lower()
AUDIO_PROVIDER_TYPE = os.getenv("AUDIO_PROVIDER", "mock").lower()

# Register provider factories
def _factory_mock() -> ImageProvider:
    """Factory for MockImageProvider."""
    return MockImageProvider()

def _factory_google() -> ImageProvider:
    """Factory for GoogleImageProvider."""
    from .google_providers import GoogleImageProvider
    return GoogleImageProvider()

def _factory_stub() -> ImageProvider:
    """Factory for StubImageProvider."""
    from .stub_providers import StubImageProvider
    return StubImageProvider()

# Register all provider factories
register_provider_factory("mock", _factory_mock)
register_provider_factory("google", _factory_google)
register_provider_factory("stub", _factory_stub)


def get_image_provider() -> ImageProvider:
    """
    Get the configured image provider with robust fallback chain.
    
    Returns:
        ImageProvider instance (guaranteed to return MockImageProvider if all others fail)
    
    Configuration:
        Set IMAGE_PROVIDER environment variable:
        - "mock" (default): Offline mock provider
        - "google": Google Vertex AI Imagen (requires VERTEX_API_KEY, VERTEX_PROJECT_ID)
        - "stub": Stub provider (placeholder, always fails gracefully)
        - "auto": Try providers in priority order (google → stub → mock)
        - Unknown values: Falls back to mock
    
    Fallback Behavior:
        - Explicit provider: If initialization fails, falls back to mock
        - Auto strategy: Tries providers in priority order until one succeeds
        - All strategies: Always end in MockImageProvider (guaranteed)
    
    Provider Priority (for "auto" strategy):
        1. google (Google Vertex AI Imagen)
        2. stub (Stub provider - placeholder)
        3. mock (Final fallback - always succeeds)
    """
    if IMAGE_PROVIDER_TYPE == "mock":
        return MockImageProvider()
    elif IMAGE_PROVIDER_TYPE == "auto":
        # Auto strategy: try providers in priority order
        return get_auto_provider()
    elif IMAGE_PROVIDER_TYPE == "google":
        # Explicit Google provider with fallback
        provider, error = _try_provider_safe("google")
        if provider is not None:
            return provider
        else:
            warnings.warn(
                f"Failed to initialize GoogleImageProvider: {error}. Falling back to mock.",
                UserWarning
            )
            return MockImageProvider()
    elif IMAGE_PROVIDER_TYPE == "stub":
        # Explicit Stub provider with fallback
        provider, error = _try_provider_safe("stub")
        if provider is not None:
            return provider
        else:
            warnings.warn(
                f"Failed to initialize StubImageProvider: {error}. Falling back to mock.",
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


def _try_provider_safe(name: str) -> Tuple[Optional[ImageProvider], Optional[str]]:
    """
    Safely try to initialize a provider, catching all exceptions.
    
    Args:
        name: Provider name
        
    Returns:
        Tuple of (provider_instance, error_message)
    """
    from .strategy import try_provider
    try:
        return try_provider(name)
    except Exception as e:
        return None, str(e)


def get_video_provider() -> VideoProvider:
    """
    Get the configured video provider with robust fallback chain.
    
    Returns:
        VideoProvider instance (guaranteed to return MockVideoProvider if all others fail)
    
    Configuration:
        Set VIDEO_PROVIDER environment variable:
        - "mock" (default): Offline mock provider
        - "veo": Google Vertex AI Veo (requires VERTEX_API_KEY, VERTEX_PROJECT_ID)
        - Unknown values: Falls back to mock
    
    Fallback Behavior:
        If real provider fails to initialize (missing credentials, etc.),
        automatically falls back to MockVideoProvider.
    """
    if VIDEO_PROVIDER_TYPE == "mock":
        return MockVideoProvider()
    elif VIDEO_PROVIDER_TYPE == "veo":
        # Explicit Veo provider with fallback
        provider, error = _try_video_provider_safe("veo")
        if provider is not None:
            return provider
        else:
            warnings.warn(
                f"Failed to initialize VeoVideoProvider: {error}. Falling back to mock.",
                UserWarning
            )
            return MockVideoProvider()
    else:
        # Unknown provider type - fallback to mock
        warnings.warn(
            f"Unknown VIDEO_PROVIDER value: '{VIDEO_PROVIDER_TYPE}'. Falling back to mock.",
            UserWarning
        )
        return MockVideoProvider()


def _try_video_provider_safe(name: str) -> Tuple[Optional[VideoProvider], Optional[str]]:
    """
    Safely try to initialize a video provider, catching all exceptions.
    
    Args:
        name: Provider name
        
    Returns:
        Tuple of (provider_instance, error_message)
    """
    if name == "veo":
        try:
            from .google_providers import VeoVideoProvider
            provider = VeoVideoProvider()
            return provider, None
        except ImportError as e:
            return None, f"Failed to import VeoVideoProvider: {e}"
        except Exception as e:
            return None, str(e)
    else:
        return None, f"Unknown video provider: {name}"


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
