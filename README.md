# PaddleOCR HTTP API

A FastAPI service for text extraction from images using PaddleOCR 3.2 with PP-OCRv5, optimized for number plate recognition.

## Features

- Fast REST API for OCR text extraction built with FastAPI
- Automatic interactive API documentation (Swagger UI)
- Supports multiple image formats (PNG, JPG, JPEG, BMP, TIFF, WEBP)
- File upload via multipart/form-data
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

**Interactive API Documentation** available at:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

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

### 2. Python example

```python
import requests

# File upload
with open('numberplate.jpg', 'rb') as f:
    files = {'image': ('numberplate.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:5000/ocr', files=files)
    result = response.json()

print(f"Extracted text: {result['text']}")
print(f"Confidence: {result['confidence']}")
```

## Response Format

```json
{
  "success": true,
  "text": "ABC123",
  "confidence": 0.95,
  "details": [
    {
      "text": "ABC123",
      "confidence": 0.95,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ]
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

Or use uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)

## Configuration

The API is pre-configured for optimal number plate recognition:

- Uses PaddleOCR 3.2 with PP-OCRv5 model for enhanced accuracy
- English language model optimized for text recognition
- Enables angle classification for rotated text detection
- CPU-only inference (suitable for containers)
- Maximum file size: 5MB
- Supports multiple image formats

## Docker Image Size Optimization

The Dockerfile uses PaddlePaddle official GPU image as base and includes only necessary dependencies to support OpenCV and PaddleOCR requirements.

## Error Handling

The API includes comprehensive error handling for:

- Invalid file formats (returns 400)
- File size limits (returns 413)
- OCR processing errors (returns 500)
- Missing image data (returns 400)

## Performance Notes

- Optimized for small images (20KB number plates)
- First OCR request may be slower due to model loading
- Subsequent requests are faster due to model caching
- Consider using GPU version for high-throughput scenarios
- Async endpoints for better concurrency