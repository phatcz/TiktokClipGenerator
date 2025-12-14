# MVP v0.1 - Lock Document

**Version:** 0.1  
**Status:** 🔒 LOCKED  
**Date:** 2024-12-14

---

## Overview

MVP v0.1 เป็นการล็อก Phase 1-5.5 ของ Creator Tool Pipeline เพื่อ validate architecture และ schema ก่อนต่อ API จริง

---

## Locked Phases

### ✅ Phase 1: Story Engine
**File:** `story_engine.py`  
**Status:** 🔒 LOCKED  
**Type:** Complete (Rule-based, no API)

- Function: `generate_story(goal, product, audience, platform)`
- Output: Story JSON with 4 scenes (hook, conflict, reveal, close)
- **ห้ามแก้:** Logic, schema, function signature

---

### ✅ Phase 2: Characters & Locations Generator
**File:** `phase2_generator.py`  
**Status:** 🔒 LOCKED (Mock)  
**Type:** Mock API

- Function: `generate_phase2_output(story, num_characters, num_locations)`
- Output: Characters + Locations candidates
- **Mock:** `mock_google_image_generation()` - returns mock image URLs
- **ห้ามแก้:** Logic, schema, function signature
- **Note:** Image generation ยังใช้ mock (จะต่อ API ใน Phase 2)

---

### ✅ Phase 3: Storyboard Builder
**File:** `phase3_storyboard.py`  
**Status:** 🔒 LOCKED  
**Type:** Complete (Rule-based, no API)

- Function: `build_storyboard_from_phase2(phase2_output, selected_character_id, selected_location_id)`
- Output: Storyboard with keyframes (1-3 per scene)
- **ห้ามแก้:** Logic, schema, function signature

---

### ✅ Phase 4: Video Plan Generator
**File:** `phase4_video_plan.py`  
**Status:** 🔒 LOCKED  
**Type:** Complete (Rule-based, no API)

- Function: `generate_video_plan(storyboard)`
- Output: Video segments with start_keyframe/end_keyframe objects
- **Contract:** Phase 4 → Phase 5 (start_keyframe/end_keyframe objects required)
- **ห้ามแก้:** Logic, schema, function signature, contract

---

### ✅ Phase 5: Segment Renderer
**File:** `phase5_segment_renderer.py`  
**Status:** 🔒 LOCKED (Mock)  
**Type:** Mock API

- Function: `render_segments_from_video_plan(video_plan, story_context)`
- Output: Rendered segment video paths (mock)
- **Mock:** `mock_google_video_generation()` - returns mock video paths
- **Duration:** Fixed 8.0 seconds per segment
- **ห้ามแก้:** Logic, schema, function signature, duration constraint
- **Note:** Video generation ยังใช้ mock (จะต่อ API ใน Phase 2)

---

### ✅ Phase 5.5: Video Assembler
**File:** `phase5_assembler.py`  
**Status:** 🔒 LOCKED (Mock)  
**Type:** Mock Processing

- Function: `assemble_video(segment_paths, output_path, retry_failed, max_retries)`
- Output: Final video path (mock)
- **Mock:** `mock_video_stitch()` - returns mock final video path
- **ห้ามแก้:** Logic, schema, function signature
- **Note:** Video stitching ยังใช้ mock (จะใช้ ffmpeg/moviepy ใน Phase 2)

---

## MVP Scope

### ✅ Included in MVP

1. **Complete Pipeline Flow**
   - Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 5.5
   - Schema validation ทุก phase
   - End-to-end test passing

2. **Schema & Contracts**
   - Phase 1 Story schema (locked)
   - Phase 2 Characters/Locations schema (locked)
   - Phase 3 Storyboard schema (locked)
   - Phase 4 Video Plan schema (locked)
   - Phase 4 → Phase 5 contract (locked)
   - Phase 5 Segment schema (locked)
   - Phase 5.5 Assembly schema (locked)

3. **Mock APIs**
   - Phase 2: Mock image generation (returns mock URLs)
   - Phase 5: Mock video generation (returns mock paths)
   - Phase 5.5: Mock video stitching (returns mock final path)

4. **Streamlit Demo App**
   - UI สำหรับทดสอบ pipeline
   - Phase-by-phase execution
   - JSON viewer, metrics display

5. **Testing**
   - End-to-end test (`tests/test_end_to_end.py`)
   - Schema validators (`validators/schema_validators.py`)

### ❌ Not Included in MVP

1. **Real API Integration**
   - Google Image Generation API (Phase 2)
   - Google Video Generation API (Phase 5)
   - Video processing libraries (Phase 5.5: ffmpeg/moviepy)

2. **Production Features**
   - Error recovery mechanisms
   - Rate limiting
   - Cost monitoring
   - Performance optimization

3. **Additional Features**
   - Unit tests (มีเฉพาะ integration test)
   - Advanced error handling
   - Logging/monitoring infrastructure

---

## Rules & Constraints

### 🔒 Schema Lock

- **ห้ามเปลี่ยน schema** ของ Phase 1-5.5 โดยไม่ได้รับอนุมัติ
- **Breaking changes** ต้องผ่าน versioning (v0.1 → v0.2)
- **Contract ระหว่าง phases** ต้องถูก maintain

### 🔒 Phase Order Lock

- **ห้ามเปลี่ยน phase order** (1 → 2 → 3 → 4 → 5 → 5.5)
- **ห้ามแก้ logic** ใน phase ที่ล็อกแล้ว
- **ห้ามเพิ่ม phase ใหม่** โดยไม่ได้รับอนุมัติ

### 🔒 Function Signature Lock

- **ห้ามเปลี่ยน function signatures** ของ public functions
- **ห้ามเปลี่ยน parameter types** หรือ return types
- **Backward compatibility** ต้อง maintain

### 🔒 Mock API Lock

- **Mock functions** ต้อง maintain interface เดิม
- **ห้ามเปลี่ยน mock return format** โดยไม่ได้รับอนุมัติ
- **Real API integration** จะทำใน Phase 2 (แยกจาก MVP)

---

## Next Steps (Post-MVP)

### Phase 2: API Integration

1. **Phase 2: Google Image Generation API**
   - แทนที่ `mock_google_image_generation()` ด้วย API call
   - เพิ่ม error handling, retry logic
   - Maintain schema compatibility

2. **Phase 5: Google Video Generation API**
   - แทนที่ `mock_google_video_generation()` ด้วย API call
   - เพิ่ม error handling, retry logic
   - Maintain 8-second duration constraint

3. **Phase 5.5: Video Processing**
   - แทนที่ `mock_video_stitch()` ด้วย ffmpeg/moviepy
   - Implement real video concatenation
   - Maintain output schema

### Phase 3: Production Hardening

- Performance optimization
- Error recovery mechanisms
- Cost monitoring
- Rate limiting
- Logging/monitoring infrastructure

---

## Files Reference

### Core Phase Modules (Locked)
- `story_engine.py` - Phase 1
- `phase2_generator.py` - Phase 2 (Mock)
- `phase3_storyboard.py` - Phase 3
- `phase4_video_plan.py` - Phase 4
- `phase5_segment_renderer.py` - Phase 5 (Mock)
- `phase5_assembler.py` - Phase 5.5 (Mock)

### Supporting Files
- `app_streamlit.py` - Streamlit demo app
- `end_to_end_run.py` - End-to-end runner
- `tests/test_end_to_end.py` - End-to-end tests
- `validators/schema_validators.py` - Schema validators
- `contracts/phase4_to_phase5.md` - Phase 4-5 contract

### Documentation
- `PROGRESS.md` - Project progress
- `WORKFLOW.md` - Development workflow
- `SETUP.md` - Setup instructions
- `readme.md` - Story schema v0.1

---

## Summary

**MVP v0.1 = Complete Pipeline + Mock APIs**

- ✅ Pipeline logic: Complete
- ✅ Schema: Locked
- ✅ Contracts: Documented
- ⚠️ APIs: Mock (Phase 2, 5, 5.5)
- ✅ Testing: End-to-end passing
- ✅ Demo: Streamlit app ready

**Status:** Ready for architecture validation and API integration planning.

---

**Last Updated:** 2024-12-14  
**Maintained By:** Development Team  
**Version:** 0.1

