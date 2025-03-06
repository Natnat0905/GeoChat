import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import logging
from sympy import parse_expr, SympifyError
import os

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def preprocess_image(image_path: str) -> Image.Image:
    """Preprocess the image to improve OCR accuracy."""
    try:
        img = Image.open(image_path)
        img = img.convert('L')  # Convert to grayscale
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)  # Increase contrast
        img = img.point(lambda x: 0 if x < 128 else 255, '1')  # Apply thresholding
        img = img.filter(ImageFilter.MedianFilter(size=3))  # Denoise
        return img
    except Exception as e:
        logging.error(f"Image preprocessing failed: {e}")
        raise RuntimeError("Image preprocessing error")

def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    try:
        processed_image = preprocess_image(image_path)
        text = pytesseract.image_to_string(processed_image)
        return text.strip()
    except Exception as e:
        logging.error(f"OCR failed: {e}")
        raise RuntimeError("OCR processing error")

def parse_math_expression(text: str) -> str:
    """Parse and extract mathematical expressions from text using SymPy."""
    try:
        # First try to parse the entire text
        expr = parse_expr(text, evaluate=False)
        return str(expr)
    except SympifyError:
        # If that fails, search for math patterns
        expressions = []
        parts = re.split(r'[.,;!?\n]', text)
        math_pattern = r'(\d+\s*[\+\-\*/\^]\s*\d+|\d+\.\d+|\(.*\)|sqrt\(.*\)|pi|\^?[a-zA-Z]+)'
        
        for part in parts:
            matches = re.findall(math_pattern, part)
            for match in matches:
                try:
                    expr = parse_expr(match, evaluate=False)
                    expressions.append(str(expr))
                except SympifyError:
                    continue
        
        return ' '.join(expressions) if expressions else text
    except Exception as e:
        logging.error(f"Math parsing error: {e}")
        return text