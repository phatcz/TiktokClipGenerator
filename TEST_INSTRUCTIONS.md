# คำแนะนำการทดสอบ Streamlit App

เอกสารนี้แนะนำวิธีการทดสอบว่า Streamlit app พร้อมใช้งาน

---

## ขั้นตอนการทดสอบ

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

ตรวจสอบการติดตั้ง:
```bash
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

---

### 2. ตรวจสอบ Syntax และ Imports

#### 2.1 ตรวจสอบ Syntax ของ app_streamlit.py

```bash
python -m py_compile app_streamlit.py
```

ถ้าไม่มี error = syntax ถูกต้อง

#### 2.2 ตรวจสอบว่า Phase modules import ได้

```bash
python -c "from story_engine import generate_story; print('OK')"
python -c "from phase2_generator import generate_phase2_output; print('OK')"
python -c "from phase3_storyboard import build_storyboard_from_phase2; print('OK')"
python -c "from phase4_video_plan import generate_video_plan; print('OK')"
python -c "from phase5_segment_renderer import render_segments_from_video_plan; print('OK')"
python -c "from phase5_assembler import assemble_video; print('OK')"
```

ถ้าทุกคำสั่งแสดง "OK" = imports ทำงานถูกต้อง

---

### 3. รัน Streamlit App

```bash
streamlit run app_streamlit.py
```

**ตรวจสอบว่า:**
- App เปิดเบราว์เซอร์ที่ `http://localhost:8501`
- ไม่มี error messages ใน terminal
- Sidebar แสดง input fields
- Main area แสดง UI สำหรับแต่ละ phase

---

### 4. ทดสอบ End-to-End Flow

ในแอป:

1. **Phase 1:**
   - ใส่ input ใน sidebar (goal, product, audience, platform)
   - กด "Generate Story (Phase 1)"
   - ตรวจสอบว่า Story และ Scenes แสดงผล

2. **Phase 2:**
   - กด "Generate Characters & Locations (Phase 2)"
   - ตรวจสอบว่า Characters และ Locations แสดงผล
   - เลือก Character และ Location

3. **Phase 3:**
   - กด "Build Storyboard (Phase 3)"
   - ตรวจสอบว่า Storyboard และ Keyframes แสดงผล

4. **Phase 4:**
   - กด "Generate Video Plan (Phase 4)"
   - ตรวจสอบว่า Video Plan และ Segments แสดงผล

5. **Phase 5:**
   - กด "Render Segments (Phase 5)"
   - ตรวจสอบว่า Rendered Segments แสดงผล

6. **Phase 5.5:**
   - กด "Assemble Final Video (Phase 5.5)"
   - ตรวจสอบว่า Final Video Path แสดงผล

---

### 5. ตรวจสอบ Error Handling

ทดสอบ edge cases:

1. **Clear button:**
   - Generate หลาย phases
   - กด "Clear"
   - ตรวจสอบว่า session state ถูกล้าง

2. **Phase dependencies:**
   - พยายาม generate Phase 2 โดยไม่ generate Phase 1
   - ควรแสดง info message "Please complete Phase 1 first"

3. **Character/Location selection:**
   - เลือก character/location ต่างกัน
   - Generate Phase 3 ใหม่
   - ตรวจสอบว่า storyboard อัพเดทตาม selection

---

## Expected Results

### เมื่อทดสอบสำเร็จ

- ✅ App รันได้โดยไม่มี errors
- ✅ ทุก phase generate ได้สำเร็จ
- ✅ Data ถูกส่งต่อระหว่าง phases ถูกต้อง
- ✅ UI แสดงผลถูกต้อง (JSON, metrics, expandable sections)
- ✅ Session state ทำงานถูกต้อง

### ปัญหาที่อาจพบ (Mock Limitations)

- ⚠️ Placeholder images/videos อาจไม่แสดง (ถ้า URLs ไม่ทำงาน)
- ⚠️ Video previews เป็น placeholder (ไม่ใช่ video จริง)
- ⚠️ Output paths เป็น mock paths (ไม่มีไฟล์จริง)

**หมายเหตุ:** นี่เป็นพฤติกรรมปกติ เพราะ app ใช้ mock output

---

## Quick Test Script

สร้างไฟล์ `test_imports.py`:

```python
"""Quick test script to verify all imports work"""

try:
    from story_engine import generate_story
    print("✓ story_engine")
except Exception as e:
    print(f"✗ story_engine: {e}")

try:
    from phase2_generator import generate_phase2_output
    print("✓ phase2_generator")
except Exception as e:
    print(f"✗ phase2_generator: {e}")

try:
    from phase3_storyboard import build_storyboard_from_phase2
    print("✓ phase3_storyboard")
except Exception as e:
    print(f"✗ phase3_storyboard: {e}")

try:
    from phase4_video_plan import generate_video_plan
    print("✓ phase4_video_plan")
except Exception as e:
    print(f"✗ phase4_video_plan: {e}")

try:
    from phase5_segment_renderer import render_segments_from_video_plan
    print("✓ phase5_segment_renderer")
except Exception as e:
    print(f"✗ phase5_segment_renderer: {e}")

try:
    from phase5_assembler import assemble_video
    print("✓ phase5_assembler")
except Exception as e:
    print(f"✗ phase5_assembler: {e}")

print("\nAll imports checked!")
```

รัน:
```bash
python test_imports.py
```

---

## Troubleshooting Tests

### ถ้า import ไม่ได้

1. ตรวจสอบว่าไฟล์ phase modules อยู่ในโฟลเดอร์เดียวกันกับ `app_streamlit.py`
2. ตรวจสอบว่าไม่มี syntax errors ในไฟล์เหล่านั้น
3. ตรวจสอบว่า Python path ถูกต้อง

### ถ้า Streamlit ไม่รัน

1. ตรวจสอบว่า streamlit ติดตั้งแล้ว: `pip list | findstr streamlit`
2. ตรวจสอบว่าใช้ Python version ที่ถูกต้อง (3.8+)
3. ตรวจสอบ error messages ใน terminal

---

**Last Updated:** 2024-12-14

