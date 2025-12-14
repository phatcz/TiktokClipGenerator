# API Integration Roadmap

**Version:** v1.0  
**Last Updated:** 2024-12-14  
**Status:** Blueprint Only (No Code)  
**Context:** MVP v0.1 LOCKED (Phase 1-5.5)

---

## 📋 Executive Summary

Roadmap นี้กำหนดลำดับการต่อ API จริงสำหรับ Creator Tool MVP v0.1 โดยแบ่งเป็น 4 Phase:

- **Phase A: Image Generation** (Phase 2) - เริ่มต้นด้วย API ที่ง่ายและ cost ต่ำ
- **Phase B: Video Segment Generation** (Phase 5) - ต่อเมื่อ Phase A stable แล้ว
- **Phase C: Video Stitching** (Phase 5.5) - ใช้ local processing (FFmpeg/MoviePy)
- **Phase D: Hardening** - Production readiness (monitoring, optimization, guardrails)

**หลักการ:**
- ✅ เริ่มจาก API ที่ง่าย → ยาก
- ✅ เริ่มจาก cost ต่ำ → cost สูง
- ✅ เริ่มจาก synchronous → asynchronous
- ✅ Maintain schema compatibility (LOCKED)
- ✅ ไม่เปลี่ยน MVP logic (LOCKED)

---

## 🎯 Phase A: Image Generation API

**Target:** Phase 2 (`phase2_generator.py`)  
**Mock Function:** `mock_google_image_generation(prompt: str) -> str`  
**Status:** 🔵 Ready for Integration

### A.1. Why Start Here?

**เหตุผลที่เลือก Phase A ก่อน:**
1. ✅ **Cost ต่ำสุด** - Image generation cost ~$0.01-0.05 per image (vs video ~$0.10-0.50 per segment)
2. ✅ **Latency ต่ำสุด** - Image generation ใช้เวลา 5-30 วินาที (vs video 5-10 นาที)
3. ✅ **Error Recovery ง่าย** - Retry image generation เร็วกว่า video
4. ✅ **API Complexity ต่ำ** - Image API ง่ายกว่า video API (no async polling, no file download)
5. ✅ **Volume ควบคุมได้** - 6-10 calls per Phase 2 run (vs 5-10 segments per Phase 5 run)
6. ✅ **Schema ง่าย** - Output เป็น URL string (ไม่ซับซ้อน)

**Risk Level:** 🟢 **Low** - Cost และ complexity ต่ำสุด

### A.2. Pre-Integration Checklist

**สิ่งที่ต้องเตรียมก่อนต่อ API:**

#### A.2.1. Infrastructure Setup
- [ ] **API Account & Keys**
  - สร้าง API account (dev/test environment)
  - รับ API keys (แยก dev/staging/prod)
  - ตั้งค่า quota limits (dev: $10/month, staging: $50/month)
  - ตั้งค่า rate limits (dev: 10 req/min, staging: 50 req/min)

- [ ] **Environment Variables**
  - สร้าง `.env.example` template
  - ตั้งค่า `GOOGLE_IMAGE_API_KEY` (หรือ provider อื่น)
  - ตั้งค่า `GOOGLE_IMAGE_API_ENDPOINT` (optional)
  - ตั้งค่า `GOOGLE_IMAGE_API_TIMEOUT` (default: 30s)
  - **ห้าม hardcode API keys ใน code**

- [ ] **Cost Monitoring**
  - ตั้งค่า cost alerts (dev: $5, staging: $20)
  - ตั้งค่า usage dashboard (optional)
  - ตั้งค่า billing notifications

#### A.2.2. Error Handling Strategy
- [ ] **Retry Logic Design**
  - Max retries: 3 attempts
  - Backoff strategy: Exponential (1s, 2s, 4s)
  - Retryable errors: Timeout, 5xx, Network errors
  - Non-retryable errors: 4xx (except 429), Invalid API key, Quota exceeded

- [ ] **Rate Limit Handling**
  - Detect 429 responses
  - Wait time: 60 seconds (configurable)
  - Max rate limit retries: 2 attempts
  - Queue requests if needed (optional)

- [ ] **Fallback Mechanism**
  - Option 1: Return mock URL (development only)
  - Option 2: Return error (production)
  - Option 3: Use cached image (if available)
  - **Decision:** ใช้ Option 2 (return error) ใน production

#### A.2.3. Schema Compatibility
- [ ] **Output Format Validation**
  - API อาจ return: URL, base64, signed URL, CDN URL
  - ต้อง transform ให้เป็น string (URL format)
  - Validate URL format (starts with `http://` or `https://`)
  - **Constraint:** Phase 2 output schema LOCKED → ต้อง return string URL

- [ ] **Input Validation**
  - Validate prompt length (API limits: 100-1000 chars)
  - Sanitize prompt (prevent injection)
  - Validate prompt encoding (UTF-8)

#### A.2.4. Testing Strategy
- [ ] **Unit Tests**
  - Test API client wrapper
  - Test retry logic
  - Test error handling
  - Test schema transformation

- [ ] **Integration Tests**
  - Test with real API (sandbox/test mode)
  - Test error scenarios (timeout, rate limit, invalid key)
  - Test schema compatibility (Phase 2 output validation)

- [ ] **Cost Testing**
  - Test with small batch (1-2 images)
  - Monitor actual cost per image
  - Validate cost estimates

### A.3. Integration Approach

**Strategy: Wrapper Function Pattern**

```
Current:
  mock_google_image_generation(prompt) -> str

After Integration:
  google_image_generation(prompt) -> str
    ├─ Validate input
    ├─ Call API (with retry)
    ├─ Transform response
    └─ Return URL string
```

**Implementation Steps (Conceptual):**
1. สร้าง `api_clients/image_generation_client.py` (new file)
2. สร้าง wrapper function `google_image_generation()` ที่เรียก API
3. แทนที่ `mock_google_image_generation()` ใน `phase2_generator.py` ด้วย wrapper
4. Maintain backward compatibility (same function signature)

**Key Constraints:**
- ✅ Function signature ต้องเหมือนเดิม: `(prompt: str) -> str`
- ✅ Output format ต้องเหมือนเดิม: URL string
- ✅ Error handling ต้องไม่ break Phase 2 logic
- ✅ Schema validation ต้องผ่าน (Phase 2 output schema LOCKED)

### A.4. What NOT to Do (First Round)

**❌ ไม่ควรทำในรอบแรก:**

1. **Parallel API Calls**
   - ❌ อย่าเรียก API พร้อมกันหลายตัว (character + location candidates)
   - ✅ เริ่มด้วย sequential calls ก่อน
   - ✅ Optimize เป็น parallel ใน Phase D (Hardening)

2. **Complex Caching**
   - ❌ อย่าสร้าง caching layer ที่ซับซ้อน
   - ✅ เริ่มด้วย no cache ก่อน
   - ✅ Optimize เป็น caching ใน Phase D (Hardening)

3. **Multiple Providers**
   - ❌ อย่ารองรับหลาย providers พร้อมกัน (Google, OpenAI, Stability)
   - ✅ เริ่มด้วย provider เดียวก่อน (Google Image API)
   - ✅ Optimize เป็น multi-provider ใน Phase D (Hardening)

4. **Advanced Features**
   - ❌ อย่าเพิ่ม features ที่ไม่จำเป็น (image editing, style transfer)
   - ✅ เริ่มด้วย basic image generation ก่อน
   - ✅ Focus on schema compatibility และ error handling

5. **Production Deployment**
   - ❌ อย่า deploy ไป production ทันที
   - ✅ เริ่มด้วย dev/staging environment ก่อน
   - ✅ Test thoroughly ก่อน production

### A.5. Success Criteria

**Phase A ถือว่าสำเร็จเมื่อ:**
- ✅ API integration ทำงานได้ใน dev environment
- ✅ Schema compatibility ผ่าน (Phase 2 output validation)
- ✅ Error handling ทำงานถูกต้อง (retry, rate limit, timeout)
- ✅ Cost monitoring ทำงาน (alerts, usage tracking)
- ✅ Integration tests ผ่าน (real API calls)
- ✅ Documentation อัพเดท (API setup, error handling)

**Timeline Estimate:** 1-2 weeks (depends on API provider setup)

---

## 🎬 Phase B: Video Segment Generation API

**Target:** Phase 5 (`phase5_segment_renderer.py`)  
**Mock Function:** `mock_google_video_generation(prompt, start_keyframe_path, end_keyframe_path, duration) -> Dict`  
**Status:** 🟡 Ready After Phase A

### B.1. Why After Phase A?

**เหตุผลที่ต้องรอ Phase A เสร็จก่อน:**
1. ✅ **Learn from Phase A** - ใช้ประสบการณ์จาก image API integration
2. ✅ **Cost สูงกว่า** - Video generation cost ~$0.10-0.50 per segment (10x image)
3. ✅ **Latency สูงกว่า** - Video generation ใช้เวลา 5-10 นาที per segment (vs image 5-30s)
4. ✅ **Complexity สูงกว่า** - Video API อาจเป็น async (submit job → poll for completion)
5. ✅ **Error Recovery ยากกว่า** - Retry video generation ใช้เวลานาน
6. ✅ **Volume สูงกว่า** - 5-10 segments per Phase 5 run (vs 6-10 images per Phase 2 run)

**Risk Level:** 🟡 **Medium** - Cost และ complexity สูงกว่า Phase A

### B.2. Pre-Integration Checklist

**สิ่งที่ต้องเตรียมก่อนต่อ API:**

#### B.2.1. Infrastructure Setup
- [ ] **API Account & Keys**
  - สร้าง API account (dev/test environment)
  - รับ API keys (แยก dev/staging/prod)
  - ตั้งค่า quota limits (dev: $50/month, staging: $200/month)
  - ตั้งค่า rate limits (dev: 2 req/min, staging: 5 req/min)
  - **Note:** Video API rate limits ต่ำกว่า image API

- [ ] **Environment Variables**
  - ตั้งค่า `GOOGLE_VIDEO_API_KEY`
  - ตั้งค่า `GOOGLE_VIDEO_API_ENDPOINT`
  - ตั้งค่า `GOOGLE_VIDEO_API_TIMEOUT` (default: 300s = 5 minutes)
  - ตั้งค่า `GOOGLE_VIDEO_POLL_INTERVAL` (default: 10s, if async)
  - ตั้งค่า `GOOGLE_VIDEO_MAX_POLL_TIME` (default: 600s = 10 minutes)

- [ ] **Cost Monitoring**
  - ตั้งค่า cost alerts (dev: $20, staging: $100)
  - ตั้งค่า usage dashboard
  - ตั้งค่า billing notifications
  - **Critical:** Video API cost สูงกว่า image API มาก

#### B.2.2. Async Handling (If Required)
- [ ] **Async API Pattern**
  - ถ้า API เป็น async (submit job → poll):
    - [ ] Implement job submission
    - [ ] Implement polling mechanism
    - [ ] Implement timeout handling
    - [ ] Implement progress tracking
  - ถ้า API เป็น sync (wait for completion):
    - [ ] Implement long timeout (300s+)
    - [ ] Implement progress callbacks (if available)

- [ ] **File Upload Handling**
  - ถ้า API ต้องการ keyframe images:
    - [ ] Implement image upload (to API storage or CDN)
    - [ ] Get signed URLs หรือ upload URLs
    - [ ] Handle upload errors
  - ถ้า API ต้องการ image paths:
    - [ ] Validate image paths exist
    - [ ] Convert paths to API format (if needed)

#### B.2.3. Duration Constraint Enforcement
- [ ] **8-Second Duration Contract**
  - **Critical:** Phase 5 duration = 8.0 seconds (FIXED, LOCKED)
  - API อาจไม่รองรับ exact 8 seconds
  - Options:
    - Option 1: API supports exact duration → Use API parameter
    - Option 2: API supports range → Request 8 seconds, validate result
    - Option 3: API doesn't support exact → Generate longer, trim to 8s
  - **Decision:** ต้อง validate video duration ≈ 8.0 seconds (tolerance: ±0.5s)

- [ ] **Video Validation**
  - Validate video file exists
  - Validate video duration (≈ 8.0 seconds)
  - Validate video format (MP4, codec compatibility)
  - Validate video size (reasonable, not corrupted)

#### B.2.4. Error Handling Strategy
- [ ] **Retry Logic Design**
  - Max retries: 2 attempts (video generation ใช้เวลานาน)
  - Backoff strategy: Exponential (5s, 10s, 20s)
  - Retryable errors: Timeout, 5xx, Network errors, Generation failed
  - Non-retryable errors: 4xx (except 429), Invalid API key, Quota exceeded, Invalid keyframes

- [ ] **Rate Limit Handling**
  - Detect 429 responses
  - Wait time: 120 seconds (video API rate limits ต่ำกว่า)
  - Max rate limit retries: 2 attempts
  - Queue requests (sequential rendering recommended)

- [ ] **Partial Failure Handling**
  - ถ้า segment บางตัว fail:
    - Option 1: Fail entire Phase 5 run
    - Option 2: Continue with successful segments (mark failed)
    - **Decision:** ใช้ Option 2 (continue with successful segments)
  - Return `failed_segments` list in output

#### B.2.5. Schema Compatibility
- [ ] **Output Format Validation**
  - API อาจ return: Video file path, Video URL, Video ID (for download)
  - ต้อง transform ให้เป็น file path (string)
  - Validate file path exists (after download)
  - **Constraint:** Phase 5 output schema LOCKED → ต้อง return file path string

- [ ] **Input Validation**
  - Validate prompt length (API limits)
  - Validate keyframe paths exist (if required)
  - Validate duration = 8.0 seconds (enforce in API call)

#### B.2.6. Testing Strategy
- [ ] **Unit Tests**
  - Test API client wrapper
  - Test async polling (if applicable)
  - Test retry logic
  - Test error handling
  - Test duration validation

- [ ] **Integration Tests**
  - Test with real API (sandbox/test mode)
  - Test error scenarios (timeout, rate limit, invalid keyframes)
  - Test schema compatibility (Phase 5 output validation)
  - Test duration enforcement (8.0 seconds)

- [ ] **Cost Testing**
  - Test with 1 segment first
  - Monitor actual cost per segment
  - Monitor generation time
  - Validate cost estimates

### B.3. Integration Approach

**Strategy: Wrapper Function Pattern (Similar to Phase A)**

```
Current:
  mock_google_video_generation(prompt, start_keyframe_path, end_keyframe_path, duration) -> Dict

After Integration:
  google_video_generation(prompt, start_keyframe_path, end_keyframe_path, duration) -> Dict
    ├─ Validate input (duration = 8.0)
    ├─ Upload keyframes (if required)
    ├─ Call API (with retry, async polling if needed)
    ├─ Download video file (if URL/ID returned)
    ├─ Validate video (duration, format)
    └─ Return result dict
```

**Implementation Steps (Conceptual):**
1. สร้าง `api_clients/video_generation_client.py` (new file)
2. สร้าง wrapper function `google_video_generation()` ที่เรียก API
3. แทนที่ `mock_google_video_generation()` ใน `phase5_segment_renderer.py` ด้วย wrapper
4. Maintain backward compatibility (same function signature)

**Key Constraints:**
- ✅ Function signature ต้องเหมือนเดิม: `(prompt, start_keyframe_path, end_keyframe_path, duration) -> Dict`
- ✅ Output format ต้องเหมือนเดิม: `{success, video_path, duration, metadata}`
- ✅ Duration ต้อง enforce = 8.0 seconds (FIXED, LOCKED)
- ✅ Error handling ต้องไม่ break Phase 5 logic
- ✅ Schema validation ต้องผ่าน (Phase 5 output schema LOCKED)

### B.4. What NOT to Do (First Round)

**❌ ไม่ควรทำในรอบแรก:**

1. **Parallel Segment Rendering**
   - ❌ อย่า render segments พร้อมกัน (cost สูง, rate limit risk)
   - ✅ เริ่มด้วย sequential rendering ก่อน (ทีละ segment)
   - ✅ Optimize เป็น parallel ใน Phase D (Hardening)

2. **Complex Video Processing**
   - ❌ อย่าเพิ่ม video processing features (trim, merge, effects)
   - ✅ เริ่มด้วย basic video generation ก่อน
   - ✅ Focus on schema compatibility และ duration enforcement

3. **Multiple Providers**
   - ❌ อย่ารองรับหลาย providers พร้อมกัน
   - ✅ เริ่มด้วย provider เดียวก่อน (Google Video API)
   - ✅ Optimize เป็น multi-provider ใน Phase D (Hardening)

4. **Advanced Features**
   - ❌ อย่าเพิ่ม features ที่ไม่จำเป็น (video editing, transitions)
   - ✅ เริ่มด้วย basic video generation ก่อน
   - ✅ Focus on 8-second duration contract

5. **Production Deployment**
   - ❌ อย่า deploy ไป production ทันที
   - ✅ เริ่มด้วย dev/staging environment ก่อน
   - ✅ Test thoroughly (cost และ time สูง)

### B.5. Success Criteria

**Phase B ถือว่าสำเร็จเมื่อ:**
- ✅ API integration ทำงานได้ใน dev environment
- ✅ Schema compatibility ผ่าน (Phase 5 output validation)
- ✅ Duration enforcement ทำงาน (8.0 seconds)
- ✅ Error handling ทำงานถูกต้อง (retry, rate limit, timeout, partial failures)
- ✅ Cost monitoring ทำงาน (alerts, usage tracking)
- ✅ Integration tests ผ่าน (real API calls, duration validation)
- ✅ Documentation อัพเดท (API setup, error handling, duration contract)

**Timeline Estimate:** 2-3 weeks (depends on API provider setup และ async complexity)

---

## 🔗 Phase C: Video Stitching/Processing

**Target:** Phase 5.5 (`phase5_assembler.py`)  
**Mock Function:** `mock_video_stitch(segment_paths, output_path) -> str`  
**Status:** 🟢 Ready (Local Processing, No API)

### C.1. Why This Phase?

**เหตุผลที่เลือก Phase C:**
1. ✅ **No API Cost** - Video stitching ใช้ local processing (FFmpeg/MoviePy)
2. ✅ **No Rate Limits** - Local processing ไม่มี rate limits
3. ✅ **Fast Execution** - Video stitching ใช้เวลา 10-60 วินาที (vs video generation 5-10 นาที)
4. ✅ **Error Recovery ง่าย** - Retry stitching เร็วกว่า video generation
5. ✅ **Low Complexity** - Video stitching logic ง่ายกว่า API integration

**Risk Level:** 🟢 **Low** - No API cost, local processing

### C.2. Pre-Integration Checklist

**สิ่งที่ต้องเตรียมก่อนต่อ API:**

#### C.2.1. Library Selection
- [ ] **Choose Processing Library**
  - **Option 1: FFmpeg (subprocess)**
    - Pros: Fast, powerful, low memory usage
    - Cons: Requires FFmpeg installation, subprocess management
    - **Recommendation:** ใช้ Option 1 (FFmpeg) สำหรับ production
  - **Option 2: MoviePy (Python)**
    - Pros: Easy integration, Python-native
    - Cons: Slower, memory intensive
    - **Recommendation:** ใช้ Option 2 (MoviePy) สำหรับ development/testing

- [ ] **Installation**
  - Install FFmpeg binary (system requirement)
  - Install MoviePy library (Python package)
  - Validate installation (test command)

#### C.2.2. File Handling
- [ ] **Segment File Validation**
  - Validate segment files exist (before stitching)
  - Validate video format compatibility (codec, container)
  - Validate video duration (≈ 8.0 seconds per segment)
  - Handle missing/corrupted segments

- [ ] **Output Path Management**
  - Generate output path (if not provided)
  - Validate output directory exists
  - Handle file permissions
  - Cleanup temporary files (if any)

#### C.2.3. Error Handling Strategy
- [ ] **Stitching Error Handling**
  - File not found → Skip segment or fail (configurable)
  - Invalid format → Convert format or fail
  - Corrupted video → Skip segment or fail
  - Insufficient storage → Fail gracefully
  - Stitching failed → Retry (max 2 attempts)

- [ ] **Partial Failure Handling**
  - ถ้า segment บางตัว missing/corrupted:
    - Option 1: Fail entire stitching
    - Option 2: Stitch only successful segments (mark failed)
    - **Decision:** ใช้ Option 2 (stitch successful segments, return failed_segments)

#### C.2.4. Schema Compatibility
- [ ] **Output Format Validation**
  - Output ต้องเป็น file path (string)
  - Validate output file exists (after stitching)
  - Validate output video format (MP4)
  - Validate output video duration (sum of segments)

- [ ] **Input Validation**
  - Validate segment_paths (list of strings)
  - Validate output_path (optional string)
  - Validate retry parameters (max_retries)

#### C.2.5. Testing Strategy
- [ ] **Unit Tests**
  - Test stitching function
  - Test error handling
  - Test partial failure handling
  - Test retry logic

- [ ] **Integration Tests**
  - Test with real segment files
  - Test error scenarios (missing files, corrupted files)
  - Test schema compatibility (Phase 5.5 output validation)
  - Test with various video formats

### C.3. Integration Approach

**Strategy: Direct Replacement (No API)**

```
Current:
  mock_video_stitch(segment_paths, output_path) -> str

After Integration:
  video_stitch(segment_paths, output_path) -> str
    ├─ Validate segment files
    ├─ Check format compatibility
    ├─ Stitch videos (FFmpeg/MoviePy)
    ├─ Validate output file
    └─ Return output path
```

**Implementation Steps (Conceptual):**
1. สร้าง `video_processing/stitcher.py` (new file)
2. สร้าง function `video_stitch()` ที่ใช้ FFmpeg/MoviePy
3. แทนที่ `mock_video_stitch()` ใน `phase5_assembler.py` ด้วย real function
4. Maintain backward compatibility (same function signature)

**Key Constraints:**
- ✅ Function signature ต้องเหมือนเดิม: `(segment_paths, output_path) -> str`
- ✅ Output format ต้องเหมือนเดิม: file path string
- ✅ Error handling ต้องไม่ break Phase 5.5 logic
- ✅ Schema validation ต้องผ่าน (Phase 5.5 output schema LOCKED)

### C.4. What NOT to Do (First Round)

**❌ ไม่ควรทำในรอบแรก:**

1. **Complex Video Processing**
   - ❌ อย่าเพิ่ม video processing features (transitions, effects, audio mixing)
   - ✅ เริ่มด้วย basic concatenation ก่อน
   - ✅ Focus on schema compatibility และ error handling

2. **Cloud Processing**
   - ❌ อย่าใช้ cloud video processing services (AWS MediaConvert, etc.)
   - ✅ เริ่มด้วย local processing (FFmpeg/MoviePy) ก่อน
   - ✅ Optimize เป็น cloud processing ใน Phase D (Hardening) ถ้าจำเป็น

3. **Advanced Features**
   - ❌ อย่าเพิ่ม features ที่ไม่จำเป็น (video editing, color correction)
   - ✅ เริ่มด้วย basic stitching ก่อน
   - ✅ Focus on reliability และ error handling

### C.5. Success Criteria

**Phase C ถือว่าสำเร็จเมื่อ:**
- ✅ Video stitching ทำงานได้ (FFmpeg/MoviePy)
- ✅ Schema compatibility ผ่าน (Phase 5.5 output validation)
- ✅ Error handling ทำงานถูกต้อง (missing files, corrupted files, partial failures)
- ✅ Integration tests ผ่าน (real segment files)
- ✅ Documentation อัพเดท (installation, error handling)

**Timeline Estimate:** 1 week (local processing, no API)

---

## 🛡️ Phase D: Hardening & Production Readiness

**Target:** All Phases (Phase A, B, C)  
**Status:** 🔵 Ready After Phase A, B, C

### D.1. Why This Phase?

**เหตุผลที่ต้องมี Phase D:**
1. ✅ **Production Readiness** - เตรียมระบบให้พร้อมสำหรับ production
2. ✅ **Performance Optimization** - Optimize API calls, caching, parallel processing
3. ✅ **Cost Optimization** - Reduce API costs, implement caching, batch processing
4. ✅ **Reliability** - Improve error handling, monitoring, alerting
5. ✅ **Scalability** - Prepare for higher volume, concurrent users

**Risk Level:** 🟢 **Low** - Optimization phase, no breaking changes

### D.2. Hardening Checklist

**สิ่งที่ต้องทำใน Phase D:**

#### D.2.1. Performance Optimization
- [ ] **Parallel API Calls**
  - Implement parallel image generation (Phase A)
  - Implement parallel video generation (Phase B) - with rate limit control
  - Implement batch processing (if API supports)

- [ ] **Caching Layer**
  - Implement image caching (Phase A)
  - Implement video caching (Phase B) - if segments reusable
  - Cache invalidation strategy
  - Cache storage (local filesystem, Redis, etc.)

- [ ] **Request Optimization**
  - Optimize API request payloads
  - Reduce unnecessary API calls
  - Implement request batching (if API supports)

#### D.2.2. Cost Optimization
- [ ] **Cost Monitoring**
  - Real-time cost tracking
  - Cost alerts (per user, per session, per day)
  - Cost reports (daily, weekly, monthly)
  - Budget caps (per user, per project)

- [ ] **Cost Reduction**
  - Implement caching (reduce duplicate API calls)
  - Implement request deduplication
  - Optimize API usage (reduce unnecessary calls)
  - Use lower-cost options (if available)

#### D.2.3. Reliability & Monitoring
- [ ] **Error Monitoring**
  - Error logging (structured logs)
  - Error tracking (Sentry, etc.)
  - Error alerts (critical errors)
  - Error analytics (error rates, types)

- [ ] **Performance Monitoring**
  - API latency tracking
  - API success rate tracking
  - Performance alerts (slow API calls)
  - Performance dashboards

- [ ] **Health Checks**
  - API health checks
  - System health checks
  - Automated testing (smoke tests)

#### D.2.4. Security Hardening
- [ ] **API Key Management**
  - Use secrets management service (production)
  - API key rotation strategy
  - API key access control
  - Audit logging (API key usage)

- [ ] **Input Validation**
  - Sanitize all inputs (prevent injection)
  - Validate all inputs (prevent invalid requests)
  - Rate limiting per user/session
  - Request size limits

#### D.2.5. Documentation
- [ ] **API Documentation**
  - API setup guide
  - Error handling guide
  - Cost estimation guide
  - Troubleshooting guide

- [ ] **Operational Documentation**
  - Deployment guide
  - Monitoring guide
  - Incident response guide
  - Runbook (common issues, solutions)

### D.3. What NOT to Do (First Round)

**❌ ไม่ควรทำใน Phase D:**

1. **Breaking Changes**
   - ❌ อย่าเปลี่ยน schema (LOCKED)
   - ❌ อย่าเปลี่ยน function signatures (LOCKED)
   - ❌ อย่าเปลี่ยน MVP logic (LOCKED)
   - ✅ Focus on optimization และ hardening เท่านั้น

2. **New Features**
   - ❌ อย่าเพิ่ม features ใหม่ (outside MVP scope)
   - ✅ Focus on existing features optimization

3. **Architecture Redesign**
   - ❌ อย่า redesign architecture
   - ✅ Focus on incremental improvements

### D.4. Success Criteria

**Phase D ถือว่าสำเร็จเมื่อ:**
- ✅ Performance optimization ทำงาน (parallel calls, caching)
- ✅ Cost optimization ทำงาน (cost reduction, monitoring)
- ✅ Reliability improvements ทำงาน (error handling, monitoring)
- ✅ Security hardening ทำงาน (API key management, input validation)
- ✅ Documentation อัพเดท (API docs, operational docs)
- ✅ Production readiness checklist ผ่าน

**Timeline Estimate:** 2-3 weeks (depends on optimization scope)

---

## 📊 Integration Timeline Summary

**Estimated Timeline (Total):**

- **Phase A (Image):** 1-2 weeks
- **Phase B (Video):** 2-3 weeks
- **Phase C (Stitching):** 1 week
- **Phase D (Hardening):** 2-3 weeks
- **Total:** 6-9 weeks

**Critical Path:**
```
Phase A → Phase B → Phase C → Phase D
  ↓         ↓         ↓         ↓
Image    Video    Stitching  Hardening
```

**Dependencies:**
- Phase B depends on Phase A (learn from experience)
- Phase C can run in parallel with Phase B (no dependencies)
- Phase D depends on Phase A, B, C (optimize all)

---

## ⚠️ Risk Mitigation

### High-Risk Areas

1. **Cost Overrun**
   - **Risk:** Video API costs สูงมาก (10x image API)
   - **Mitigation:**
     - Set strict budget caps (dev: $50, staging: $200)
     - Monitor costs daily
     - Use test/sandbox APIs when possible
     - Implement cost alerts

2. **Rate Limit Violations**
   - **Risk:** Video API rate limits ต่ำ (2-5 req/min)
   - **Mitigation:**
     - Implement sequential rendering (not parallel)
     - Implement rate limit handling (429 responses)
     - Queue requests if needed
     - Monitor rate limit usage

3. **Schema Breaking Changes**
   - **Risk:** API response format อาจไม่ตรงกับ schema
   - **Mitigation:**
     - Use adapter/wrapper pattern
     - Transform API responses to match schema
     - Maintain backward compatibility
     - Test schema validation thoroughly

4. **Long Generation Times**
   - **Risk:** Video generation ใช้เวลานาน (5-10 minutes)
   - **Mitigation:**
     - Implement async polling (if API supports)
     - Implement progress tracking
     - Implement timeout handling
     - Set reasonable timeouts (10 minutes max)

### Low-Risk Areas

1. **Image API Integration** (Phase A)
   - Low cost, low latency, simple API
   - Low risk of cost overrun
   - Easy error recovery

2. **Video Stitching** (Phase C)
   - No API costs, local processing
   - Fast execution, easy error recovery
   - Low complexity

---

## 📝 Pre-Integration Readiness Checklist

**ก่อนเริ่ม Phase A ต้องมี:**

### Infrastructure
- [ ] API accounts created (dev/staging)
- [ ] API keys obtained (dev/staging)
- [ ] Environment variables setup (.env.example)
- [ ] Cost monitoring setup (alerts, dashboards)

### Code
- [ ] MVP v0.1 LOCKED (Phase 1-5.5)
- [ ] Schema validators working
- [ ] End-to-end tests passing
- [ ] Mock functions documented

### Documentation
- [ ] API integration plan reviewed
- [ ] Error handling strategy defined
- [ ] Cost estimation completed
- [ ] Timeline approved

### Team
- [ ] API provider selected
- [ ] API documentation reviewed
- [ ] Support channels identified
- [ ] Escalation path defined

---

## 🔗 Related Documents

- `MVP_LOCK.md` - Locked phases and constraints
- `API_INTEGRATION_PLAN.md` - Detailed integration checklist
- `API_DECISION_POINTS.md` - Decision points and considerations
- `PHASE_CONTRACTS.md` - Phase contracts and schemas
- `contracts/phase4_to_phase5.md` - Phase 4-5 contract

---

## 📌 Notes

**Important Constraints:**
- ✅ **Schema LOCKED** - Phase 1-5.5 schemas ห้ามเปลี่ยน
- ✅ **Function Signatures LOCKED** - Public function signatures ห้ามเปลี่ยน
- ✅ **MVP Logic LOCKED** - Phase 1-5.5 logic ห้ามเปลี่ยน
- ✅ **No Breaking Changes** - ต้อง maintain backward compatibility

**This is a Blueprint Only:**
- ❌ **No Code** - Roadmap นี้ไม่มี code implementation
- ❌ **No API Calls** - Roadmap นี้ไม่มี API calls
- ✅ **Planning Only** - Roadmap นี้เป็น planning document เท่านั้น

---

**Last Updated:** 2024-12-14  
**Maintained By:** Development Team  
**Version:** 1.0

