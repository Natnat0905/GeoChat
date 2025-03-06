# image.py (full update)
import requests
import logging
import os

OCR_API_KEY = os.getenv("OCR_API_KEY")
OCR_API_URL = "https://api.ocr.space/parse/image"

def extract_text_from_image(image_path: str, content_type: str) -> str:
    """Extract text from an image using OCR SPACE API."""
    try:
        with open(image_path, 'rb') as img_file:
            # Process content_type to get MIME type and extension
            mime_type = content_type.split(';')[0].strip().lower() if content_type else 'application/octet-stream'
            main_type, _, sub_type = mime_type.partition('/')
            
            if main_type != 'image':
                raise ValueError(f"Invalid content type: {content_type}")

            # Map MIME subtype to file extension
            extension_map = {
                'jpeg': 'jpg',
                'png': 'png',
                'gif': 'gif',
                'bmp': 'bmp',
                'jpg': 'jpg',
            }
            extension = extension_map.get(sub_type, sub_type)
            filename = f'image.{extension}'

            # Prepare API request parameters
            files = {'image': (filename, img_file, mime_type)}
            payload = {'apikey': OCR_API_KEY, 'isOverlayRequired': False}

            # Set OCR filetype parameter
            filetype_map = {
                'image/png': 'PNG',
                'image/jpeg': 'JPG',
                'image/jpg': 'JPG',
                'image/gif': 'GIF',
                'image/bmp': 'BMP',
            }
            if mime_type in filetype_map:
                payload['filetype'] = filetype_map[mime_type]

            # Make API request
            response = requests.post(OCR_API_URL, files=files, data=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("OCRExitCode") == 1:
                    text = result.get("ParsedResults")[0].get("ParsedText")
                    return text.strip() if text else ""
                else:
                    error_msg = result.get("ErrorMessage", ["OCR failed"])[0]
                    logging.error(f"OCR API Error: {error_msg}")
                    raise RuntimeError("OCR processing failed")
            else:
                logging.error(f"OCR request failed: {response.status_code}")
                raise RuntimeError("OCR API error")

    except Exception as e:
        logging.error(f"OCR failed: {str(e)}")
        raise RuntimeError("Image processing error")