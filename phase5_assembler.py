"""
Phase 5.5: Video Assembler

Input: list ของ segment video files
Output: final video file (mock path ได้)

Features:
- Stitch video segments together
- Retry support for failed segments
"""

from typing import List, Optional, Dict, Any, Callable
import os
from datetime import datetime
import uuid


def mock_video_stitch(segment_paths: List[str], output_path: Optional[str] = None) -> str:
    """
    Mock function สำหรับ stitch video segments
    
    ในอนาคตจะแทนที่ด้วย library จริง (เช่น moviepy, ffmpeg)
    
    Args:
        segment_paths: List of segment video file paths
        output_path: Optional output path (ถ้าไม่ระบุจะสร้าง path ใหม่)
    
    Returns:
        Path ของ final video file (mock)
    """
    # Mock: สร้าง output path ถ้าไม่ได้ระบุ
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_path = f"output/final_video_{timestamp}_{unique_id}.mp4"
    
    # Mock: ตรวจสอบว่า segment files มีอยู่จริง (ถ้าเป็น mock path ก็ skip)
    # ใน production จะต้องตรวจสอบจริง
    
    # Mock: simulate stitching process
    # ใน production จะใช้ video library จริง เช่น:
    # - moviepy: VideoFileClip.concatenate_videoclips()
    # - ffmpeg: subprocess call
    
    return output_path


def assemble_video(segment_paths: List[str], output_path: Optional[str] = None, retry_failed: bool = True, max_retries: int = 3) -> Dict[str, Any]:
    """
    ประกอบ video segments เป็น final video file
    
    Args:
        segment_paths: List of segment video file paths
        output_path: Optional output path สำหรับ final video
        retry_failed: เปิดใช้ retry สำหรับ segment ที่ล้มเหลว (default: True)
        max_retries: จำนวนครั้งสูงสุดในการ retry (default: 3)
    
    Returns:
        Dictionary ที่มี:
        - success: bool
        - output_path: str (path ของ final video file)
        - failed_segments: List[int] (indices ของ segments ที่ล้มเหลว)
        - retry_count: int (จำนวนครั้งที่ retry)
    """
    if not segment_paths:
        raise ValueError("segment_paths cannot be empty")
    
    failed_segments = []
    retry_count = 0
    valid_segments = []
    
    # ตรวจสอบ segments ที่มีอยู่
    for idx, segment_path in enumerate(segment_paths):
        # Mock: ตรวจสอบว่า file มีอยู่จริง
        # ใน production จะใช้ os.path.exists() หรือตรวจสอบจาก segment renderer
        # ตอนนี้ mock ว่า files มีครบ (หรือสามารถ mock failed segments ได้)
        if segment_path and len(segment_path) > 0:
            valid_segments.append(segment_path)
        else:
            failed_segments.append(idx)
    
    # ถ้ามี segment ที่ล้มเหลวและเปิด retry
    if retry_failed and failed_segments and retry_count < max_retries:
        # Mock: retry logic สำหรับ failed segments
        # ใน production จะต้อง:
        # 1. เรียก segment renderer ใหม่สำหรับ segment ที่ล้มเหลว
        # 2. ตรวจสอบว่า render สำเร็จ
        # 3. เพิ่ม retry_count
        retry_count += 1
        
        # Mock: หลังจาก retry สมมติว่าได้ segments มาใหม่
        # ใน production จะต้องอัพเดท valid_segments และ failed_segments
    
    # ถ้ายังมี failed segments หลัง retry แล้ว
    # ตอนนี้จะยัง stitch ต่อด้วย valid segments (หรือจะ fail ก็ได้ ขึ้นอยู่กับ requirement)
    
    # Stitch video segments
    try:
        final_path = mock_video_stitch(valid_segments, output_path)
        
        result = {
            "success": len(failed_segments) == 0,
            "output_path": final_path,
            "failed_segments": failed_segments,
            "retry_count": retry_count,
            "total_segments": len(segment_paths),
            "successful_segments": len(valid_segments)
        }
        
        return result
        
    except Exception as e:
        # Handle stitching error
        return {
            "success": False,
            "output_path": None,
            "failed_segments": failed_segments + list(range(len(valid_segments), len(segment_paths))),
            "retry_count": retry_count,
            "total_segments": len(segment_paths),
            "successful_segments": len(valid_segments),
            "error": str(e)
        }


def retry_segment(segment_index: int, segment_paths: List[str], render_segment_fn: Optional[Callable[[int], str]] = None) -> Optional[str]:
    """
    Retry render segment ที่ล้มเหลว
    
    Args:
        segment_index: Index ของ segment ที่ต้องการ retry
        segment_paths: List of segment paths (จะถูก update ถ้า retry สำเร็จ)
        render_segment_fn: Optional function สำหรับ render segment ใหม่
                          (ถ้าไม่ระบุจะ mock)
    
    Returns:
        New segment path ถ้า retry สำเร็จ, None ถ้าล้มเหลว
    """
    if segment_index < 0 or segment_index >= len(segment_paths):
        return None
    
    # Mock: retry render segment
    # ใน production จะต้องเรียก render_segment_fn หรือ segment renderer
    
    if render_segment_fn:
        try:
            new_path = render_segment_fn(segment_index)
            # Update segment_paths
            segment_paths[segment_index] = new_path
            return new_path
        except Exception:
            return None
    else:
        # Mock: สมมติว่า retry สำเร็จ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mock_path = f"output/segment_{segment_index}_retry_{timestamp}.mp4"
        segment_paths[segment_index] = mock_path
        return mock_path


def assemble_video_with_retry(segment_paths: List[str], output_path: Optional[str] = None, max_retries: int = 3, render_segment_fn: Optional[Callable[[int], str]] = None) -> Dict[str, Any]:
    """
    ประกอบ video segments พร้อม retry สำหรับ segments ที่ล้มเหลว
    
    Args:
        segment_paths: List of segment video file paths
        output_path: Optional output path สำหรับ final video
        max_retries: จำนวนครั้งสูงสุดในการ retry
        render_segment_fn: Optional function สำหรับ render segment ใหม่
    
    Returns:
        Dictionary ที่มีผลลัพธ์การ assemble
    """
    current_segments = segment_paths.copy()
    failed_segments = []
    retry_count = 0
    
    # ตรวจสอบ segments ครั้งแรก
    for idx, segment_path in enumerate(current_segments):
        # Mock: ตรวจสอบว่า file มีอยู่จริง
        # ใน production จะใช้การตรวจสอบที่เหมาะสม
        if not segment_path or not os.path.exists(segment_path):
            failed_segments.append(idx)
    
    # Retry failed segments
    while retry_count < max_retries and failed_segments:
        retry_count += 1
        retried_segments = []
        
        for idx in failed_segments[:]:  # Copy list to iterate safely
            new_path = retry_segment(idx, current_segments, render_segment_fn)
            if new_path:
                failed_segments.remove(idx)
                retried_segments.append(idx)
        
        # ถ้าไม่มี segment ที่ retry สำเร็จเลย ให้หยุด
        if not retried_segments:
            break
    
    # Stitch final video
    result = assemble_video(
        current_segments,
        output_path,
        retry_failed=False,  # ไม่ต้อง retry อีกเพราะทำไปแล้ว
        max_retries=0
    )
    
    # Update retry_count
    result["retry_count"] = retry_count
    
    return result


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Mock segment paths
    mock_segments = [
        "output/segment_0.mp4",
        "output/segment_1.mp4",
        "output/segment_2.mp4",
        "output/segment_3.mp4"
    ]
    
    # Test: assemble video
    print("=== Test: Assemble Video ===")
    result = assemble_video(mock_segments, output_path="output/final_test.mp4")
    print(f"Success: {result['success']}")
    print(f"Output Path: {result['output_path']}")
    print(f"Failed Segments: {result['failed_segments']}")
    print(f"Retry Count: {result['retry_count']}")
    print()
    
    # Test: assemble with retry
    print("=== Test: Assemble Video with Retry ===")
    mock_segments_with_failures = [
        "output/segment_0.mp4",
        "",  # Failed segment
        "output/segment_2.mp4",
        None  # Failed segment
    ]
    
    result_with_retry = assemble_video_with_retry(
        mock_segments_with_failures,
        output_path="output/final_test_retry.mp4",
        max_retries=3
    )
    print(f"Success: {result_with_retry['success']}")
    print(f"Output Path: {result_with_retry['output_path']}")
    print(f"Failed Segments: {result_with_retry['failed_segments']}")
    print(f"Retry Count: {result_with_retry['retry_count']}")
    print(f"Successful Segments: {result_with_retry['successful_segments']}/{result_with_retry['total_segments']}")

