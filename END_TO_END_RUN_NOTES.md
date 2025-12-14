# End-to-End Mock Run - เอกสารสรุป

## ไฟล์ที่ใช้

- `end_to_end_run.py` - Script หลักสำหรับรัน End-to-End Mock Run

## Flow การทำงาน

```
Phase 1 (Story Engine)
  ↓
Phase 2 (Generator)
  ↓
Phase 3 (Storyboard)
  ↓
Phase 4 (Video Plan)
  ↓
Phase 5 (Segment Renderer)
  ↓
Phase 5.5 (Video Assembler)
```

## วิธีใช้งาน

```bash
python end_to_end_run.py
```

หรือเรียกใช้ฟังก์ชัน `run_end_to_end()` โดยตรง:

```python
from end_to_end_run import run_end_to_end

result = run_end_to_end(
    goal="ขายคอร์สออนไลน์",
    product="AI Creator Tool",
    audience="มือใหม่ ไม่เก่งเทค",
    platform="Facebook Reel",
    selected_character_id=1,
    selected_location_id=1
)
```

## ตัวอย่าง Output

```
============================================================
End-to-End Mock Run
============================================================

[Phase 1] Generating Story...
  Goal: ขายคอร์สออนไลน์
  Product: AI Creator Tool
  Audience: มือใหม่ ไม่เก่งเทค
  Platform: Facebook Reel

✓ Phase 1 Complete: 4 scenes

[Phase 2] Generating Characters & Locations...
  Characters: 4
  Locations: 4

✓ Phase 2 Complete: 4 characters, 4 locations

[Phase 3] Building Storyboard...
  Selected Character ID: 1
  Selected Location ID: 1

✓ Phase 3 Complete: 4 scenes, 7 keyframes

[Phase 4] Generating Video Plan...

✓ Phase 4 Complete: 7 segments, 10.83s total duration

[Phase 5] Rendering Segments (Mock)...

✓ Phase 5 Complete: 7/7 segments rendered

[Phase 5.5] Assembling Final Video (Mock)...

✓ Phase 5.5 Complete: Final video assembled

============================================================
Summary
============================================================
Total Segments: 7
Segment IDs: [1, 2, 3, 4, 5, 6, 7]
Final Video Path: output/final_video_20251214_182145_be3bb977.mp4
Total Duration: 10.83s
Successful Segments: 7/7
Assemble Success: True
```

## จุดที่ต้องระวัง

### 1. Schema Contract
- **Phase 4 → Phase 5**: Phase 4 ต้องส่ง `start_keyframe` และ `end_keyframe` objects ที่มีครบทุก field (id, image_path, description, timing)
- **Validation**: Phase 4 มี validation เพื่อให้แน่ใจว่า keyframes มีข้อมูลครบถ้วน

### 2. Segment Duration
- **Phase 4**: Segment duration ไม่ fix 8 วินาที (ตามที่ระบุ)
- **Phase 5**: แต่ละ segment ที่ render จะเป็น 8 วินาที (fix)
- **หมายเหตุ**: Phase 4 duration เป็น "intention" เท่านั้น Phase 5 จะ render เป็น 8 วินาทีเสมอ

### 3. Keyframe Continuity
- **Cross-scene segments**: Segment อาจข้าม scene boundaries ได้ (end_keyframe อาจอยู่ใน scene ถัดไป)
- **Last segment**: Segment สุดท้ายจะใช้ keyframe เดียวกันเป็นทั้ง start และ end

### 4. Mock vs Production
- **Phase 5**: ใช้ mock Google Video Gen API (ไม่ render video จริง)
- **Phase 5.5**: ใช้ mock video stitch (ไม่ stitch video จริง)
- **Output paths**: เป็น mock paths เท่านั้น ไม่มีไฟล์จริง

### 5. Error Handling
- **Missing keyframes**: Phase 4 จะ raise ValueError ถ้า keyframe ไม่มีข้อมูลครบ
- **Failed segments**: Phase 5 จะรายงาน failed segments แต่ยังคง render ต่อ
- **Assemble failure**: Phase 5.5 จะรายงาน success/failure status

### 6. Encoding (Windows)
- Script มีการ fix encoding สำหรับ Windows console (UTF-8)
- ถ้าใช้ PowerShell อาจต้องตั้งค่า encoding ก่อน

### 7. Dependencies
- ต้องมีทุก phase files ในโฟลเดอร์เดียวกัน:
  - `story_engine.py`
  - `phase2_generator.py`
  - `phase3_storyboard.py`
  - `phase4_video_plan.py`
  - `phase5_segment_renderer.py`
  - `phase5_assembler.py`

## Return Value Structure

```python
{
    "phase1_story": {...},              # Story object
    "phase2_output": {...},             # Phase 2 output
    "phase3_storyboard": {...},         # Storyboard object
    "phase4_video_plan": {...},         # Video plan object
    "phase5_render_result": {...},      # Render result
    "phase5_5_assemble_result": {...},  # Assemble result
    "summary": {
        "total_segments": 7,
        "segment_ids": [1, 2, 3, 4, 5, 6, 7],
        "final_video_path": "output/final_video_...mp4",
        "total_duration": 10.83,
        "successful_segments": 7,
        "failed_segments": [],
        "assemble_success": True
    }
}
```

## Testing

Script นี้ใช้สำหรับ:
- ✅ ทดสอบ End-to-End flow
- ✅ ตรวจสอบ schema compatibility
- ✅ ตรวจสอบ continuity ระหว่าง phases
- ❌ ไม่ใช้สำหรับ production (ใช้ mock เท่านั้น)

