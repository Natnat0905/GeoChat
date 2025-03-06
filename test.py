import pytesseract
from PIL import Image

# Set the full path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Open an image file (using raw string for file path)
img = Image.open(r'C:\Users\user\Downloads\test.png')  # Replace with correct path

# Use pytesseract to do OCR on the image
text = pytesseract.image_to_string(img)

# Print the extracted text
print(text)
