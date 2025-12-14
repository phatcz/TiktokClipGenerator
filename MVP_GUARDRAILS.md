# MVP v0.1 - Guardrails & Constraints

**Version:** 0.1  
**Status:** 🔒 ENFORCED  
**Date:** 2024-12-14

---

## Overview

เอกสารนี้อธิบาย **guardrails** สำหรับ MVP v0.1 ระบุสิ่งที่ห้ามแก้ สิ่งที่แก้ได้ และสิ่งที่ต้อง bump version เท่านั้นถึงจะแก้ได้

**หลักการ:**
- **DO NOT TOUCH** = ห้ามแก้โดยเด็ดขาด (จะทำลาย contract/schema)
- **EDITABLE** = แก้ได้ (ไม่กระทบ contract/schema)
- **VERSION BUMP REQUIRED** = ต้อง bump version (v0.1 → v0.2) ก่อนแก้

---

## 🔴 DO NOT TOUCH (ห้ามแก้โดยเด็ดขาด)

### 1. Schema Definitions

**ห้ามแก้:**
- Field names ใน output schema (เช่น `goal`, `product`, `scenes`, `keyframes`)
- Field types (เช่น `id` ต้องเป็น `int`, `description` ต้องเป็น `string`)
- Required vs Optional fields
- Nested object structures (เช่น `start_keyframe`, `end_keyframe` objects)

**ไฟล์ที่ห้ามแก้ schema:**
- `story_engine.py` - Story schema
- `phase2_generator.py` - Phase 2 output schema
- `phase3_storyboard.py` - Storyboard schema
- `phase4_video_plan.py` - Video Plan schema
- `phase5_segment_renderer.py` - Segment schema
- `phase5_assembler.py` - Assembly result schema

**เหตุผล:** Schema = contract ระหว่าง phases, เปลี่ยนแล้วจะทำลาย backward compatibility

---

### 2. Function Signatures

**ห้ามแก้:**
- Function names (เช่น `generate_story`, `build_storyboard_from_phase2`)
- Parameter names (เช่น `goal`, `product`, `story`, `video_plan`)
- Parameter types (เช่น `str`, `Dict[str, Any]`, `List[str]`)
- Return types (เช่น `Dict[str, Any]`, `str`)
- Required vs Optional parameters
- Default parameter values (เช่น `num_characters: int = 4`)

**ตัวอย่างที่ห้ามแก้:**
```python
# ❌ ห้ามเปลี่ยน
def generate_story(goal: str, product: str, audience: str, platform: str) -> Dict[str, Any]:
    ...

# ❌ ห้ามเปลี่ยน
def render_segments_from_video_plan(
    video_plan: Dict[str, Any],
    story_context: Optional[Dict[str, Any]] = None,
    output_dir: str = "output/segments"
) -> Dict[str, Any]:
    ...
```

**เหตุผล:** Function signature = public API, เปลี่ยนแล้วจะทำลาย caller code

---

### 3. Phase Order & Flow

**ห้ามแก้:**
- Phase order: 1 → 2 → 3 → 4 → 5 → 5.5
- Phase dependencies (Phase N ต้องใช้ output จาก Phase N-1)
- Phase contracts (เช่น Phase 4 → Phase 5 contract)

**ไฟล์ที่ห้ามแก้ flow:**
- `end_to_end_run.py` - Phase execution order
- `app_streamlit.py` - Phase button order
- Phase modules - Input/output dependencies

**เหตุผล:** Phase order = architecture invariant, เปลี่ยนแล้วจะทำลาย pipeline

---

### 4. Critical Invariants

**ห้ามแก้:**

#### Phase 1 Invariants
- Scene purposes: `hook`, `conflict`, `reveal`, `close` (4 scenes)
- Scene order: เรียงตาม `id` (1, 2, 3, 4)
- Scene duration: 3, 4, หรือ 5 วินาที (integer)

#### Phase 3 Invariants
- Keyframe ID format: `scene_{scene_id}_kf_{n}` (unique ข้าม scene)
- Keyframe count logic:
  - `duration <= 3`: 1 keyframe
  - `duration <= 5`: 2 keyframes
  - `duration > 5`: 3 keyframes
- Image path format: `storyboard/scene_{scene_id}/keyframe_{n}.jpg`

#### Phase 4 Invariants
- `start_keyframe` และ `end_keyframe` ต้องเป็น **objects** (dict) ไม่ใช่ string หรือ null
- Keyframe objects ต้องมี fields ครบ: `id`, `image_path`, `description`, `timing`
- Minimum segment duration: 1.0 วินาที

#### Phase 5 Invariants
- **Segment duration = 8.0 วินาที (FIX)** - ห้ามเปลี่ยน
- **Render per segment** - ห้าม gen วิดีโอยาวรวดเดียว
- `start_keyframe` และ `end_keyframe` validation (strict, no fallback)

#### Phase 5.5 Invariants
- Retry logic structure (ถ้ามี)
- Output path format (ถ้ามี)

**เหตุผล:** Invariants = business rules, เปลี่ยนแล้วจะทำลาย logic

---

### 5. Contract Definitions

**ห้ามแก้:**
- Phase 4 → Phase 5 contract (`contracts/phase4_to_phase5.md`)
- Phase contracts (`PHASE_CONTRACTS.md`)
- Schema contracts ระหว่าง phases

**ไฟล์ที่ห้ามแก้:**
- `contracts/phase4_to_phase5.md`
- `PHASE_CONTRACTS.md`

**เหตุผล:** Contracts = สัญญาระหว่าง phases, เปลี่ยนแล้วจะทำลาย integration

---

### 6. Mock API Interfaces

**ห้ามแก้:**
- Mock function signatures (เช่น `mock_google_image_generation(prompt: str) -> str`)
- Mock return format (เช่น return type, structure)
- Mock function names

**ไฟล์ที่ห้ามแก้ mock interface:**
- `phase2_generator.py` - `mock_google_image_generation()`
- `phase5_segment_renderer.py` - `mock_google_video_generation()`
- `phase5_assembler.py` - `mock_video_stitch()`

**หมายเหตุ:** Mock implementation (body) แก้ได้ แต่ interface ต้องเหมือนเดิม

**เหตุผล:** Mock interface = contract สำหรับ API integration, เปลี่ยนแล้วจะทำลาย migration path

---

### 7. Validation Logic (Core)

**ห้ามแก้:**
- Required field validation (เช่น ตรวจสอบว่า `start_keyframe` มีอยู่)
- Type validation (เช่น ตรวจสอบว่า `start_keyframe` เป็น dict)
- Contract validation (เช่น Phase 4 → Phase 5 contract validation)

**ตัวอย่างที่ห้ามแก้:**
```python
# ❌ ห้ามลบหรือแก้ validation นี้
if "start_keyframe" not in segment:
    raise ValueError(f"Segment {segment.get('id')} missing 'start_keyframe' field")

# ❌ ห้ามลบหรือแก้ validation นี้
if not isinstance(start_keyframe, dict):
    raise ValueError(f"Segment {segment.get('id')} 'start_keyframe' must be an object (dict)")
```

**เหตุผล:** Validation = guardrail, เปลี่ยนแล้วจะทำให้ invalid data ผ่านได้

---

### 8. Test Fixtures & Expected Outputs

**ห้ามแก้:**
- Test fixtures (`tests/fixtures/*.json`)
- Expected outputs ใน tests
- Test assertions (ถ้า test ผ่านแล้ว)

**ไฟล์ที่ห้ามแก้:**
- `tests/fixtures/sample_story_1.json`
- `tests/fixtures/sample_story_2.json`
- `tests/fixtures/sample_story_3.json`
- `tests/test_end_to_end.py` - Expected outputs

**เหตุผล:** Test fixtures = regression tests, เปลี่ยนแล้วจะทำลาย test coverage

---

## 🟡 EDITABLE (แก้ได้ - ไม่กระทบ contract)

### 1. Mock Implementation (Body Only)

**แก้ได้:**
- Mock function body (implementation)
- Mock return values (ถ้า format เหมือนเดิม)
- Mock error simulation

**ตัวอย่างที่แก้ได้:**
```python
# ✅ แก้ได้: Mock implementation
def mock_google_image_generation(prompt: str) -> str:
    # แก้ logic นี้ได้ (แต่ return type ต้องเป็น str)
    image_id = hash(prompt) % 1000000
    return f"https://mock-images.google.com/generated/{image_id}.jpg"
```

**ข้อจำกัด:** ต้อง maintain return type และ format เดิม

---

### 2. Error Messages (Text Only)

**แก้ได้:**
- Error message text (เช่น "Segment missing field" → "Segment is missing required field")
- Error message language (ถ้าไม่เปลี่ยน structure)

**ตัวอย่างที่แก้ได้:**
```python
# ✅ แก้ได้: Error message text
raise ValueError(f"Segment {segment.get('id')} missing 'start_keyframe' field")
# → แก้เป็น
raise ValueError(f"Segment {segment.get('id')} is missing required 'start_keyframe' field")
```

**ข้อจำกัด:** ต้อง maintain error type (เช่น `ValueError`) และ structure เดิม

---

### 3. Comments & Docstrings

**แก้ได้:**
- Comments (เช่น `# TODO`, `# NOTE`)
- Docstrings (เช่น function descriptions, parameter descriptions)
- Documentation strings

**ตัวอย่างที่แก้ได้:**
```python
# ✅ แก้ได้: Comments
# Mock API สำหรับ Google Image Generation
# ในอนาคตจะแทนที่ด้วย API จริง

# ✅ แก้ได้: Docstrings
"""
สร้าง Story JSON จาก inputs ที่ได้รับ

Args:
    goal: เป้าหมาย (เช่น "ขายคอร์สออนไลน์")
    ...
"""
```

**ข้อจำกัด:** ต้อง maintain accuracy (ไม่เขียนผิด)

---

### 4. Logging & Debug Output

**แก้ได้:**
- Log messages
- Debug print statements
- Logging levels

**ตัวอย่างที่แก้ได้:**
```python
# ✅ แก้ได้: Log messages
print(f"Generating story for goal: {goal}")
# → แก้เป็น
logger.info(f"Starting story generation for goal: {goal}")
```

**ข้อจำกัด:** ต้องไม่เปลี่ยน logic flow

---

### 5. Code Style & Formatting

**แก้ได้:**
- Code formatting (เช่น whitespace, line breaks)
- Variable naming (local variables, not function parameters)
- Code organization (เช่น function order, import order)

**ตัวอย่างที่แก้ได้:**
```python
# ✅ แก้ได้: Code formatting
def generate_story(goal: str, product: str, audience: str, platform: str) -> Dict[str, Any]:
    scenes = []
    # ...

# → แก้เป็น
def generate_story(
    goal: str,
    product: str,
    audience: str,
    platform: str
) -> Dict[str, Any]:
    scenes = []
    # ...
```

**ข้อจำกัด:** ต้องไม่เปลี่ยน logic หรือ function signature

---

### 6. Helper Functions (Private)

**แก้ได้:**
- Private helper functions (functions ที่ไม่ได้ export)
- Internal utility functions
- Helper logic (ถ้าไม่เปลี่ยน public interface)

**ตัวอย่างที่แก้ได้:**
```python
# ✅ แก้ได้: Private helper function
def _calculate_keyframe_timing(duration: float, num_keyframes: int) -> float:
    # แก้ logic นี้ได้ (ถ้าไม่เปลี่ยน return type)
    ...
```

**ข้อจำกัด:** ต้องไม่เปลี่ยน public interface หรือ output format

---

### 7. Default Values (Non-Critical)

**แก้ได้:**
- Default values ที่ไม่กระทบ contract (เช่น `output_dir: str = "output/segments"`)
- Optional parameter defaults

**ตัวอย่างที่แก้ได้:**
```python
# ✅ แก้ได้: Default value (ไม่กระทบ contract)
def render_segments_from_video_plan(
    video_plan: Dict[str, Any],
    story_context: Optional[Dict[str, Any]] = None,
    output_dir: str = "output/segments"  # แก้ได้
) -> Dict[str, Any]:
    ...
```

**ข้อจำกัด:** ต้องไม่เปลี่ยน required parameters หรือ return types

---

### 8. Supporting Files (Non-Core)

**แก้ได้:**
- Documentation files (เช่น `PROGRESS.md`, `SETUP.md`)
- UI files (เช่น `app_streamlit.py` - UI logic only, not phase logic)
- Test utilities (ถ้าไม่เปลี่ยน test assertions)

**ไฟล์ที่แก้ได้:**
- `PROGRESS.md`
- `SETUP.md`
- `readme.md` (documentation only)
- `app_streamlit.py` (UI only, not phase logic)
- `end_to_end_run.py` (runner only, not phase logic)

**ข้อจำกัด:** ต้องไม่เปลี่ยน phase logic หรือ schema

---

## 🟠 VERSION BUMP REQUIRED (ต้อง bump version ก่อนแก้)

### 1. Schema Changes

**ต้อง bump version:**
- เพิ่ม field ใหม่ (breaking change)
- ลบ field (breaking change)
- เปลี่ยน field type (breaking change)
- เปลี่ยน required → optional หรือ vice versa (breaking change)

**ตัวอย่างที่ต้อง bump version:**
```python
# ❌ ต้อง bump version: เพิ่ม field ใหม่
{
    "goal": "string",
    "product": "string",
    "new_field": "string"  # ← ต้อง bump version
}

# ❌ ต้อง bump version: เปลี่ยน field type
{
    "duration": 3,  # int → float
    "duration": 3.0  # ← ต้อง bump version
}
```

**Process:**
1. Bump version: v0.1 → v0.2
2. Update schema documentation
3. Update contracts
4. Update tests
5. Migration guide (ถ้าจำเป็น)

---

### 2. Function Signature Changes

**ต้อง bump version:**
- เพิ่ม required parameter (breaking change)
- ลบ parameter (breaking change)
- เปลี่ยน parameter type (breaking change)
- เปลี่ยน return type (breaking change)

**ตัวอย่างที่ต้อง bump version:**
```python
# ❌ ต้อง bump version: เพิ่ม required parameter
def generate_story(
    goal: str,
    product: str,
    audience: str,
    platform: str,
    new_param: str  # ← ต้อง bump version
) -> Dict[str, Any]:
    ...

# ❌ ต้อง bump version: เปลี่ยน return type
def generate_story(...) -> Dict[str, Any]:  # → str  # ← ต้อง bump version
    ...
```

**Process:**
1. Bump version: v0.1 → v0.2
2. Update function documentation
3. Update callers
4. Backward compatibility layer (ถ้าจำเป็น)

---

### 3. Phase Order Changes

**ต้อง bump version:**
- เปลี่ยน phase order (breaking change)
- เพิ่ม phase ใหม่ (breaking change)
- ลบ phase (breaking change)

**ตัวอย่างที่ต้อง bump version:**
```
# ❌ ต้อง bump version: เปลี่ยน phase order
Phase 1 → Phase 3 → Phase 2 → ...  # ← ต้อง bump version

# ❌ ต้อง bump version: เพิ่ม phase ใหม่
Phase 1 → Phase 2 → Phase 2.5 → Phase 3 → ...  # ← ต้อง bump version
```

**Process:**
1. Bump version: v0.1 → v0.2
2. Update architecture documentation
3. Update contracts
4. Migration guide

---

### 4. Invariant Changes

**ต้อง bump version:**
- เปลี่ยน business rules (เช่น scene purposes, keyframe count logic)
- เปลี่ยน constraints (เช่น duration constraints, format constraints)

**ตัวอย่างที่ต้อง bump version:**
```python
# ❌ ต้อง bump version: เปลี่ยน scene purposes
# เดิม: hook, conflict, reveal, close
# ใหม่: hook, conflict, reveal, close, outro  # ← ต้อง bump version

# ❌ ต้อง bump version: เปลี่ยน duration constraint
# เดิม: duration = 8.0 (fix)
# ใหม่: duration = variable  # ← ต้อง bump version
```

**Process:**
1. Bump version: v0.1 → v0.2
2. Update invariant documentation
3. Update contracts
4. Update tests
5. Migration guide

---

### 5. Contract Changes

**ต้อง bump version:**
- เปลี่ยน contract ระหว่าง phases (breaking change)
- เปลี่ยน contract format (breaking change)

**ตัวอย่างที่ต้อง bump version:**
```python
# ❌ ต้อง bump version: เปลี่ยน contract
# เดิม: start_keyframe และ end_keyframe ต้องเป็น objects
# ใหม่: start_keyframe_id และ end_keyframe_id (string)  # ← ต้อง bump version
```

**Process:**
1. Bump version: v0.1 → v0.2
2. Update contract documentation
3. Update both phases
4. Migration guide

---

## 📋 Quick Reference Checklist

### ก่อนแก้ไขไฟล์ Phase Module

- [ ] ตรวจสอบว่าไฟล์อยู่ใน "DO NOT TOUCH" หรือไม่
- [ ] ตรวจสอบว่าแก้ไขอยู่ใน "EDITABLE" หรือไม่
- [ ] ถ้าแก้ไขอยู่ใน "VERSION BUMP REQUIRED" → ขออนุมัติก่อน
- [ ] ตรวจสอบว่าไม่เปลี่ยน schema, function signature, หรือ contract
- [ ] ตรวจสอบว่าไม่เปลี่ยน phase order หรือ flow
- [ ] ตรวจสอบว่าไม่เปลี่ยน invariants หรือ business rules

### ก่อนแก้ไข Schema

- [ ] ตรวจสอบว่าเป็น breaking change หรือไม่
- [ ] ถ้าเป็น breaking change → bump version (v0.1 → v0.2)
- [ ] อัพเดท documentation
- [ ] อัพเดท contracts
- [ ] อัพเดท tests
- [ ] Migration guide (ถ้าจำเป็น)

### ก่อนแก้ไข Function Signature

- [ ] ตรวจสอบว่าเป็น breaking change หรือไม่
- [ ] ถ้าเป็น breaking change → bump version (v0.1 → v0.2)
- [ ] อัพเดท callers
- [ ] Backward compatibility layer (ถ้าจำเป็น)

---

## 🚨 Critical Warnings

### ⚠️ ห้ามแก้ไขโดยเด็ดขาด

1. **Schema fields** - เปลี่ยนแล้วจะทำลาย backward compatibility
2. **Function signatures** - เปลี่ยนแล้วจะทำลาย caller code
3. **Phase order** - เปลี่ยนแล้วจะทำลาย pipeline
4. **Invariants** - เปลี่ยนแล้วจะทำลาย business logic
5. **Contracts** - เปลี่ยนแล้วจะทำลาย phase integration

### ⚠️ ต้องขออนุมัติก่อน

1. **Version bump** - ต้องได้รับอนุมัติจาก System Lead
2. **Breaking changes** - ต้องได้รับอนุมัติจาก System Lead
3. **Architecture changes** - ต้องได้รับอนุมัติจาก System Lead

### ⚠️ ถ้าไม่แน่ใจ

1. **หยุด** - ห้ามแก้ไขต่อ
2. **ถามกลับ** - ถาม System Lead หรือ Product Owner
3. **อย่าสมมติ** - ห้ามสมมติว่าการแก้ไขจะไม่กระทบ

---

## 📚 Related Documents

- `MVP_LOCK.md` - MVP Lock Document
- `WORKFLOW.md` - Development Workflow
- `PHASE_CONTRACTS.md` - Phase Contracts
- `contracts/phase4_to_phase5.md` - Phase 4-5 Contract

---

## Summary

**DO NOT TOUCH:**
- Schema definitions
- Function signatures
- Phase order & flow
- Critical invariants
- Contract definitions
- Mock API interfaces
- Validation logic (core)
- Test fixtures

**EDITABLE:**
- Mock implementation (body)
- Error messages (text)
- Comments & docstrings
- Logging & debug output
- Code style & formatting
- Helper functions (private)
- Default values (non-critical)
- Supporting files (non-core)

**VERSION BUMP REQUIRED:**
- Schema changes
- Function signature changes
- Phase order changes
- Invariant changes
- Contract changes

---

**Last Updated:** 2024-12-14  
**Maintained By:** Development Team  
**Version:** 0.1
