# Phase Contracts

> เอกสารนี้กำหนดสัญญา (contracts) ระหว่าง Phase ต่างๆ ในระบบ Story Engine  
> **Contract = Input Schema + Output Schema + Invariants**

---

## หลักการ

1. **Schema = สัญญา**: Phase ถัดไปต้องรับ output จาก Phase ก่อนหน้าได้โดยไม่ต้องแปลง
2. **Invariants = ห้ามเปลี่ยน**: Phase ก่อนหน้า = invariant สำหรับ Phase ถัดไป
3. **Breaking Changes = ต้องแจ้งล่วงหน้า**: ห้ามเปลี่ยน schema โดยไม่ได้รับอนุมัติ

---

## Phase 1: Story Logic

**Status**: ✅ ล็อกแล้ว (เสร็จสมบูรณ์)

### Input Schema

```python
# Function parameters
goal: str          # เป้าหมาย (เช่น "ขายคอร์สออนไลน์")
product: str       # ชื่อสินค้า/บริการ
audience: str      # กลุ่มเป้าหมาย
platform: str      # แพลตฟอร์มที่ใช้ (เช่น "Facebook Reel")
```

### Output Schema

```json
{
  "goal": "string",
  "product": "string",
  "audience": "string",
  "platform": "string",
  "scenes": [
    {
      "id": 1,
      "purpose": "hook|conflict|reveal|close",
      "emotion": "string",
      "duration": 3|4|5,
      "description": "string"
    }
  ]
}
```

### Invariants

- ✅ **Scene structure**: ทุก scene ต้องมี `id`, `purpose`, `emotion`, `duration`, `description`
- ✅ **Scene purposes**: ต้องเป็น `hook`, `conflict`, `reveal`, `close` เท่านั้น
- ✅ **Scene order**: scenes เรียงตาม `id` (1, 2, 3, 4)
- ✅ **Duration**: scene duration เป็นจำนวนเต็ม (3, 4, หรือ 5 วินาที)
- ✅ **Story fields**: `goal`, `product`, `audience`, `platform` ต้องมีครบ

### Notes

- Phase 1 เป็น Phase แรก ไม่มี input จาก Phase ก่อนหน้า
- Output ใช้เป็น input สำหรับ Phase 2

---

## Phase 2: Character & Location Generator

**Status**: ✅ ล็อกแล้ว (เสร็จสมบูรณ์)

### Input Schema

```python
# Function parameters
story: Dict[str, Any]  # Story object จาก Phase 1
num_characters: int = 4
num_locations: int = 4
selected_character_id: Optional[int] = None
selected_location_id: Optional[int] = None
```

**Required fields ใน `story`:**
- `goal`, `product`, `audience`, `platform`, `scenes`

### Output Schema

```json
{
  "story": { /* Story object จาก Phase 1 */ },
  "characters": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "style": "string",
      "age_range": "string",
      "personality": "string",
      "image_url": "string",
      "image_prompt": "string"
    }
  ],
  "locations": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "scene_purposes": ["string"],
      "style": "string",
      "mood": "string",
      "image_url": "string",
      "image_prompt": "string"
    }
  ],
  "selection": {
    "selected_character_id": 1,
    "selected_location_id": 1
  }
}
```

### Invariants

- ✅ **Story preservation**: `story` object จาก Phase 1 ต้องถูกเก็บไว้ครบถ้วน (immutable)
- ✅ **Character structure**: ทุก character ต้องมี `id`, `name`, `description`, `style`, `age_range`, `personality`, `image_url`, `image_prompt`
- ✅ **Location structure**: ทุก location ต้องมี `id`, `name`, `description`, `scene_purposes`, `style`, `mood`, `image_url`, `image_prompt`
- ✅ **Selection validation**: `selected_character_id` และ `selected_location_id` ต้องมีอยู่ใน `characters` และ `locations` ตามลำดับ
- ✅ **ID uniqueness**: character IDs และ location IDs ต้อง unique

### Notes

- Phase 2 เพิ่ม candidates และ selection แต่ไม่แก้ story จาก Phase 1
- Output ใช้เป็น input สำหรับ Phase 3

---

## Phase 3: Storyboard Builder

**Status**: ✅ ล็อกแล้ว (เสร็จสมบูรณ์)

### Input Schema

```python
# Function parameters
story: Dict[str, Any]                    # Story object จาก Phase 1
selected_character: Optional[Dict]       # Selected character จาก Phase 2
selected_location: Optional[Dict]        # Selected location จาก Phase 2
```

**หรือ**

```python
phase2_output: Dict[str, Any]           # Phase 2 output
selected_character_id: Optional[int]
selected_location_id: Optional[int]
```

**Required fields ใน `story`:**
- `goal`, `product`, `audience`, `platform`, `scenes`

### Output Schema

```json
{
  "story": {
    "goal": "string",
    "product": "string",
    "audience": "string",
    "platform": "string"
  },
  "selected_character": { /* Character object */ },
  "selected_location": { /* Location object */ },
  "scenes": [
    {
      "scene_id": 1,
      "purpose": "hook|conflict|reveal|close",
      "emotion": "string",
      "duration": 3|4|5,
      "description": "string",
      "keyframes": [
        {
          "id": "scene_1_kf_1",
          "timing": 1.5,
          "description": "string",
          "image_path": "storyboard/scene_1/keyframe_1.jpg",
          "image_prompt": "string"
        }
      ]
    }
  ]
}
```

### Invariants

- ✅ **Keyframe ID format**: ต้องเป็น `scene_{scene_id}_kf_{n}` (unique ข้าม scene)
- ✅ **Keyframe structure**: ทุก keyframe ต้องมี `id`, `timing`, `description`, `image_path`, `image_prompt`
- ✅ **Keyframe count**: จำนวน keyframes ตาม duration:
  - `duration <= 3`: 1 keyframe
  - `duration <= 5`: 2 keyframes
  - `duration > 5`: 3 keyframes
- ✅ **Story metadata**: `story` object ต้องมี `goal`, `product`, `audience`, `platform` (ไม่ต้องมี `scenes`)
- ✅ **Scene preservation**: scene `purpose`, `emotion`, `duration`, `description` ต้องตรงกับ Phase 1

### Notes

- Phase 3 แปลง scenes เป็น keyframes แต่ไม่แก้ scene structure จาก Phase 1
- Keyframe ID format เป็น invariant สำคัญ (แก้ไขแล้วจาก bug เดิม)
- Output ใช้เป็น input สำหรับ Phase 4

---

## Phase 4: Video Plan Generator

**Status**: ✅ ล็อกแล้ว (เสร็จสมบูรณ์)

### Input Schema

```python
# Function parameters
storyboard: Dict[str, Any]  # Storyboard object จาก Phase 3
```

**Required fields ใน `storyboard`:**
- `story`, `scenes` (แต่ละ scene ต้องมี `keyframes`)

### Output Schema

```json
{
  "storyboard_metadata": {
    "story": { /* Story metadata */ },
    "selected_character": { /* Character object */ },
    "selected_location": { /* Location object */ }
  },
  "segments": [
    {
      "id": 1,
      "scene_id": 1,
      "duration": 1.66,
      "start_time": 0.0,
      "end_time": 1.66,
      "description": "string",
      "purpose": "hook|conflict|reveal|close",
      "emotion": "string",
      "start_keyframe": {
        "id": "scene_1_kf_1",
        "image_path": "string",
        "description": "string",
        "timing": 0.0
      },
      "end_keyframe": {
        "id": "scene_1_kf_2",
        "image_path": "string",
        "description": "string",
        "timing": 1.66
      }
    }
  ],
  "total_duration": 17.0,
  "segment_count": 7
}
```

### Invariants

- ✅ **Segment structure**: ทุก segment ต้องมี `id`, `scene_id`, `duration`, `start_time`, `end_time`, `description`, `purpose`, `emotion`
- ✅ **Keyframe objects**: `start_keyframe` และ `end_keyframe` ต้องเป็น objects (dict) ที่มี:
  - `id`: string (keyframe ID format)
  - `image_path`: string
  - `description`: string
  - `timing`: float
- ✅ **Keyframe completeness**: `start_keyframe` และ `end_keyframe` ต้องมี required fields ครบ (Phase 5 ใช้ตรง ๆ โดยไม่ fallback)
- ✅ **Duration calculation**: segment duration คำนวณจาก keyframe timing (minimum = 1.0 วินาที)
- ✅ **Storyboard metadata**: `storyboard_metadata` ต้องเก็บ `story`, `selected_character`, `selected_location` ไว้

### Notes

- Phase 4 แปลง keyframes เป็น segments แต่ไม่แก้ keyframe structure จาก Phase 3
- **Contract กับ Phase 5**: `start_keyframe` และ `end_keyframe` ต้องเป็น objects ครบถ้วน (Phase 5 ใช้ตรง ๆ)
- Output ใช้เป็น input สำหรับ Phase 5

---

## Phase 5: Segment Renderer

**Status**: ✅ ล็อกแล้ว (เสร็จสมบูรณ์)

### Input Schema

```python
# Function parameters
video_plan: Dict[str, Any]  # Video Plan object จาก Phase 4
story_context: Optional[Dict[str, Any]] = None
output_dir: str = "output/segments"
```

**Required fields ใน `video_plan`:**
- `segments` (แต่ละ segment ต้องมี `start_keyframe`, `end_keyframe` objects ครบ)

### Output Schema

```json
{
  "success": true,
  "total_segments": 7,
  "successful_segments": 7,
  "failed_segments": [],
  "rendered_segments": [
    {
      "success": true,
      "segment_id": 1,
      "video_path": "output/segments/segment_123456_20241214_abc123.mp4",
      "duration": 8.0,
      "prompt": "string",
      "error": null,
      "metadata": { /* API metadata */ }
    }
  ]
}
```

### Invariants

- ✅ **Segment duration**: **ทุก segment = 8.0 วินาที (fix)** - ห้ามเปลี่ยน
- ✅ **Render per segment**: ห้าม gen วิดีโอยาวรวดเดียว ต้อง render ทีละ segment
- ✅ **Segment schema**: ทุก segment ต้องมี:
  - `start_keyframe`: object (dict) ต้องมี `id`, `image_path`, `description`, `timing`
  - `end_keyframe`: object (dict) ต้องมี `id`, `image_path`, `description`, `timing`
  - `directive`: object (dict) ต้องมี `motion_type`, `camera_movement`, `transition_style`
  - `continuity_locks`: object (dict) ต้องมี `character`, `location`, `style`, `emotion`
- ✅ **Keyframe validation**: `start_keyframe` และ `end_keyframe` ต้องเป็น objects (dict) ไม่ใช่ string หรือ null
- ✅ **Duration validation**: ถ้า segment `duration` ไม่ใช่ 8.0 จะ return error

### Contract: Phase 4 → Phase 5

**สำคัญมาก**: Phase 4 ต้องส่ง `start_keyframe` และ `end_keyframe` เป็น objects ครบถ้วน

**Phase 4 รับผิดชอบ:**
- ✅ สร้าง `start_keyframe` object ที่มี: `id`, `image_path`, `description`, `timing`
- ✅ สร้าง `end_keyframe` object ที่มี: `id`, `image_path`, `description`, `timing`
- ✅ Validate ว่า keyframe objects มี required fields ครบ

**Phase 5 รับผิดชอบ:**
- ✅ Validate ว่า `start_keyframe` และ `end_keyframe` เป็น objects
- ✅ Validate ว่า keyframe objects มี required fields ครบ
- ✅ **ไม่ fallback**: ถ้า keyframe objects ไม่ครบ จะ return error (ไม่สร้างเอง)

**8 วินาที Contract:**
- ✅ Phase 4 ส่ง segment ที่มี `duration` ตาม keyframe timing (variable)
- ✅ Phase 5 **ต้องแปลงทุก segment เป็น 8.0 วินาที** (fix)
- ✅ Phase 5 ห้ามใช้ `duration` จาก Phase 4 โดยตรง

### Notes

- Phase 5 เป็น Phase ที่ render video segments (8 วินาทีต่อ segment)
- **8 วินาที = invariant**: ห้ามเปลี่ยน duration
- Output ใช้เป็น input สำหรับ Phase 5.5

---

## Phase 5.5: Video Assembler

**Status**: ✅ ล็อกแล้ว (เสร็จสมบูรณ์)

### Input Schema

```python
# Function parameters
segment_paths: List[str]  # List of segment video file paths
output_path: Optional[str] = None
retry_failed: bool = True
max_retries: int = 3
```

**หรือ**

```python
render_result: Dict[str, Any]  # Render result จาก Phase 5
```

### Output Schema

```json
{
  "success": true,
  "output_path": "output/final_video_20241214_abc123.mp4",
  "failed_segments": [],
  "retry_count": 0,
  "total_segments": 7,
  "successful_segments": 7
}
```

### Invariants

- ✅ **Segment paths**: `segment_paths` ต้องเป็น list of strings (file paths)
- ✅ **Retry logic**: ถ้า segment ล้มเหลว ต้อง retry ตาม `max_retries`
- ✅ **Output path**: ถ้าไม่ระบุ `output_path` จะสร้าง path ใหม่
- ✅ **Success criteria**: `success = true` เมื่อ `failed_segments` ว่าง

### Notes

- Phase 5.5 ประกอบ video segments เป็น final video
- รับ segment paths จาก Phase 5 (rendered video files)
- Output = final video file path

---

## Contract Summary

### Phase Flow

```
Phase 1 (Story) 
  → Phase 2 (Characters/Locations)
    → Phase 3 (Storyboard)
      → Phase 4 (Video Plan)
        → Phase 5 (Segment Renderer) [8 วินาที]
          → Phase 5.5 (Assembler)
```

### Critical Contracts

1. **Phase 1 → Phase 2**: Story object ต้อง immutable
2. **Phase 3 → Phase 4**: Keyframe ID format = `scene_{id}_kf_{n}`
3. **Phase 4 → Phase 5**: 
   - `start_keyframe` และ `end_keyframe` ต้องเป็น objects ครบถ้วน
   - **8 วินาที contract**: Phase 5 แปลงทุก segment เป็น 8.0 วินาที (fix)
4. **Phase 5 → Phase 5.5**: Segment paths ต้องเป็น valid file paths

### Breaking Changes Policy

- ห้ามเปลี่ยน schema โดยไม่ได้รับอนุมัติ
- ถ้าจำเป็นต้องเปลี่ยน ต้อง:
  1. ขออนุมัติก่อน
  2. ใช้ versioning (v0.1, v0.2, ...)
  3. พยายาม backward-compatible เสมอ

---

*เอกสารนี้เป็น contract หลักของระบบ - Version: v0.1*

