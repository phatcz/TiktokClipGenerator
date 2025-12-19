# Adapter Layer Overview

## Purpose

The adapter layer provides a **clean separation** between the core pipeline (Phase 1-5.5) and external provider APIs (Google, Veo, OpenAI, etc.). This allows:

1. **Core pipeline stays unchanged** when switching providers
2. **Easy provider swapping** via environment variables
3. **Offline development** with mock providers
4. **Future-proof architecture** for new providers

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Core Pipeline (Phase 1-5.5)                 │
│  (story_engine.py, phase2_generator.py, etc.)          │
│                                                           │
│  Current (EP_S04): Direct API calls                      │
│  Target (EP_S05+): adapters.get_image_provider()         │
│                     adapters.get_video_provider()        │
│                     adapters.get_audio_provider()        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Adapter Layer (adapters/)                   │
│                                                           │
│  ┌──────────────────────────────────────────────┐       │
│  │  interfaces.py                                │       │
│  │  - ImageProvider (ABC)                        │       │
│  │  - VideoProvider (ABC)                        │       │
│  │  - AudioProvider (ABC)                        │       │
│  └──────────────────────────────────────────────┘       │
│                                                           │
│  ┌──────────────────────────────────────────────┐       │
│  │  mock_providers.py                             │       │
│  │  - MockImageProvider                            │       │
│  │  - MockVideoProvider                            │       │
│  │  - MockAudioProvider                            │       │
│  └──────────────────────────────────────────────┘       │
│                                                           │
│  ┌──────────────────────────────────────────────┐       │
│  │  __init__.py (Factory)                        │       │
│  │  - get_image_provider()                        │       │
│  │  - get_video_provider()                         │       │
│  │  - get_audio_provider()                         │       │
│  └──────────────────────────────────────────────┘       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│         Future: Real Providers (EP_S05+)                │
│                                                           │
│  - google_providers.py (Google Imagen, Veo)              │
│  - openai_providers.py (DALL-E, Sora)                    │
│  - stability_providers.py (Stable Diffusion)             │
│  - etc.                                                   │
└─────────────────────────────────────────────────────────┘
```

## Folder Layout

```
adapters/
├── __init__.py          # Factory functions (get_*_provider)
├── interfaces.py         # Abstract base classes (contracts)
└── mock_providers.py     # Mock implementations (offline)

# Future additions (EP_S05+):
├── google_providers.py   # Google Imagen, Veo implementations
├── openai_providers.py   # OpenAI DALL-E, Sora implementations
└── ...
```

## How Core Pipeline Will Stay Clean (EP_S05+)

**Current State (EP_S04):**
The core pipeline still uses direct API calls. The adapter layer exists but is not yet integrated.

**Target State (EP_S05+):**
The core pipeline will use adapters instead of direct API calls.

### Current (Tightly Coupled) - EP_S04
```python
# phase2_generator.py - Current: Direct API calls
def generate_image_with_vertex(prompt: str) -> str:
    api_key = os.getenv("VERTEX_API_KEY")
    response = requests.post("https://vertex-ai...", ...)
    # Hard to test, hard to swap providers
```

### Target (Adapter Pattern) - EP_S05+
```python
# phase2_generator.py - Planned: Uses adapter
from adapters import get_image_provider

def generate_character_image(prompt: str) -> str:
    provider = get_image_provider()  # Gets mock or real provider
    request = ImageGenerationRequest(prompt=prompt)
    result = provider.generate_image(request)
    return result.image_url or result.image_path
```

## Provider Selection

Providers are selected via **environment variables**:

```bash
# Default: Mock (offline)
IMAGE_PROVIDER=mock
VIDEO_PROVIDER=mock
AUDIO_PROVIDER=mock

# Future: Real providers
IMAGE_PROVIDER=google
VIDEO_PROVIDER=veo
AUDIO_PROVIDER=elevenlabs
```

The factory functions in `adapters/__init__.py` handle selection:

```python
def get_image_provider() -> ImageProvider:
    provider_type = os.getenv("IMAGE_PROVIDER", "mock").lower()
    if provider_type == "mock":
        return MockImageProvider()
    elif provider_type == "google":
        return GoogleImageProvider()  # Future
    # ...
```

## Interfaces (Contracts)

All providers must implement the interfaces defined in `interfaces.py`:

### ImageProvider
- `generate_image(request: ImageGenerationRequest) -> ImageGenerationResult`
- `generate_images(requests: List[...]) -> List[...]` (optional batch)

### VideoProvider
- `generate_video_segment(request: VideoGenerationRequest) -> VideoGenerationResult`

### AudioProvider
- `generate_voiceover(request: AudioGenerationRequest) -> AudioGenerationResult`
- `generate_sfx(description: str, duration: float) -> AudioGenerationResult` (optional)

## Error Handling

All providers raise standardized exceptions:
- `ProviderError`: Base exception
- `ProviderTimeoutError`: Request timeout
- `ProviderQuotaExceededError`: Rate limit/quota exceeded
- `ProviderAuthenticationError`: Auth failure
- `ProviderValidationError`: Invalid input

## Current Status

**EP_S04 (Current):**
- ✅ Adapter interfaces defined
- ✅ Mock providers implemented
- ✅ Factory pattern in place
- ✅ Works offline (default: mock)
- ❌ **Adapter layer NOT yet integrated into core pipeline** (planned for EP_S05+)
- ❌ Real providers NOT implemented (future EP)

**EP_S05+ (Planned):**
- Will integrate adapter layer into core pipeline (replace direct API calls)
- Will add real provider implementations
- Will NOT modify core pipeline logic (only replace API calls with adapter calls)
- Will NOT modify interfaces (backward compatible)

## Usage Example (Planned for EP_S05+)

**Note:** This example shows how the adapter layer will be used once integrated into the core pipeline. Currently (EP_S04), the adapter layer exists but is not yet used by the pipeline.

```python
# Planned usage in core pipeline (EP_S05+)
from adapters import get_image_provider, get_video_provider
from adapters.interfaces import ImageGenerationRequest, VideoGenerationRequest

# Get providers (automatically selects mock or real based on env)
image_provider = get_image_provider()
video_provider = get_video_provider()

# Generate image
image_request = ImageGenerationRequest(
    prompt="A professional character, modern style",
    width=1024,
    height=1024
)
image_result = image_provider.generate_image(image_request)
if image_result.success:
    print(f"Image: {image_result.image_url}")

# Generate video segment
video_request = VideoGenerationRequest(
    prompt="Smooth transition from start to end",
    duration=8.0,
    start_keyframe_path="path/to/start.jpg",
    end_keyframe_path="path/to/end.jpg"
)
video_result = video_provider.generate_video_segment(video_request)
if video_result.success:
    print(f"Video: {video_result.video_path}")
```

## Benefits

1. **Testability**: Easy to test with mocks
2. **Flexibility**: Swap providers without code changes
3. **Offline Development**: Works without API keys
4. **Future-Proof**: New providers don't require pipeline changes
5. **Clean Separation**: Core logic separate from API details

## Migration Path

**Step 1: Integrate Adapter Layer (EP_S05+)**
- Replace direct API calls in Phase 2 and Phase 5 with adapter calls
- Test end-to-end with mock providers
- Verify pipeline still works

**Step 2: Add Real Providers (EP_S05+)**
1. Create new provider file (e.g., `google_providers.py`)
2. Implement interfaces from `interfaces.py`
3. Add provider selection in `__init__.py`
4. Set environment variable to use real provider
5. **No changes needed** to core pipeline logic (only adapter calls, already integrated)

## See Also

- `INTEGRATION_STRATEGY.md`: Step-by-step guide for adding real providers
- `PROVIDER_DECISION_MATRIX.md`: Comparison of provider options
- `EXECUTION_ORDER_EP_S04.md`: What was changed in this EP
