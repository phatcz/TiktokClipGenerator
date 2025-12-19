# Integration Strategy - Adding Real Providers

This document provides a step-by-step guide for integrating real API providers (Google, Veo, OpenAI, etc.) in future EPs without modifying the core pipeline.

## Overview

The adapter layer is designed so that adding real providers requires:
1. ✅ Creating a new provider implementation file
2. ✅ Implementing the interface contracts
3. ✅ Adding provider selection logic
4. ❌ **NO changes to core pipeline** (Phase 1-5.5)
5. ❌ **NO changes to interfaces** (backward compatible)

## Step-by-Step Integration Process

### Step 1: Choose Provider and Gather Requirements

**For Image Generation:**
- Research provider API documentation
- Identify required credentials (API keys, OAuth, etc.)
- Check rate limits, quotas, pricing
- Understand request/response formats

**For Video Generation:**
- Same as above, plus:
- Check video generation time (can be minutes)
- Understand async/polling patterns if needed
- Check supported resolutions, durations

**For Audio Generation:**
- Same as above, plus:
- Check available voices/languages
- Understand TTS parameters

### Step 2: Create Provider Implementation File

Create a new file in `adapters/` directory:

```python
# adapters/google_providers.py

# Note: This example uses `requests` for illustration.
# Real implementations may use official SDKs (e.g., google-cloud-aiplatform)
# or other HTTP libraries depending on provider requirements.

from typing import Optional
import os
import requests  # Example: May use SDK instead
from .interfaces import (
    ImageProvider,
    ImageGenerationRequest,
    ImageGenerationResult,
    VideoProvider,
    VideoGenerationRequest,
    VideoGenerationResult,
    ProviderError,
    ProviderTimeoutError,
    # ... other exceptions
)

class GoogleImageProvider(ImageProvider):
    """Google Imagen API implementation"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_IMAGE_API_KEY")
        self.project_id = os.getenv("GOOGLE_PROJECT_ID")
        self.location = os.getenv("GOOGLE_LOCATION", "us-central1")
        
        if not self.api_key or not self.project_id:
            raise ProviderAuthenticationError(
                "GOOGLE_IMAGE_API_KEY and GOOGLE_PROJECT_ID required"
            )
    
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        # Implement Google Imagen API call
        # Handle errors, timeouts, etc.
        pass

class GoogleVideoProvider(VideoProvider):
    """Google Veo API implementation"""
    
    def __init__(self):
        # Similar initialization
        pass
    
    def generate_video_segment(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        # Implement Google Veo API call
        # Handle async/polling if needed
        pass
```

### Step 3: Implement Interface Methods

**Key Requirements:**
- Must implement all abstract methods from interfaces
- Must raise standardized exceptions (ProviderError, etc.)
- Must return proper result dataclasses
- Must handle errors gracefully (with fallback to mock if configured)

**Example Error Handling:**
```python
# Note: This example uses `requests` for illustration.
# Real implementations may use official SDKs or other HTTP libraries.

def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
    try:
        # API call (example: may use SDK instead of requests)
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 429:
            raise ProviderQuotaExceededError("Rate limit exceeded")
        elif response.status_code == 401:
            raise ProviderAuthenticationError("Invalid API key")
        elif response.status_code != 200:
            raise ProviderError(f"API error: {response.status_code}")
        
        # Process response
        return ImageGenerationResult(success=True, ...)
        
    except requests.Timeout:
        raise ProviderTimeoutError("Request timed out")
    except ProviderError:
        raise  # Re-raise provider errors
    except Exception as e:
        raise ProviderError(f"Unexpected error: {str(e)}")
```

### Step 4: Add Provider Selection Logic

Update `adapters/__init__.py`:

```python
# Add imports
from .google_providers import GoogleImageProvider, GoogleVideoProvider

# Update factory functions
def get_image_provider() -> ImageProvider:
    provider_type = os.getenv("IMAGE_PROVIDER", "mock").lower()
    
    if provider_type == "mock":
        return MockImageProvider()
    elif provider_type == "google":
        return GoogleImageProvider()  # NEW
    elif provider_type == "openai":
        return OpenAIImageProvider()  # Future
    else:
        # Fallback to mock for unknown providers
        return MockImageProvider()

def get_video_provider() -> ImageProvider:
    provider_type = os.getenv("VIDEO_PROVIDER", "mock").lower()
    
    if provider_type == "mock":
        return MockVideoProvider()
    elif provider_type == "google" or provider_type == "veo":
        return GoogleVideoProvider()  # NEW
    else:
        return MockVideoProvider()
```

### Step 5: Update Environment Variables

Add to `env.example`:

```bash
# Google Provider
GOOGLE_IMAGE_API_KEY=your_google_image_api_key
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_LOCATION=us-central1

# Provider Selection
IMAGE_PROVIDER=google  # or "mock" for offline
VIDEO_PROVIDER=veo     # or "mock" for offline
```

### Step 6: Implement Fallback Strategy

**Option A: Automatic Fallback to Mock**
```python
def get_image_provider() -> ImageProvider:
    provider_type = os.getenv("IMAGE_PROVIDER", "mock").lower()
    
    try:
        if provider_type == "google":
            return GoogleImageProvider()
        # ...
    except ProviderAuthenticationError:
        # Missing credentials - fallback to mock
        print("Warning: Provider auth failed, using mock")
        return MockImageProvider()
    
    return MockImageProvider()
```

**Option B: Explicit Fallback Configuration**
```python
# In provider implementation
def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
    try:
        # Real API call
        return real_api_call(request)
    except ProviderError as e:
        # Check if fallback enabled
        if os.getenv("PROVIDER_FALLBACK_TO_MOCK", "true").lower() == "true":
            print(f"Warning: {e}, falling back to mock")
            return MockImageProvider().generate_image(request)
        raise
```

### Step 7: Add Retry Logic (Optional)

For transient errors, implement retry:

```python
import time
from typing import Optional

def generate_image(self, request: ImageGenerationRequest, max_retries: int = 3) -> ImageGenerationResult:
    for attempt in range(max_retries):
        try:
            return self._call_api(request)
        except ProviderTimeoutError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
            raise
        except ProviderQuotaExceededError:
            # Don't retry quota errors
            raise
```

### Step 8: Testing Strategy

**Unit Tests:**
```python
# tests/test_google_providers.py

def test_google_image_provider_success():
    provider = GoogleImageProvider()
    request = ImageGenerationRequest(prompt="test")
    result = provider.generate_image(request)
    assert result.success
    assert result.image_url is not None

def test_google_image_provider_auth_error():
    # Test with invalid credentials
    pass

def test_google_image_provider_timeout():
    # Test timeout handling
    pass
```

**Integration Tests:**
- Test with real API (use test API keys)
- Test error scenarios
- Test fallback behavior

**Manual Testing:**
1. Set `IMAGE_PROVIDER=google` in `.env`
2. Run pipeline end-to-end
3. Verify images are generated
4. Test error scenarios (invalid key, network failure)

### Step 9: Safe Rollout Plan

**Phase 1: Development**
- Use mock provider (`IMAGE_PROVIDER=mock`)
- Implement real provider in separate branch
- Test thoroughly

**Phase 2: Staging**
- Deploy with real provider but low usage
- Monitor for errors
- Test fallback behavior

**Phase 3: Production**
- Enable real provider for all users
- Monitor quotas, costs, errors
- Keep mock as fallback

**Feature Flags (Optional):**
```python
# Use feature flags for gradual rollout
def get_image_provider() -> ImageProvider:
    provider_type = os.getenv("IMAGE_PROVIDER", "mock").lower()
    use_real = os.getenv("ENABLE_REAL_PROVIDERS", "false").lower() == "true"
    
    if provider_type == "google" and use_real:
        return GoogleImageProvider()
    return MockImageProvider()
```

## Provider-Specific Considerations

### Google Imagen/Veo
- Requires OAuth2 or service account
- May need GCS bucket for outputs
- Check regional availability
- Understand quota limits

### OpenAI DALL-E/Sora
- API key authentication
- Rate limits per tier
- Check model availability
- Understand pricing per image/video

### Stability AI
- API key authentication
- Different models for different use cases
- Check resolution limits

## Environment Variables Checklist

For each provider, document required env vars:

```bash
# Provider Selection
IMAGE_PROVIDER=google|openai|stability|mock
VIDEO_PROVIDER=veo|runway|pika|mock
AUDIO_PROVIDER=elevenlabs|google|openai|mock

# Google Provider
GOOGLE_IMAGE_API_KEY=...
GOOGLE_PROJECT_ID=...
GOOGLE_LOCATION=us-central1

# OpenAI Provider
OPENAI_API_KEY=...

# Fallback Behavior
PROVIDER_FALLBACK_TO_MOCK=true|false
PROVIDER_MAX_RETRIES=3
PROVIDER_TIMEOUT=60
```

## Quota Management

**Monitor Usage:**
- Track API calls per day/week
- Set up alerts for quota limits
- Implement rate limiting if needed

**Handle Quota Exceeded:**
```python
except ProviderQuotaExceededError:
    # Log error
    # Optionally: fallback to mock
    # Optionally: queue request for later
    raise
```

## Cost Management

**Track Costs:**
- Monitor API usage
- Set budget alerts
- Implement cost limits if needed

**Optimize:**
- Cache results when possible
- Batch requests when supported
- Use lower quality/resolution for testing

## Verification Checklist

Before marking integration complete:

- [ ] Provider implementation file created
- [ ] All interface methods implemented
- [ ] Error handling implemented (all exception types)
- [ ] Provider selection added to factory
- [ ] Environment variables documented
- [ ] Unit tests written
- [ ] Integration tests pass
- [ ] Fallback behavior tested
- [ ] Documentation updated
- [ ] Core pipeline unchanged (verified)
- [ ] Works offline (mock still works)

## Common Pitfalls

1. **Modifying Core Pipeline**: ❌ Don't change Phase 1-5.5 code
2. **Changing Interfaces**: ❌ Don't break backward compatibility
3. **Hardcoding Credentials**: ❌ Always use environment variables
4. **No Error Handling**: ❌ Handle all error cases
5. **No Fallback**: ❌ Always have mock as fallback
6. **Ignoring Quotas**: ❌ Monitor and handle quota limits

## Next Steps After Integration

1. Update `PROVIDER_DECISION_MATRIX.md` with real provider data
2. Update `ADAPTER_OVERVIEW.md` with new provider
3. Create `EXECUTION_ORDER_EP_S05.md` documenting changes
4. Test end-to-end pipeline with real provider
5. Monitor production usage

## See Also

- `ADAPTER_OVERVIEW.md`: Architecture overview
- `PROVIDER_DECISION_MATRIX.md`: Provider comparison
- `EXECUTION_ORDER_EP_S04.md`: Current adapter implementation
