"""
Phase 5: Segment Renderer

Input:
- video_plan จาก Phase 4

Output:
- rendered segment video files (ทีละ segment)
- แต่ละ segment = 8 วินาที (fix)

Features:
- ออกแบบ segment schema (start_keyframe, end_keyframe, directive, continuity locks)
- ออกแบบ render prompt template
- mock Google Video Gen API
- gen ทีละ segment (ไม่ gen วิดีโอยาวรวดเดียว)

กติกา:
- 1 segment = 8 วินาที (fix)
- ห้ามเปลี่ยน duration
- ห้าม gen วิดีโอยาวรวดเดียว
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


# ==================== Segment Schema ====================

def create_segment_schema(
    segment_id: int,
    start_keyframe: Dict[str, Any],
    end_keyframe: Dict[str, Any],
    directive: Dict[str, Any],
    continuity_locks: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    สร้าง Segment Schema ตามข้อกำหนด
    
    Args:
        segment_id: ID ของ segment
        start_keyframe: Keyframe เริ่มต้น (ต้องมี image_path, description)
        end_keyframe: Keyframe สิ้นสุด (ต้องมี image_path, description)
        directive: คำสั่งสำหรับ motion/camera (motion_type, camera_movement)
        continuity_locks: ข้อมูลสำหรับ continuity (character, location, style)
        metadata: ข้อมูลเพิ่มเติม (optional)
    
    Returns:
        Dictionary ที่มีโครงสร้างตาม Segment Schema
    """
    segment = {
        "id": segment_id,
        "duration": 8.0,  # Fix: 8 วินาที
        "start_keyframe": {
            "id": start_keyframe.get("id"),
            "image_path": start_keyframe.get("image_path"),
            "description": start_keyframe.get("description"),
            "timing": start_keyframe.get("timing", 0.0)
        },
        "end_keyframe": {
            "id": end_keyframe.get("id"),
            "image_path": end_keyframe.get("image_path"),
            "description": end_keyframe.get("description"),
            "timing": end_keyframe.get("timing", 0.0)
        },
        "directive": {
            "motion_type": directive.get("motion_type", "smooth"),  # smooth, dynamic, static
            "camera_movement": directive.get("camera_movement", "none"),  # none, zoom_in, zoom_out, pan_left, pan_right, tilt_up, tilt_down
            "transition_style": directive.get("transition_style", "fade")  # fade, cut, dissolve
        },
        "continuity_locks": {
            "character": continuity_locks.get("character"),
            "location": continuity_locks.get("location"),
            "style": continuity_locks.get("style"),
            "emotion": continuity_locks.get("emotion")
        }
    }
    
    if metadata:
        segment["metadata"] = metadata
    
    return segment


# ==================== Render Prompt Template ====================

def build_render_prompt(segment: Dict[str, Any], story_context: Optional[Dict[str, Any]] = None) -> str:
    """
    สร้าง Render Prompt Template สำหรับ Google Video Gen API
    
    Contract: segment ต้องมี start_keyframe และ end_keyframe objects ที่มี required fields ครบแล้ว
    
    Args:
        segment: Segment object ที่มี start_keyframe, end_keyframe, directive, continuity_locks
        story_context: Story context จาก Phase 1 (optional)
    
    Returns:
        Prompt string สำหรับ video generation
    
    Raises:
        ValueError: ถ้า segment ไม่มี start_keyframe หรือ end_keyframe หรือขาด required fields
    """
    # Strict validation: ต้องมี start_keyframe และ end_keyframe
    if "start_keyframe" not in segment:
        raise ValueError("segment must have 'start_keyframe' field")
    if "end_keyframe" not in segment:
        raise ValueError("segment must have 'end_keyframe' field")
    
    start_kf = segment.get("start_keyframe")
    end_kf = segment.get("end_keyframe")
    directive = segment.get("directive", {})
    continuity = segment.get("continuity_locks", {})
    
    # Validate keyframe fields
    if not isinstance(start_kf, dict) or "description" not in start_kf:
        raise ValueError("segment 'start_keyframe' must be an object with 'description' field")
    if not isinstance(end_kf, dict) or "description" not in end_kf:
        raise ValueError("segment 'end_keyframe' must be an object with 'description' field")
    
    # เริ่มต้น prompt
    prompt_parts = []
    
    # Scene description จาก keyframes (strict: ต้องมีแล้ว)
    prompt_parts.append(f"Start: {start_kf.get('description')}")
    prompt_parts.append(f"End: {end_kf.get('description')}")
    
    # Continuity locks
    if continuity.get("character"):
        prompt_parts.append(f"Character: {continuity.get('character')}")
    if continuity.get("location"):
        prompt_parts.append(f"Location: {continuity.get('location')}")
    if continuity.get("style"):
        prompt_parts.append(f"Style: {continuity.get('style')}")
    if continuity.get("emotion"):
        prompt_parts.append(f"Emotion: {continuity.get('emotion')}")
    
    # Motion directive
    motion_type = directive.get("motion_type", "smooth")
    camera_movement = directive.get("camera_movement", "none")
    transition_style = directive.get("transition_style", "fade")
    
    prompt_parts.append(f"Motion: {motion_type}")
    if camera_movement != "none":
        prompt_parts.append(f"Camera: {camera_movement}")
    prompt_parts.append(f"Transition: {transition_style}")
    
    # Story context (ถ้ามี)
    if story_context:
        product = story_context.get("product", "")
        platform = story_context.get("platform", "")
        if product:
            prompt_parts.append(f"Product context: {product}")
        if platform:
            prompt_parts.append(f"Platform: {platform}")
    
    # Duration
    prompt_parts.append("Duration: 8 seconds")
    
    # รวม prompt
    full_prompt = " | ".join(prompt_parts)
    
    return full_prompt


# ==================== Mock Google Video Gen API ====================

def mock_google_video_generation(
    prompt: str,
    start_keyframe_path: Optional[str] = None,
    end_keyframe_path: Optional[str] = None,
    duration: float = 8.0
) -> Dict[str, Any]:
    """
    Mock API สำหรับ Google Video Generation
    
    ในอนาคตจะแทนที่ด้วย Google Video Gen API จริง
    
    Args:
        prompt: Render prompt สำหรับ video generation
        start_keyframe_path: Path ของ start keyframe image (optional)
        end_keyframe_path: Path ของ end keyframe image (optional)
        duration: Duration ของ video (default: 8.0 seconds)
    
    Returns:
        Dictionary ที่มี:
        - success: bool
        - video_path: str (path ของ generated video)
        - duration: float
        - metadata: dict (additional info)
    """
    # Mock: สร้าง video path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    video_id = hash(prompt) % 1000000
    
    video_path = f"output/segments/segment_{video_id}_{timestamp}_{unique_id}.mp4"
    
    # Mock: simulate API call
    # ใน production จะต้อง:
    # 1. เรียก Google Video Gen API
    # 2. ส่ง prompt, keyframes, parameters
    # 3. รอ response
    # 4. ดาวน์โหลด video file
    
    result = {
        "success": True,
        "video_path": video_path,
        "duration": duration,
        "metadata": {
            "prompt": prompt,
            "start_keyframe": start_keyframe_path,
            "end_keyframe": end_keyframe_path,
            "generated_at": timestamp,
            "api_version": "mock_v1.0"
        }
    }
    
    return result


# ==================== Segment Rendering ====================

def render_segment(
    segment: Dict[str, Any],
    story_context: Optional[Dict[str, Any]] = None,
    output_dir: str = "output/segments"
) -> Dict[str, Any]:
    """
    Render video segment (8.0 seconds)
    
    Duration Contract:
    - Phase 4 sends segments with any duration (not fixed to 8.0)
    - Phase 5 ALWAYS overrides duration to 8.0 seconds
    - Original Phase 4 duration is stored in metadata.original_duration for reference
    
    กติกา:
    - 1 segment = 8 วินาที (fix ใน Phase 5)
    - ห้าม gen วิดีโอยาวรวดเดียว
    - ต้องมี start_keyframe, end_keyframe, directive, continuity_locks
    
    Args:
        segment: Segment object from Phase 4 (must have start_keyframe, end_keyframe objects)
        story_context: Story context จาก Phase 1 (optional)
        output_dir: Directory สำหรับ output (default: "output/segments")
    
    Returns:
        Dictionary ที่มี:
        - success: bool
        - segment_id: int
        - video_path: str
        - duration: float (always 8.0)
        - prompt: str
        - metadata: dict (includes original_duration from Phase 4)
        - error: str (ถ้ามี)
    """
    # Validate segment
    if not isinstance(segment, dict):
        return {
            "success": False,
            "segment_id": None,
            "video_path": None,
            "duration": 8.0,
            "prompt": None,
            "error": "segment must be a dictionary"
        }
    
    segment_id = segment.get("id")
    if segment_id is None:
        return {
            "success": False,
            "segment_id": None,
            "video_path": None,
            "duration": 8.0,
            "prompt": None,
            "error": "segment must have 'id' field"
        }
    
    # Validate required fields
    required_fields = ["start_keyframe", "end_keyframe", "directive", "continuity_locks"]
    for field in required_fields:
        if field not in segment:
            return {
                "success": False,
                "segment_id": segment_id,
                "video_path": None,
                "duration": 8.0,
                "prompt": None,
                "error": f"segment must have '{field}' field"
            }
    
    # Strict validation: start_keyframe และ end_keyframe ต้องเป็น objects และมี required fields
    start_keyframe = segment.get("start_keyframe")
    end_keyframe = segment.get("end_keyframe")
    
    if not isinstance(start_keyframe, dict):
        return {
            "success": False,
            "segment_id": segment_id,
            "video_path": None,
            "duration": 8.0,
            "prompt": None,
            "error": f"segment 'start_keyframe' must be an object (dict), got {type(start_keyframe)}"
        }
    
    if not isinstance(end_keyframe, dict):
        return {
            "success": False,
            "segment_id": segment_id,
            "video_path": None,
            "duration": 8.0,
            "prompt": None,
            "error": f"segment 'end_keyframe' must be an object (dict), got {type(end_keyframe)}"
        }
    
    # Validate keyframe required fields
    required_keyframe_fields = ["id", "image_path", "description", "timing"]
    for field in required_keyframe_fields:
        if field not in start_keyframe:
            return {
                "success": False,
                "segment_id": segment_id,
                "video_path": None,
                "duration": 8.0,
                "prompt": None,
                "error": f"segment 'start_keyframe' missing required field '{field}'"
            }
        if field not in end_keyframe:
            return {
                "success": False,
                "segment_id": segment_id,
                "video_path": None,
                "duration": 8.0,
                "prompt": None,
                "error": f"segment 'end_keyframe' missing required field '{field}'"
            }
    
    # Duration Contract: Phase 5 ALWAYS uses 8.0 seconds (overrides Phase 4 duration)
    # Phase 4 duration is stored in metadata.original_duration for reference
    original_duration = segment.get("duration", 8.0)
    duration = 8.0  # Fix: Phase 5 always renders 8.0 seconds regardless of Phase 4 duration
    
    # Build render prompt
    try:
        prompt = build_render_prompt(segment, story_context)
    except Exception as e:
        return {
            "success": False,
            "segment_id": segment_id,
            "video_path": None,
            "duration": 8.0,
            "prompt": None,
            "error": f"failed to build prompt: {str(e)}"
        }
    
    # Get keyframe paths (strict: ต้องมีแล้วจากการ validate ด้านบน)
    start_keyframe_path = start_keyframe.get("image_path")
    end_keyframe_path = end_keyframe.get("image_path")
    
    # Call mock Google Video Gen API
    try:
        api_result = mock_google_video_generation(
            prompt=prompt,
            start_keyframe_path=start_keyframe_path,
            end_keyframe_path=end_keyframe_path,
            duration=8.0  # Fix: 8 วินาที
        )
        
        if api_result.get("success"):
            # Store original duration from Phase 4 in metadata for reference
            metadata = api_result.get("metadata", {})
            metadata["original_duration"] = original_duration
            
            return {
                "success": True,
                "segment_id": segment_id,
                "video_path": api_result.get("video_path"),
                "duration": 8.0,  # Phase 5 always uses 8.0 seconds
                "prompt": prompt,
                "error": None,
                "metadata": metadata
            }
        else:
            return {
                "success": False,
                "segment_id": segment_id,
                "video_path": None,
                "duration": 8.0,
                "prompt": prompt,
                "error": "API call failed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "segment_id": segment_id,
            "video_path": None,
            "duration": 8.0,
            "prompt": prompt,
            "error": f"API error: {str(e)}"
        }


def render_segments_from_video_plan(
    video_plan: Dict[str, Any],
    story_context: Optional[Dict[str, Any]] = None,
    output_dir: str = "output/segments"
) -> Dict[str, Any]:
    """
    Render segments ทั้งหมดจาก video_plan (ทีละ segment)
    
    Duration Contract:
    - Phase 4 sends segments with any duration (not fixed to 8.0)
    - Phase 5 ALWAYS overrides duration to 8.0 seconds for rendering
    - Original Phase 4 duration stored in metadata.original_duration
    
    กติกา:
    - แต่ละ segment = 8 วินาที (fix ใน Phase 5)
    - ห้าม gen วิดีโอยาวรวดเดียว
    - Render ทีละ segment
    
    Args:
        video_plan: Video Plan object จาก Phase 4
        story_context: Story context จาก Phase 1 (optional)
        output_dir: Directory สำหรับ output (default: "output/segments")
    
    Returns:
        Dictionary ที่มี:
        - success: bool
        - total_segments: int
        - successful_segments: int
        - failed_segments: List[int]
        - rendered_segments: List[Dict] (results)
    """
    if not isinstance(video_plan, dict):
        raise ValueError("video_plan must be a dictionary")
    
    if "segments" not in video_plan:
        raise ValueError("video_plan must contain 'segments' field")
    
    segments = video_plan.get("segments", [])
    if not segments:
        raise ValueError("video_plan must contain at least one segment")
    
    # Get story context from video_plan if available
    if story_context is None:
        storyboard_metadata = video_plan.get("storyboard_metadata", {})
        story_context = storyboard_metadata.get("story")
    
    # Render ทีละ segment
    rendered_segments = []
    successful_count = 0
    failed_segments = []
    
    for segment in segments:
        # Phase 4 ต้องส่ง start_keyframe และ end_keyframe objects มาให้ครบแล้ว
        # ไม่รองรับ schema เก่า (strict mode)
        
        # Validate: ต้องมี start_keyframe และ end_keyframe
        if "start_keyframe" not in segment:
            raise ValueError(f"Segment {segment.get('id')} missing 'start_keyframe' field. Phase 4 must provide start_keyframe object.")
        if "end_keyframe" not in segment:
            raise ValueError(f"Segment {segment.get('id')} missing 'end_keyframe' field. Phase 4 must provide end_keyframe object.")
        
        # Validate: start_keyframe และ end_keyframe ต้องเป็น objects
        start_keyframe = segment.get("start_keyframe")
        end_keyframe = segment.get("end_keyframe")
        
        if not isinstance(start_keyframe, dict):
            raise ValueError(f"Segment {segment.get('id')} 'start_keyframe' must be an object (dict), got {type(start_keyframe)}")
        if not isinstance(end_keyframe, dict):
            raise ValueError(f"Segment {segment.get('id')} 'end_keyframe' must be an object (dict), got {type(end_keyframe)}")
        
        # Validate: start_keyframe และ end_keyframe ต้องมี required fields
        required_keyframe_fields = ["id", "image_path", "description", "timing"]
        for field in required_keyframe_fields:
            if field not in start_keyframe:
                raise ValueError(f"Segment {segment.get('id')} 'start_keyframe' missing required field '{field}'")
            if field not in end_keyframe:
                raise ValueError(f"Segment {segment.get('id')} 'end_keyframe' missing required field '{field}'")
        
        phase5_segment = create_segment_schema(
            segment_id=segment.get("id"),
            start_keyframe=start_keyframe,
            end_keyframe=end_keyframe,
            directive={
                "motion_type": "smooth",  # Default
                "camera_movement": "none",  # Default
                "transition_style": "fade"  # Default
            },
            continuity_locks={
                "character": None,  # จะได้จาก storyboard_metadata
                "location": None,  # จะได้จาก storyboard_metadata
                "style": None,
                "emotion": segment.get("emotion")
            },
            metadata={
                "scene_id": segment.get("scene_id"),
                "purpose": segment.get("purpose"),
                "original_duration": segment.get("duration")
            }
        )
        
        # Get continuity locks from storyboard_metadata
        storyboard_metadata = video_plan.get("storyboard_metadata", {})
        selected_character = storyboard_metadata.get("selected_character")
        selected_location = storyboard_metadata.get("selected_location")
        
        if selected_character:
            phase5_segment["continuity_locks"]["character"] = selected_character.get("name")
        if selected_location:
            phase5_segment["continuity_locks"]["location"] = selected_location.get("name")
        
        # Render segment
        result = render_segment(phase5_segment, story_context, output_dir)
        rendered_segments.append(result)
        
        if result.get("success"):
            successful_count += 1
        else:
            failed_segments.append(segment.get("id"))
    
    return {
        "success": len(failed_segments) == 0,
        "total_segments": len(segments),
        "successful_segments": successful_count,
        "failed_segments": failed_segments,
        "rendered_segments": rendered_segments
    }


# ==================== Helper Functions ====================

def convert_phase4_to_phase5_segment(
    phase4_segment: Dict[str, Any],
    next_segment: Optional[Dict[str, Any]] = None,
    storyboard_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convert Phase 4 segment เป็น Phase 5 segment schema
    
    Contract: Phase 4 ต้องส่ง start_keyframe และ end_keyframe objects มาให้ครบแล้ว
    ไม่รองรับ schema เก่า (strict mode)
    
    Args:
        phase4_segment: Segment จาก Phase 4 (ต้องมี start_keyframe และ end_keyframe objects)
        next_segment: Segment ถัดไป (deprecated, ไม่ใช้แล้ว)
        storyboard_metadata: Metadata จาก storyboard (optional)
    
    Returns:
        Phase 5 segment schema
    
    Raises:
        ValueError: ถ้า phase4_segment ไม่มี start_keyframe หรือ end_keyframe
    """
    # Strict validation: Phase 4 ต้องส่ง start_keyframe และ end_keyframe มาให้ครบ
    if "start_keyframe" not in phase4_segment:
        raise ValueError(f"Phase 4 segment {phase4_segment.get('id')} missing 'start_keyframe' field. Phase 4 must provide start_keyframe object.")
    if "end_keyframe" not in phase4_segment:
        raise ValueError(f"Phase 4 segment {phase4_segment.get('id')} missing 'end_keyframe' field. Phase 4 must provide end_keyframe object.")
    
    # Validate: start_keyframe และ end_keyframe ต้องเป็น objects
    start_keyframe = phase4_segment.get("start_keyframe")
    end_keyframe = phase4_segment.get("end_keyframe")
    
    if not isinstance(start_keyframe, dict):
        raise ValueError(f"Phase 4 segment {phase4_segment.get('id')} 'start_keyframe' must be an object (dict), got {type(start_keyframe)}")
    if not isinstance(end_keyframe, dict):
        raise ValueError(f"Phase 4 segment {phase4_segment.get('id')} 'end_keyframe' must be an object (dict), got {type(end_keyframe)}")
    
    # Validate: start_keyframe และ end_keyframe ต้องมี required fields
    required_keyframe_fields = ["id", "image_path", "description", "timing"]
    for field in required_keyframe_fields:
        if field not in start_keyframe:
            raise ValueError(f"Phase 4 segment {phase4_segment.get('id')} 'start_keyframe' missing required field '{field}'")
        if field not in end_keyframe:
            raise ValueError(f"Phase 4 segment {phase4_segment.get('id')} 'end_keyframe' missing required field '{field}'")
    
    # Get continuity locks
    continuity_locks = {
        "character": None,
        "location": None,
        "style": None,
        "emotion": phase4_segment.get("emotion")
    }
    
    if storyboard_metadata:
        selected_character = storyboard_metadata.get("selected_character")
        selected_location = storyboard_metadata.get("selected_location")
        
        if selected_character:
            continuity_locks["character"] = selected_character.get("name")
        if selected_location:
            continuity_locks["location"] = selected_location.get("name")
            continuity_locks["style"] = selected_location.get("style")
    
    # Create Phase 5 segment
    phase5_segment = create_segment_schema(
        segment_id=phase4_segment.get("id"),
        start_keyframe=start_keyframe,
        end_keyframe=end_keyframe,
        directive={
            "motion_type": "smooth",
            "camera_movement": "none",
            "transition_style": "fade"
        },
        continuity_locks=continuity_locks,
        metadata={
            "scene_id": phase4_segment.get("scene_id"),
            "purpose": phase4_segment.get("purpose"),
            "original_duration": phase4_segment.get("duration")
        }
    )
    
    return phase5_segment


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Import Phase 4
    from phase4_video_plan import generate_video_plan
    from phase3_storyboard import build_storyboard_from_phase2
    from phase2_generator import generate_phase2_output
    from story_engine import generate_story
    
    # สร้าง story จาก Phase 1
    story = generate_story(
        goal="ขายคอร์สออนไลน์",
        product="AI Creator Tool",
        audience="มือใหม่ ไม่เก่งเทค",
        platform="Facebook Reel"
    )
    
    # สร้าง Phase 2 output
    phase2_output = generate_phase2_output(story, num_characters=4, num_locations=4)
    
    # เลือก character และ location
    selected_character_id = 1
    selected_location_id = 1
    
    # สร้าง storyboard
    storyboard = build_storyboard_from_phase2(phase2_output, selected_character_id, selected_location_id)
    
    # สร้าง video plan
    video_plan = generate_video_plan(storyboard)
    
    print("=== Phase 5: Segment Renderer ===")
    print(f"Total Segments: {video_plan.get('segment_count')}")
    print()
    
    # Render segments
    render_result = render_segments_from_video_plan(video_plan, story)
    
    print("=== Render Results ===")
    print(f"Success: {render_result['success']}")
    print(f"Successful Segments: {render_result['successful_segments']}/{render_result['total_segments']}")
    print(f"Failed Segments: {render_result['failed_segments']}")
    print()
    
    # แสดงผลลัพธ์ของแต่ละ segment
    print("=== Rendered Segments ===")
    for result in render_result['rendered_segments']:
        print(f"Segment {result['segment_id']}:")
        print(f"  Success: {result['success']}")
        print(f"  Video Path: {result['video_path']}")
        print(f"  Duration: {result['duration']}s")
        if result.get('error'):
            print(f"  Error: {result['error']}")
        print()

