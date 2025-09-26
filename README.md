# PaddleOCR HTTP API

A simple Flask API for text extraction from images using PaddleOCR 3.2 with PP-OCRv5, optimized for number plate recognition.

## Features

- REST API for OCR text extraction
- Supports multiple image formats (PNG, JPG, JPEG, BMP, TIFF, WEBP)
- Accepts both file uploads and base64 encoded images
- Optimized for small images (~20KB number plates)
- Returns text with confidence scores and bounding boxes
- Docker containerized for easy deployment
- Health check endpoint

## Quick Start with Docker

### Build and run with Docker Compose (recommended)

```bash
docker-compose up --build
```

### Or build and run with Docker directly

```bash
# Build the image
docker build -t paddle-ocr-api .

# Run the container
docker run -p 5000:5000 paddle-ocr-api
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```

### OCR Text Extraction
```
POST /ocr
```

## Usage Examples

### 1. Upload image file (multipart/form-data)

```bash
curl -X POST -F "image=@numberplate.jpg" http://localhost:5000/ocr
```

### 2. Send base64 encoded image (JSON)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image_data_here"}' \
  http://localhost:5000/ocr
```

### 3. Python example

```python
import requests
import base64

# Method 1: File upload
with open('numberplate.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/ocr', files=files)
    result = response.json()

# Method 2: Base64 JSON
with open('numberplate.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')
    payload = {'image': image_data}
    response = requests.post('http://localhost:5000/ocr', json=payload)
    result = response.json()

print(f"Extracted text: {result['full_text']}")
```

## Response Format

```json
{
  "success": true,
  "full_text": "ABC123",
  "detailed_results": [
    {
      "text": "ABC123",
      "confidence": 0.95,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ],
  "text_count": 1,
  "image_info": {
    "width": 640,
    "height": 480,
    "mode": "RGB"
  }
}
```

## Local Development

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)  
- `DEBUG`: Enable debug mode (default: False)

## Configuration

The API is pre-configured for optimal number plate recognition:

- Uses PaddleOCR 3.2 with PP-OCRv5 model for enhanced accuracy
- English language model optimized for text recognition
- Enables angle classification for rotated text detection
- CPU-only inference (suitable for containers)
- Maximum file size: 5MB
- Supports multiple image formats

## Docker Image Size Optimization

The Dockerfile uses `python:3.9-slim` base image and includes only necessary system dependencies to keep the image size reasonable while supporting OpenCV and PaddleOCR requirements.

## Error Handling

The API includes comprehensive error handling for:

- Invalid file formats
- Corrupted images
- Missing image data
- File size limits
- OCR processing errors

## Performance Notes

- Optimized for small images (20KB number plates)
- First OCR request may be slower due to model loading
- Subsequent requests are faster due to model caching
- Consider using GPU version for high-throughput scenarios