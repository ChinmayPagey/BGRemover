import io
import uuid
import boto3
from services.config import settings


class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.REGION_NAME
        )

    def upload_image(self, image, original_url):
        try:
            filename = f"{uuid.uuid4()}_processed.png"
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            self.s3_client.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=filename,
                Body=img_byte_arr,
                ContentType='image/png'
            )
            
            public_url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.REGION_NAME}.amazonaws.com/{filename}"
            return public_url
        except Exception as e:
            raise ValueError(f"S3 upload failed: {str(e)}")