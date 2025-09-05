"""
Script to load and test the YOLO model for P&ID symbol detection.
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np

def test_yolo_model():
    """Test loading and running the YOLO model."""
    print("Testing YOLO model loading...")
    
    # Get the model path
    models_dir = Path("models")
    weights_path = models_dir / "yolov5s.pt"
    
    if not weights_path.exists():
        print(f"❌ Error: Model file not found at {weights_path}")
        return False
    
    print(f"✅ Found YOLO model at {weights_path}")
    
    try:
        # Test PyTorch import
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
    except ImportError:
        print("❌ PyTorch not installed. Installing...")
        os.system("pip install torch torchvision")
        try:
            import torch
            print(f"✅ PyTorch installed successfully. Version: {torch.__version__}")
        except ImportError:
            print("❌ Failed to install PyTorch. Please install manually.")
            return False
    
    try:
        # Test ultralytics import
        import ultralytics
        print(f"✅ Ultralytics version: {ultralytics.__version__}")
    except ImportError:
        print("❌ Ultralytics not installed. Installing...")
        os.system("pip install ultralytics")
        try:
            import ultralytics
            print(f"✅ Ultralytics installed successfully. Version: {ultralytics.__version__}")
        except ImportError:
            print("❌ Failed to install Ultralytics. Please install manually.")
            return False
    
    # Test loading the model using backend
    try:
        print("\nTesting YOLO detection with the backend API...")
        from backend.services.yolo_symbols import YOLOSymbolDetector
        
        # Create a new detector instance
        detector = YOLOSymbolDetector()
        
        # Load the model
        success = detector.load_model(str(weights_path))
        
        if success:
            print("✅ YOLO model loaded successfully!")
            
            # Check if we have any test images
            test_images = list(Path("data/samples").glob("*.png"))
            
            if test_images:
                print(f"\nTesting detection on sample image: {test_images[0]}")
                result = detector.detect_symbols(str(test_images[0]))
                print(f"Detected {len(result['nodes'])} symbols in the test image!")
                for i, node in enumerate(result['nodes']):
                    print(f"  {i+1}. {node.type} (confidence: {node.confidence:.2f})")
            else:
                print("No test images found in data/samples directory.")
                
            return True
        else:
            print("❌ Failed to load YOLO model")
            return False
        
    except Exception as e:
        print(f"❌ Error testing YOLO model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("YOLO Model Testing Utility")
    print("=" * 30)
    
    if test_yolo_model():
        print("\nYOLO model is working correctly!")
        print("\nYou can now run the backend server:")
        print("python -m uvicorn backend.main:app --reload --port 8000")
    else:
        print("\nYOLO model test failed. Please check the error messages above.")
