# PaddleOCR HTTP API

A FastAPI service for text extraction from images using PaddleOCR 3.2 with PP-OCRv5 server models, optimized for number plate recognition.

## Features

- Fast REST API for OCR text extraction built with FastAPI
- Automatic interactive API documentation (Swagger UI)
- Supports multiple image formats (PNG, JPG, JPEG, BMP, TIFF, WEBP)
- File upload via multipart/form-data
- Optimized for small to medium images (up to 20MB)
- Returns text with confidence scores and bounding boxes
- Docker containerized for easy deployment
- GPU support available via docker-compose configuration
- Health check endpoint
- Textline orientation detection for rotated text

## Quick Start with Docker

### Build and run with Docker Compose (recommended)

```bash
docker compose up --build
```

The service includes GPU support configuration in `docker-compose.yml`. To use GPU acceleration, ensure you have:
- NVIDIA GPU with CUDA support
- NVIDIA Docker runtime installed
- Uncomment GPU base image in `Dockerfile`

### Or build and run with Docker directly

```bash
# Build the image
docker build -t paddle-ocr-api .

# Run the container (CPU)
docker run -p 5000:5000 paddle-ocr-api

# Run with GPU support (requires nvidia-docker)
docker run --gpus all -p 5000:5000 paddle-ocr-api
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
  "text": "ABC 123",
  "confidence": 0.95,
  "rec_texts": ["ABC", "123"],
  "rec_scores": [0.96, 0.94],
  "details": [
    {
      "text": "ABC",
      "confidence": 0.96,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    },
    {
      "text": "123",
      "confidence": 0.94,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ]
}
```

**Response Fields:**
- `success`: Boolean indicating if OCR was successful
- `text`: Combined text from all detected regions (space-separated)
- `confidence`: Average confidence score across all detections
- `rec_texts`: Array of individual recognized text segments
- `rec_scores`: Array of confidence scores for each text segment
- `details`: Detailed results with text, confidence, and bounding box coordinates for each detection

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

The API is pre-configured for optimal text recognition:

- **PaddleOCR Version**: 3.2 with PP-OCRv5 server models
- **Detection Model**: PP-OCRv5_server_det (high accuracy detection)
- **Recognition Model**: PP-OCRv5_server_rec (high accuracy recognition)
- **Textline Orientation**: Enabled for rotated text detection
- **Language**: English (default)
- **Processing Mode**: CPU-only by default (GPU support configurable)
- **Maximum File Size**: 20MB
- **Supported Formats**: PNG, JPG, JPEG, BMP, TIFF, WEBP

## Docker Image Size Optimization

The Dockerfile uses PaddlePaddle 3.2.0 official image as base and includes only necessary dependencies to support OpenCV and PaddleOCR requirements. GPU support is available by switching to the GPU base image (commented in Dockerfile).

## Testing

A test script is included to verify the API functionality:

```bash
python test_api.py
```

The test script will:
- Check the health endpoint
- Test OCR with file upload using `test2.jpg`
- Create a synthetic test image if needed
- Display results and confidence scores

You can specify a custom API URL:
```bash
python test_api.py http://localhost:5000
```

## Error Handling

The API includes comprehensive error handling for:

- Invalid file formats (returns 400)
- File size limits exceeded - max 20MB (returns 413)
- OCR processing errors (returns 500)
- Missing image data (returns 400)

## Performance Notes

- Optimized for images up to 20MB
- Uses PP-OCRv5 server models for enhanced accuracy
- First OCR request may be slower due to model loading
- Subsequent requests are faster due to model caching
- GPU support available for high-throughput scenarios (configure in docker-compose.yml)
- Async endpoints for better concurrency
- Textline orientation detection helps with rotated or angled text