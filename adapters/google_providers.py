"""
Google Provider Implementations

Real provider implementations for Google Cloud services.
Currently supports:
- GoogleImageProvider: Vertex AI Imagen API for image generation

All providers implement the adapter interfaces and handle errors gracefully,
falling back to mock providers when credentials are missing or API calls fail.
"""

import os
import base64
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from .interfaces import (
    ImageProvider,
    ImageGenerationRequest,
    ImageGenerationResult,
    ProviderError,
    ProviderTimeoutError,
    ProviderQuotaExceededError,
    ProviderAuthenticationError,
    ProviderValidationError,
)


class GoogleImageProvider(ImageProvider):
    """
    Google Vertex AI Imagen provider for image generation.
    
    Uses Vertex AI Imagen API (imagen-3.0-generate-001 or imagen-4.0-generate-001).
    
    Required environment variables:
    - VERTEX_API_KEY: Google Cloud API key or OAuth2 token
    - VERTEX_PROJECT_ID: Google Cloud project ID
    - VERTEX_LOCATION: (optional) Region, defaults to "us-central1"
    
    If credentials are missing or API calls fail, the provider will raise
    exceptions that should be caught by the factory to fallback to mock.
    """
    
    def __init__(self):
        """Initialize Google Image Provider with credentials from environment."""
        self.api_key = os.getenv("VERTEX_API_KEY")
        self.project_id = os.getenv("VERTEX_PROJECT_ID")
        self.location = os.getenv("VERTEX_LOCATION", "us-central1")
        
        # Validate required credentials
        if not self.api_key or not self.project_id:
            raise ProviderAuthenticationError(
                "Missing required credentials: VERTEX_API_KEY and VERTEX_PROJECT_ID must be set"
            )
    
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate image using Google Vertex AI Imagen API.
        
        Args:
            request: Image generation request
            
        Returns:
            ImageGenerationResult with success status and image path
            
        Raises:
            ProviderAuthenticationError: If credentials are invalid
            ProviderTimeoutError: If request times out
            ProviderQuotaExceededError: If quota exceeded
            ProviderError: For other provider errors
        """
        try:
            # Build API endpoint
            model_name = "imagen-3.0-generate-001"  # Use stable version
            endpoint = (
                f"https://{self.location}-aiplatform.googleapis.com/v1/"
                f"projects/{self.project_id}/locations/{self.location}/"
                f"publishers/google/models/{model_name}:predict"
            )
            
            # Build request payload
            payload = {
                "instances": [
                    {
                        "prompt": request.prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": self._map_aspect_ratio(request.aspect_ratio),
                    "safetyFilterLevel": "block_some",
                    "personGeneration": "allow_all"
                }
            }
            
            # Add quality parameter if HD
            if request.quality == "hd":
                payload["parameters"]["quality"] = "hd"
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=60  # 60 seconds timeout
            )
            
            # Handle authentication errors
            if response.status_code == 401 or response.status_code == 403:
                # Try API key as query parameter (alternative auth method)
                endpoint_with_key = f"{endpoint}?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    endpoint_with_key,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 401 or response.status_code == 403:
                    raise ProviderAuthenticationError(
                        f"Authentication failed: Invalid API key or insufficient permissions"
                    )
            
            # Handle quota/rate limit errors
            if response.status_code == 429:
                raise ProviderQuotaExceededError(
                    "Rate limit or quota exceeded for Vertex AI Imagen API"
                )
            
            # Handle timeout (if response took too long)
            if response.status_code == 504:
                raise ProviderTimeoutError(
                    "Request to Vertex AI Imagen API timed out"
                )
            
            # Handle other HTTP errors
            if response.status_code != 200:
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = str(error_data["error"])
                except:
                    error_msg = f"HTTP {response.status_code}"
                
                raise ProviderError(
                    f"Vertex AI Imagen API error: {error_msg}"
                )
            
            # Parse successful response
            result = response.json()
            
            if "predictions" not in result or len(result["predictions"]) == 0:
                raise ProviderError(
                    "Vertex AI Imagen API returned empty predictions"
                )
            
            prediction = result["predictions"][0]
            
            # Extract image data
            image_bytes = None
            image_url = None
            
            if "bytesBase64Encoded" in prediction:
                # Decode base64 image
                image_bytes = base64.b64decode(prediction["bytesBase64Encoded"])
            elif "gcsUri" in prediction:
                # GCS URI (cloud storage)
                image_url = prediction["gcsUri"]
            else:
                raise ProviderError(
                    "Vertex AI Imagen API response missing image data"
                )
            
            # Save image to local file if we have bytes
            image_path = None
            if image_bytes:
                output_dir = "output/images"
                os.makedirs(output_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"vertex_image_{timestamp}_{unique_id}.jpg"
                image_path = os.path.join(output_dir, filename)
                
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
            
            return ImageGenerationResult(
                success=True,
                image_url=image_url,
                image_path=image_path,
                metadata={
                    "provider": "google",
                    "model": model_name,
                    "prompt": request.prompt,
                    "width": request.width,
                    "height": request.height,
                    "aspect_ratio": request.aspect_ratio,
                    "quality": request.quality,
                    "generated_at": datetime.now().isoformat(),
                }
            )
            
        except requests.exceptions.Timeout:
            raise ProviderTimeoutError(
                "Request to Vertex AI Imagen API timed out"
            )
        except requests.exceptions.RequestException as e:
            raise ProviderError(
                f"Network error calling Vertex AI Imagen API: {str(e)}"
            )
        except (ProviderError, ProviderTimeoutError, ProviderQuotaExceededError, 
                ProviderAuthenticationError, ProviderValidationError):
            # Re-raise provider-specific errors
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise ProviderError(
                f"Unexpected error in GoogleImageProvider: {str(e)}"
            )
    
    def _map_aspect_ratio(self, aspect_ratio: str) -> str:
        """
        Map adapter aspect ratio to Vertex AI format.
        
        Vertex AI supports: "1:1", "9:16", "16:9", "4:3", "3:4"
        """
        # Normalize aspect ratio string
        aspect_ratio = aspect_ratio.strip().lower()
        
        # Direct mapping for common ratios
        mapping = {
            "1:1": "1:1",
            "9:16": "9:16",
            "16:9": "16:9",
            "4:3": "4:3",
            "3:4": "3:4",
        }
        
        return mapping.get(aspect_ratio, "1:1")  # Default to 1:1 if unknown


__all__ = [
    "GoogleImageProvider",
]
