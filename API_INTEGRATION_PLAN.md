# API Integration Plan

**Version:** v1.0  
**Last Updated:** 2024-12-14  
**Status:** Planning

---

## ภาพรวม

เอกสารนี้ระบุ checklist สำหรับการ integrate API จริงในแต่ละ Phase:

- **Phase 2:** Google Image Generation API
- **Phase 5:** Google Video Generation API
- **Phase 5.5:** ffmpeg/moviepy (Video Stitching)

---

## Phase 2: Google Image Generation API

### Current Implementation
- **Function:** `mock_google_image_generation(prompt: str) -> str`
- **Location:** `phase2_generator.py`
- **Usage:** 
  - `generate_character_candidates()` - เรียก 3-5 ครั้ง
  - `generate_location_candidates()` - เรียก 3-5 ครั้ง
  - **Total:** 6-10 API calls ต่อ Phase 2 run

### Required Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | `string` | ✅ REQUIRED | Image generation prompt (Thai/English) |
| | | | Format: `"{name}, {style} style, age {age_range}, {personality}, suitable for {audience} audience"` |

**Example Prompt:**
```
ผู้เชี่ยวชาญ, professional style, age 30-45, confident, knowledgeable, suitable for มือใหม่ ไม่เก่งเทค audience
```

### Expected Outputs

| Field | Type | Description |
|-------|------|-------------|
| `image_url` | `string` | URL ของ generated image |
| | | Format: `https://...` หรือ local path |

**Current Mock Output:**
```python
f"https://mock-images.google.com/generated/{image_id}.jpg"
```

### Error Cases

| Error Type | Scenario | Handling |
|------------|----------|----------|
| **API Timeout** | Request timeout > 30s | Retry with exponential backoff |
| **Rate Limit** | 429 Too Many Requests | Wait and retry (respect rate limit) |
| **Invalid Prompt** | 400 Bad Request | Log error, use fallback image or skip |
| **API Failure** | 500 Internal Server Error | Retry with exponential backoff |
| **Network Error** | Connection failed | Retry with exponential backoff |
| **Quota Exceeded** | 403 Forbidden (quota) | Fail gracefully, notify user |

### Retry Strategy (Conceptual)

```
1. Initial attempt
2. If error → Wait 1s → Retry (max 3 attempts)
3. If rate limit → Wait 60s → Retry (max 2 attempts)
4. If quota exceeded → Fail immediately
5. If timeout → Exponential backoff: 2s, 4s, 8s (max 3 attempts)
```

**Retry Logic:**
- **Max Retries:** 3 attempts
- **Backoff Strategy:** Exponential (1s, 2s, 4s)
- **Rate Limit:** Wait 60s before retry
- **Timeout:** 30 seconds per request

### Integration Checklist

- [ ] Replace `mock_google_image_generation()` with real API call
- [ ] Add API key management (environment variables)
- [ ] Add request timeout (30s)
- [ ] Implement retry logic with exponential backoff
- [ ] Handle rate limiting (429 responses)
- [ ] Handle quota exceeded (403 responses)
- [ ] Add error logging
- [ ] Add request/response logging (for debugging)
- [ ] Validate prompt length (API limits)
- [ ] Handle API response format (URL vs base64)
- [ ] Add fallback mechanism (if API fails completely)
- [ ] Test with real API (sandbox/test mode)
- [ ] Monitor API usage/quota

### Dependencies

- Google Image Generation API client library
- Environment variable management (`GOOGLE_IMAGE_API_KEY`)
- Retry library (e.g., `tenacity`)

---

## Phase 5: Google Video Generation API

### Current Implementation
- **Function:** `mock_google_video_generation(prompt, start_keyframe_path, end_keyframe_path, duration) -> Dict`
- **Location:** `phase5_segment_renderer.py`
- **Usage:** 
  - `render_segment()` - เรียกทีละ segment
  - **Total:** 1 API call ต่อ segment (อาจมี 5-10 segments)

### Required Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | `string` | ✅ REQUIRED | Video generation prompt |
| | | | Format: `"Start: {description} | End: {description} | Character: {name} | Location: {name} | Motion: {type} | Duration: 8 seconds"` |
| `start_keyframe_path` | `string` | ⚪ OPTIONAL | Path ของ start keyframe image |
| `end_keyframe_path` | `string` | ⚪ OPTIONAL | Path ของ end keyframe image |
| `duration` | `float` | ✅ REQUIRED | Video duration (fix = 8.0 seconds) |

**Example Prompt:**
```
Start: เปิดฉากด้วยคำถามที่น่าสนใจ | End: แสดงปัญหาและความยากลำบาก | Character: ผู้เชี่ยวชาญ | Location: สถานที่ทำงาน | Motion: smooth | Camera: none | Transition: fade | Duration: 8 seconds
```

### Expected Outputs

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | API call สำเร็จหรือไม่ |
| `video_path` | `string` | Path ของ generated video file |
| `duration` | `float` | Video duration (8.0 seconds) |
| `metadata` | `dict` | Additional info (prompt, keyframes, generated_at, api_version) |

**Current Mock Output:**
```python
{
    "success": True,
    "video_path": "output/segments/segment_{id}_{timestamp}_{uuid}.mp4",
    "duration": 8.0,
    "metadata": {...}
}
```

### Error Cases

| Error Type | Scenario | Handling |
|------------|----------|----------|
| **API Timeout** | Request timeout > 300s (video gen takes time) | Retry with exponential backoff |
| **Rate Limit** | 429 Too Many Requests | Wait and retry (respect rate limit) |
| **Invalid Prompt** | 400 Bad Request | Log error, fail segment |
| **Invalid Keyframe** | 400 Bad Request (keyframe format) | Log error, fail segment |
| **API Failure** | 500 Internal Server Error | Retry with exponential backoff |
| **Network Error** | Connection failed | Retry with exponential backoff |
| **Quota Exceeded** | 403 Forbidden (quota) | Fail gracefully, notify user |
| **Generation Failed** | Video generation failed | Retry segment (max 2 attempts) |
| **File Download Failed** | Cannot download video | Retry download (max 3 attempts) |

### Retry Strategy (Conceptual)

```
1. Initial attempt
2. If error → Wait 5s → Retry (max 2 attempts)
3. If rate limit → Wait 120s → Retry (max 2 attempts)
4. If timeout → Exponential backoff: 10s, 20s, 40s (max 3 attempts)
5. If generation failed → Retry segment (max 2 attempts)
6. If download failed → Retry download (max 3 attempts)
```

**Retry Logic:**
- **Max Retries:** 2-3 attempts (depends on error type)
- **Backoff Strategy:** Exponential (5s, 10s, 20s)
- **Rate Limit:** Wait 120s before retry
- **Timeout:** 300 seconds per request (video generation takes time)
- **Segment Retry:** Max 2 attempts per segment

### Integration Checklist

- [ ] Replace `mock_google_video_generation()` with real API call
- [ ] Add API key management (environment variables)
- [ ] Add request timeout (300s for video generation)
- [ ] Implement retry logic with exponential backoff
- [ ] Handle rate limiting (429 responses)
- [ ] Handle quota exceeded (403 responses)
- [ ] Add error logging
- [ ] Add request/response logging (for debugging)
- [ ] Validate prompt length (API limits)
- [ ] Upload keyframe images to API (if required)
- [ ] Handle async API calls (video generation is async)
- [ ] Poll for completion (if API is async)
- [ ] Download video file from API response
- [ ] Validate video file (format, duration, size)
- [ ] Handle partial failures (some segments fail)
- [ ] Add fallback mechanism (if API fails completely)
- [ ] Test with real API (sandbox/test mode)
- [ ] Monitor API usage/quota
- [ ] Add progress tracking (for long-running requests)

### Dependencies

- Google Video Generation API client library
- Environment variable management (`GOOGLE_VIDEO_API_KEY`)
- Retry library (e.g., `tenacity`)
- Async/await support (if API is async)
- File download library (if video is hosted)

### Special Considerations

- **Async Processing:** Video generation may be async (submit job → poll for completion)
- **Long Timeout:** Video generation takes time (5-10 minutes per segment)
- **File Size:** Generated videos may be large (need storage management)
- **Concurrent Requests:** May need to limit concurrent API calls (rate limiting)

---

## Phase 5.5: ffmpeg/moviepy (Video Stitching)

### Current Implementation
- **Function:** `mock_video_stitch(segment_paths, output_path) -> str`
- **Location:** `phase5_assembler.py`
- **Usage:** 
  - `assemble_video()` - เรียกครั้งเดียวต่อ final video
  - **Total:** 1 call ต่อ final video

### Required Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `segment_paths` | `List[str]` | ✅ REQUIRED | List of segment video file paths |
| `output_path` | `string` | ⚪ OPTIONAL | Output path for final video (auto-generate if not provided) |

**Example:**
```python
segment_paths = [
    "output/segments/segment_1.mp4",
    "output/segments/segment_2.mp4",
    "output/segments/segment_3.mp4"
]
output_path = "output/final_video_20241214_123456.mp4"
```

### Expected Outputs

| Field | Type | Description |
|-------|------|-------------|
| `output_path` | `string` | Path ของ final stitched video file |
| | | Format: `output/final_video_{timestamp}_{uuid}.mp4` |

**Current Mock Output:**
```python
f"output/final_video_{timestamp}_{unique_id}.mp4"
```

### Error Cases

| Error Type | Scenario | Handling |
|------------|----------|----------|
| **File Not Found** | Segment file doesn't exist | Skip segment or fail (configurable) |
| **Invalid Video Format** | Segment format not supported | Convert format or fail |
| **Corrupted Video** | Segment file is corrupted | Skip segment or fail |
| **Insufficient Storage** | Not enough disk space | Fail gracefully, notify user |
| **Stitching Failed** | ffmpeg/moviepy error | Retry (max 2 attempts) |
| **Timeout** | Stitching takes too long | Fail after timeout (300s) |
| **Codec Mismatch** | Different codecs in segments | Convert to same codec |

### Retry Strategy (Conceptual)

```
1. Initial attempt
2. If stitching failed → Retry (max 2 attempts)
3. If file not found → Skip segment or fail (configurable)
4. If codec mismatch → Convert segments to same codec → Retry
5. If timeout → Fail immediately
```

**Retry Logic:**
- **Max Retries:** 2 attempts
- **Backoff Strategy:** None (immediate retry)
- **Timeout:** 300 seconds per stitch operation
- **Partial Failure:** Skip failed segments or fail entire operation (configurable)

### Integration Checklist

- [ ] Choose library: `ffmpeg` (subprocess) or `moviepy` (Python)
- [ ] Replace `mock_video_stitch()` with real stitching function
- [ ] Validate segment files exist before stitching
- [ ] Check video format compatibility
- [ ] Handle codec mismatch (convert to same codec)
- [ ] Add error handling for corrupted videos
- [ ] Add timeout handling (300s)
- [ ] Add progress tracking (for long videos)
- [ ] Handle partial failures (some segments missing)
- [ ] Add retry logic for stitching failures
- [ ] Validate output video (format, duration, size)
- [ ] Add logging (stitching progress, errors)
- [ ] Test with various video formats
- [ ] Test with large videos (storage management)
- [ ] Add cleanup (delete temporary files)

### Dependencies

**Option 1: ffmpeg (subprocess)**
- `ffmpeg` binary installed on system
- `subprocess` module (built-in)

**Option 2: moviepy (Python)**
- `moviepy` library
- `ffmpeg` binary (moviepy dependency)

### Implementation Options

#### Option 1: ffmpeg (subprocess)
```python
# Conceptual
subprocess.run([
    "ffmpeg",
    "-i", "concat:segment1.mp4|segment2.mp4|segment3.mp4",
    "-c", "copy",
    "output.mp4"
])
```

**Pros:**
- Fast (native binary)
- Full ffmpeg features
- Low memory usage

**Cons:**
- Requires ffmpeg installation
- Subprocess management
- Error handling more complex

#### Option 2: moviepy (Python)
```python
# Conceptual
from moviepy.editor import VideoFileClip, concatenate_videoclips

clips = [VideoFileClip(path) for path in segment_paths]
final = concatenate_videoclips(clips)
final.write_videofile(output_path)
```

**Pros:**
- Pure Python
- Easier error handling
- More control over process

**Cons:**
- Slower than ffmpeg
- Higher memory usage
- Requires ffmpeg binary anyway

### Special Considerations

- **Video Format:** Ensure all segments are same format/codec
- **Resolution:** Handle different resolutions (scale or crop)
- **Audio:** Handle audio tracks (merge or keep first)
- **Duration:** Validate final video duration matches sum of segments
- **Storage:** Large videos need sufficient disk space
- **Memory:** Long videos may need streaming (not load all at once)

---

## Common Integration Patterns

### 1. API Key Management

**Pattern:**
```python
# Conceptual (not actual code)
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_IMAGE_API_KEY")
```

**Checklist:**
- [ ] Use environment variables (not hardcode)
- [ ] Use `.env` file for local development
- [ ] Use secret management for production
- [ ] Validate API key exists before making requests

### 2. Error Handling

**Pattern:**
```python
# Conceptual (not actual code)
try:
    result = api_call(...)
except APITimeoutError:
    # Retry with backoff
except RateLimitError:
    # Wait and retry
except QuotaExceededError:
    # Fail gracefully
except Exception as e:
    # Log and handle
```

**Checklist:**
- [ ] Catch specific exceptions (not bare `except`)
- [ ] Log errors with context
- [ ] Return structured error responses
- [ ] Don't expose API keys in error messages

### 3. Retry Logic

**Pattern:**
```python
# Conceptual (not actual code)
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def api_call_with_retry(...):
    # API call
```

**Checklist:**
- [ ] Use exponential backoff
- [ ] Set max retry attempts
- [ ] Don't retry on client errors (4xx)
- [ ] Retry on server errors (5xx) and timeouts

### 4. Rate Limiting

**Pattern:**
```python
# Conceptual (not actual code)
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls, time_window):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
    
    def wait_if_needed(self):
        # Check and wait
```

**Checklist:**
- [ ] Respect API rate limits
- [ ] Implement rate limiting client-side
- [ ] Handle 429 responses properly
- [ ] Queue requests if needed

### 5. Logging

**Pattern:**
```python
# Conceptual (not actual code)
import logging

logger = logging.getLogger(__name__)

logger.info("API call started", extra={"prompt": prompt})
logger.error("API call failed", extra={"error": str(e)})
```

**Checklist:**
- [ ] Log API requests (without sensitive data)
- [ ] Log API responses (success/failure)
- [ ] Log retry attempts
- [ ] Log errors with context
- [ ] Don't log API keys

---

## Testing Strategy

### Unit Tests
- [ ] Test API client functions
- [ ] Test error handling
- [ ] Test retry logic
- [ ] Test rate limiting

### Integration Tests
- [ ] Test with real API (sandbox/test mode)
- [ ] Test error scenarios (timeout, rate limit, etc.)
- [ ] Test end-to-end flow (Phase 2 → 5 → 5.5)

### Load Tests
- [ ] Test concurrent API calls
- [ ] Test rate limiting behavior
- [ ] Test quota management

---

## Monitoring & Observability

### Metrics to Track
- [ ] API call success rate
- [ ] API call latency
- [ ] Retry count
- [ ] Rate limit hits
- [ ] Quota usage
- [ ] Error rates by type

### Alerts
- [ ] API failure rate > threshold
- [ ] Quota usage > 80%
- [ ] Rate limit hits > threshold
- [ ] Timeout rate > threshold

---

## Security Considerations

- [ ] Never commit API keys to version control
- [ ] Use environment variables for API keys
- [ ] Rotate API keys regularly
- [ ] Use least privilege principle
- [ ] Validate API responses (prevent injection)
- [ ] Sanitize prompts (prevent prompt injection)

---

## Cost Management

### Phase 2 (Image Generation)
- **Cost per image:** ~$0.01-0.05 (estimate)
- **Per Phase 2 run:** 6-10 images = $0.06-0.50
- **Monthly estimate:** Depends on usage

### Phase 5 (Video Generation)
- **Cost per video:** ~$0.10-0.50 (estimate)
- **Per Phase 5 run:** 5-10 segments = $0.50-5.00
- **Monthly estimate:** Depends on usage

### Cost Optimization
- [ ] Cache generated images/videos (if reusable)
- [ ] Use lower quality for testing
- [ ] Monitor quota usage
- [ ] Set budget alerts

---

## Migration Plan

### Phase 1: Preparation
- [ ] Set up API accounts
- [ ] Get API keys
- [ ] Set up environment variables
- [ ] Create test accounts

### Phase 2: Implementation
- [ ] Implement Phase 2 API integration
- [ ] Test Phase 2 with real API
- [ ] Implement Phase 5 API integration
- [ ] Test Phase 5 with real API
- [ ] Implement Phase 5.5 video stitching
- [ ] Test Phase 5.5

### Phase 3: Testing
- [ ] End-to-end testing
- [ ] Load testing
- [ ] Error scenario testing
- [ ] User acceptance testing

### Phase 4: Deployment
- [ ] Deploy to staging
- [ ] Monitor for issues
- [ ] Deploy to production
- [ ] Monitor production metrics

---

**หมายเหตุ:** เอกสารนี้เป็น planning document - ต้องอัปเดตเมื่อมีการ implement จริง

