"""Image generation and Cloud Storage upload tool for SoundCheck."""

import re
import uuid
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# IMPORTANT: Hardcoded constants as required to ensure correct project and bucket targeting
PROJECT_ID = "qwiklabs-gcp-04-9b2fabbcbad5"
BUCKET_NAME = "soundcheck-media-9b2fabbcbad5"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
LOCATION = "global"


async def generate_component_diagram(
    item_description: str,
    item_name: str = "component_diagram",
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """Generate a technical exploded diagram or schematic illustration for an appliance part,
    save it as an artifact in the session, and upload the image bytes directly to public Cloud Storage.

    Args:
        item_description: Detailed description of the appliance component or repair diagram to illustrate
                          (e.g., 'Exploded view schematic of a washing machine drive belt and motor pulley',
                          'Cross-section diagram of a refrigerator evaporator fan motor in the freezer').
        item_name: Short identifier or name of the component for the filename (e.g., 'washer_drive_belt').
        tool_context: ADK ToolContext automatically injected at runtime.

    Returns:
        A dictionary containing the public HTTPS URL, artifact filename, and status.
    """
    # 1. Initialize Vertex AI GenAI Client in global location
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    prompt = (
        f"Clean technical engineering schematic, exploded parts diagram, and mechanical illustration of {item_description}. "
        "High resolution, crisp lines, professional repair manual style with clear component outlines."
    )

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
    except Exception as e:
        return {"error": f"Failed to generate image with {IMAGE_MODEL}: {e}"}

    # Extract image bytes and mime type from response
    image_bytes = None
    mime_type = "image/jpeg"
    for part in response.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            if part.inline_data.mime_type:
                mime_type = part.inline_data.mime_type
            break

    if not image_bytes:
        return {"error": "Model did not return any image data."}

    # Format unique object filename
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", item_name).lower().strip("_")
    ext = "jpg" if "jpeg" in mime_type else "png"
    filename = f"{safe_name}_{uuid.uuid4().hex[:8]}.{ext}"

    # (1) Save artifact with tool_context.save_artifact for Playground Artifacts panel
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        except Exception as e:
            # Fallback gracefully if artifact storage service is unavailable
            print(f"Notice: tool_context.save_artifact skipped: {e}")

    # (2) Upload image bytes directly into the public Cloud Storage bucket (in-memory, no local file)
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    except Exception as e:
        return {"error": f"Failed to upload image to Cloud Storage bucket {BUCKET_NAME}: {e}"}

    return {
        "status": "success",
        "public_url": public_url,
        "filename": filename,
        "item_name": item_name,
        "description": item_description,
    }
