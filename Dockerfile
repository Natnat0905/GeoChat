# Use a Python base image
FROM python:3.10-slim

# Install system dependencies, including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app will run on
EXPOSE 5000

# Ensure the command properly references the environment variable for the port
ENTRYPOINT ["sh", "-c", "uvicorn visual:app --host 0.0.0.0 --port ${PORT:-5000}"]
