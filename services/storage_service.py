import io
import uuid
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from services.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        """
        Initializes the S3 client with the provided AWS credentials and region.
        """
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY,
                region_name=settings.REGION_NAME
            )
            logger.info("S3 client initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize S3 client: %s", str(e))
            raise ValueError("Failed to initialize S3 client.")

    def upload_image(self, image, original_url):
        """
        Uploads an image to an S3 bucket and returns its public URL.

        Args:
            image (io.BytesIO): The image to upload, provided as an in-memory buffer.
            original_url (str): The original image URL for reference.

        Returns:
            str: Public URL of the uploaded image.

        Raises:
            ValueError: If the upload fails.
        """
        try:
            # Generate a unique filename for the processed image
            filename = f"{uuid.uuid4()}_processed.png"
            logger.info("Generated unique filename: %s", filename)

            # Ensure the image buffer is at the start
            if isinstance(image, io.BytesIO):
                image.seek(0)
            
            # Upload the image to S3
            self.s3_client.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=filename,
                Body=image,
                ContentType='image/png'
            )
            logger.info("Image uploaded to S3 bucket: %s", settings.AWS_BUCKET_NAME)

            # Construct and return the public URL
            public_url = (
                f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.REGION_NAME}.amazonaws.com/{filename}"
            )
            logger.info("Public URL of uploaded image: %s", public_url)

            return public_url
        except (BotoCoreError, ClientError) as e:
            logger.error("S3 upload failed: %s", str(e))
            raise ValueError(f"S3 upload failed: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during S3 upload: %s", str(e))
            raise ValueError(f"Unexpected error during S3 upload: {str(e)}")

    def delete_image(self, file_key):
        """
        Deletes an image from the S3 bucket using its file key.

        Args:
            file_key (str): The key of the file to delete in the S3 bucket.

        Returns:
            bool: True if deletion was successful, False otherwise.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            self.s3_client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_key)
            logger.info("Deleted file from S3: %s", file_key)
            return True
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to delete file from S3: %s", str(e))
            raise ValueError(f"Failed to delete file from S3: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during S3 deletion: %s", str(e))
            raise ValueError(f"Unexpected error during S3 deletion: {str(e)}")
