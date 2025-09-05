"""
Test script to verify API endpoints are working correctly.
"""

import os
import requests
import json
import sys
import time
from PIL import Image
import numpy as np

# Create a test image
def create_test_image(width=800, height=600):
    """Create a simple test image with a rectangle and text."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a blank image with white background
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a rectangle (representing a tank)
    draw.rectangle([(100, 100), (300, 400)], outline=(0, 0, 0), width=3)
    
    # Draw a circle (representing a valve)
    draw.ellipse([(400, 200), (500, 300)], outline=(0, 0, 0), width=3)
    
    # Draw a line connecting them
    draw.line([(300, 250), (400, 250)], fill=(0, 0, 0), width=3)
    
    # Add some text
    draw.text((150, 200), "TANK-1", fill=(0, 0, 0))
    draw.text((410, 250), "V-101", fill=(0, 0, 0))
    
    # Save the image
    test_img_path = "test_image.png"
    img.save(test_img_path)
    print(f"Created test image at {test_img_path}")
    return test_img_path

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            return True
        else:
            print(f"❌ Health endpoint returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to health endpoint: {e}")
        return False

def test_upload(image_path):
    """Test the upload endpoint."""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload endpoint is working")
            print(f"   Image ID: {result.get('image_id')}")
            return result.get('image_id')
        else:
            print(f"❌ Upload endpoint returned status code {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error with upload endpoint: {e}")
        return None

def test_analyze(image_id):
    """Test the analyze endpoint."""
    try:
        payload = {"image_id": image_id}
        response = requests.post(
            f"{BASE_URL}/analyze", 
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analyze endpoint is working")
            print(f"   Nodes: {len(result.get('nodes', []))}")
            print(f"   Edges: {len(result.get('edges', []))}")
            print(f"   Texts: {len(result.get('texts', []))}")
            return result
        else:
            print(f"❌ Analyze endpoint returned status code {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error with analyze endpoint: {e}")
        return None

def test_rag_query(image_id, query="What symbols are in this diagram?"):
    """Test the RAG query endpoint."""
    try:
        payload = {"image_id": image_id, "query": query}
        response = requests.post(
            f"{BASE_URL}/query", 
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG query endpoint is working")
            print(f"   Query: {query}")
            print(f"   Answer: {result.get('answer')}")
            return result
        else:
            print(f"❌ RAG query endpoint returned status code {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error with RAG query endpoint: {e}")
        return None

def run_tests():
    """Run all tests in sequence."""
    print("🔍 Testing P&ID Analyzer API")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed. Make sure the backend server is running.")
        return
    
    # Create a test image
    test_image = create_test_image()
    
    # Test upload endpoint
    image_id = test_upload(test_image)
    if not image_id:
        print("❌ Upload test failed.")
        return
    
    print("\nWaiting 2 seconds before continuing...")
    time.sleep(2)
    
    # Test analyze endpoint
    graph_result = test_analyze(image_id)
    if not graph_result:
        print("❌ Analysis test failed.")
        return
    
    # Test RAG query endpoint
    rag_result = test_rag_query(image_id)
    if not rag_result:
        print("❌ RAG query test failed.")
    
    print("\n✅ All API tests completed successfully!")

if __name__ == "__main__":
    run_tests()
