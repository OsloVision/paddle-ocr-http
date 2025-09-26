#!/usr/bin/env python3
"""
Test script for PaddleOCR API
Creates a sample image with text and tests the API endpoints
"""

import requests
import json
import base64
import io
import os
from PIL import Image, ImageDraw, ImageFont
import sys

def create_test_image():
    """Create a simple test image with number plate text"""
    # Create a white image (like a number plate)
    width, height = 300, 100
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add black border (like a number plate)
    border_width = 3
    draw.rectangle([0, 0, width-1, height-1], outline='black', width=border_width)
    
    # Add text (simulate number plate)
    text = "ABC 123"
    try:
        # Try to use a better font if available
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    return image

def test_health_endpoint(base_url):
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_ocr_file_upload(base_url, image_path):
    """Test OCR with file upload"""
    print("\n🔍 Testing OCR with file upload...")
    try:
        # Open the test image file
        with open(image_path, 'rb') as f:
            files = {'image': ('test2.jpg', f, 'image/jpeg')}
            response = requests.post(f"{base_url}/ocr", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File upload OCR test passed")
            print(f"   Extracted text: '{result.get('full_text', '')}'")
            print(f"   Confidence: {result.get('detailed_results', [{}])[0].get('confidence', 0) if result.get('detailed_results') else 'N/A'}")
            return True
        else:
            print(f"❌ File upload OCR test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ File upload OCR test failed: {str(e)}")
        return False

def test_ocr_base64(base_url, image_path):
    """Test OCR with base64 JSON"""
    print("\n🔍 Testing OCR with base64 JSON...")
    try:
        # Convert image file to base64
        with open(image_path, 'rb') as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {'image': img_base64}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{base_url}/ocr", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Base64 JSON OCR test passed")
            print(f"   Extracted text: '{result.get('full_text', '')}'")
            print(f"   Confidence: {result.get('detailed_results', [{}])[0].get('confidence', 0) if result.get('detailed_results') else 'N/A'}")
            return True
        else:
            print(f"❌ Base64 JSON OCR test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Base64 JSON OCR test failed: {str(e)}")
        return False



def main():
    """Main test function"""
    base_url = "http://localhost:5000"
    image_path = "test2.jpg"
    
    # Allow custom URL via command line
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    
    print(f"🚀 Testing PaddleOCR API at {base_url}")
    print("=" * 50)
    
    # Check if test image exists
    if not os.path.exists(image_path):
        print(f"❌ Test image '{image_path}' not found!")
        print("📸 Creating synthetic test image as fallback...")
        test_image = create_test_image()
        test_image.save("test_numberplate.png")
        image_path = "test_numberplate.png"
        print("✅ Fallback test image created")
    else:
        print(f"📸 Using test image: {image_path}")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_health_endpoint(base_url):
        tests_passed += 1
    
    if test_ocr_file_upload(base_url, image_path):
        tests_passed += 1
    
    if test_ocr_base64(base_url, image_path):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the API server and try again.")
        return 1

if __name__ == "__main__":
    exit(main())