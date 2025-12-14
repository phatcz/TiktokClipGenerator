import json
from typing import Dict, List, Any, Optional
import random
import os
import requests
import base64
from datetime import datetime
import uuid


def mock_google_image_generation(prompt: str) -> str:
    """
    Mock API สำหรับ Google Image Generation
    ใช้เป็น fallback เมื่อ Vertex AI API ล้มเหลว
    
    Args:
        prompt: คำอธิบายภาพที่ต้องการสร้าง
        
    Returns:
        URL ของภาพ (mock)
    """
    # Mock: สร้าง URL จำลอง
    image_id = hash(prompt) % 1000000
    return f"https://mock-images.google.com/generated/{image_id}.jpg"


def generate_image_with_vertex(prompt: str) -> str:
    """
    สร้างภาพด้วย Google Vertex AI Imagen API
    
    Args:
        prompt: คำอธิบายภาพที่ต้องการสร้าง
        
    Returns:
        URL หรือ path ของภาพที่สร้างได้
        
    Note:
        - ใช้ environment variables: VERTEX_API_KEY, VERTEX_PROJECT_ID, VERTEX_LOCATION
        - Fallback เป็น mock ถ้า API ล้มเหลว
    """
    # อ่าน environment variables
    api_key = os.getenv("VERTEX_API_KEY")
    project_id = os.getenv("VERTEX_PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    
    # ตรวจสอบว่ามี API key หรือไม่
    if not api_key or not project_id:
        print(f"[Phase 2] Warning: VERTEX_API_KEY or VERTEX_PROJECT_ID not set, using mock")
        return mock_google_image_generation(prompt)
    
    try:
        # Vertex AI Imagen API endpoint
        # Model name format: imagen-3.0-generate-001 or imagen-4.0-generate-001
        # Try imagen-3.0 first (more stable)
        model_name = "imagen-3.0-generate-001"
        endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:predict"
        
        # Request payload for Vertex AI Imagen
        # Format according to Vertex AI Imagen API specification
        payload = {
            "instances": [
                {
                    "prompt": prompt
                }
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1",
                "safetyFilterLevel": "block_some",
                "personGeneration": "allow_all"
            }
        }
        
        # Vertex AI uses OAuth2 Bearer token, not API key directly
        # API key format provided might need to be used with OAuth2 flow
        # Try Bearer token first (most common for Vertex AI)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # เรียก API
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=60  # 60 seconds timeout
        )
        
        # ถ้า Bearer token ไม่ได้ผล ลองใช้ API key as query parameter
        if response.status_code == 401 or response.status_code == 403:
            endpoint_with_key = f"{endpoint}?key={api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(
                endpoint_with_key,
                json=payload,
                headers=headers,
                timeout=60
            )
        
        # ตรวจสอบ response
        if response.status_code == 200:
            result = response.json()
            
            # Extract image bytes base64 จาก response
            if "predictions" in result and len(result["predictions"]) > 0:
                prediction = result["predictions"][0]
                
                # Vertex AI Imagen returns base64 encoded image
                if "bytesBase64Encoded" in prediction:
                    # Decode base64 image
                    image_bytes = base64.b64decode(prediction["bytesBase64Encoded"])
                    
                    # สร้าง output directory ถ้ายังไม่มี
                    output_dir = "output/images"
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # สร้าง unique filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"vertex_image_{timestamp}_{unique_id}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Save image
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                    
                    print(f"[Phase 2] Successfully generated image with Vertex AI: {filepath}")
                    return filepath
                elif "gcsUri" in prediction:
                    # ถ้า API return GCS URI
                    print(f"[Phase 2] Successfully generated image with Vertex AI (GCS): {prediction['gcsUri']}")
                    return prediction["gcsUri"]
            
            # ถ้า response format ไม่ตรงที่คาดหวัง
            print(f"[Phase 2] Warning: Unexpected response format from Vertex AI, using mock")
            return mock_google_image_generation(prompt)
        else:
            # API error - print error message for debugging (but not API key)
            error_msg = ""
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = str(error_data["error"]).replace(api_key, "***REDACTED***")
                print(f"[Phase 2] Warning: Vertex AI API error (status {response.status_code}): {error_msg}")
            except:
                print(f"[Phase 2] Warning: Vertex AI API error (status {response.status_code}), using mock")
            return mock_google_image_generation(prompt)
            
    except requests.exceptions.Timeout:
        print(f"[Phase 2] Warning: Vertex AI API timeout, using mock")
        return mock_google_image_generation(prompt)
    except requests.exceptions.RequestException as e:
        print(f"[Phase 2] Warning: Vertex AI API request failed, using mock")
        # ไม่ print exception details ที่อาจมี sensitive info
        return mock_google_image_generation(prompt)
    except Exception as e:
        print(f"[Phase 2] Warning: Unexpected error calling Vertex AI, using mock")
        # ไม่ print exception details
        return mock_google_image_generation(prompt)


def generate_character_candidates(story: Dict[str, Any], num_candidates: int = 4) -> List[Dict[str, Any]]:
    """
    สร้าง character candidates 3-5 แบบ จาก story context
    
    Args:
        story: Story object จาก Phase 1
        num_candidates: จำนวน candidates ที่ต้องการ (default: 4)
        
    Returns:
        List ของ character objects
    """
    goal = story.get("goal", "")
    product = story.get("product", "")
    audience = story.get("audience", "")
    platform = story.get("platform", "")
    
    # Rule-based logic สำหรับสร้าง character candidates
    characters = []
    
    # Character styles ตาม audience และ goal
    character_templates = [
        {
            "name": "ผู้เชี่ยวชาญ",
            "description": f"ผู้เชี่ยวชาญที่เข้าใจปัญหาและแนะนำ{product}",
            "style": "professional",
            "age_range": "30-45",
            "personality": "confident, knowledgeable"
        },
        {
            "name": "ผู้ใช้จริง",
            "description": f"ตัวแทนของ{audience}ที่ประสบความสำเร็จด้วย{product}",
            "style": "relatable",
            "age_range": "25-40",
            "personality": "friendly, authentic"
        },
        {
            "name": "ผู้เริ่มต้น",
            "description": f"คนที่เพิ่งเริ่มต้นและกำลังเรียนรู้เกี่ยวกับ{product}",
            "style": "approachable",
            "age_range": "20-35",
            "personality": "curious, eager"
        },
        {
            "name": "ผู้สร้างคอนเทนต์",
            "description": f"ผู้สร้างคอนเทนต์ที่ใช้{product}บน{platform}",
            "style": "creative",
            "age_range": "22-38",
            "personality": "innovative, energetic"
        },
        {
            "name": "ผู้สอน",
            "description": f"ผู้สอนที่ช่วยให้{audience}เข้าใจ{product}",
            "style": "educational",
            "age_range": "28-42",
            "personality": "patient, clear"
        }
    ]
    
    # เลือก candidates ตาม num_candidates
    selected_templates = character_templates[:num_candidates]
    
    for idx, template in enumerate(selected_templates, start=1):
        # สร้าง prompt สำหรับ image generation
        image_prompt = f"{template['name']}, {template['style']} style, age {template['age_range']}, {template['personality']}, suitable for {audience} audience"
        
        character = {
            "id": idx,
            "name": template["name"],
            "description": template["description"],
            "style": template["style"],
            "age_range": template["age_range"],
            "personality": template["personality"],
            "image_url": generate_image_with_vertex(image_prompt),
            "image_prompt": image_prompt
        }
        characters.append(character)
    
    return characters


def generate_location_candidates(story: Dict[str, Any], num_candidates: int = 4) -> List[Dict[str, Any]]:
    """
    สร้าง location/background candidates 3-5 แบบ จาก story context
    
    Args:
        story: Story object จาก Phase 1
        num_candidates: จำนวน candidates ที่ต้องการ (default: 4)
        
    Returns:
        List ของ location objects
    """
    goal = story.get("goal", "")
    product = story.get("product", "")
    audience = story.get("audience", "")
    platform = story.get("platform", "")
    scenes = story.get("scenes", [])
    
    # Rule-based logic สำหรับสร้าง location candidates
    locations = []
    
    # Location templates ตาม scene purposes
    location_templates = [
        {
            "name": "สถานที่ทำงาน",
            "description": "สถานที่ทำงานที่สะท้อนปัญหาและความท้าทาย",
            "scene_purposes": ["hook", "conflict"],
            "style": "modern office",
            "mood": "professional, challenging"
        },
        {
            "name": "บ้าน/พื้นที่ส่วนตัว",
            "description": "พื้นที่ส่วนตัวที่สะท้อนความสะดวกสบายและความเป็นส่วนตัว",
            "scene_purposes": ["reveal", "close"],
            "style": "cozy home",
            "mood": "comfortable, personal"
        },
        {
            "name": "สตูดิโอ",
            "description": "สตูดิโอสำหรับสร้างคอนเทนต์และทำงานสร้างสรรค์",
            "scene_purposes": ["reveal", "close"],
            "style": "creative studio",
            "mood": "creative, inspiring"
        },
        {
            "name": "พื้นที่สาธารณะ",
            "description": "พื้นที่สาธารณะที่สะท้อนการใช้งานจริง",
            "scene_purposes": ["hook", "conflict", "reveal"],
            "style": "public space",
            "mood": "realistic, relatable"
        },
        {
            "name": "พื้นที่ดิจิทัล",
            "description": "พื้นหลังที่แสดงผลลัพธ์บนแพลตฟอร์มดิจิทัล",
            "scene_purposes": ["reveal", "close"],
            "style": "digital interface",
            "mood": "modern, tech-forward"
        }
    ]
    
    # เลือก candidates ตาม num_candidates
    selected_templates = location_templates[:num_candidates]
    
    for idx, template in enumerate(selected_templates, start=1):
        # สร้าง prompt สำหรับ image generation
        image_prompt = f"{template['name']}, {template['style']} style, {template['mood']}, suitable for {platform} content, {audience} audience"
        
        location = {
            "id": idx,
            "name": template["name"],
            "description": template["description"],
            "scene_purposes": template["scene_purposes"],
            "style": template["style"],
            "mood": template["mood"],
            "image_url": generate_image_with_vertex(image_prompt),
            "image_prompt": image_prompt
        }
        locations.append(location)
    
    return locations


def generate_phase2_output(story: Dict[str, Any], num_characters: int = 4, num_locations: int = 4, selected_character_id: Optional[int] = None, selected_location_id: Optional[int] = None) -> Dict[str, Any]:
    """
    สร้าง Phase 2 output ที่มี characters และ locations candidates
    
    Args:
        story: Story object จาก Phase 1
        num_characters: จำนวน character candidates (default: 4)
        num_locations: จำนวน location candidates (default: 4)
        selected_character_id: ID ของ character ที่เลือก (ถ้าไม่ระบุ default = 1)
        selected_location_id: ID ของ location ที่เลือก (ถ้าไม่ระบุ default = 1)
        
    Returns:
        Dictionary ที่มีโครงสร้าง Phase 2 output
    """
    # Validate input
    if not isinstance(story, dict):
        raise ValueError("story must be a dictionary")
    
    required_fields = ["goal", "product", "audience", "platform", "scenes"]
    for field in required_fields:
        if field not in story:
            raise ValueError(f"story must contain '{field}' field")
    
    # Generate candidates
    characters = generate_character_candidates(story, num_characters)
    locations = generate_location_candidates(story, num_locations)
    
    # ตั้งค่า default selection = ตัวแรก (id = 1)
    if selected_character_id is None:
        selected_character_id = 1 if characters else None
    
    if selected_location_id is None:
        selected_location_id = 1 if locations else None
    
    # Validate selection IDs
    if selected_character_id is not None:
        character_ids = [char.get("id") for char in characters]
        if selected_character_id not in character_ids:
            raise ValueError(f"selected_character_id {selected_character_id} not found in characters")
    
    if selected_location_id is not None:
        location_ids = [loc.get("id") for loc in locations]
        if selected_location_id not in location_ids:
            raise ValueError(f"selected_location_id {selected_location_id} not found in locations")
    
    # สร้าง Phase 2 output
    phase2_output = {
        "story": story,  # เก็บ story จาก Phase 1 ไว้ด้วย
        "characters": characters,
        "locations": locations,
        "selection": {
            "selected_character_id": selected_character_id,
            "selected_location_id": selected_location_id
        }
    }
    
    return phase2_output


def generate_phase2_json(story_json: str, num_characters: int = 4, num_locations: int = 4, selected_character_id: Optional[int] = None, selected_location_id: Optional[int] = None) -> str:
    """
    สร้าง Phase 2 JSON string จาก story JSON string
    
    Args:
        story_json: JSON string ของ Story จาก Phase 1
        num_characters: จำนวน character candidates (default: 4)
        num_locations: จำนวน location candidates (default: 4)
        selected_character_id: ID ของ character ที่เลือก (ถ้าไม่ระบุ default = 1)
        selected_location_id: ID ของ location ที่เลือก (ถ้าไม่ระบุ default = 1)
        
    Returns:
        JSON string ของ Phase 2 output
    """
    story = json.loads(story_json)
    phase2_output = generate_phase2_output(story, num_characters, num_locations, selected_character_id, selected_location_id)
    return json.dumps(phase2_output, ensure_ascii=False, indent=2)


def update_selection(phase2_output: Dict[str, Any], selected_character_id: Optional[int] = None, selected_location_id: Optional[int] = None) -> Dict[str, Any]:
    """
    อัปเดต selection ใน Phase 2 output
    
    Args:
        phase2_output: Phase 2 output ที่มี characters, locations
        selected_character_id: ID ของ character ที่เลือก (ถ้าไม่ระบุจะไม่เปลี่ยน)
        selected_location_id: ID ของ location ที่เลือก (ถ้าไม่ระบุจะไม่เปลี่ยน)
        
    Returns:
        Phase 2 output ที่อัปเดต selection แล้ว
    """
    if not isinstance(phase2_output, dict):
        raise ValueError("phase2_output must be a dictionary")
    
    characters = phase2_output.get("characters", [])
    locations = phase2_output.get("locations", [])
    
    # ตรวจสอบว่า selection มีอยู่แล้วหรือไม่
    if "selection" not in phase2_output:
        phase2_output["selection"] = {}
    
    # อัปเดต selected_character_id
    if selected_character_id is not None:
        character_ids = [char.get("id") for char in characters]
        if selected_character_id not in character_ids:
            raise ValueError(f"selected_character_id {selected_character_id} not found in characters")
        phase2_output["selection"]["selected_character_id"] = selected_character_id
    
    # อัปเดต selected_location_id
    if selected_location_id is not None:
        location_ids = [loc.get("id") for loc in locations]
        if selected_location_id not in location_ids:
            raise ValueError(f"selected_location_id {selected_location_id} not found in locations")
        phase2_output["selection"]["selected_location_id"] = selected_location_id
    
    return phase2_output


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Import Phase 1
    from story_engine import generate_story
    
    # สร้าง story จาก Phase 1
    story = generate_story(
        goal="ขายคอร์สออนไลน์",
        product="AI Creator Tool",
        audience="มือใหม่ ไม่เก่งเทค",
        platform="Facebook Reel"
    )
    
    # สร้าง Phase 2 output (default selection = ตัวแรก)
    phase2_output = generate_phase2_output(story, num_characters=4, num_locations=4)
    
    print(json.dumps(phase2_output, ensure_ascii=False, indent=2))

