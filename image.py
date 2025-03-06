import requests
import logging
import os

OCR_API_KEY = os.getenv("OCR_API_KEY")  # Your OCR SPACE API key
OCR_API_URL = "https://api.ocr.space/parse/image"  # OCR SPACE endpoint

def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image using OCR SPACE API."""
    try:
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            payload = {'apikey': OCR_API_KEY}
            
            # Make the API request
            response = requests.post(OCR_API_URL, files=files, data=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if OCR was successful
                if result.get("OCRExitCode") == 1:
                    text = result.get("ParsedResults")[0].get("ParsedText")
                    return text.strip() if text else ""
                else:
                    logging.error(f"OCR API Error: {result.get('ErrorMessage')}")
                    raise RuntimeError("OCR API processing failed")
            else:
                logging.error(f"OCR API Request failed with status code {response.status_code}")
                raise RuntimeError("OCR API request failed")
    
    except Exception as e:
        logging.error(f"OCR failed: {e}")
        raise RuntimeError("OCR processing error")
