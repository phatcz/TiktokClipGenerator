# UI-Backend Alignment Review

> เอกสารนี้ตรวจสอบความสอดคล้องระหว่าง Streamlit UI (`app_streamlit.py`) กับ Backend (Phase 1-5.5)  
> **Review Date**: 2024-12-14  
> **Status**: MVP v0.1 - Backend LOCKED

---

## สรุปผลการตรวจสอบ

### ✅ OK (สอดคล้อง)

### ⚠️ Missing (Backend มี แต่ UI ไม่เรียก)

### 🔴 Risk (UI เรียก แต่ Backend ไม่รองรับ / ลำดับผิด)

---

## Phase-by-Phase Review

### Phase 1: Story Generation

**UI Function Call:**
```python
story = generate_story(goal, product, audience, platform)
```

**Backend Function:**
```python
def generate_story(goal: str, product: str, audience: str, platform: str) -> Dict[str, Any]
```

**Status**: ✅ **OK**

- ✅ Parameters ตรงกันครบถ้วน
- ✅ Return type ตรงกัน
- ✅ Session state: `phase1_story` ถูกเก็บถูกต้อง

---

### Phase 2: Characters & Locations

**UI Function Call:**
```python
phase2_output = generate_phase2_output(
    st.session_state.phase1_story,
    num_characters=num_characters,
    num_locations=num_locations
)
```

**Backend Function:**
```python
def generate_phase2_output(
    story: Dict[str, Any],
    num_characters: int = 4,
    num_locations: int = 4,
    selected_character_id: Optional[int] = None,
    selected_location_id: Optional[int] = None
) -> Dict[str, Any]
```

**Status**: ⚠️ **Missing**

**Gap:**
- ⚠️ UI ไม่ส่ง `selected_character_id` และ `selected_location_id` ไปยัง `generate_phase2_output`
- ⚠️ Backend มี parameter `selected_character_id` และ `selected_location_id` (optional) แต่ UI ไม่ใช้
- ⚠️ Backend จะใช้ default = 1 (ตัวแรก) ซึ่งอาจไม่ตรงกับที่ user เลือกใน UI

**Impact:**
- Phase 2 output จะมี `selection` field ที่มี `selected_character_id=1` และ `selected_location_id=1` เสมอ
- User เลือก character/location ใน UI แต่ Phase 2 output ไม่สะท้อนการเลือกนั้น

**Note:**
- Phase 3 ใช้ `selected_character_id` และ `selected_location_id` จาก session_state แทน (ไม่ใช้จาก phase2_output.selection)
- ดังนั้นผลกระทบอาจไม่รุนแรง แต่ไม่สอดคล้องกับ contract

---

### Phase 3: Storyboard Builder

**UI Function Call:**
```python
storyboard = build_storyboard_from_phase2(
    st.session_state.phase2_output,
    selected_character_id=st.session_state.selected_character_id,
    selected_location_id=st.session_state.selected_location_id
)
```

**Backend Function:**
```python
def build_storyboard_from_phase2(
    phase2_output: Dict[str, Any],
    selected_character_id: Optional[int] = None,
    selected_location_id: Optional[int] = None
) -> Dict[str, Any]
```

**Status**: ✅ **OK**

- ✅ Parameters ตรงกัน
- ✅ Backend สามารถอ่าน `selection` จาก `phase2_output` ได้ (fallback)
- ✅ UI ส่ง `selected_character_id` และ `selected_location_id` จาก session_state (override)
- ✅ Session state: `phase3_storyboard` ถูกเก็บถูกต้อง

**Note:**
- Backend มี fallback logic: ถ้าไม่ส่ง parameter จะอ่านจาก `phase2_output.selection`
- UI ส่ง parameter ไปเสมอ (override) ซึ่งถูกต้อง

---

### Phase 4: Video Plan Generator

**UI Function Call:**
```python
video_plan = generate_video_plan(st.session_state.phase3_storyboard)
```

**Backend Function:**
```python
def generate_video_plan(storyboard: Dict[str, Any]) -> Dict[str, Any]
```

**Status**: ✅ **OK**

- ✅ Parameters ตรงกัน
- ✅ Return type ตรงกัน
- ✅ Session state: `phase4_video_plan` ถูกเก็บถูกต้อง
- ✅ UI แสดง segments พร้อม `start_keyframe` และ `end_keyframe` objects ถูกต้อง

---

### Phase 5: Segment Renderer

**UI Function Call:**
```python
render_result = render_segments_from_video_plan(
    st.session_state.phase4_video_plan,
    story_context=st.session_state.phase1_story
)
```

**Backend Function:**
```python
def render_segments_from_video_plan(
    video_plan: Dict[str, Any],
    story_context: Optional[Dict[str, Any]] = None,
    output_dir: str = "output/segments"
) -> Dict[str, Any]
```

**Status**: ✅ **OK**

- ✅ Parameters ตรงกัน
- ✅ `story_context` ส่งจาก `phase1_story` ถูกต้อง
- ✅ `output_dir` ไม่ส่ง (ใช้ default) ซึ่งถูกต้อง
- ✅ Session state: `phase5_render_result` ถูกเก็บถูกต้อง
- ✅ UI แสดง render result พร้อม `rendered_segments` ถูกต้อง

**Note:**
- Backend มี `output_dir` parameter แต่ UI ไม่ใช้ (ใช้ default) ซึ่งถูกต้อง

---

### Phase 5.5: Video Assembler

**UI Function Call:**
```python
# Extract segment paths
segment_paths = []
for rendered_seg in st.session_state.phase5_render_result.get("rendered_segments", []):
    if rendered_seg.get("success"):
        segment_paths.append(rendered_seg.get("video_path"))

assemble_result = assemble_video(
    segment_paths,
    output_path=None,
    retry_failed=False
)
```

**Backend Function:**
```python
def assemble_video(
    segment_paths: List[str],
    output_path: Optional[str] = None,
    retry_failed: bool = True,
    max_retries: int = 3
) -> Dict[str, Any]
```

**Status**: ⚠️ **Missing**

**Gap:**
- ⚠️ UI ส่ง `retry_failed=False` แต่ Backend มี default `retry_failed=True`
- ⚠️ Backend มี `assemble_video_with_retry()` function ที่รองรับ retry logic ดีกว่า แต่ UI ไม่ใช้

**Impact:**
- ถ้ามี segment ที่ล้มเหลว UI จะไม่ retry (เพราะ `retry_failed=False`)
- Backend มี retry logic แต่ UI ปิดไว้

**Note:**
- UI extract segment paths จาก `rendered_segments` ถูกต้อง
- UI filter เฉพาะ `success=True` ถูกต้อง

---

## Session State Review

### Session State Variables

| Variable | Phase | Status | Notes |
|----------|-------|--------|-------|
| `phase1_story` | Phase 1 | ✅ OK | เก็บ Story object |
| `phase2_output` | Phase 2 | ✅ OK | เก็บ Phase 2 output |
| `phase3_storyboard` | Phase 3 | ✅ OK | เก็บ Storyboard object |
| `phase4_video_plan` | Phase 4 | ✅ OK | เก็บ Video Plan object |
| `phase5_render_result` | Phase 5 | ✅ OK | เก็บ Render result |
| `phase5_5_assemble_result` | Phase 5.5 | ✅ OK | เก็บ Assemble result |
| `selected_character_id` | Phase 2-3 | ✅ OK | เก็บ selection state |
| `selected_location_id` | Phase 2-3 | ✅ OK | เก็บ selection state |

**Status**: ✅ **OK**

- ✅ Session state ครบถ้วนทุก Phase
- ✅ Clear button ล้าง session state ครบถ้วน
- ✅ Phase dependencies ถูกต้อง (Phase N ต้องมี Phase N-1)

---

## Phase Flow Review

### Expected Flow

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 5.5
```

### UI Flow

```
Phase 1 (Generate Story)
  ↓ (requires phase1_story)
Phase 2 (Generate Characters & Locations)
  ↓ (requires phase2_output)
Phase 3 (Build Storyboard)
  ↓ (requires phase3_storyboard)
Phase 4 (Generate Video Plan)
  ↓ (requires phase4_video_plan)
Phase 5 (Render Segments)
  ↓ (requires phase5_render_result)
Phase 5.5 (Assemble Final Video)
```

**Status**: ✅ **OK**

- ✅ Phase dependencies ถูกต้อง
- ✅ UI แสดง info message เมื่อ Phase ก่อนหน้ายังไม่เสร็จ
- ✅ Button แต่ละ Phase ถูก disable เมื่อ Phase ก่อนหน้ายังไม่เสร็จ (implicit)

---

## Function Call Alignment

### Summary Table

| Phase | UI Function | Backend Function | Parameters Match | Status |
|-------|------------|------------------|------------------|--------|
| Phase 1 | `generate_story()` | `generate_story()` | ✅ Yes | ✅ OK |
| Phase 2 | `generate_phase2_output()` | `generate_phase2_output()` | ⚠️ Missing `selected_*_id` | ⚠️ Missing |
| Phase 3 | `build_storyboard_from_phase2()` | `build_storyboard_from_phase2()` | ✅ Yes | ✅ OK |
| Phase 4 | `generate_video_plan()` | `generate_video_plan()` | ✅ Yes | ✅ OK |
| Phase 5 | `render_segments_from_video_plan()` | `render_segments_from_video_plan()` | ✅ Yes | ✅ OK |
| Phase 5.5 | `assemble_video()` | `assemble_video()` | ⚠️ `retry_failed=False` | ⚠️ Missing |

---

## Gap Analysis

### 1. Phase 2: Missing Selection Parameters

**Gap:**
- UI ไม่ส่ง `selected_character_id` และ `selected_location_id` ไปยัง `generate_phase2_output()`

**Backend Support:**
- ✅ Backend รองรับ `selected_character_id` และ `selected_location_id` parameters (optional)

**Impact:**
- Phase 2 output จะมี `selection.selected_character_id=1` และ `selection.selected_location_id=1` เสมอ
- User เลือก character/location ใน UI แต่ Phase 2 output ไม่สะท้อนการเลือกนั้น
- Phase 3 ใช้ selection จาก session_state แทน (ไม่ใช้จาก phase2_output.selection) ดังนั้นผลกระทบไม่รุนแรง

**Risk Level**: 🟡 **Low** (Phase 3 override ด้วย session_state)

**Recommendation:**
- ไม่ต้องแก้ (Phase 3 ใช้ session_state อยู่แล้ว)
- หรือส่ง `selected_character_id` และ `selected_location_id` ไปยัง Phase 2 (แต่ต้องมี default = 1)

---

### 2. Phase 5.5: Retry Logic Disabled

**Gap:**
- UI ส่ง `retry_failed=False` ไปยัง `assemble_video()`
- Backend มี `assemble_video_with_retry()` ที่รองรับ retry logic ดีกว่า แต่ UI ไม่ใช้

**Backend Support:**
- ✅ Backend มี `assemble_video()` (retry_failed parameter)
- ✅ Backend มี `assemble_video_with_retry()` (retry logic ดีกว่า)

**Impact:**
- ถ้ามี segment ที่ล้มเหลว UI จะไม่ retry
- Backend มี retry logic แต่ UI ปิดไว้

**Risk Level**: 🟡 **Low** (Mock MVP - ไม่มี segment ล้มเหลวจริง)

**Recommendation:**
- ไม่ต้องแก้ (Mock MVP)
- หรือเปลี่ยนเป็น `retry_failed=True` หรือใช้ `assemble_video_with_retry()`

---

## Backend Functions Not Used by UI

### 1. `generate_phase2_json()`

**Function:**
```python
def generate_phase2_json(story_json: str, ...) -> str
```

**Status**: ⚠️ **Not Used**

**Note:**
- UI ใช้ `generate_phase2_output()` แทน (return dict)
- Function นี้ return JSON string (สำหรับ API)
- ไม่จำเป็นสำหรับ UI

---

### 2. `build_storyboard_json()`

**Function:**
```python
def build_storyboard_json(story_json: str, ...) -> str
```

**Status**: ⚠️ **Not Used**

**Note:**
- UI ใช้ `build_storyboard_from_phase2()` แทน (return dict)
- Function นี้ return JSON string (สำหรับ API)
- ไม่จำเป็นสำหรับ UI

---

### 3. `generate_video_plan_json()`

**Function:**
```python
def generate_video_plan_json(storyboard_json: str) -> str
```

**Status**: ⚠️ **Not Used**

**Note:**
- UI ใช้ `generate_video_plan()` แทน (return dict)
- Function นี้ return JSON string (สำหรับ API)
- ไม่จำเป็นสำหรับ UI

---

### 4. `assemble_video_with_retry()`

**Function:**
```python
def assemble_video_with_retry(
    segment_paths: List[str],
    output_path: Optional[str] = None,
    max_retries: int = 3,
    render_segment_fn: Optional[Callable[[int], str]] = None
) -> Dict[str, Any]
```

**Status**: ⚠️ **Not Used**

**Note:**
- UI ใช้ `assemble_video()` แทน
- Function นี้มี retry logic ดีกว่า
- ไม่จำเป็นสำหรับ Mock MVP

---

## UI Features Not Backed by Backend

**Status**: ✅ **None**

- ✅ ทุก UI feature มี backend support
- ✅ ไม่มี UI feature ที่ backend ไม่รองรับ

---

## Recommendations

### Priority: Low

1. **Phase 2 Selection**: 
   - ไม่ต้องแก้ (Phase 3 ใช้ session_state อยู่แล้ว)
   - หรือส่ง `selected_character_id` และ `selected_location_id` ไปยัง Phase 2 (optional)

2. **Phase 5.5 Retry**:
   - ไม่ต้องแก้ (Mock MVP)
   - หรือเปลี่ยนเป็น `retry_failed=True` หรือใช้ `assemble_video_with_retry()`

### Priority: None (สำหรับ Mock MVP)

- JSON functions (`*_json()`) ไม่จำเป็นสำหรับ UI
- `assemble_video_with_retry()` ไม่จำเป็นสำหรับ Mock MVP

---

## Conclusion

### Overall Status: ✅ **OK**

**Summary:**
- ✅ Phase 1-5.5 ถูกเรียกครบถ้วน
- ✅ Button แต่ละ phase เรียก function ที่ถูกต้อง
- ✅ Session state ถูกใช้ถูกทาง
- ⚠️ มี gap เล็กน้อย (Phase 2 selection, Phase 5.5 retry) แต่ไม่รุนแรง

**Risk Assessment:**
- 🟢 **Low Risk**: UI-Backend alignment ดี
- 🟡 **Minor Gaps**: Phase 2 selection, Phase 5.5 retry (ไม่รุนแรง)
- 🔴 **No Critical Issues**: ไม่มี gap ที่ทำให้ระบบพัง

**Readiness:**
- ✅ **Ready for MVP**: UI-Backend alignment พร้อมสำหรับ MVP v0.1
- ✅ **No Breaking Changes**: ไม่ต้องแก้ backend logic
- ✅ **No UI Redesign**: ไม่ต้อง redesign UI

---

*เอกสารนี้เป็น review document - Version: v0.1*
