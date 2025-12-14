"""
Phase 3: Storyboard Builder

Input:
- story JSON จาก Phase 1
- selected character/location จาก Phase 2

Output:
- storyboard JSON
- แต่ละ scene มี 1–3 keyframes (image reference)
"""

import json
from typing import Dict, List, Any, Optional


def map_scene_to_keyframes(scene: Dict[str, Any], selected_character: Optional[Dict[str, Any]] = None, selected_location: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Map scene เป็น keyframes (1-3 keyframes ต่อ scene)
    
    Args:
        scene: Scene object จาก Phase 1
        selected_character: Selected character จาก Phase 2 (optional)
        selected_location: Selected location จาก Phase 2 (optional)
    
    Returns:
        List ของ keyframe objects
    """
    scene_id = scene.get("id")
    purpose = scene.get("purpose", "")
    emotion = scene.get("emotion", "")
    duration = scene.get("duration", 0)
    description = scene.get("description", "")
    
    keyframes = []
    
    # กำหนดจำนวน keyframes ตาม duration
    # Scene สั้น (<= 3 วินาที): 1 keyframe
    # Scene ปานกลาง (4-5 วินาที): 2 keyframes
    # Scene ยาว (> 5 วินาที): 3 keyframes
    if duration <= 3:
        num_keyframes = 1
    elif duration <= 5:
        num_keyframes = 2
    else:
        num_keyframes = 3
    
    # สร้าง keyframes ตาม purpose และ emotion
    for idx in range(num_keyframes):
        # Fix: ใช้ format scene_{scene_id}_kf_{n} เพื่อให้ keyframe_id unique ข้าม scene
        keyframe_local_id = idx + 1
        keyframe_id = f"scene_{scene_id}_kf_{keyframe_local_id}"
        
        # คำนวณ timing ของ keyframe (กระจายตาม duration)
        if num_keyframes == 1:
            timing = duration / 2  # กลาง scene
        else:
            timing = (duration / (num_keyframes + 1)) * (idx + 1)
        
        # สร้าง description สำหรับ keyframe ตาม purpose
        keyframe_descriptions = {
            "hook": [
                f"เปิดฉากด้วยคำถามที่น่าสนใจ - {description}",
                f"แสดงความสงสัยและความอยากรู้ - {description}",
                f"ดึงดูดความสนใจด้วยคำถามชวนคิด - {description}"
            ],
            "conflict": [
                f"แสดงปัญหาและความยากลำบาก - {description}",
                f"โชว์ความยุ่งยากที่ต้องเผชิญ - {description}",
                f"สะท้อนความท้าทายและอุปสรรค - {description}"
            ],
            "reveal": [
                f"แนะนำวิธีแก้ปัญหา - {description}",
                f"เปิดเผยทางออกและแนวทาง - {description}",
                f"แสดงผลลัพธ์และความสำเร็จ - {description}"
            ],
            "close": [
                f"เชิญชวนให้ดำเนินการ - {description}",
                f"สรุปและเรียกร้องให้ลงมือทำ - {description}",
                f"ปิดท้ายด้วยการกระตุ้นให้ลอง - {description}"
            ]
        }
        
        purpose_descriptions = keyframe_descriptions.get(purpose, [description] * 3)
        keyframe_desc = purpose_descriptions[min(idx, len(purpose_descriptions) - 1)]
        
        # สร้าง image path/reference
        # Format: storyboard/scene_{scene_id}/keyframe_{keyframe_local_id}.jpg
        image_path = f"storyboard/scene_{scene_id}/keyframe_{keyframe_local_id}.jpg"
        
        # สร้าง prompt สำหรับ image generation (ถ้าต้องการ)
        character_info = ""
        if selected_character:
            character_info = f", {selected_character.get('name', '')} character, {selected_character.get('style', '')} style"
        
        location_info = ""
        if selected_location:
            location_info = f", {selected_location.get('name', '')} location, {selected_location.get('style', '')} style"
        
        image_prompt = f"{keyframe_desc}, emotion: {emotion}{character_info}{location_info}"
        
        keyframe = {
            "id": keyframe_id,
            "timing": round(timing, 2),
            "description": keyframe_desc,
            "image_path": image_path,
            "image_prompt": image_prompt
        }
        
        keyframes.append(keyframe)
    
    return keyframes


def build_storyboard(story: Dict[str, Any], selected_character: Optional[Dict[str, Any]] = None, selected_location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    สร้าง Storyboard JSON จาก story และ selected character/location
    
    Args:
        story: Story object จาก Phase 1
        selected_character: Selected character จาก Phase 2 (optional)
        selected_location: Selected location จาก Phase 2 (optional)
    
    Returns:
        Dictionary ที่มีโครงสร้างตาม Storyboard schema
    """
    # Validate input
    if not isinstance(story, dict):
        raise ValueError("story must be a dictionary")
    
    required_fields = ["goal", "product", "audience", "platform", "scenes"]
    for field in required_fields:
        if field not in story:
            raise ValueError(f"story must contain '{field}' field")
    
    scenes = story.get("scenes", [])
    if not scenes:
        raise ValueError("story must contain at least one scene")
    
    # สร้าง storyboard scenes พร้อม keyframes
    storyboard_scenes = []
    
    for scene in scenes:
        keyframes = map_scene_to_keyframes(scene, selected_character, selected_location)
        
        storyboard_scene = {
            "scene_id": scene.get("id"),
            "purpose": scene.get("purpose"),
            "emotion": scene.get("emotion"),
            "duration": scene.get("duration"),
            "description": scene.get("description"),
            "keyframes": keyframes
        }
        
        storyboard_scenes.append(storyboard_scene)
    
    # สร้าง Storyboard object
    storyboard = {
        "story": {
            "goal": story.get("goal"),
            "product": story.get("product"),
            "audience": story.get("audience"),
            "platform": story.get("platform")
        },
        "selected_character": selected_character,
        "selected_location": selected_location,
        "scenes": storyboard_scenes
    }
    
    return storyboard


def build_storyboard_json(story_json: str, selected_character: Optional[Dict[str, Any]] = None, selected_location: Optional[Dict[str, Any]] = None) -> str:
    """
    สร้าง Storyboard JSON string จาก story JSON string
    
    Args:
        story_json: JSON string ของ Story จาก Phase 1
        selected_character: Selected character จาก Phase 2 (optional)
        selected_location: Selected location จาก Phase 2 (optional)
    
    Returns:
        JSON string ของ Storyboard
    """
    story = json.loads(story_json)
    storyboard = build_storyboard(story, selected_character, selected_location)
    return json.dumps(storyboard, ensure_ascii=False, indent=2)


def build_storyboard_from_phase2(phase2_output: Dict[str, Any], selected_character_id: Optional[int] = None, selected_location_id: Optional[int] = None) -> Dict[str, Any]:
    """
    สร้าง Storyboard จาก Phase 2 output พร้อม selected character/location
    
    Args:
        phase2_output: Phase 2 output ที่มี story, characters, locations, selection
        selected_character_id: ID ของ character ที่เลือก (optional, ถ้าไม่ระบุจะอ่านจาก selection)
        selected_location_id: ID ของ location ที่เลือก (optional, ถ้าไม่ระบุจะอ่านจาก selection)
        
    Returns:
        Dictionary ที่มีโครงสร้างตาม Storyboard schema
    """
    # Validate input
    if not isinstance(phase2_output, dict):
        raise ValueError("phase2_output must be a dictionary")
    
    if "story" not in phase2_output:
        raise ValueError("phase2_output must contain 'story' field")
    
    story = phase2_output.get("story")
    characters = phase2_output.get("characters", [])
    locations = phase2_output.get("locations", [])
    
    # อ่าน selection จาก phase2_output ถ้าไม่ระบุ parameter
    selection = phase2_output.get("selection", {})
    if selected_character_id is None:
        selected_character_id = selection.get("selected_character_id")
    if selected_location_id is None:
        selected_location_id = selection.get("selected_location_id")
    
    # หา selected character
    selected_character = None
    if selected_character_id is not None:
        for char in characters:
            if char.get("id") == selected_character_id:
                selected_character = char
                break
    
    # หา selected location
    selected_location = None
    if selected_location_id is not None:
        for loc in locations:
            if loc.get("id") == selected_location_id:
                selected_location = loc
                break
    
    # สร้าง storyboard
    return build_storyboard(story, selected_character, selected_location)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Import Phase 1 และ Phase 2
    from story_engine import generate_story
    from phase2_generator import generate_phase2_output
    
    # สร้าง story จาก Phase 1
    story = generate_story(
        goal="ขายคอร์สออนไลน์",
        product="AI Creator Tool",
        audience="มือใหม่ ไม่เก่งเทค",
        platform="Facebook Reel"
    )
    
    # สร้าง Phase 2 output
    phase2_output = generate_phase2_output(story, num_characters=4, num_locations=4)
    
    # เลือก character และ location (ตัวอย่าง: เลือกตัวแรก)
    selected_character_id = 1
    selected_location_id = 1
    
    # สร้าง storyboard จาก Phase 2 output
    storyboard = build_storyboard_from_phase2(phase2_output, selected_character_id, selected_location_id)
    
    print(json.dumps(storyboard, ensure_ascii=False, indent=2))

