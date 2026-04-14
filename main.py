from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import tempfile
import os
from typing import Dict, Any

# Import our local modules
from image_moderation import moderate_image_content
from text_moderation import process_text_from_image

app = FastAPI(
    title="Content Moderation API",
    description="Check images for explicit content and profanity in embedded text.",
    version="1.0.0"
)

@app.post("/moderate", response_model=Dict[str, Any])
async def moderate_image(file: UploadFile = File(...)):
    """
    Endpoint to moderate an uploaded image.
    
    - Validates file type (image only)
    - Saves image temporarily
    - Runs image moderation (NudeNet)
    - Extracts text via OCR and moderates it (profanity check)
    - Returns combined result
    """
    # 1. Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only images (JPEG, PNG, etc.) are allowed."
        )
    
    # 2. Save uploaded file to a temporary location
    #    Using suffix to preserve original extension (helps some libraries)
    suffix = os.path.splitext(file.filename)[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name
    
    try:
        # 3. Image content moderation (explicit photos)
        image_result = moderate_image_content(temp_path)
        
        # 4. OCR + text moderation
        text_result = process_text_from_image(temp_path)
        
        # 5. Overall appropriateness: both image AND text must be appropriate
        overall_appropriate = image_result["is_appropriate"] and text_result["is_appropriate"]
        
        return JSONResponse(content={
            "is_appropriate": overall_appropriate,
            "image_moderation": {
                "is_appropriate": image_result["is_appropriate"],
                "reasons": image_result["reasons"]
            },
            "text_moderation": {
                "is_appropriate": text_result["is_appropriate"],
                "reasons": text_result["reasons"],
                "extracted_text": text_result["extracted_text"]   # may be empty
            }
        })
    
    except Exception as e:
        # Log the error (you may want to use proper logging)
        print(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # 6. Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}