"""
Test script to verify the RAG query endpoint is working correctly.
This script will:
1. Create a simple test image
2. Upload it to the backend
3. Send a query to the RAG service
"""

import os
import requests
import json
import time
from PIL import Image, ImageDraw

# Create a test image
def create_test_image(filename="test_image.png", width=800, height=600):
    """Create a simple test image with a rectangle and text."""
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
    img.save(filename)
    print(f"Created test image at {filename}")
    return filename

# Upload an image to the backend
def upload_image(image_path, base_url="http://localhost:8000"):
    """Upload an image to the backend and return the image_id."""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Uploaded image successfully")
            print(f"   Image ID: {result.get('image_id')}")
            return result.get('image_id')
        else:
            print(f"❌ Upload failed with status code {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return None

# Send a query to the RAG service
def query_rag(image_id, query, base_url="http://localhost:8000"):
    """Send a query to the RAG service and return the response."""
    try:
        payload = {"image_id": image_id, "query": query}
        response = requests.post(
            f"{base_url}/query", 
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG query successful")
            print(f"   Query: {query}")
            print(f"   Answer: {result.get('answer')}")
            print(f"   Confidence: {result.get('confidence')}")
            return result
        else:
            print(f"❌ RAG query failed with status code {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error querying RAG: {e}")
        return None

def main():
    """Main function to run the test."""
    print("🔍 Testing RAG Query Endpoint")
    print("=" * 50)
    
    # Create a test image
    image_path = create_test_image()
    
    # Upload the image
    image_id = upload_image(image_path)
    if not image_id:
        print("❌ Test failed: Could not upload image")
        return
    
    # Wait a moment to ensure the image is processed
    print("Waiting 2 seconds before querying...")
    time.sleep(2)
    
    # Send a query to the RAG service
    query = "What equipment is shown in this diagram?"
    result = query_rag(image_id, query)
    
    if result:
        print("\n✅ RAG query test completed successfully!")
        print(f"Analysis summary:")
        print(f"  - Symbols detected: {result.get('analysis_summary', {}).get('symbols_detected', 0)}")
        print(f"  - Text elements: {result.get('analysis_summary', {}).get('text_elements', 0)}")
        print(f"  - Issues found: {result.get('analysis_summary', {}).get('issues_found', 0)}")
    else:
        print("\n❌ RAG query test failed")
    
if __name__ == "__main__":
    main()
