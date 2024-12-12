import io
import requests
from PIL import Image
from rembg import remove
import numpy as np
import logging
import time
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    @staticmethod
    def download_image(image_url):
        """Download image from URL"""
        try:
            logger.info(f"Downloading image from URL: {image_url}")
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            image.verify()  # Verify image integrity
            image = Image.open(io.BytesIO(response.content))  # Reopen after verification
            if image.format not in ["JPEG", "PNG", "BMP"]:
                raise ValueError(f"Unsupported image format: {image.format}")
            logger.info("Image downloaded and verified successfully")
            return image
        except requests.exceptions.Timeout:
            raise ValueError("The request timed out while trying to download the image")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"An error occurred while downloading the image: {str(e)}")
        except IOError:
            raise ValueError("Failed to open the image. The file might be corrupted or unsupported.")

    @staticmethod
    def download_image_with_retries(image_url, retries=3, delay=2):
        """Download image with retry logic"""
        for attempt in range(retries):
            try:
                return ImageProcessor.download_image(image_url)
            except ValueError as e:
                if attempt < retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{retries} after failure: {str(e)}")
                    time.sleep(delay)
                else:
                    raise

    @staticmethod
    def validate_bounding_box(image, bounding_box):
        """Validate if the bounding box is within image dimensions"""
        width, height = image.size
        x_min, y_min, x_max, y_max = (
            bounding_box.get('x_min', 0), 
            bounding_box.get('y_min', 0), 
            bounding_box.get('x_max', 0), 
            bounding_box.get('y_max', 0)
        )
        if not (0 <= x_min < x_max <= width and 0 <= y_min < y_max <= height):
            raise ValueError(
                f"Bounding box is invalid: {bounding_box}. "
                f"Image dimensions are {width}x{height}."
            )
        logger.info("Bounding box validated successfully")

    @staticmethod
    def crop_image(image, bounding_box):
        """Crop image to specified bounding box"""
        x_min, y_min, x_max, y_max = (
            bounding_box['x_min'], 
            bounding_box['y_min'], 
            bounding_box['x_max'], 
            bounding_box['y_max']
        )
        cropped = image.crop((x_min, y_min, x_max, y_max))
        logger.info("Image cropped successfully")
        return cropped.convert(image.mode)

    @staticmethod
    def remove_background(image):
        """Remove background from image"""
        try:
            logger.info("Removing background from image")
            # Ensure image has RGBA mode
            if image.mode not in ["RGB", "RGBA"]:
                image = image.convert("RGB")  # Convert to RGB first
                logger.info("Image mode converted to RGB")
            image = image.convert("RGBA")
            
            # Convert PIL Image to NumPy array
            input_array = np.array(image)
            
            # Remove background
            output_array = remove(input_array)
            
            # Convert back to PIL Image
            if output_array.ndim == 3 and output_array.shape[2] == 4:  # Ensure it's RGBA
                logger.info("Background removed successfully")
                return Image.fromarray(output_array, "RGBA")
            else:
                raise ValueError("Unexpected array shape during background removal")
        except Exception as e:
            raise ValueError(f"Background removal failed: {str(e)}")

    @classmethod
    def process_image(cls, image_url, bounding_box):
        """Complete image processing pipeline"""
        try:
            logger.info(f"Processing image: {image_url}")
            
            # Download image with retries
            image = cls.download_image_with_retries(image_url)
            
            # Validate bounding box
            cls.validate_bounding_box(image, bounding_box)
            
            # Crop to specified region
            cropped_image = cls.crop_image(image, bounding_box)
            
            # Remove background
            processed_image = cls.remove_background(cropped_image)
            
            logger.info("Image processing completed successfully")
            return processed_image
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}\n{traceback.format_exc()}")
            raise

# Example usage
if __name__ == "__main__":
    url = "https://images.unsplash.com/photo-1469285994282-454ceb49e63c"
    bbox = {"x_min": 10, "y_min": 10, "x_max": 500, "y_max": 500}

    try:
        processor = ImageProcessor()
        final_image = processor.process_image(url, bbox)
        final_image.show()  # Display the processed image
    except Exception as e:
        logger.error(f"Failed to process image: {e}")
