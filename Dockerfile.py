# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1-mesa-glx

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Command to run the application
CMD ["python", "app.py"]