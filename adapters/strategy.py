"""
Provider Selection Strategy

Defines provider priority order and fallback chain logic for multi-provider support.
"""

from typing import List, Optional, Callable, Tuple
import warnings

from .interfaces import ImageProvider


# Provider priority order for "auto" strategy
# Providers are tried in this order until one succeeds
# Fallback always ends in MockImageProvider
IMAGE_PROVIDER_PRIORITY = [
    "google",  # Highest priority: Google Vertex AI Imagen
    "stub",    # Placeholder/stub provider (for testing)
    # Future providers can be added here:
    # "openai",  # OpenAI DALL-E
    # "stability",  # Stability AI
    # etc.
]

# Provider factory functions
# Maps provider name to factory function that returns provider instance
# Factory functions should handle their own initialization errors
_PROVIDER_FACTORIES: dict[str, Callable[[], ImageProvider]] = {}


def register_provider_factory(name: str, factory: Callable[[], ImageProvider]) -> None:
    """
    Register a provider factory function.
    
    Args:
        name: Provider name (e.g., "google", "stub")
        factory: Factory function that returns ImageProvider instance
    """
    _PROVIDER_FACTORIES[name] = factory


def get_provider_factory(name: str) -> Optional[Callable[[], ImageProvider]]:
    """
    Get provider factory function by name.
    
    Args:
        name: Provider name
        
    Returns:
        Factory function or None if not found
    """
    return _PROVIDER_FACTORIES.get(name)


def try_provider(name: str) -> Tuple[Optional[ImageProvider], Optional[str]]:
    """
    Try to initialize a provider by name.
    
    Args:
        name: Provider name
        
    Returns:
        Tuple of (provider_instance, error_message)
        - If successful: (provider, None)
        - If failed: (None, error_message)
    """
    factory = get_provider_factory(name)
    if factory is None:
        return None, f"Provider factory not found: {name}"
    
    try:
        provider = factory()
        return provider, None
    except Exception as e:
        return None, str(e)


def get_provider_with_fallback(
    provider_names: List[str],
    fallback_name: str = "mock"
) -> ImageProvider:
    """
    Try providers in order until one succeeds, fallback to specified provider.
    
    Args:
        provider_names: List of provider names to try in order
        fallback_name: Provider name to use as final fallback (default: "mock")
        
    Returns:
        ImageProvider instance (guaranteed to return fallback if all others fail)
    """
    # Try each provider in order
    for provider_name in provider_names:
        provider, error = try_provider(provider_name)
        if provider is not None:
            return provider
        else:
            # Log warning but continue to next provider
            warnings.warn(
                f"Failed to initialize provider '{provider_name}': {error}. "
                f"Trying next provider in chain.",
                UserWarning
            )
    
    # All providers failed - use fallback
    fallback_provider, fallback_error = try_provider(fallback_name)
    if fallback_provider is not None:
        warnings.warn(
            f"All providers failed. Using fallback: {fallback_name}",
            UserWarning
        )
        return fallback_provider
    else:
        # Even fallback failed - this should never happen for mock
        # But handle it gracefully
        raise RuntimeError(
            f"Critical error: Fallback provider '{fallback_name}' failed: {fallback_error}"
        )


def get_auto_provider() -> ImageProvider:
    """
    Get provider using "auto" strategy.
    
    Tries providers in priority order until one succeeds.
    Always falls back to MockImageProvider if all fail.
    
    Returns:
        ImageProvider instance (guaranteed to return MockImageProvider if all others fail)
    """
    return get_provider_with_fallback(
        provider_names=IMAGE_PROVIDER_PRIORITY,
        fallback_name="mock"
    )


__all__ = [
    "IMAGE_PROVIDER_PRIORITY",
    "register_provider_factory",
    "get_provider_factory",
    "try_provider",
    "get_provider_with_fallback",
    "get_auto_provider",
]
