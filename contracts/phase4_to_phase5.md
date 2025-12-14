# Phase 4 → Phase 5 Contract

**Version:** v1.0  
**Last Updated:** 2024-12-14  
**Status:** Locked

---

## ภาพรวม

เอกสารนี้กำหนด **contract** ระหว่าง Phase 4 (Video Plan Generator) และ Phase 5 (Segment Renderer)

**หลักการ:**
- Phase 4 ต้องส่ง segments ที่มี `start_keyframe` และ `end_keyframe` objects ครบ
- Phase 5 ใช้ข้อมูลจาก Phase 4 โดยตรง **ไม่ fallback**
- Phase 5 จะสร้าง `directive` และ `continuity_locks` เอง

---

## Input Schema จาก Phase 4

Phase 4 ส่ง `video_plan` object ที่มีโครงสร้าง:

```json
{
  "storyboard_metadata": {
    "story": {...},
    "selected_character": {...},
    "selected_location": {...}
  },
  "segments": [
    {
      "id": 1,
      "scene_id": 1,
      "duration": 1.5,
      "start_time": 0.0,
      "end_time": 1.5,
      "description": "start → end",
      "purpose": "hook",
      "emotion": "curious",
      "start_keyframe": {
        "id": "scene_1_kf_1",
        "image_path": "storyboard/scene_1/keyframe_1.jpg",
        "description": "เปิดฉากด้วยคำถามที่น่าสนใจ",
        "timing": 1.5
      },
      "end_keyframe": {
        "id": "scene_2_kf_1",
        "image_path": "storyboard/scene_2/keyframe_1.jpg",
        "description": "แสดงปัญหาและความยากลำบาก",
        "timing": 1.67
      }
    }
  ],
  "total_duration": 10.83,
  "segment_count": 7
}
```

### Segment Schema (Phase 4 Output)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `int` | ✅ REQUIRED | Segment ID (unique) |
| `scene_id` | `int` | ✅ REQUIRED | Scene ID ที่ segment นี้อยู่ |
| `duration` | `float` | ✅ REQUIRED | Duration ของ segment (วินาที) - **ไม่ fix = 8** |
| `start_time` | `float` | ✅ REQUIRED | Start time ใน video (วินาที) |
| `end_time` | `float` | ✅ REQUIRED | End time ใน video (วินาที) |
| `description` | `string` | ✅ REQUIRED | Description ของ segment |
| `purpose` | `string` | ✅ REQUIRED | Scene purpose (hook/conflict/reveal/close) |
| `emotion` | `string` | ✅ REQUIRED | Emotion ของ scene |
| `start_keyframe` | `object` | ✅ **REQUIRED** | Start keyframe object (ดูด้านล่าง) |
| `end_keyframe` | `object` | ✅ **REQUIRED** | End keyframe object (ดูด้านล่าง) |

### Start Keyframe Object Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | ✅ **REQUIRED** | Keyframe ID (format: `scene_{scene_id}_kf_{n}`) |
| `image_path` | `string` | ✅ **REQUIRED** | Path ของ keyframe image |
| `description` | `string` | ✅ **REQUIRED** | Description ของ keyframe |
| `timing` | `float` | ✅ **REQUIRED** | Timing ใน scene (วินาที) |

### End Keyframe Object Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | ✅ **REQUIRED** | Keyframe ID (format: `scene_{scene_id}_kf_{n}`) |
| `image_path` | `string` | ✅ **REQUIRED** | Path ของ keyframe image |
| `description` | `string` | ✅ **REQUIRED** | Description ของ keyframe |
| `timing` | `float` | ✅ **REQUIRED** | Timing ใน scene (วินาที) |

---

## Output Schema ที่ Phase 5 ต้องการ

Phase 5 ต้องการ segment ที่มีโครงสร้าง:

```json
{
  "id": 1,
  "duration": 8.0,
  "start_keyframe": {
    "id": "scene_1_kf_1",
    "image_path": "storyboard/scene_1/keyframe_1.jpg",
    "description": "เปิดฉากด้วยคำถามที่น่าสนใจ",
    "timing": 1.5
  },
  "end_keyframe": {
    "id": "scene_2_kf_1",
    "image_path": "storyboard/scene_2/keyframe_1.jpg",
    "description": "แสดงปัญหาและความยากลำบาก",
    "timing": 1.67
  },
  "directive": {
    "motion_type": "smooth",
    "camera_movement": "none",
    "transition_style": "fade"
  },
  "continuity_locks": {
    "character": "ผู้เชี่ยวชาญ",
    "location": "สถานที่ทำงาน",
    "style": "professional",
    "emotion": "curious"
  },
  "metadata": {
    "scene_id": 1,
    "purpose": "hook",
    "original_duration": 1.5
  }
}
```

### Segment Schema (Phase 5 Input)

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `id` | `int` | ✅ REQUIRED | จาก Phase 4 |
| `duration` | `float` | ✅ REQUIRED | **Fix = 8.0** (Phase 5 จะ override) |
| `start_keyframe` | `object` | ✅ **REQUIRED** | จาก Phase 4 (ใช้โดยตรง) |
| `end_keyframe` | `object` | ✅ **REQUIRED** | จาก Phase 4 (ใช้โดยตรง) |
| `directive` | `object` | ✅ REQUIRED | **Phase 5 สร้างเอง** |
| `continuity_locks` | `object` | ✅ REQUIRED | **Phase 5 สร้างเอง** (จาก storyboard_metadata) |
| `metadata` | `object` | ⚪ OPTIONAL | Phase 5 สร้างเอง (scene_id, purpose, original_duration) |

### Directive Object (Phase 5 สร้างเอง)

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `motion_type` | `string` | ✅ REQUIRED | `"smooth"` |
| `camera_movement` | `string` | ✅ REQUIRED | `"none"` |
| `transition_style` | `string` | ✅ REQUIRED | `"fade"` |

### Continuity Locks Object (Phase 5 สร้างเอง)

| Field | Type | Required | Source |
|-------|------|----------|--------|
| `character` | `string` | ⚪ OPTIONAL | จาก `storyboard_metadata.selected_character.name` |
| `location` | `string` | ⚪ OPTIONAL | จาก `storyboard_metadata.selected_location.name` |
| `style` | `string` | ⚪ OPTIONAL | จาก `storyboard_metadata.selected_location.style` |
| `emotion` | `string` | ✅ REQUIRED | จาก Phase 4 segment `emotion` |

---

## กติกา Duration

### Phase 4
- **ไม่ fix duration = 8**
- Duration คำนวณจาก keyframe timing
- Minimum duration = 1.0 วินาที
- Duration อาจเป็นค่าใดก็ได้ (เช่น 1.5, 2.3, 5.7 วินาที)

### Phase 5
- **Fix duration = 8.0 วินาที**
- Phase 5 จะ override duration เป็น 8.0 เสมอ
- Phase 4 duration เก็บไว้ใน `metadata.original_duration`

**หมายเหตุ:** Phase 4 duration ไม่ต้องตรงกับ 8.0 เพราะ Phase 5 จะจัดการเอง

---

## Field ที่ REQUIRED / OPTIONAL

### Phase 4 Segment (Output)

#### REQUIRED Fields
- ✅ `id` (int)
- ✅ `scene_id` (int)
- ✅ `duration` (float)
- ✅ `start_time` (float)
- ✅ `end_time` (float)
- ✅ `description` (string)
- ✅ `purpose` (string)
- ✅ `emotion` (string)
- ✅ **`start_keyframe`** (object) - **CRITICAL**
- ✅ **`end_keyframe`** (object) - **CRITICAL**

#### Keyframe Object REQUIRED Fields
- ✅ `id` (string)
- ✅ `image_path` (string)
- ✅ `description` (string)
- ✅ `timing` (float)

### Phase 5 Segment (Input)

#### REQUIRED Fields
- ✅ `id` (int) - จาก Phase 4
- ✅ `duration` (float) - Fix = 8.0 (Phase 5 override)
- ✅ **`start_keyframe`** (object) - จาก Phase 4
- ✅ **`end_keyframe`** (object) - จาก Phase 4
- ✅ `directive` (object) - Phase 5 สร้างเอง
- ✅ `continuity_locks` (object) - Phase 5 สร้างเอง

#### OPTIONAL Fields
- ⚪ `metadata` (object) - Phase 5 สร้างเอง

---

## สิ่งที่ Phase 4 "ต้องรับประกัน"

Phase 4 **ต้องรับประกัน** ว่า:

### 1. Start Keyframe และ End Keyframe Objects
- ✅ **ทุก segment ต้องมี `start_keyframe` และ `end_keyframe` objects**
- ✅ **`start_keyframe` และ `end_keyframe` ต้องเป็น objects (dict) ไม่ใช่ null หรือ undefined**
- ✅ **ห้ามส่ง `start_keyframe_id` หรือ `end_keyframe_id` (ใช้ object แทน)**

### 2. Keyframe Object Fields
- ✅ **`start_keyframe` ต้องมี fields ครบ: `id`, `image_path`, `description`, `timing`**
- ✅ **`end_keyframe` ต้องมี fields ครบ: `id`, `image_path`, `description`, `timing`**
- ✅ **ทุก field ต้องไม่เป็น `null`, `undefined`, หรือ empty string**

### 3. Keyframe ID Format
- ✅ **Keyframe ID ต้องเป็น string**
- ✅ **Format: `scene_{scene_id}_kf_{n}` (เช่น `scene_1_kf_1`)**
- ✅ **Keyframe ID ต้อง unique ข้าม scene**

### 4. Image Path Format
- ✅ **Image path ต้องเป็น string**
- ✅ **Format: `storyboard/scene_{scene_id}/keyframe_{n}.jpg`**
- ✅ **Image path ต้องไม่เป็น empty string**

### 5. Duration
- ✅ **Duration ไม่ต้อง fix = 8.0**
- ✅ **Duration ต้องเป็น float >= 1.0**
- ✅ **Phase 5 จะ override duration เป็น 8.0 เอง**

### 6. Validation
- ✅ **Phase 4 ต้อง validate segments ก่อนส่ง**
- ✅ **ถ้า segment ขาด required fields → Phase 4 ต้อง raise ValueError**
- ✅ **Phase 5 จะไม่ fallback → ถ้าขาด fields จะ error ทันที**

---

## Error Handling

### Phase 4 Validation Errors
Phase 4 ต้อง validate และ raise `ValueError` ถ้า:
- Segment ไม่มี `start_keyframe` หรือ `end_keyframe`
- `start_keyframe` หรือ `end_keyframe` ไม่เป็น object (dict)
- Keyframe object ขาด required fields (`id`, `image_path`, `description`, `timing`)

### Phase 5 Validation Errors
Phase 5 จะ return error (ไม่ raise) ถ้า:
- Segment ไม่มี `start_keyframe` หรือ `end_keyframe` → `error: "segment must have 'start_keyframe' field"`
- `start_keyframe` หรือ `end_keyframe` ไม่เป็น object → `error: "segment 'start_keyframe' must be an object (dict)"`
- Keyframe object ขาด required fields → `error: "segment 'start_keyframe' missing required field 'id'"`

---

## ตัวอย่างการใช้งาน

### Phase 4 Output (ถูกต้อง)
```json
{
  "id": 1,
  "scene_id": 1,
  "duration": 1.5,
  "start_time": 0.0,
  "end_time": 1.5,
  "description": "start → end",
  "purpose": "hook",
  "emotion": "curious",
  "start_keyframe": {
    "id": "scene_1_kf_1",
    "image_path": "storyboard/scene_1/keyframe_1.jpg",
    "description": "เปิดฉากด้วยคำถามที่น่าสนใจ",
    "timing": 1.5
  },
  "end_keyframe": {
    "id": "scene_2_kf_1",
    "image_path": "storyboard/scene_2/keyframe_1.jpg",
    "description": "แสดงปัญหาและความยากลำบาก",
    "timing": 1.67
  }
}
```

### Phase 4 Output (ผิด - จะ error)
```json
{
  "id": 1,
  "scene_id": 1,
  "duration": 1.5,
  "start_keyframe_id": "scene_1_kf_1",  // ❌ ผิด: ต้องเป็น object
  "end_keyframe_id": "scene_2_kf_1"     // ❌ ผิด: ต้องเป็น object
}
```

---

## Breaking Changes

### v1.0 (Current)
- ✅ Phase 4 ต้องส่ง `start_keyframe` และ `end_keyframe` objects
- ✅ Phase 5 ไม่รองรับ schema เก่า (strict mode)
- ✅ Phase 5 ไม่ fallback → ถ้าขาด fields จะ error ทันที

### Migration Notes
- ❌ **ห้ามใช้ `start_keyframe_id` หรือ `end_keyframe_id`**
- ✅ **ต้องใช้ `start_keyframe` และ `end_keyframe` objects**

---

## Testing Checklist

Phase 4 ต้องผ่าน:
- [ ] ทุก segment มี `start_keyframe` object
- [ ] ทุก segment มี `end_keyframe` object
- [ ] `start_keyframe` มี fields ครบ: `id`, `image_path`, `description`, `timing`
- [ ] `end_keyframe` มี fields ครบ: `id`, `image_path`, `description`, `timing`
- [ ] Keyframe ID format ถูกต้อง: `scene_{scene_id}_kf_{n}`
- [ ] Image path format ถูกต้อง: `storyboard/scene_{scene_id}/keyframe_{n}.jpg`
- [ ] Phase 5 สามารถใช้ Phase 4 output โดยตรงได้ (ไม่ error)

---

**หมายเหตุ:** Contract นี้เป็น **invariant** - ห้ามเปลี่ยนโดยไม่แจ้งล่วงหน้า

