"""
Stub Provider Implementations

Placeholder/stub providers for future integrations.
These providers are lightweight implementations that can be used for testing
or as placeholders until real providers are implemented.

Currently supports:
- StubImageProvider: Placeholder image provider that always fails gracefully
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime

from .interfaces import (
    ImageProvider,
    ImageGenerationRequest,
    ImageGenerationResult,
    ProviderError,
)


class StubImageProvider(ImageProvider):
    """
    Stub image provider for testing and placeholder purposes.
    
    This provider always returns a failure result, making it useful for:
    - Testing fallback chains
    - Placeholder until real provider is implemented
    - Demonstrating multi-provider strategy
    
    It does not make any API calls and always fails gracefully,
    allowing the fallback chain to proceed to the next provider.
    """
    
    def __init__(self):
        """Initialize Stub Image Provider."""
        # Stub provider doesn't need credentials
        pass
    
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate image (stub implementation - always fails).
        
        Args:
            request: Image generation request
            
        Returns:
            ImageGenerationResult with success=False
            
        Note:
            This provider always fails to allow fallback chain testing.
            In a real scenario, this would be replaced with an actual provider.
        """
        return ImageGenerationResult(
            success=False,
            error="StubImageProvider: Placeholder provider (not implemented)",
            metadata={
                "provider": "stub",
                "prompt": request.prompt,
                "reason": "stub_provider_not_implemented",
            }
        )


__all__ = [
    "StubImageProvider",
]
