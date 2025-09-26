#!/usr/bin/env python3
"""
Flask API for PaddleOCR text extraction from images.
Uses PaddleOCR 3.2 for enhanced accuracy.
Optimized for number plate recognition on small 20KB images.
"""

import os
import io
import base64
import json
import tempfile
from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Initialize PaddleOCR 3.2 with simplified configuration
logger.info("Initializing PaddleOCR 3.2")

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)



def process_image(image_data):
    """
    Process image data and return OCR results using PaddleOCR 3.2
    """
    try:
        # Save image to temporary file for PaddleOCR 3.2 predict method
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            # Save PIL image to temporary file
            image_data.save(tmp_file.name, format='JPEG')
            
            # Run OCR using predict method
            result = ocr.predict(input=tmp_file.name)
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
        
        # Process results
        if not result:
            return {
                'success': True,
                'text': '',
                'confidence': 0.0,
                'details': []
            }
        
        # Extract text and confidence from PaddleOCR 3.2 results
        texts = []
        confidences = []
        details = []
        
        # Process the result from PaddleOCR 3.2
        for res in result:
            # PaddleOCR 3.2 result structure
            if hasattr(res, 'texts') and res.texts:
                for text_info in res.texts:
                    text = text_info.get('text', '')
                    confidence = text_info.get('score', 0.0)
                    bbox = text_info.get('bbox', [])
                    
                    if text.strip():  # Only add non-empty text
                        texts.append(text)
                        confidences.append(confidence)
                        details.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': bbox
                        })
        
        # Combine all text
        full_text = ' '.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'success': True,
            'text': full_text,
            'confidence': avg_confidence,
            'details': details
        }
        
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'paddle-ocr-api',
        'version': '1.0.0',
        'paddleocr_version': '3.2',
        'gpu_enabled': False
    })

@app.route('/ocr', methods=['POST'])
def extract_text():
    """
    Extract text from uploaded image using PaddleOCR
    
    Accepts:
    - File upload (multipart/form-data) with key 'image'
    - JSON with base64 encoded image in 'image' field
    
    Returns:
    JSON response with extracted text and metadata
    """
    try:
        image = None
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Validate file type
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                return jsonify({
                    'success': False,
                    'error': 'Unsupported file type. Use PNG, JPG, JPEG, BMP, TIFF, or WEBP'
                }), 400
            
            try:
                image = Image.open(file.stream)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Invalid image file: {str(e)}'
                }), 400
        
        # Handle JSON with base64 image
        elif request.is_json:
            data = request.get_json()
            if not data or 'image' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing image data in JSON request'
                }), 400
            
            try:
                # Decode base64 image
                image_data = base64.b64decode(data['image'])
                image = Image.open(io.BytesIO(image_data))
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Invalid base64 image data: {str(e)}'
                }), 400
        
        else:
            return jsonify({
                'success': False,
                'error': 'No image provided. Send as file upload or base64 JSON.'
            }), 400
        
        # Convert to RGB if necessary (remove alpha channel, handle grayscale)
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Log image info
        logger.info(f"Processing image: {image.size[0]}x{image.size[1]} pixels, mode: {image.mode}")
        
        # Process with OCR
        result = process_image(image)
        
        # Add metadata
        result['image_info'] = {
            'width': image.size[0],
            'height': image.size[1],
            'mode': image.mode
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'full_text': '',
            'detailed_results': [],
            'text_count': 0
        }), 500



@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 5MB.'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found. Use POST /ocr to extract text from images.'
    }), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting PaddleOCR API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)