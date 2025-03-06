# Use the official Python 3.9 image as the base image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files and buffer output
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install Tesseract and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the tesseract path environment variable
ENV TESSERACT_CMD=/usr/bin/tesseract

# Create and set the working directory
WORKDIR /app

# Copy the requirements.txt file and install the dependencies
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Expose the port your application will run on
EXPOSE 8080

# Command to run your application (replace with the command to run your server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
