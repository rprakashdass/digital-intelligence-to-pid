"""
Test script to help diagnose issues with the API endpoints.
"""
import requests
import os
import json

# Base URL of the FastAPI server
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the /health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(response.json())

def test_upload_image(image_path):
    """Test the /upload endpoint with an image"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None
        
    print(f"Uploading image: {image_path}")
    
    with open(image_path, "rb") as img:
        files = {"file": img}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        
    print(f"Upload response: {response.status_code}")
    if response.ok:
        print(json.dumps(response.json(), indent=2))
        return response.json().get("image_id")
    else:
        print(f"Error: {response.text}")
        return None

def test_analysis(image_id, analysis_type):
    """Test an analysis endpoint"""
    if not image_id:
        print("No image ID provided")
        return
        
    print(f"Running {analysis_type} analysis for image {image_id}")
    
    response = requests.post(f"{BASE_URL}/run/{analysis_type}")
    
    print(f"Analysis response: {response.status_code}")
    if response.ok:
        result = response.json()
        if analysis_type == "graph":
            print(f"Graph contains: {len(result.get('nodes', []))} nodes, " +
                  f"{len(result.get('edges', []))} edges, " +
                  f"{len(result.get('texts', []))} texts")
        elif analysis_type == "ocr":
            print(f"OCR found {len(result.get('texts', []))} text elements")
        elif analysis_type == "validate":
            print(f"Validation found {len(result.get('issues', []))} issues")
    else:
        print(f"Error: {response.text}")

def create_test_image(path):
    """Create a simple test image with some shapes if one doesn't exist"""
    try:
        import numpy as np
        from PIL import Image, ImageDraw
        
        # Create a blank image with white background
        img = Image.new('RGB', (500, 500), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a rectangle (representing a valve)
        draw.rectangle([(100, 100), (200, 150)], outline='black', width=2)
        
        # Draw a circle (representing a pump)
        draw.ellipse([(250, 200), (350, 300)], outline='black', width=2)
        
        # Draw some lines
        draw.line([(200, 125), (250, 250)], fill='black', width=2)
        draw.line([(350, 250), (400, 250)], fill='black', width=2)
        
        # Add some text
        draw.text((120, 120), "V-101", fill='black')
        draw.text((290, 250), "P-102", fill='black')
        
        # Save the image
        img.save(path)
        print(f"Created test image at {path}")
        return True
    except Exception as e:
        print(f"Error creating test image: {e}")
        return False

if __name__ == "__main__":
    # Step 1: Test health check
    test_health()
    
    # Step 2: Prepare and upload a sample image
    image_path = "data/samples/test_image.png"
    if not os.path.exists(image_path):
        create_test_image(image_path)
    
    image_id = test_upload_image(image_path)
    
    # Step 3: Test different analysis types
    if image_id:
        test_analysis(image_id, "graph")
        test_analysis(image_id, "ocr")
        test_analysis(image_id, "validate")
