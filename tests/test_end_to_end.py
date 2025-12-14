"""
End-to-End Regression Test

ทดสอบว่า pipeline ตั้งแต่ Phase 1 → Phase 5.5 ทำงานได้ถูกต้อง
และ schema ของทุก phase ครบถ้วน
"""

import sys
import os
from typing import Dict, List, Any

# Try to import pytest, but fallback to basic assert if not available
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from end_to_end_run import run_end_to_end


def validate_phase1_story(story: Dict[str, Any]) -> None:
    """
    Validate Phase 1 Story schema
    
    Required fields:
    - goal: str
    - product: str
    - audience: str
    - platform: str
    - scenes: List[Dict]
    
    Each scene must have:
    - id: int
    - purpose: str (hook/conflict/reveal/close)
    - emotion: str
    - duration: int
    - description: str
    """
    assert isinstance(story, dict), "Phase 1 story must be a dictionary"
    
    required_fields = ["goal", "product", "audience", "platform", "scenes"]
    for field in required_fields:
        assert field in story, f"Phase 1 story must have '{field}' field"
    
    assert isinstance(story["scenes"], list), "Phase 1 scenes must be a list"
    assert len(story["scenes"]) > 0, "Phase 1 must have at least one scene"
    
    valid_purposes = ["hook", "conflict", "reveal", "close"]
    for scene in story["scenes"]:
        assert isinstance(scene, dict), "Each scene must be a dictionary"
        assert "id" in scene, "Scene must have 'id' field"
        assert "purpose" in scene, "Scene must have 'purpose' field"
        assert scene["purpose"] in valid_purposes, f"Scene purpose must be one of {valid_purposes}"
        assert "emotion" in scene, "Scene must have 'emotion' field"
        assert "duration" in scene, "Scene must have 'duration' field"
        assert "description" in scene, "Scene must have 'description' field"
        assert isinstance(scene["duration"], (int, float)) and scene["duration"] > 0, "Scene duration must be positive"


def validate_phase2_output(phase2_output: Dict[str, Any]) -> None:
    """
    Validate Phase 2 Output schema
    
    Required fields:
    - story: Dict (Phase 1 story)
    - characters: List[Dict]
    - locations: List[Dict]
    """
    assert isinstance(phase2_output, dict), "Phase 2 output must be a dictionary"
    
    required_fields = ["story", "characters", "locations"]
    for field in required_fields:
        assert field in phase2_output, f"Phase 2 output must have '{field}' field"
    
    # Validate story (should be Phase 1 story)
    validate_phase1_story(phase2_output["story"])
    
    # Validate characters
    assert isinstance(phase2_output["characters"], list), "Phase 2 characters must be a list"
    assert len(phase2_output["characters"]) > 0, "Phase 2 must have at least one character"
    
    for char in phase2_output["characters"]:
        assert isinstance(char, dict), "Each character must be a dictionary"
        assert "id" in char, "Character must have 'id' field"
        assert "name" in char, "Character must have 'name' field"
        assert "image_url" in char, "Character must have 'image_url' field"
    
    # Validate locations
    assert isinstance(phase2_output["locations"], list), "Phase 2 locations must be a list"
    assert len(phase2_output["locations"]) > 0, "Phase 2 must have at least one location"
    
    for loc in phase2_output["locations"]:
        assert isinstance(loc, dict), "Each location must be a dictionary"
        assert "id" in loc, "Location must have 'id' field"
        assert "name" in loc, "Location must have 'name' field"
        assert "image_url" in loc, "Location must have 'image_url' field"


def validate_phase3_storyboard(storyboard: Dict[str, Any]) -> None:
    """
    Validate Phase 3 Storyboard schema
    
    Required fields:
    - scenes: List[Dict]
    
    Each scene must have:
    - scene_id: int
    - keyframes: List[Dict]
    
    Each keyframe must have:
    - id: str
    - image_path: str
    - description: str
    - timing: float
    """
    assert isinstance(storyboard, dict), "Phase 3 storyboard must be a dictionary"
    assert "scenes" in storyboard, "Phase 3 storyboard must have 'scenes' field"
    
    scenes = storyboard["scenes"]
    assert isinstance(scenes, list), "Phase 3 scenes must be a list"
    assert len(scenes) > 0, "Phase 3 must have at least one scene"
    
    for scene in scenes:
        assert isinstance(scene, dict), "Each scene must be a dictionary"
        assert "scene_id" in scene, "Scene must have 'scene_id' field"
        assert "keyframes" in scene, "Scene must have 'keyframes' field"
        
        keyframes = scene["keyframes"]
        assert isinstance(keyframes, list), "Scene keyframes must be a list"
        assert len(keyframes) > 0, "Scene must have at least one keyframe"
        
        for kf in keyframes:
            assert isinstance(kf, dict), "Each keyframe must be a dictionary"
            assert "id" in kf, "Keyframe must have 'id' field"
            assert "image_path" in kf, "Keyframe must have 'image_path' field"
            assert "description" in kf, "Keyframe must have 'description' field"
            assert "timing" in kf, "Keyframe must have 'timing' field"


def validate_phase4_video_plan(video_plan: Dict[str, Any]) -> None:
    """
    Validate Phase 4 Video Plan schema
    
    Required fields:
    - segments: List[Dict]
    - segment_count: int
    - total_duration: float
    
    Each segment must have:
    - id: int
    - start_keyframe: Dict (must have id, image_path, description, timing)
    - end_keyframe: Dict (must have id, image_path, description, timing)
    """
    assert isinstance(video_plan, dict), "Phase 4 video plan must be a dictionary"
    
    required_fields = ["segments", "segment_count", "total_duration"]
    for field in required_fields:
        assert field in video_plan, f"Phase 4 video plan must have '{field}' field"
    
    segments = video_plan["segments"]
    assert isinstance(segments, list), "Phase 4 segments must be a list"
    assert len(segments) > 0, "Phase 4 must have at least one segment"
    assert video_plan["segment_count"] == len(segments), "segment_count must match segments list length"
    
    for segment in segments:
        assert isinstance(segment, dict), "Each segment must be a dictionary"
        assert "id" in segment, "Segment must have 'id' field"
        assert "start_keyframe" in segment, "Segment must have 'start_keyframe' field"
        assert "end_keyframe" in segment, "Segment must have 'end_keyframe' field"
        
        # Validate start_keyframe
        start_kf = segment["start_keyframe"]
        assert isinstance(start_kf, dict), "start_keyframe must be a dictionary"
        kf_required_fields = ["id", "image_path", "description", "timing"]
        for field in kf_required_fields:
            assert field in start_kf, f"start_keyframe must have '{field}' field"
        
        # Validate end_keyframe
        end_kf = segment["end_keyframe"]
        assert isinstance(end_kf, dict), "end_keyframe must be a dictionary"
        for field in kf_required_fields:
            assert field in end_kf, f"end_keyframe must have '{field}' field"


def validate_phase5_render_result(render_result: Dict[str, Any]) -> None:
    """
    Validate Phase 5 Render Result schema
    
    Required fields:
    - rendered_segments: List[Dict]
    - successful_segments: int
    - total_segments: int
    - failed_segments: List[int]
    
    Each rendered_segment must have:
    - segment_id: int
    - success: bool
    - video_path: str (if success=True)
    - duration: float
    - prompt: str
    """
    assert isinstance(render_result, dict), "Phase 5 render result must be a dictionary"
    
    required_fields = ["rendered_segments", "successful_segments", "total_segments", "failed_segments"]
    for field in required_fields:
        assert field in render_result, f"Phase 5 render result must have '{field}' field"
    
    rendered_segments = render_result["rendered_segments"]
    assert isinstance(rendered_segments, list), "Phase 5 rendered_segments must be a list"
    assert render_result["total_segments"] == len(rendered_segments), "total_segments must match rendered_segments list length"
    
    for seg in rendered_segments:
        assert isinstance(seg, dict), "Each rendered segment must be a dictionary"
        assert "segment_id" in seg, "Rendered segment must have 'segment_id' field"
        assert "success" in seg, "Rendered segment must have 'success' field"
        assert "duration" in seg, "Rendered segment must have 'duration' field"
        assert "prompt" in seg, "Rendered segment must have 'prompt' field"
        
        if seg["success"]:
            assert "video_path" in seg, "Successful segment must have 'video_path' field"
            assert seg["video_path"], "video_path must not be empty"


def validate_phase5_5_assemble_result(assemble_result: Dict[str, Any]) -> None:
    """
    Validate Phase 5.5 Assemble Result schema
    
    Required fields:
    - success: bool
    - output_path: str
    - failed_segments: List[int]
    - retry_count: int
    - total_segments: int
    - successful_segments: int
    """
    assert isinstance(assemble_result, dict), "Phase 5.5 assemble result must be a dictionary"
    
    required_fields = ["success", "output_path", "failed_segments", "retry_count", "total_segments", "successful_segments"]
    for field in required_fields:
        assert field in assemble_result, f"Phase 5.5 assemble result must have '{field}' field"
    
    assert isinstance(assemble_result["success"], bool), "success must be a boolean"
    assert isinstance(assemble_result["output_path"], str), "output_path must be a string"
    if assemble_result["success"]:
        assert assemble_result["output_path"], "output_path must not be empty when success=True"


def test_end_to_end_pipeline():
    """
    Test ที่ทดสอบ end-to-end pipeline ตั้งแต่ Phase 1 → Phase 5.5
    """
    # Run end-to-end pipeline
    result = run_end_to_end(
        goal="ขายคอร์สออนไลน์",
        product="AI Creator Tool",
        audience="มือใหม่ ไม่เก่งเทค",
        platform="Facebook Reel",
        selected_character_id=1,
        selected_location_id=1,
        num_characters=4,
        num_locations=4
    )
    
    # Assert pipeline ไม่ error (ถ้ามี error จะ throw exception แล้ว)
    assert result is not None, "End-to-end pipeline should return a result"
    assert isinstance(result, dict), "Result should be a dictionary"
    
    # Assert schema ครบทุก phase
    validate_phase1_story(result["phase1_story"])
    validate_phase2_output(result["phase2_output"])
    validate_phase3_storyboard(result["phase3_storyboard"])
    validate_phase4_video_plan(result["phase4_video_plan"])
    validate_phase5_render_result(result["phase5_render_result"])
    validate_phase5_5_assemble_result(result["phase5_5_assemble_result"])
    
    # Assert summary
    assert "summary" in result, "Result should have 'summary' field"
    summary = result["summary"]
    assert "total_segments" in summary, "Summary should have 'total_segments'"
    assert "final_video_path" in summary, "Summary should have 'final_video_path'"
    assert "assemble_success" in summary, "Summary should have 'assemble_success'"
    
    # Assert pipeline success
    assert summary["assemble_success"], "Pipeline should complete successfully"
    assert summary["final_video_path"], "Final video path should not be empty"


def test_end_to_end_pipeline_custom_inputs():
    """
    Test end-to-end pipeline with different inputs
    """
    result = run_end_to_end(
        goal="เพิ่มผู้ติดตาม",
        product="Social Media Tool",
        audience="นักสร้างคอนเทนต์",
        platform="TikTok",
        selected_character_id=1,
        selected_location_id=1,
        num_characters=3,
        num_locations=3
    )
    
    # Assert ไม่ error
    assert result is not None, "End-to-end pipeline should return a result"
    
    # Assert schema ครบ
    validate_phase1_story(result["phase1_story"])
    validate_phase2_output(result["phase2_output"])
    validate_phase3_storyboard(result["phase3_storyboard"])
    validate_phase4_video_plan(result["phase4_video_plan"])
    validate_phase5_render_result(result["phase5_render_result"])
    validate_phase5_5_assemble_result(result["phase5_5_assemble_result"])
    
    # Assert inputs are preserved
    assert result["phase1_story"]["goal"] == "เพิ่มผู้ติดตาม"
    assert result["phase1_story"]["product"] == "Social Media Tool"
    assert result["phase1_story"]["audience"] == "นักสร้างคอนเทนต์"
    assert result["phase1_story"]["platform"] == "TikTok"


if __name__ == "__main__":
    # Run tests directly
    print("=" * 60)
    print("Running End-to-End Regression Tests")
    print("=" * 60)
    print()
    
    try:
        print("Test 1: test_end_to_end_pipeline")
        test_end_to_end_pipeline()
        print("✓ PASSED")
        print()
        
        print("Test 2: test_end_to_end_pipeline_custom_inputs")
        test_end_to_end_pipeline_custom_inputs()
        print("✓ PASSED")
        print()
        
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

