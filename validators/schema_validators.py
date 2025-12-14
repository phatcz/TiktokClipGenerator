"""
Schema Validators
================

Validation functions สำหรับ Phase 2, 3, 4 outputs

Features:
- validate_phase2_output: ตรวจสอบ Phase 2 output schema
- validate_phase3_storyboard: ตรวจสอบ Phase 3 storyboard schema
- validate_phase4_video_plan: ตรวจสอบ Phase 4 video_plan schema

Rules:
- ไม่แก้ logic หลัก
- ไม่เปลี่ยน schema
- เพิ่ม validation layer เท่านั้น
"""

from typing import Dict, List, Any, Optional, Tuple


def validate_phase2_output(phase2_output: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 2 output schema
    
    Phase 2 output structure:
    {
        "story": {...},  # Story object จาก Phase 1
        "characters": [...],  # List of character objects
        "locations": [...],  # List of location objects
        "selection": {
            "selected_character_id": int,
            "selected_location_id": int
        }
    }
    
    Args:
        phase2_output: Phase 2 output dictionary
    
    Returns:
        (is_valid, error_message)
        - is_valid: True ถ้า schema ถูกต้อง
        - error_message: ข้อความ error ถ้าไม่ถูกต้อง (None ถ้าถูกต้อง)
    """
    if not isinstance(phase2_output, dict):
        return False, "phase2_output must be a dictionary"
    
    # ตรวจสอบ required fields
    required_fields = ["story", "characters", "locations", "selection"]
    for field in required_fields:
        if field not in phase2_output:
            return False, f"phase2_output missing required field: '{field}'"
    
    # ตรวจสอบ story
    story = phase2_output.get("story")
    if not isinstance(story, dict):
        return False, "phase2_output.story must be a dictionary"
    
    story_required_fields = ["goal", "product", "audience", "platform", "scenes"]
    for field in story_required_fields:
        if field not in story:
            return False, f"phase2_output.story missing required field: '{field}'"
    
    # ตรวจสอบ characters
    characters = phase2_output.get("characters")
    if not isinstance(characters, list):
        return False, "phase2_output.characters must be a list"
    
    if len(characters) == 0:
        return False, "phase2_output.characters must contain at least one character"
    
    character_required_fields = ["id", "name", "description", "style", "age_range", "personality", "image_url", "image_prompt"]
    for idx, character in enumerate(characters):
        if not isinstance(character, dict):
            return False, f"phase2_output.characters[{idx}] must be a dictionary"
        
        for field in character_required_fields:
            if field not in character:
                return False, f"phase2_output.characters[{idx}] missing required field: '{field}'"
        
        # ตรวจสอบ types
        if not isinstance(character.get("id"), int):
            return False, f"phase2_output.characters[{idx}].id must be an integer"
        if not isinstance(character.get("name"), str):
            return False, f"phase2_output.characters[{idx}].name must be a string"
        if not isinstance(character.get("description"), str):
            return False, f"phase2_output.characters[{idx}].description must be a string"
    
    # ตรวจสอบ locations
    locations = phase2_output.get("locations")
    if not isinstance(locations, list):
        return False, "phase2_output.locations must be a list"
    
    if len(locations) == 0:
        return False, "phase2_output.locations must contain at least one location"
    
    location_required_fields = ["id", "name", "description", "scene_purposes", "style", "mood", "image_url", "image_prompt"]
    for idx, location in enumerate(locations):
        if not isinstance(location, dict):
            return False, f"phase2_output.locations[{idx}] must be a dictionary"
        
        for field in location_required_fields:
            if field not in location:
                return False, f"phase2_output.locations[{idx}] missing required field: '{field}'"
        
        # ตรวจสอบ types
        if not isinstance(location.get("id"), int):
            return False, f"phase2_output.locations[{idx}].id must be an integer"
        if not isinstance(location.get("name"), str):
            return False, f"phase2_output.locations[{idx}].name must be a string"
        if not isinstance(location.get("description"), str):
            return False, f"phase2_output.locations[{idx}].description must be a string"
        if not isinstance(location.get("scene_purposes"), list):
            return False, f"phase2_output.locations[{idx}].scene_purposes must be a list"
    
    # ตรวจสอบ selection
    selection = phase2_output.get("selection")
    if not isinstance(selection, dict):
        return False, "phase2_output.selection must be a dictionary"
    
    selection_required_fields = ["selected_character_id", "selected_location_id"]
    for field in selection_required_fields:
        if field not in selection:
            return False, f"phase2_output.selection missing required field: '{field}'"
    
    # ตรวจสอบ selected IDs อยู่ใน characters/locations หรือไม่
    selected_character_id = selection.get("selected_character_id")
    if selected_character_id is not None:
        character_ids = [char.get("id") for char in characters]
        if selected_character_id not in character_ids:
            return False, f"phase2_output.selection.selected_character_id {selected_character_id} not found in characters"
    
    selected_location_id = selection.get("selected_location_id")
    if selected_location_id is not None:
        location_ids = [loc.get("id") for loc in locations]
        if selected_location_id not in location_ids:
            return False, f"phase2_output.selection.selected_location_id {selected_location_id} not found in locations"
    
    return True, None


def validate_phase3_storyboard(storyboard: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 3 storyboard schema
    
    Storyboard structure:
    {
        "story": {
            "goal": str,
            "product": str,
            "audience": str,
            "platform": str
        },
        "selected_character": {...},  # Optional
        "selected_location": {...},  # Optional
        "scenes": [
            {
                "scene_id": int,
                "purpose": str,
                "emotion": str,
                "duration": float,
                "description": str,
                "keyframes": [
                    {
                        "id": str,
                        "timing": float,
                        "description": str,
                        "image_path": str,
                        "image_prompt": str
                    }
                ]
            }
        ]
    }
    
    Args:
        storyboard: Storyboard dictionary
    
    Returns:
        (is_valid, error_message)
        - is_valid: True ถ้า schema ถูกต้อง
        - error_message: ข้อความ error ถ้าไม่ถูกต้อง (None ถ้าถูกต้อง)
    """
    if not isinstance(storyboard, dict):
        return False, "storyboard must be a dictionary"
    
    # ตรวจสอบ required fields
    required_fields = ["story", "scenes"]
    for field in required_fields:
        if field not in storyboard:
            return False, f"storyboard missing required field: '{field}'"
    
    # ตรวจสอบ story
    story = storyboard.get("story")
    if not isinstance(story, dict):
        return False, "storyboard.story must be a dictionary"
    
    story_required_fields = ["goal", "product", "audience", "platform"]
    for field in story_required_fields:
        if field not in story:
            return False, f"storyboard.story missing required field: '{field}'"
        if not isinstance(story.get(field), str):
            return False, f"storyboard.story.{field} must be a string"
    
    # ตรวจสอบ selected_character (optional)
    selected_character = storyboard.get("selected_character")
    if selected_character is not None:
        if not isinstance(selected_character, dict):
            return False, "storyboard.selected_character must be a dictionary or None"
    
    # ตรวจสอบ selected_location (optional)
    selected_location = storyboard.get("selected_location")
    if selected_location is not None:
        if not isinstance(selected_location, dict):
            return False, "storyboard.selected_location must be a dictionary or None"
    
    # ตรวจสอบ scenes
    scenes = storyboard.get("scenes")
    if not isinstance(scenes, list):
        return False, "storyboard.scenes must be a list"
    
    if len(scenes) == 0:
        return False, "storyboard.scenes must contain at least one scene"
    
    scene_required_fields = ["scene_id", "purpose", "emotion", "duration", "description", "keyframes"]
    for scene_idx, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            return False, f"storyboard.scenes[{scene_idx}] must be a dictionary"
        
        for field in scene_required_fields:
            if field not in scene:
                return False, f"storyboard.scenes[{scene_idx}] missing required field: '{field}'"
        
        # ตรวจสอบ types
        if not isinstance(scene.get("scene_id"), int):
            return False, f"storyboard.scenes[{scene_idx}].scene_id must be an integer"
        if not isinstance(scene.get("purpose"), str):
            return False, f"storyboard.scenes[{scene_idx}].purpose must be a string"
        if not isinstance(scene.get("emotion"), str):
            return False, f"storyboard.scenes[{scene_idx}].emotion must be a string"
        if not isinstance(scene.get("duration"), (int, float)):
            return False, f"storyboard.scenes[{scene_idx}].duration must be a number"
        if not isinstance(scene.get("description"), str):
            return False, f"storyboard.scenes[{scene_idx}].description must be a string"
        
        # ตรวจสอบ keyframes
        keyframes = scene.get("keyframes")
        if not isinstance(keyframes, list):
            return False, f"storyboard.scenes[{scene_idx}].keyframes must be a list"
        
        keyframe_required_fields = ["id", "timing", "description", "image_path", "image_prompt"]
        for kf_idx, keyframe in enumerate(keyframes):
            if not isinstance(keyframe, dict):
                return False, f"storyboard.scenes[{scene_idx}].keyframes[{kf_idx}] must be a dictionary"
            
            for field in keyframe_required_fields:
                if field not in keyframe:
                    return False, f"storyboard.scenes[{scene_idx}].keyframes[{kf_idx}] missing required field: '{field}'"
            
            # ตรวจสอบ types
            if not isinstance(keyframe.get("id"), str):
                return False, f"storyboard.scenes[{scene_idx}].keyframes[{kf_idx}].id must be a string"
            if not isinstance(keyframe.get("timing"), (int, float)):
                return False, f"storyboard.scenes[{scene_idx}].keyframes[{kf_idx}].timing must be a number"
            if not isinstance(keyframe.get("description"), str):
                return False, f"storyboard.scenes[{scene_idx}].keyframes[{kf_idx}].description must be a string"
            if not isinstance(keyframe.get("image_path"), str):
                return False, f"storyboard.scenes[{scene_idx}].keyframes[{kf_idx}].image_path must be a string"
            if not isinstance(keyframe.get("image_prompt"), str):
                return False, f"storyboard.scenes[{scene_idx}].keyframes[{kf_idx}].image_prompt must be a string"
    
    return True, None


def validate_phase4_video_plan(video_plan: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 4 video_plan schema
    
    Video Plan structure:
    {
        "storyboard_metadata": {
            "story": {...},
            "selected_character": {...},  # Optional
            "selected_location": {...}  # Optional
        },
        "segments": [
            {
                "id": int,
                "scene_id": int,
                "duration": float,
                "start_time": float,
                "end_time": float,
                "description": str,
                "purpose": str,
                "emotion": str,
                "start_keyframe": {
                    "id": str,
                    "image_path": str,
                    "description": str,
                    "timing": float
                },
                "end_keyframe": {
                    "id": str,
                    "image_path": str,
                    "description": str,
                    "timing": float
                }
            }
        ],
        "total_duration": float,
        "segment_count": int
    }
    
    Args:
        video_plan: Video plan dictionary
    
    Returns:
        (is_valid, error_message)
        - is_valid: True ถ้า schema ถูกต้อง
        - error_message: ข้อความ error ถ้าไม่ถูกต้อง (None ถ้าถูกต้อง)
    """
    if not isinstance(video_plan, dict):
        return False, "video_plan must be a dictionary"
    
    # ตรวจสอบ required fields
    required_fields = ["storyboard_metadata", "segments", "total_duration", "segment_count"]
    for field in required_fields:
        if field not in video_plan:
            return False, f"video_plan missing required field: '{field}'"
    
    # ตรวจสอบ storyboard_metadata
    storyboard_metadata = video_plan.get("storyboard_metadata")
    if not isinstance(storyboard_metadata, dict):
        return False, "video_plan.storyboard_metadata must be a dictionary"
    
    if "story" not in storyboard_metadata:
        return False, "video_plan.storyboard_metadata missing required field: 'story'"
    
    story = storyboard_metadata.get("story")
    if not isinstance(story, dict):
        return False, "video_plan.storyboard_metadata.story must be a dictionary"
    
    story_required_fields = ["goal", "product", "audience", "platform"]
    for field in story_required_fields:
        if field not in story:
            return False, f"video_plan.storyboard_metadata.story missing required field: '{field}'"
    
    # ตรวจสอบ selected_character (optional)
    selected_character = storyboard_metadata.get("selected_character")
    if selected_character is not None:
        if not isinstance(selected_character, dict):
            return False, "video_plan.storyboard_metadata.selected_character must be a dictionary or None"
    
    # ตรวจสอบ selected_location (optional)
    selected_location = storyboard_metadata.get("selected_location")
    if selected_location is not None:
        if not isinstance(selected_location, dict):
            return False, "video_plan.storyboard_metadata.selected_location must be a dictionary or None"
    
    # ตรวจสอบ segments
    segments = video_plan.get("segments")
    if not isinstance(segments, list):
        return False, "video_plan.segments must be a list"
    
    if len(segments) == 0:
        return False, "video_plan.segments must contain at least one segment"
    
    segment_required_fields = ["id", "scene_id", "duration", "start_time", "end_time", "description", "purpose", "emotion", "start_keyframe", "end_keyframe"]
    for seg_idx, segment in enumerate(segments):
        if not isinstance(segment, dict):
            return False, f"video_plan.segments[{seg_idx}] must be a dictionary"
        
        for field in segment_required_fields:
            if field not in segment:
                return False, f"video_plan.segments[{seg_idx}] missing required field: '{field}'"
        
        # ตรวจสอบ types
        if not isinstance(segment.get("id"), int):
            return False, f"video_plan.segments[{seg_idx}].id must be an integer"
        if not isinstance(segment.get("scene_id"), int):
            return False, f"video_plan.segments[{seg_idx}].scene_id must be an integer"
        if not isinstance(segment.get("duration"), (int, float)):
            return False, f"video_plan.segments[{seg_idx}].duration must be a number"
        if not isinstance(segment.get("start_time"), (int, float)):
            return False, f"video_plan.segments[{seg_idx}].start_time must be a number"
        if not isinstance(segment.get("end_time"), (int, float)):
            return False, f"video_plan.segments[{seg_idx}].end_time must be a number"
        if not isinstance(segment.get("description"), str):
            return False, f"video_plan.segments[{seg_idx}].description must be a string"
        if not isinstance(segment.get("purpose"), str):
            return False, f"video_plan.segments[{seg_idx}].purpose must be a string"
        if not isinstance(segment.get("emotion"), str):
            return False, f"video_plan.segments[{seg_idx}].emotion must be a string"
        
        # ตรวจสอบ start_keyframe
        start_keyframe = segment.get("start_keyframe")
        if not isinstance(start_keyframe, dict):
            return False, f"video_plan.segments[{seg_idx}].start_keyframe must be a dictionary"
        
        start_kf_required_fields = ["id", "image_path", "description", "timing"]
        for field in start_kf_required_fields:
            if field not in start_keyframe:
                return False, f"video_plan.segments[{seg_idx}].start_keyframe missing required field: '{field}'"
        
        if not isinstance(start_keyframe.get("id"), str):
            return False, f"video_plan.segments[{seg_idx}].start_keyframe.id must be a string"
        if not isinstance(start_keyframe.get("image_path"), str):
            return False, f"video_plan.segments[{seg_idx}].start_keyframe.image_path must be a string"
        if not isinstance(start_keyframe.get("description"), str):
            return False, f"video_plan.segments[{seg_idx}].start_keyframe.description must be a string"
        if not isinstance(start_keyframe.get("timing"), (int, float)):
            return False, f"video_plan.segments[{seg_idx}].start_keyframe.timing must be a number"
        
        # ตรวจสอบ end_keyframe
        end_keyframe = segment.get("end_keyframe")
        if not isinstance(end_keyframe, dict):
            return False, f"video_plan.segments[{seg_idx}].end_keyframe must be a dictionary"
        
        end_kf_required_fields = ["id", "image_path", "description", "timing"]
        for field in end_kf_required_fields:
            if field not in end_keyframe:
                return False, f"video_plan.segments[{seg_idx}].end_keyframe missing required field: '{field}'"
        
        if not isinstance(end_keyframe.get("id"), str):
            return False, f"video_plan.segments[{seg_idx}].end_keyframe.id must be a string"
        if not isinstance(end_keyframe.get("image_path"), str):
            return False, f"video_plan.segments[{seg_idx}].end_keyframe.image_path must be a string"
        if not isinstance(end_keyframe.get("description"), str):
            return False, f"video_plan.segments[{seg_idx}].end_keyframe.description must be a string"
        if not isinstance(end_keyframe.get("timing"), (int, float)):
            return False, f"video_plan.segments[{seg_idx}].end_keyframe.timing must be a number"
    
    # ตรวจสอบ total_duration
    total_duration = video_plan.get("total_duration")
    if not isinstance(total_duration, (int, float)):
        return False, "video_plan.total_duration must be a number"
    
    # ตรวจสอบ segment_count
    segment_count = video_plan.get("segment_count")
    if not isinstance(segment_count, int):
        return False, "video_plan.segment_count must be an integer"
    
    # ตรวจสอบ segment_count ตรงกับจำนวน segments จริงหรือไม่
    if segment_count != len(segments):
        return False, f"video_plan.segment_count ({segment_count}) does not match actual number of segments ({len(segments)})"
    
    return True, None


def validate_phase1_story(story: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 1 Story schema
    
    Story structure:
    {
        "goal": str,
        "product": str,
        "audience": str,
        "platform": str,
        "scenes": [
            {
                "id": int,
                "purpose": str,  # hook/conflict/reveal/close
                "emotion": str,
                "duration": int/float,
                "description": str
            }
        ]
    }
    
    Args:
        story: Story dictionary
    
    Returns:
        (is_valid, error_message)
        - is_valid: True ถ้า schema ถูกต้อง
        - error_message: ข้อความ error ถ้าไม่ถูกต้อง (None ถ้าถูกต้อง)
    """
    if not isinstance(story, dict):
        return False, "story must be a dictionary"
    
    # ตรวจสอบ required fields
    required_fields = ["goal", "product", "audience", "platform", "scenes"]
    for field in required_fields:
        if field not in story:
            return False, f"story missing required field: '{field}'"
    
    # ตรวจสอบ types ของ top-level fields
    if not isinstance(story.get("goal"), str):
        return False, "story.goal must be a string"
    if not isinstance(story.get("product"), str):
        return False, "story.product must be a string"
    if not isinstance(story.get("audience"), str):
        return False, "story.audience must be a string"
    if not isinstance(story.get("platform"), str):
        return False, "story.platform must be a string"
    
    # ตรวจสอบ scenes
    scenes = story.get("scenes")
    if not isinstance(scenes, list):
        return False, "story.scenes must be a list"
    
    if len(scenes) == 0:
        return False, "story.scenes must contain at least one scene"
    
    valid_purposes = ["hook", "conflict", "reveal", "close"]
    scene_required_fields = ["id", "purpose", "emotion", "duration", "description"]
    
    for scene_idx, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            return False, f"story.scenes[{scene_idx}] must be a dictionary"
        
        for field in scene_required_fields:
            if field not in scene:
                return False, f"story.scenes[{scene_idx}] missing required field: '{field}'"
        
        # ตรวจสอบ types และ values
        if not isinstance(scene.get("id"), int):
            return False, f"story.scenes[{scene_idx}].id must be an integer"
        
        purpose = scene.get("purpose")
        if not isinstance(purpose, str):
            return False, f"story.scenes[{scene_idx}].purpose must be a string"
        if purpose not in valid_purposes:
            return False, f"story.scenes[{scene_idx}].purpose must be one of {valid_purposes}, got '{purpose}'"
        
        if not isinstance(scene.get("emotion"), str):
            return False, f"story.scenes[{scene_idx}].emotion must be a string"
        
        duration = scene.get("duration")
        if not isinstance(duration, (int, float)):
            return False, f"story.scenes[{scene_idx}].duration must be a number"
        if duration <= 0:
            return False, f"story.scenes[{scene_idx}].duration must be positive"
        
        if not isinstance(scene.get("description"), str):
            return False, f"story.scenes[{scene_idx}].description must be a string"
    
    return True, None


def validate_phase5_render_result(render_result: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 5 Render Result schema
    
    Render Result structure:
    {
        "success": bool,
        "total_segments": int,
        "successful_segments": int,
        "failed_segments": List[int],
        "rendered_segments": [
            {
                "success": bool,
                "segment_id": int,
                "video_path": str (if success=True),
                "duration": float,
                "prompt": str,
                "error": str (if success=False),
                "metadata": dict (optional)
            }
        ]
    }
    
    Args:
        render_result: Render result dictionary
    
    Returns:
        (is_valid, error_message)
        - is_valid: True ถ้า schema ถูกต้อง
        - error_message: ข้อความ error ถ้าไม่ถูกต้อง (None ถ้าถูกต้อง)
    """
    if not isinstance(render_result, dict):
        return False, "render_result must be a dictionary"
    
    # ตรวจสอบ required fields
    required_fields = ["success", "total_segments", "successful_segments", "failed_segments", "rendered_segments"]
    for field in required_fields:
        if field not in render_result:
            return False, f"render_result missing required field: '{field}'"
    
    # ตรวจสอบ types
    if not isinstance(render_result.get("success"), bool):
        return False, "render_result.success must be a boolean"
    if not isinstance(render_result.get("total_segments"), int):
        return False, "render_result.total_segments must be an integer"
    if not isinstance(render_result.get("successful_segments"), int):
        return False, "render_result.successful_segments must be an integer"
    if not isinstance(render_result.get("failed_segments"), list):
        return False, "render_result.failed_segments must be a list"
    
    # ตรวจสอบ rendered_segments
    rendered_segments = render_result.get("rendered_segments")
    if not isinstance(rendered_segments, list):
        return False, "render_result.rendered_segments must be a list"
    
    # ตรวจสอบ total_segments ตรงกับจำนวน rendered_segments
    if render_result.get("total_segments") != len(rendered_segments):
        total_segments = render_result.get("total_segments")
        actual_count = len(rendered_segments)
        return False, f"render_result.total_segments ({total_segments}) does not match actual number of rendered_segments ({actual_count})"
    
    # ตรวจสอบแต่ละ rendered_segment
    for seg_idx, segment in enumerate(rendered_segments):
        if not isinstance(segment, dict):
            return False, f"render_result.rendered_segments[{seg_idx}] must be a dictionary"
        
        # Required fields
        if "success" not in segment:
            return False, f"render_result.rendered_segments[{seg_idx}] missing required field: 'success'"
        if "segment_id" not in segment:
            return False, f"render_result.rendered_segments[{seg_idx}] missing required field: 'segment_id'"
        if "duration" not in segment:
            return False, f"render_result.rendered_segments[{seg_idx}] missing required field: 'duration'"
        if "prompt" not in segment:
            return False, f"render_result.rendered_segments[{seg_idx}] missing required field: 'prompt'"
        
        # ตรวจสอบ types
        if not isinstance(segment.get("success"), bool):
            return False, f"render_result.rendered_segments[{seg_idx}].success must be a boolean"
        
        segment_id = segment.get("segment_id")
        if segment_id is not None and not isinstance(segment_id, int):
            return False, f"render_result.rendered_segments[{seg_idx}].segment_id must be an integer or None"
        
        duration = segment.get("duration")
        if not isinstance(duration, (int, float)):
            return False, f"render_result.rendered_segments[{seg_idx}].duration must be a number"
        if duration != 8.0:
            return False, f"render_result.rendered_segments[{seg_idx}].duration must be 8.0 (got {duration})"
        
        if not isinstance(segment.get("prompt"), (str, type(None))):
            return False, f"render_result.rendered_segments[{seg_idx}].prompt must be a string or None"
        
        # ถ้า success=True ต้องมี video_path
        if segment.get("success"):
            if "video_path" not in segment:
                return False, f"render_result.rendered_segments[{seg_idx}] missing required field: 'video_path' (success=True)"
            if not isinstance(segment.get("video_path"), str):
                return False, f"render_result.rendered_segments[{seg_idx}].video_path must be a string"
            if not segment.get("video_path"):
                return False, f"render_result.rendered_segments[{seg_idx}].video_path must not be empty"
    
    return True, None


def validate_phase5_5_assemble_result(assemble_result: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 5.5 Assemble Result schema
    
    Assemble Result structure:
    {
        "success": bool,
        "output_path": str,
        "failed_segments": List[int],
        "retry_count": int,
        "total_segments": int,
        "successful_segments": int,
        "error": str (optional, if success=False)
    }
    
    Args:
        assemble_result: Assemble result dictionary
    
    Returns:
        (is_valid, error_message)
        - is_valid: True ถ้า schema ถูกต้อง
        - error_message: ข้อความ error ถ้าไม่ถูกต้อง (None ถ้าถูกต้อง)
    """
    if not isinstance(assemble_result, dict):
        return False, "assemble_result must be a dictionary"
    
    # ตรวจสอบ required fields
    required_fields = ["success", "output_path", "failed_segments", "retry_count", "total_segments", "successful_segments"]
    for field in required_fields:
        if field not in assemble_result:
            return False, f"assemble_result missing required field: '{field}'"
    
    # ตรวจสอบ types
    if not isinstance(assemble_result.get("success"), bool):
        return False, "assemble_result.success must be a boolean"
    if not isinstance(assemble_result.get("output_path"), (str, type(None))):
        return False, "assemble_result.output_path must be a string or None"
    if not isinstance(assemble_result.get("failed_segments"), list):
        return False, "assemble_result.failed_segments must be a list"
    if not isinstance(assemble_result.get("retry_count"), int):
        return False, "assemble_result.retry_count must be an integer"
    if not isinstance(assemble_result.get("total_segments"), int):
        return False, "assemble_result.total_segments must be an integer"
    if not isinstance(assemble_result.get("successful_segments"), int):
        return False, "assemble_result.successful_segments must be an integer"
    
    # ถ้า success=True ต้องมี output_path และไม่เป็น empty
    if assemble_result.get("success"):
        output_path = assemble_result.get("output_path")
        if not output_path:
            return False, "assemble_result.output_path must not be empty when success=True"
    
    # ตรวจสอบ logical consistency
    total_segments = assemble_result.get("total_segments")
    successful_segments = assemble_result.get("successful_segments")
    failed_segments = assemble_result.get("failed_segments")
    
    if successful_segments + len(failed_segments) != total_segments:
        return False, f"assemble_result: successful_segments ({successful_segments}) + failed_segments count ({len(failed_segments)}) != total_segments ({total_segments})"
    
    return True, None


# ==================== Validation Error Classes ====================

class ValidationError(Exception):
    """Base validation error class"""
    def __init__(self, phase: str, message: str):
        self.phase = phase
        self.message = message
        super().__init__(f"[{phase}] {message}")


class PhaseOrderError(ValidationError):
    """Error when phase order is violated"""
    def __init__(self, current_phase: str, required_phase: str):
        message = f"Cannot run {current_phase} without completing {required_phase} first"
        super().__init__(current_phase, message)


# ==================== Phase Input Validation ====================

def validate_phase_input(phase_name: str, input_data: Any, required_type: type, required_fields: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ input สำหรับ phase
    
    Args:
        phase_name: ชื่อ phase (เช่น "Phase 2")
        input_data: ข้อมูล input ที่ต้องการตรวจสอบ
        required_type: Type ที่ต้องการ (dict, list, etc.)
        required_fields: List ของ required fields (ถ้า input_data เป็น dict)
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(input_data, required_type):
        return False, f"{phase_name} input must be {required_type.__name__}, got {type(input_data).__name__}"
    
    if required_fields and isinstance(input_data, dict):
        for field in required_fields:
            if field not in input_data:
                return False, f"{phase_name} input missing required field: '{field}'"
    
    return True, None


def validate_phase2_input(phase1_story: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 1 story ก่อนส่งให้ Phase 2
    
    Args:
        phase1_story: Story จาก Phase 1
    
    Returns:
        (is_valid, error_message)
    """
    return validate_phase1_story(phase1_story)


def validate_phase3_input(phase2_output: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 2 output ก่อนส่งให้ Phase 3
    
    Args:
        phase2_output: Output จาก Phase 2
    
    Returns:
        (is_valid, error_message)
    """
    return validate_phase2_output(phase2_output)


def validate_phase4_input(storyboard: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 3 storyboard ก่อนส่งให้ Phase 4
    
    Args:
        storyboard: Storyboard จาก Phase 3
    
    Returns:
        (is_valid, error_message)
    """
    return validate_phase3_storyboard(storyboard)


def validate_phase5_input(video_plan: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 4 video plan ก่อนส่งให้ Phase 5
    
    Args:
        video_plan: Video plan จาก Phase 4
    
    Returns:
        (is_valid, error_message)
    """
    return validate_phase4_video_plan(video_plan)


def validate_phase5_5_input(render_result: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    ตรวจสอบ Phase 5 render result ก่อนส่งให้ Phase 5.5
    
    Args:
        render_result: Render result จาก Phase 5
    
    Returns:
        (is_valid, error_message)
    """
    return validate_phase5_render_result(render_result)
