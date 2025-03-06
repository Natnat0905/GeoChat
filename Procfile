web: uvicorn visual:app --host 0.0.0.0 --port $PORT

web: bash -c "apt-get update && apt-get install -y tesseract-ocr libtesseract-dev && exec uvicorn visual:app --host 0.0.0.0 --port $PORT"
