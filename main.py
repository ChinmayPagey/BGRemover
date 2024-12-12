from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from services.image_processor import ImageProcessor
from services.storage_service import StorageService
import io

# Initialize FastAPI app
app = FastAPI(title="Background Removal API")

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint to indicate that the API is running.
    """
    return {"message": "Welcome to the Background Removal API. Use /remove-background endpoint to process images."}

# Define request model
class ImageProcessRequest(BaseModel):
    image_url: str = Field(..., description="Public URL of the image")
    bounding_box: dict = Field(..., description="Coordinates of the product area")

# Define response model
class ImageProcessResponse(BaseModel):
    original_image_url: str
    processed_image_url: str

@app.post("/remove-background", response_model=ImageProcessResponse)
async def remove_background(request: ImageProcessRequest):
    """
    API endpoint to remove the background of an image and upload the processed image.

    Args:
        request (ImageProcessRequest): Input data containing image URL and bounding box.

    Returns:
        ImageProcessResponse: Original and processed image URLs.
    """
    try:
        # Process the image using ImageProcessor
        processed_image = ImageProcessor.process_image(
            image_url=request.image_url, 
            bounding_box=request.bounding_box
        )
        
        # Save processed image to a buffer (in-memory image)
        image_buffer = io.BytesIO()
        processed_image.save(image_buffer, format="PNG")  # Save as PNG or your preferred format
        image_buffer.seek(0)  # Move the pointer to the beginning of the buffer
        
        # Upload processed image to storage
        storage_service = StorageService()
        processed_image_url = storage_service.upload_image(
            image=image_buffer,  # Pass the buffer instead of a file path
            original_image_url=request.image_url
        )
        
        # Return the response
        return {
            "original_image_url": request.image_url,
            "processed_image_url": processed_image_url
        }
    
    except ValueError as e:
        # Handle input-related errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")

# Run the app if executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
