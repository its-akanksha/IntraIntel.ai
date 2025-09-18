import boto3
from botocore.exceptions import ClientError
from config import settings
import logging

logger = logging.getLogger(__name__)

class TextractService:
    def __init__(self):
        self.client = boto3.client(
            'textract',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using AWS Textract"""
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            response = self.client.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            # Extract text from blocks
            text_lines = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text_lines.append(block['Text'])
            
            return '\n'.join(text_lines)
            
        except ClientError as e:
            logger.error(f"AWS Textract error: {e}")
            raise Exception(f"Text extraction failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Text extraction failed: {e}")