# คู่มือการติดตั้งและใช้งาน Streamlit App

เอกสารนี้แนะนำวิธีการติดตั้ง dependencies และรัน Streamlit Demo App สำหรับ Creator Tool

---

## Prerequisites

- **Python 3.8 หรือสูงกว่า**
- **pip** (Python package installer)

ตรวจสอบ Python version:
```bash
python --version
# หรือ
python3 --version
```

---

## การติดตั้ง Dependencies

### 1. ติดตั้ง Streamlit

```bash
pip install -r requirements.txt
```

หรือติดตั้งโดยตรง:
```bash
pip install streamlit>=1.28.0
```

### 2. ตรวจสอบการติดตั้ง

```bash
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

ควรแสดง Streamlit version ถ้าติดตั้งสำเร็จ

---

## วิธีรันแอป

### 1. รัน Streamlit App

จากโฟลเดอร์หลักของโปรเจกต์ (ที่อยู่ของ `app_streamlit.py`):

```bash
streamlit run app_streamlit.py
```

หรือ

```bash
python -m streamlit run app_streamlit.py
```

### 2. เข้าถึงแอป

Streamlit จะเปิดเบราว์เซอร์อัตโนมัติที่:
- **URL:** `http://localhost:8501`

ถ้าไม่เปิดอัตโนมัติ ให้เปิดเบราว์เซอร์และไปที่ URL ด้านบน

---

## การใช้งานแอป

### Flow การทำงาน

1. **Phase 1: Generate Story**
   - ใส่ input parameters ใน sidebar (goal, product, audience, platform)
   - กด "Generate Story (Phase 1)"

2. **Phase 2: Generate Characters & Locations**
   - กด "Generate Characters & Locations (Phase 2)"
   - เลือก Character และ Location จาก dropdown

3. **Phase 3: Build Storyboard**
   - กด "Build Storyboard (Phase 3)"
   - ดู keyframes ที่ถูกสร้าง

4. **Phase 4: Generate Video Plan**
   - กด "Generate Video Plan (Phase 4)"
   - ดู segments ที่ถูกสร้าง

5. **Phase 5: Render Segments**
   - กด "Render Segments (Phase 5)" (Mock)
   - ดู rendered segment paths

6. **Phase 5.5: Assemble Final Video**
   - กด "Assemble Final Video (Phase 5.5)" (Mock)
   - ดู final video path

---

## Troubleshooting

### ปัญหา: ModuleNotFoundError: No module named 'streamlit'

**แก้ไข:**
```bash
pip install streamlit
```

หรือ
```bash
pip install -r requirements.txt
```

---

### ปัญหา: Port 8501 ถูกใช้งานแล้ว

**แก้ไข:**

1. หยุด Streamlit ที่รันอยู่ (Ctrl+C)

2. หรือใช้ port อื่น:
```bash
streamlit run app_streamlit.py --server.port 8502
```

3. จากนั้นเข้าถึงที่ `http://localhost:8502`

---

### ปัญหา: Encoding errors บน Windows (ตัวอักษรไทยแสดงผิด)

**แก้ไข:**

App มีการ fix encoding อัตโนมัติแล้ว แต่ถ้ายังมีปัญหา:

1. ตั้งค่า PowerShell encoding:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

2. หรือใช้ Command Prompt แทน PowerShell

---

### ปัญหา: Import errors จาก phase modules

**ตรวจสอบ:**

1. ตรวจสอบว่าไฟล์ phase modules อยู่ในโฟลเดอร์เดียวกัน:
   - `story_engine.py`
   - `phase2_generator.py`
   - `phase3_storyboard.py`
   - `phase4_video_plan.py`
   - `phase5_segment_renderer.py`
   - `phase5_assembler.py`

2. ตรวจสอบว่า imports ทำงาน:
```bash
python -c "from story_engine import generate_story; from phase2_generator import generate_phase2_output; print('All imports OK')"
```

---

### ปัญหา: แอปไม่แสดงผลหรือ error

**ตรวจสอบ:**

1. ดู error messages ใน terminal ที่รัน Streamlit

2. ตรวจสอบว่า Phase modules ไม่มี syntax errors:
```bash
python -m py_compile app_streamlit.py
python -m py_compile story_engine.py
python -m py_compile phase2_generator.py
# ... ตรวจสอบทุกไฟล์
```

3. ตรวจสอบ logs ใน terminal

---

### ปัญหา: Placeholder images/videos ไม่แสดง

**หมายเหตุ:**

- App ใช้ placeholder URLs สำหรับ images/videos (mock)
- ถ้า placeholder URLs ไม่ทำงาน อาจต้อง:
  - ตรวจสอบ internet connection
  - เปลี่ยน placeholder URLs ใน code (ถ้าจำเป็น)

---

## การหยุดแอป

กด `Ctrl+C` ใน terminal ที่รัน Streamlit

---

## หมายเหตุสำคัญ

1. **Mock Output:** App ใช้ mock output ทั้งหมด (ไม่ render video จริง)
   - Image URLs: mock URLs
   - Video paths: mock paths
   - Video preview: placeholder video

2. **Schema:** App ใช้ schema เดิมจาก Phase 1-5 ห้ามเปลี่ยน

3. **Production Logic:** Phase modules ถูก lock แล้ว ห้ามแก้ไข

4. **Session State:** App ใช้ Streamlit session state เพื่อเก็บผลลัพธ์ระหว่าง phases

---

## Support

ถ้ามีปัญหาหรือคำถาม:
1. ตรวจสอบ error messages ใน terminal
2. ตรวจสอบ logs
3. ดูเอกสาร `PROGRESS.md` และ `WORKFLOW.md`

---

**Last Updated:** 2024-12-14

