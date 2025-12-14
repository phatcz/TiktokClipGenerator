# API Decision Points

เอกสารนี้ระบุจุดตัดสินใจสำคัญเมื่อจะต่อ API จริงสำหรับ Creator Tool MVP v0.1

**Last Updated:** 2024-12-14  
**Status:** Pre-API Integration Planning

---

## 📋 Overview

MVP v0.1 ใช้ mock APIs สำหรับ:
- Phase 2: Image Generation (mock_google_image_generation)
- Phase 5: Video Generation (mock_google_video_generation)
- Phase 5.5: Video Stitching (mock_video_stitch)

เอกสารนี้อธิบายจุดตัดสินใจและข้อควรระวังเมื่อจะแทนที่ด้วย API จริง

---

## 🎯 Phase 2: Image Generation API

### Decision Points

#### 1. Provider Selection
**ต้องตัดสินใจ:** เลือก image generation provider

**Options:**
- Google Image Generation API (imagen)
- OpenAI DALL-E 3
- Stability AI (Stable Diffusion)
- Midjourney API
- Custom/On-premise solution

**Considerations:**
- Cost per image
- Quality/consistency
- API latency
- Rate limits
- Availability in target regions

#### 2. API Integration Strategy
**ต้องตัดสินใจ:** วิธีแทนที่ mock function

**Current Mock:**
```python
def mock_google_image_generation(prompt: str) -> str:
    # Returns mock URL
```

**Integration Options:**
- Direct replacement: แทนที่ mock function โดยตรง
- Wrapper approach: สร้าง wrapper function ที่เรียก API
- Adapter pattern: สร้าง adapter layer เพื่อรองรับหลาย providers

**Recommendation:** ใช้ wrapper/adapter เพื่อ maintain backward compatibility

#### 3. Error Handling
**ต้องตัดสินใจ:** วิธีจัดการ API errors

**Scenarios:**
- API timeout
- Rate limit exceeded
- Invalid API key
- Network errors
- API service downtime

**Considerations:**
- Retry logic (max retries, exponential backoff)
- Fallback mechanism (use mock? cache? skip?)
- Error reporting/monitoring

#### 4. Cost Control
**ต้องตัดสินใจ:** วิธีควบคุม cost

**Risks:**
- Unbounded API calls (infinite loop, bug)
- Accidental production usage during testing
- Cost overrun from unexpected usage

**Mitigations:**
- Cost monitoring/threshold alerts
- Rate limiting per user/session
- Budget caps
- Separate dev/staging API keys with lower limits

#### 5. Schema Compatibility
**ต้องตัดสินใจ:** วิธีรักษา schema compatibility

**Constraint:** Phase 2 output schema ต้องไม่เปลี่ยน (LOCKED)

**Considerations:**
- API response format อาจต่างจาก mock
- ต้อง transform API response ให้ตรงกับ schema
- URL format อาจต่าง (CDN, signed URLs, etc.)

---

## 🎬 Phase 5: Video Generation API

### Decision Points

#### 1. Provider Selection
**ต้องตัดสินใจ:** เลือก video generation provider

**Options:**
- Google Video Generation API (imagen video)
- RunwayML Gen-2
- Pika Labs API
- Stable Video Diffusion
- Custom/On-premise solution

**Considerations:**
- Cost per second of video
- Generation time/latency
- Video quality
- Duration constraints (must support 8-second segments)
- Rate limits
- Keyframe-to-keyframe transition support

#### 2. Duration Constraint
**ต้องตัดสินใจ:** วิธี enforce 8-second duration

**Constraint:** Phase 5 duration = 8.0 seconds (FIXED)

**Considerations:**
- API อาจไม่รองรับ exact 8 seconds
- อาจต้อง trim/extend video
- อาจต้อง use different API endpoints for different durations
- Validation: ตรวจสอบว่า video duration ใกล้เคียง 8 seconds

#### 3. Segment Rendering Strategy
**ต้องตัดสินใจ:** วิธี render multiple segments

**Current Behavior:** Render segments sequentially (ทีละ segment)

**Considerations:**
- Parallel rendering (เร็วกว่า แต่ cost สูงกว่า)
- Sequential rendering (ช้ากว่า แต่ควบคุม cost ได้ดีกว่า)
- Batch rendering (ถ้า API รองรับ)

**Recommendation:** เริ่มด้วย sequential แล้ว optimize เป็น parallel ถ้าจำเป็น

#### 4. Keyframe Input Handling
**ต้องตัดสินใจ:** วิธีส่ง keyframes ให้ API

**Current Schema:**
- start_keyframe: {id, image_path, description, timing}
- end_keyframe: {id, image_path, description, timing}

**Considerations:**
- API อาจต้องการ image files ไม่ใช่ paths
- อาจต้อง upload images ไปยัง storage ก่อน
- API อาจต้องการ different format (base64, signed URLs, etc.)

#### 5. Cost & Time Estimation
**ต้องตัดสินใจ:** วิธี estimate cost และ time

**Risks:**
- Video generation costs มากกว่า image generation มาก
- Generation time อาจนาน (minutes per segment)
- Cost overrun จาก long generation times

**Considerations:**
- Cost estimation per segment (ก่อน render)
- Progress tracking/notification
- Timeout handling (ถ้า generation ใช้เวลานานเกินไป)
- Cost alerts/thresholds

---

## 🔗 Phase 5.5: Video Stitching/Processing

### Decision Points

#### 1. Processing Engine Selection
**ต้องตัดสินใจ:** เลือก video processing solution

**Options:**
- **FFmpeg** (local processing)
  - Pros: Free, powerful, no API costs
  - Cons: Requires installation, server resources
- **MoviePy** (Python library)
  - Pros: Easy integration, Python-native
  - Cons: Slower than FFmpeg, memory intensive
- **Cloud Video Processing** (AWS MediaConvert, Google Video Intelligence, etc.)
  - Pros: Scalable, no server resources needed
  - Cons: API costs, latency

**Recommendation:** เริ่มด้วย FFmpeg (local) เพื่อ avoid API costs

#### 2. Segment File Handling
**ต้องตัดสินใจ:** วิธีจัดการ segment video files

**Current Behavior:** Expects list of file paths

**Considerations:**
- Files อาจอยู่ใน local filesystem
- Files อาจอยู่ใน cloud storage (S3, GCS, etc.)
- May need to download files before stitching
- File format compatibility (codec, container format)

#### 3. Error Recovery
**ต้องตัดสินใจ:** วิธีจัดการ failed segments

**Current Behavior:** Retry logic available (assemble_video_with_retry)

**Considerations:**
- ถ้า segment file ไม่มี/เสียหาย → ต้อง re-render?
- Partial stitching (stitch only successful segments)?
- Fallback mechanism

---

## ⚠️ Risk Areas (สิ่งที่ *ไม่ควร* ทำ)

### 1. Cost Risks

#### ❌ **ไม่ควร:** เรียก API โดยไม่มี cost monitoring
**Risk:** Cost overrun, surprise bills

**Mitigation:**
- Set up cost alerts
- Use separate dev/test API keys with limits
- Monitor API usage regularly

#### ❌ **ไม่ควร:** Parallel API calls โดยไม่จำกัดจำนวน
**Risk:** Exponential cost increase, rate limit violations

**Mitigation:**
- Limit concurrent API calls
- Use queue system for rate limiting
- Monitor rate limits

#### ❌ **ไม่ควร:** Retry logic ที่ aggressive เกินไป
**Risk:** เรียก API ซ้ำหลายครั้งเมื่อ error, เพิ่ม cost

**Mitigation:**
- Set reasonable max retries
- Use exponential backoff
- Distinguish retryable vs non-retryable errors

---

### 2. Rate Limit Risks

#### ❌ **ไม่ควร:** ไม่ตรวจสอบ rate limits ก่อนเรียก API
**Risk:** API calls fail, service disruption

**Mitigation:**
- Check rate limit documentation
- Implement rate limiting/throttling
- Handle rate limit errors gracefully

#### ❌ **ไม่ควร:** Burst API calls ในช่วงสั้นๆ
**Risk:** Hit rate limit, API calls rejected

**Mitigation:**
- Spread API calls over time
- Use queue/batch processing
- Monitor rate limit usage

---

### 3. Schema/Breaking Change Risks

#### ❌ **ไม่ควร:** เปลี่ยน schema เมื่อต่อ API
**Constraint:** Phase schemas LOCKED

**Risk:** Break downstream phases, break contracts

**Mitigation:**
- Maintain schema compatibility
- Transform API responses to match schema
- Use adapter layer

#### ❌ **ไม่ควร:** เปลี่ยน function signatures
**Constraint:** Function signatures LOCKED

**Risk:** Break integration points, break tests

**Mitigation:**
- Maintain backward compatibility
- Use wrapper functions if needed
- Update only internal implementation

---

### 4. Error Handling Risks

#### ❌ **ไม่ควร:** Silently fail เมื่อ API error
**Risk:** Lost data, incomplete results, debugging difficulty

**Mitigation:**
- Log all API errors
- Return meaningful error messages
- Notify users/system of failures

#### ❌ **ไม่ควร:** ไม่มี fallback mechanism
**Risk:** System completely broken เมื่อ API down

**Mitigation:**
- Consider fallback to mock (during development)
- Graceful degradation
- Error recovery mechanisms

---

### 5. Security Risks

#### ❌ **ไม่ควร:** Hardcode API keys ใน code
**Risk:** API keys exposed in version control

**Mitigation:**
- Use environment variables (.env file)
- Never commit .env to git
- Use secrets management service (production)

#### ❌ **ไม่ควร:** ใช้ production API keys ใน development
**Risk:** Accidental production usage, cost overrun

**Mitigation:**
- Separate dev/staging/prod API keys
- Use mock APIs in development
- API key rotation

---

## 📝 Implementation Checklist

### Pre-Integration
- [ ] Choose API providers for each phase
- [ ] Review API documentation and pricing
- [ ] Set up API accounts and get API keys (dev/test)
- [ ] Understand rate limits and quotas
- [ ] Set up cost monitoring/alerts
- [ ] Plan error handling strategy

### Integration Phase
- [ ] Create adapter/wrapper functions
- [ ] Implement API client (with retry logic)
- [ ] Add error handling
- [ ] Add cost/time estimation
- [ ] Test with small batch first
- [ ] Validate schema compatibility

### Post-Integration
- [ ] Monitor API usage and costs
- [ ] Monitor error rates
- [ ] Performance testing
- [ ] Update documentation

---

## 🔗 Related Documents

- `MVP_LOCK.md` - Locked phases and constraints
- `contracts/phase4_to_phase5.md` - Phase 4-5 contract
- `.env.example` - Environment variables template

---

**Note:** เอกสารนี้เป็น planning document - ไม่มีการเรียก API จริง

