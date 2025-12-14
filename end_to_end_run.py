"""
End-to-End Mock Run
===================

Script สำหรับรันทุก Phase ตั้งแต่ Phase 1 → Phase 5.5 (Video Assembler)

Flow:
1. Phase 1: Generate Story
2. Phase 2: Generate Characters & Locations
3. Phase 3: Build Storyboard
4. Phase 4: Generate Video Plan
5. Phase 5: Render Segments (Mock)
6. Phase 5.5: Assemble Final Video (Mock)

Output:
- จำนวน segments
- segment ids
- final video path
"""

import json
import sys
import io
from typing import Dict, List, Any

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import all phases
from story_engine import generate_story
from phase2_generator import generate_phase2_output
from phase3_storyboard import build_storyboard_from_phase2
from phase4_video_plan import generate_video_plan
from phase5_segment_renderer import render_segments_from_video_plan
from phase5_assembler import assemble_video

# Import validators
from validators.schema_validators import (
    validate_phase1_story,
    validate_phase2_output,
    validate_phase3_storyboard,
    validate_phase4_video_plan,
    validate_phase5_render_result,
    validate_phase5_5_assemble_result,
    validate_phase2_input,
    validate_phase3_input,
    validate_phase4_input,
    validate_phase5_input,
    validate_phase5_5_input,
    ValidationError,
    PhaseOrderError
)


def run_end_to_end(
    goal: str = "ขายคอร์สออนไลน์",
    product: str = "AI Creator Tool",
    audience: str = "มือใหม่ ไม่เก่งเทค",
    platform: str = "Facebook Reel",
    selected_character_id: int = 1,
    selected_location_id: int = 1,
    num_characters: int = 4,
    num_locations: int = 4,
    output_path: str = None
) -> Dict[str, Any]:
    """
    รัน End-to-End Mock Run ตั้งแต่ Phase 1 → Phase 5.5
    
    Args:
        goal: เป้าหมาย (default: "ขายคอร์สออนไลน์")
        product: ชื่อสินค้า/บริการ (default: "AI Creator Tool")
        audience: กลุ่มเป้าหมาย (default: "มือใหม่ ไม่เก่งเทค")
        platform: แพลตฟอร์มที่ใช้ (default: "Facebook Reel")
        selected_character_id: ID ของ character ที่เลือก (default: 1)
        selected_location_id: ID ของ location ที่เลือก (default: 1)
        num_characters: จำนวน characters ที่จะ generate (default: 4)
        num_locations: จำนวน locations ที่จะ generate (default: 4)
        output_path: Path สำหรับ final video (optional)
    
    Returns:
        Dictionary ที่มีผลลัพธ์ทั้งหมด:
        - phase1_story: Story object
        - phase2_output: Phase 2 output
        - phase3_storyboard: Storyboard object
        - phase4_video_plan: Video plan object
        - phase5_render_result: Render result
        - phase5_5_assemble_result: Assemble result
        - summary: สรุปผลลัพธ์
    """
    print("=" * 60)
    print("End-to-End Mock Run")
    print("=" * 60)
    print()
    
    # ==================== Phase 1: Generate Story ====================
    print("[Phase 1] Generating Story...")
    print(f"  Goal: {goal}")
    print(f"  Product: {product}")
    print(f"  Audience: {audience}")
    print(f"  Platform: {platform}")
    print()
    
    phase1_story = generate_story(goal, product, audience, platform)
    
    # Validate Phase 1 output
    is_valid, error_msg = validate_phase1_story(phase1_story)
    if not is_valid:
        raise ValidationError("Phase 1", f"Output validation failed: {error_msg}")
    
    print(f"✓ Phase 1 Complete: {len(phase1_story.get('scenes', []))} scenes")
    print()
    
    # ==================== Phase 2: Generate Characters & Locations ====================
    print("[Phase 2] Generating Characters & Locations...")
    print(f"  Characters: {num_characters}")
    print(f"  Locations: {num_locations}")
    print()
    
    # Validate Phase 1 output before Phase 2
    is_valid, error_msg = validate_phase2_input(phase1_story)
    if not is_valid:
        raise PhaseOrderError("Phase 2", "Phase 1 output invalid: " + error_msg)
    
    phase2_output = generate_phase2_output(
        phase1_story,
        num_characters=num_characters,
        num_locations=num_locations
    )
    
    # Validate Phase 2 output
    is_valid, error_msg = validate_phase2_output(phase2_output)
    if not is_valid:
        raise ValidationError("Phase 2", f"Output validation failed: {error_msg}")
    
    print(f"✓ Phase 2 Complete: {len(phase2_output.get('characters', []))} characters, {len(phase2_output.get('locations', []))} locations")
    print()
    
    # ==================== Phase 3: Build Storyboard ====================
    print("[Phase 3] Building Storyboard...")
    print(f"  Selected Character ID: {selected_character_id}")
    print(f"  Selected Location ID: {selected_location_id}")
    print()
    
    # Validate Phase 2 output before Phase 3
    is_valid, error_msg = validate_phase3_input(phase2_output)
    if not is_valid:
        raise PhaseOrderError("Phase 3", "Phase 2 output invalid: " + error_msg)
    
    phase3_storyboard = build_storyboard_from_phase2(
        phase2_output,
        selected_character_id=selected_character_id,
        selected_location_id=selected_location_id
    )
    
    # Validate Phase 3 output
    is_valid, error_msg = validate_phase3_storyboard(phase3_storyboard)
    if not is_valid:
        raise ValidationError("Phase 3", f"Output validation failed: {error_msg}")
    
    # นับ keyframes ทั้งหมด
    total_keyframes = sum(
        len(scene.get('keyframes', []))
        for scene in phase3_storyboard.get('scenes', [])
    )
    print(f"✓ Phase 3 Complete: {len(phase3_storyboard.get('scenes', []))} scenes, {total_keyframes} keyframes")
    print()
    
    # ==================== Phase 4: Generate Video Plan ====================
    print("[Phase 4] Generating Video Plan...")
    print()
    
    # Validate Phase 3 output before Phase 4
    is_valid, error_msg = validate_phase4_input(phase3_storyboard)
    if not is_valid:
        raise PhaseOrderError("Phase 4", "Phase 3 output invalid: " + error_msg)
    
    phase4_video_plan = generate_video_plan(phase3_storyboard)
    
    # Validate Phase 4 output
    is_valid, error_msg = validate_phase4_video_plan(phase4_video_plan)
    if not is_valid:
        raise ValidationError("Phase 4", f"Output validation failed: {error_msg}")
    
    segment_count = phase4_video_plan.get('segment_count', 0)
    total_duration = phase4_video_plan.get('total_duration', 0)
    
    print(f"✓ Phase 4 Complete: {segment_count} segments, {total_duration}s total duration")
    print()
    
    # ==================== Phase 5: Render Segments ====================
    print("[Phase 5] Rendering Segments (Mock)...")
    print()
    
    # Validate Phase 4 output before Phase 5
    is_valid, error_msg = validate_phase5_input(phase4_video_plan)
    if not is_valid:
        raise PhaseOrderError("Phase 5", "Phase 4 output invalid: " + error_msg)
    
    phase5_render_result = render_segments_from_video_plan(
        phase4_video_plan,
        story_context=phase1_story
    )
    
    # Validate Phase 5 output
    is_valid, error_msg = validate_phase5_render_result(phase5_render_result)
    if not is_valid:
        raise ValidationError("Phase 5", f"Output validation failed: {error_msg}")
    
    successful_segments = phase5_render_result.get('successful_segments', 0)
    total_segments = phase5_render_result.get('total_segments', 0)
    
    print(f"✓ Phase 5 Complete: {successful_segments}/{total_segments} segments rendered")
    print()
    
    # ==================== Phase 5.5: Assemble Final Video ====================
    print("[Phase 5.5] Assembling Final Video (Mock)...")
    print()
    
    # Validate Phase 5 output before Phase 5.5
    is_valid, error_msg = validate_phase5_5_input(phase5_render_result)
    if not is_valid:
        raise PhaseOrderError("Phase 5.5", "Phase 5 output invalid: " + error_msg)
    
    # รวบรวม video paths จาก rendered segments
    segment_paths = []
    for rendered_segment in phase5_render_result.get('rendered_segments', []):
        if rendered_segment.get('success'):
            segment_paths.append(rendered_segment.get('video_path'))
    
    if not segment_paths:
        raise ValidationError("Phase 5.5", "No successful segments to assemble")
    
    phase5_5_assemble_result = assemble_video(
        segment_paths,
        output_path=output_path,
        retry_failed=False
    )
    
    # Validate Phase 5.5 output
    is_valid, error_msg = validate_phase5_5_assemble_result(phase5_5_assemble_result)
    if not is_valid:
        raise ValidationError("Phase 5.5", f"Output validation failed: {error_msg}")
    
    print(f"✓ Phase 5.5 Complete: Final video assembled")
    print()
    
    # ==================== Summary ====================
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    # รวบรวม segment IDs
    segment_ids = [seg.get('id') for seg in phase4_video_plan.get('segments', [])]
    
    summary = {
        "total_segments": segment_count,
        "segment_ids": segment_ids,
        "final_video_path": phase5_5_assemble_result.get('output_path'),
        "total_duration": total_duration,
        "successful_segments": successful_segments,
        "failed_segments": phase5_render_result.get('failed_segments', []),
        "assemble_success": phase5_5_assemble_result.get('success', False)
    }
    
    print(f"Total Segments: {summary['total_segments']}")
    print(f"Segment IDs: {summary['segment_ids']}")
    print(f"Final Video Path: {summary['final_video_path']}")
    print(f"Total Duration: {summary['total_duration']}s")
    print(f"Successful Segments: {summary['successful_segments']}/{summary['total_segments']}")
    if summary['failed_segments']:
        print(f"Failed Segments: {summary['failed_segments']}")
    print(f"Assemble Success: {summary['assemble_success']}")
    print()
    
    return {
        "phase1_story": phase1_story,
        "phase2_output": phase2_output,
        "phase3_storyboard": phase3_storyboard,
        "phase4_video_plan": phase4_video_plan,
        "phase5_render_result": phase5_render_result,
        "phase5_5_assemble_result": phase5_5_assemble_result,
        "summary": summary
    }


if __name__ == "__main__":
    # Run End-to-End Mock Run
    try:
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
        
        print("=" * 60)
        print("End-to-End Mock Run Completed Successfully!")
        print("=" * 60)
        
    except ValidationError as e:
        print()
        print("=" * 60)
        print("Validation Error")
        print("=" * 60)
        print(f"Phase: {e.phase}")
        print(f"Error: {e.message}")
        print()
        print("This indicates a schema mismatch or missing required fields.")
        print("Please check the phase output and ensure it matches the expected schema.")
        sys.exit(1)
    except PhaseOrderError as e:
        print()
        print("=" * 60)
        print("Phase Order Error")
        print("=" * 60)
        print(f"Phase: {e.phase}")
        print(f"Error: {e.message}")
        print()
        print("This indicates that a required previous phase was not completed successfully.")
        print("Please ensure all previous phases complete without errors.")
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print("Error occurred during End-to-End Mock Run")
        print("=" * 60)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

