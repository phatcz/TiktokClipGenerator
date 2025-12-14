"""
Phase 4: Video Plan Generator

Input:
- storyboard จาก Phase 3

Output:
- video_plan JSON
- total duration
- จำนวน segment (ยังไม่ fix 8 วิ)

Features:
- Map storyboard → video segments
- แต่ละ segment อ้างอิง keyframe จาก storyboard
- คำนวณ total duration และ segment count
"""

import json
from typing import Dict, List, Any, Optional


def map_storyboard_to_segments(storyboard: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Map storyboard scenes และ keyframes เป็น video segments
    
    แต่ละ segment = การเคลื่อนจาก keyframe A → B
    Segment จะมีข้อมูลที่จำเป็นสำหรับการ render video
    
    Contract:
    - แต่ละ segment ต้องมี start_keyframe และ end_keyframe objects ครบ
    - start_keyframe และ end_keyframe ต้องมี: id, image_path, description, timing
    - Phase 5 สามารถใช้ข้อมูลนี้ตรง ๆ โดยไม่ fallback
    
    Duration Contract:
    - Phase 4 duration ไม่ fix = 8.0 วินาที
    - Duration คำนวณจาก keyframe timing (minimum = 1.0 วินาที)
    - Phase 5 จะ override duration เป็น 8.0 เสมอ (original duration เก็บใน metadata.original_duration)
    
    Args:
        storyboard: Storyboard object จาก Phase 3
    
    Returns:
        List ของ video segment objects ที่มี start_keyframe และ end_keyframe objects
    """
    if not isinstance(storyboard, dict):
        raise ValueError("storyboard must be a dictionary")
    
    if "scenes" not in storyboard:
        raise ValueError("storyboard must contain 'scenes' field")
    
    scenes = storyboard.get("scenes", [])
    if not scenes:
        raise ValueError("storyboard must contain at least one scene")
    
    segments = []
    current_time = 0.0
    segment_id = 1
    
    # รวบรวม keyframes ทั้งหมดจากทุก scene พร้อม scene context
    all_keyframes = []
    for scene in scenes:
        scene_id = scene.get("scene_id")
        scene_duration = scene.get("duration", 0)
        scene_purpose = scene.get("purpose", "")
        scene_emotion = scene.get("emotion", "")
        keyframes = scene.get("keyframes", [])
        
        for keyframe in keyframes:
            all_keyframes.append({
                "keyframe": keyframe,
                "scene_id": scene_id,
                "scene_duration": scene_duration,
                "scene_purpose": scene_purpose,
                "scene_emotion": scene_emotion
            })
    
    # สร้าง segments โดยแต่ละ segment = การเคลื่อนจาก keyframe A → B
    for idx, keyframe_data in enumerate(all_keyframes):
        keyframe = keyframe_data["keyframe"]
        scene_id = keyframe_data["scene_id"]
        scene_purpose = keyframe_data["scene_purpose"]
        scene_emotion = keyframe_data["scene_emotion"]
        
        # สร้าง start_keyframe object (ต้องมีครบทุก field)
        start_keyframe_id = keyframe.get("id")
        start_keyframe_path = keyframe.get("image_path")
        start_keyframe_desc = keyframe.get("description", "")
        start_timing = keyframe.get("timing", 0)
        
        # Validate start_keyframe fields
        if not start_keyframe_id:
            raise ValueError(f"Keyframe at index {idx} missing 'id' field")
        if not start_keyframe_path:
            raise ValueError(f"Keyframe at index {idx} missing 'image_path' field")
        if not start_keyframe_desc:
            raise ValueError(f"Keyframe at index {idx} missing 'description' field")
        
        # หา end_keyframe (keyframe ถัดไป หรือ keyframe เดียวกันถ้าเป็นตัวสุดท้าย)
        if idx < len(all_keyframes) - 1:
            # มี keyframe ถัดไป
            next_keyframe_data = all_keyframes[idx + 1]
            end_keyframe = next_keyframe_data["keyframe"]
            end_keyframe_id = end_keyframe.get("id")
            end_keyframe_path = end_keyframe.get("image_path")
            end_keyframe_desc = end_keyframe.get("description", "")
            end_timing = end_keyframe.get("timing", 0)
            
            # Validate end_keyframe fields
            if not end_keyframe_id:
                raise ValueError(f"End keyframe at index {idx + 1} missing 'id' field")
            if not end_keyframe_path:
                raise ValueError(f"End keyframe at index {idx + 1} missing 'image_path' field")
            if not end_keyframe_desc:
                raise ValueError(f"End keyframe at index {idx + 1} missing 'description' field")
            
            # คำนวณ duration จาก timing ของ keyframes
            # ถ้า end_keyframe อยู่ใน scene เดียวกัน ใช้ timing จาก keyframe
            # ถ้า end_keyframe อยู่ใน scene ถัดไป ใช้ scene_duration - start_timing
            if next_keyframe_data["scene_id"] != scene_id:
                # end_keyframe อยู่ใน scene ถัดไป
                segment_duration = keyframe_data["scene_duration"] - start_timing
            else:
                # end_keyframe อยู่ใน scene เดียวกัน
                segment_duration = end_timing - start_timing
        else:
            # เป็น keyframe สุดท้าย ใช้ keyframe เดียวกันเป็นทั้ง start และ end
            end_keyframe_id = start_keyframe_id
            end_keyframe_path = start_keyframe_path
            end_keyframe_desc = start_keyframe_desc
            end_timing = start_timing + keyframe_data["scene_duration"] - start_timing
            
            # คำนวณ duration จาก scene_duration
            segment_duration = keyframe_data["scene_duration"] - start_timing
        
        # กำหนด minimum duration = 1 วินาที
        # NOTE: Duration ไม่ fix = 8.0 (Phase 5 จะ override เป็น 8.0)
        if segment_duration < 1.0:
            segment_duration = 1.0
        
        # สร้าง start_keyframe และ end_keyframe objects (contract-ready)
        start_keyframe_obj = {
            "id": start_keyframe_id,
            "image_path": start_keyframe_path,
            "description": start_keyframe_desc,
            "timing": round(start_timing, 2)
        }
        
        end_keyframe_obj = {
            "id": end_keyframe_id,
            "image_path": end_keyframe_path,
            "description": end_keyframe_desc,
            "timing": round(end_timing, 2)
        }
        
        # สร้าง segment (contract-ready: มี start_keyframe และ end_keyframe objects ครบ)
        segment = {
            "id": segment_id,
            "scene_id": scene_id,
            "duration": round(segment_duration, 2),
            "start_time": round(current_time, 2),
            "end_time": round(current_time + segment_duration, 2),
            "description": f"{start_keyframe_desc} → {end_keyframe_desc}",
            "purpose": scene_purpose,
            "emotion": scene_emotion,
            "start_keyframe": start_keyframe_obj,
            "end_keyframe": end_keyframe_obj
        }
        
        segments.append(segment)
        current_time += segment_duration
        segment_id += 1
    
    return segments


def generate_video_plan(storyboard: Dict[str, Any]) -> Dict[str, Any]:
    """
    สร้าง Video Plan JSON จาก storyboard
    
    Duration Contract:
    - Phase 4 segments มี duration ไม่ fix = 8.0 (อาจเป็นค่าใดก็ได้ เช่น 1.5, 2.3, 5.7 วินาที)
    - Duration คำนวณจาก keyframe timing
    - Phase 5 จะ override duration เป็น 8.0 วินาทีเสมอ (original duration เก็บใน metadata.original_duration)
    
    Args:
        storyboard: Storyboard object จาก Phase 3
    
    Returns:
        Dictionary ที่มีโครงสร้างตาม Video Plan schema
    """
    # Validate input
    if not isinstance(storyboard, dict):
        raise ValueError("storyboard must be a dictionary")
    
    # Map storyboard เป็น segments
    segments = map_storyboard_to_segments(storyboard)
    
    # คำนวณ total duration
    total_duration = 0.0
    if segments:
        last_segment = segments[-1]
        total_duration = last_segment.get("end_time", 0.0)
    
    # นับจำนวน segments
    segment_count = len(segments)
    
    # สร้าง Video Plan object
    video_plan = {
        "storyboard_metadata": {
            "story": storyboard.get("story", {}),
            "selected_character": storyboard.get("selected_character"),
            "selected_location": storyboard.get("selected_location")
        },
        "segments": segments,
        "total_duration": round(total_duration, 2),
        "segment_count": segment_count
    }
    
    return video_plan


def generate_video_plan_json(storyboard_json: str) -> str:
    """
    สร้าง Video Plan JSON string จาก storyboard JSON string
    
    Args:
        storyboard_json: JSON string ของ Storyboard จาก Phase 3
    
    Returns:
        JSON string ของ Video Plan
    """
    storyboard = json.loads(storyboard_json)
    video_plan = generate_video_plan(storyboard)
    return json.dumps(video_plan, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Import Phase 1, Phase 2, และ Phase 3
    from story_engine import generate_story
    from phase2_generator import generate_phase2_output
    from phase3_storyboard import build_storyboard_from_phase2
    
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
    
    # สร้าง video plan จาก storyboard
    video_plan = generate_video_plan(storyboard)
    
    print("=== Video Plan ===")
    print(json.dumps(video_plan, ensure_ascii=False, indent=2))
    print()
    print(f"Total Duration: {video_plan['total_duration']} seconds")
    print(f"Segment Count: {video_plan['segment_count']}")

