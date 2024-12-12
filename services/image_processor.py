import io
import requests
from PIL import Image
from rembg import remove
import numpy as np
import logging

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
            if image.format not in ["JPEG", "PNG", "BMP"]:
                raise ValueError(f"Unsupported image format: {image.format}")
            logger.info("Image downloaded successfully")
            return image
        except requests.exceptions.Timeout:
            raise ValueError("The request timed out while trying to download the image")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"An error occurred while downloading the image: {str(e)}")
        except IOError:
            raise ValueError("Failed to open the image. The file might be corrupted or unsupported.")

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
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            # Convert PIL Image to NumPy array
            input_array = np.array(image)
            
            # Remove background
            output_array = remove(input_array)
            
            # Convert back to PIL Image
            logger.info("Background removed successfully")
            return Image.fromarray(output_array)
        except Exception as e:
            raise ValueError(f"Background removal failed: {str(e)}")

    @classmethod
    def process_image(cls, image_url, bounding_box):
        """Complete image processing pipeline"""
        try:
            logger.info(f"Processing image: {image_url}")
            
            # Download image
            image = cls.download_image(image_url)
            
            # Validate bounding box
            cls.validate_bounding_box(image, bounding_box)
            
            # Crop to specified region
            cropped_image = cls.crop_image(image, bounding_box)
            
            # Remove background
            processed_image = cls.remove_background(cropped_image)
            
            logger.info("Image processing completed successfully")
            return processed_image
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise
