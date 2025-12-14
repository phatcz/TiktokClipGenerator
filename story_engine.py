import json
from typing import Dict, List, Any


def generate_story(goal: str, product: str, audience: str, platform: str) -> Dict[str, Any]:
    """
    สร้าง Story JSON จาก inputs ที่ได้รับ
    
    Args:
        goal: เป้าหมาย (เช่น "ขายคอร์สออนไลน์")
        product: ชื่อสินค้า/บริการ
        audience: กลุ่มเป้าหมาย
        platform: แพลตฟอร์มที่ใช้ (เช่น "Facebook Reel")
    
    Returns:
        Dictionary ที่มีโครงสร้างตาม Story schema
    """
    
    # Rule-based logic สำหรับสร้าง scenes
    scenes = []
    
    # Scene 1: Hook - เริ่มต้นด้วยคำถามหรือข้อความที่ดึงดูด
    hook_descriptions = {
        "ขายคอร์สออนไลน์": f"ตั้งคำถามว่าทำไม{audience}ถึงยังไม่ได้เริ่มใช้{product}",
        "เพิ่มผู้ติดตาม": f"คุณรู้หรือไม่ว่า{audience}ต้องการอะไรจาก{platform}",
        "สร้างแบรนด์": f"ทำไม{product}ถึงเป็นที่นิยมในกลุ่ม{audience}",
    }
    hook_desc = hook_descriptions.get(goal, f"ตั้งคำถามที่น่าสนใจเกี่ยวกับ{product}สำหรับ{audience}")
    
    scenes.append({
        "id": 1,
        "purpose": "hook",
        "emotion": "curious",
        "duration": 3,
        "description": hook_desc
    })
    
    # Scene 2: Conflict - แสดงปัญหา/ความยากลำบาก
    conflict_descriptions = {
        "ขายคอร์สออนไลน์": f"โชว์ความยุ่งยากที่{audience}ต้องเจอเมื่อต้องเรียนรู้เอง",
        "เพิ่มผู้ติดตาม": f"แสดงปัญหาในการสร้างคอนเทนต์สำหรับ{platform}",
        "สร้างแบรนด์": f"ความยากในการทำให้{audience}รู้จักและเชื่อใจ",
    }
    conflict_desc = conflict_descriptions.get(goal, f"แสดงปัญหาและความท้าทายที่{audience}ต้องเผชิญ")
    
    scenes.append({
        "id": 2,
        "purpose": "conflict",
        "emotion": "frustrated",
        "duration": 5,
        "description": conflict_desc
    })
    
    # Scene 3: Reveal - แนะนำวิธีแก้ปัญหา
    reveal_descriptions = {
        "ขายคอร์สออนไลน์": f"แนะนำ{product}ที่ทำให้{audience}เรียนรู้ได้ง่ายและรวดเร็ว",
        "เพิ่มผู้ติดตาม": f"เปิดเผยวิธีใช้{product}เพื่อสร้างคอนเทนต์ที่โดนใจบน{platform}",
        "สร้างแบรนด์": f"แนะนำ{product}ที่เป็นทางออกสำหรับ{audience}",
    }
    reveal_desc = reveal_descriptions.get(goal, f"แนะนำ{product}ที่เป็นทางออกสำหรับปัญหา")
    
    scenes.append({
        "id": 3,
        "purpose": "reveal",
        "emotion": "relief",
        "duration": 5,
        "description": reveal_desc
    })
    
    # Scene 4: Close - เชิญชวนให้ดำเนินการ
    close_descriptions = {
        "ขายคอร์สออนไลน์": f"เชิญชวนให้{audience}สมัครเรียน{product}",
        "เพิ่มผู้ติดตาม": f"เชิญชวนให้ติดตามและลองใช้{product}บน{platform}",
        "สร้างแบรนด์": f"เชิญชวนให้{audience}ลองใช้{product}และติดตามผลลัพธ์",
    }
    close_desc = close_descriptions.get(goal, f"เชิญชวนให้ลองใช้{product}")
    
    scenes.append({
        "id": 4,
        "purpose": "close",
        "emotion": "confident",
        "duration": 4,
        "description": close_desc
    })
    
    # สร้าง Story object
    story = {
        "goal": goal,
        "product": product,
        "audience": audience,
        "platform": platform,
        "scenes": scenes
    }
    
    return story


def generate_story_json(goal: str, product: str, audience: str, platform: str) -> str:
    """
    สร้าง Story JSON string จาก inputs ที่ได้รับ
    
    Args:
        goal: เป้าหมาย
        product: ชื่อสินค้า/บริการ
        audience: กลุ่มเป้าหมาย
        platform: แพลตฟอร์มที่ใช้
    
    Returns:
        JSON string ของ Story
    """
    story = generate_story(goal, product, audience, platform)
    return json.dumps(story, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    story = generate_story(
        goal="ขายคอร์สออนไลน์",
        product="AI Creator Tool",
        audience="มือใหม่ ไม่เก่งเทค",
        platform="Facebook Reel"
    )
    
    print(json.dumps(story, ensure_ascii=False, indent=2))

