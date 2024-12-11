import io
import requests
from PIL import Image
from rembg import remove
import numpy as np

class ImageProcessor:
    @staticmethod
    def download_image(image_url):
        """Download image from URL"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            raise ValueError(f"Failed to download image: {str(e)}")

    @staticmethod
    def crop_image(image, bounding_box):
        """Crop image to specified bounding box"""
        x_min, y_min, x_max, y_max = (
            bounding_box['x_min'], 
            bounding_box['y_min'], 
            bounding_box['x_max'], 
            bounding_box['y_max']
        )
        return image.crop((x_min, y_min, x_max, y_max))

    @staticmethod
    def remove_background(image):
        """Remove background from image"""
        try:
            # Convert PIL Image to NumPy array
            input_array = np.array(image)
            
            # Remove background
            output_array = remove(input_array)
            
            # Convert back to PIL Image
            return Image.fromarray(output_array)
        except Exception as e:
            raise ValueError(f"Background removal failed: {str(e)}")

    @classmethod
    def process_image(cls, image_url, bounding_box):
        """Complete image processing pipeline"""
        # Download image
        image = cls.download_image(image_url)
        
        # Crop to specified region
        cropped_image = cls.crop_image(image, bounding_box)
        
        # Remove background
        processed_image = cls.remove_background(cropped_image)
        
        return processed_image