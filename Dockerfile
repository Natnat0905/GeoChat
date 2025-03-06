FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

ENV TESSERACT_CMD=/usr/bin/tesseract

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the Procfile
COPY Procfile /Procfile

EXPOSE 8080

# Use a command to run the application from the Procfile
CMD ["sh", "-c", "exec $(cat /Procfile | grep web | cut -d ' ' -f2-)" ]
