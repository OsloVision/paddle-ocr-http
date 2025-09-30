#!/usr/bin/env python3
"""
FastAPI for PaddleOCR text extraction from images.
Uses PaddleOCR 3.2 for enhanced accuracy.
Optimized for number plate recognition on small 20KB images.
"""

import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import logging
from logging.config import dictConfig
import uvicorn

# Set up initial logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
}

dictConfig(log_config)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Initialize PaddleOCR 3.2 with simplified configuration
logger.info("Initializing PaddleOCR 3.2")

from paddleocr import PaddleOCR
import traceback

ocr = PaddleOCR(
    # text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_textline_orientation=True,
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec"
)

# CRITICAL: Reconfigure logging AFTER PaddleOCR initialization
# PaddleOCR hijacks the logging configuration, so we need to restore it
dictConfig(log_config)
logger = logging.getLogger(__name__)

logger.info("PaddleOCR initialization complete, logging reconfigured")

def process_image(image_path):
    """
    Process image file and return OCR results using PaddleOCR
    
    Args:
        image_path: Path to the image file
    """
    try:
        # Run OCR using the file path with ocr.predict()
        logger.info(f"Running OCR on image: {image_path}")
        result = ocr.predict(image_path)

        logger.info(f"OCR result type: {type(result)}, length: {len(result) if result else 0}")
        
        # Process results
        if not result or len(result) == 0:
            return {
                'success': True,
                'text': '',
                'confidence': 0.0,
                'rec_texts': [],
                'rec_scores': [],
                'details': []
            }

        # result is a list of dictionaries
        # Each dict contains rec_texts, rec_scores, rec_polys, etc.
        all_texts = []
        all_scores = []
        all_details = []
        
        for page_result in result:
            rec_texts = page_result.get('rec_texts', [])
            rec_scores = page_result.get('rec_scores', [])
            rec_polys = page_result.get('rec_polys', [])
            
            # Add to aggregated lists
            all_texts.extend(rec_texts)
            all_scores.extend(rec_scores)
            
            # Build detailed results with bboxes
            for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                bbox = rec_polys[i].tolist() if i < len(rec_polys) else []
                all_details.append({
                    'text': text,
                    'confidence': float(score),
                    'bbox': bbox
                })
        
        # Combine all text
        full_text = ' '.join(all_texts)
        avg_confidence = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        return {
            'success': True,
            'text': full_text,
            'confidence': float(avg_confidence),
            'rec_texts': all_texts,
            'rec_scores': [float(score) for score in all_scores],
            'details': all_details
        }
        
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        stack_trace = traceback.format_exc()
        logger.error(stack_trace)
        return {
            'success': False,
            'error': str(e)
        }

@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'paddle-ocr-api',
        'version': '1.0.0',
        'paddleocr_version': '3.2',
        'gpu_enabled': False
    }

@app.post('/ocr')
async def extract_text(image: UploadFile = File(...)):
    """
    Extract text from uploaded image using PaddleOCR
    
    Args:
        image: Uploaded image file (PNG, JPG, JPEG, BMP, TIFF, or WEBP)
    
    Returns:
        JSON response with extracted text and metadata
    """
    temp_file_path = None
    logger.info("Received OCR request")
    
    try:
        # Validate file type
        if not image.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
            raise HTTPException(
                status_code=400,
                detail='Unsupported file type. Use PNG, JPG, JPEG, BMP, TIFF, or WEBP'
            )
        
        # Check file size (5MB limit)
        contents = await image.read()
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB.")
        
        # Save uploaded file to temporary file with correct extension
        _, ext = os.path.splitext(image.filename)
        ext = ext.lower() if ext else '.jpg'
        
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
            tmp_file.write(contents)
            temp_file_path = tmp_file.name
        
        # Log image info
        logger.info(f"Processing image: {temp_file_path}")
        
        # Process with OCR
        result = process_image(temp_file_path)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)





if __name__ == '__main__':
    host = "0.0.0.0"
    port = 5000
    logger.info(f"Starting PaddleOCR API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
