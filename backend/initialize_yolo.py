#!/usr/bin/env python3
"""
Script to initialize the YOLO service with the existing model.
This script automatically configures the system to use the yolov5s.pt model.
"""

import os
import sys
from pathlib import Path
import subprocess

def install_dependency(package):
    """Install a Python package if it's not already installed."""
    try:
        __import__(package)
        print(f"✅ {package} is already installed")
        return True
    except ImportError:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Successfully installed {package}")
            return True
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")
            return False

def initialize_yolo():
    """Initialize YOLO model for symbol detection."""
    # Install required dependencies
    print("Checking and installing required dependencies...")
    dependencies = ["torch", "torchvision", "ultralytics"]
    
    for dep in dependencies:
        install_dependency(dep)
    
    # Get the model path
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    weights_path = models_dir / "yolov5s.pt"
    
    if not weights_path.exists():
        print(f"❌ Model file not found at {weights_path}")
        print("Attempting to download a default YOLOv5 model...")
        try:
            import torch
            # Download a default YOLOv5s model
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, trust_repo=True)
            # Save the model
            model.save(str(models_dir))
            print(f"✅ Downloaded and saved YOLOv5s model to {weights_path}")
        except Exception as e:
            print(f"❌ Failed to download model: {e}")
            print("Please manually download a YOLOv5 model and place it in the models/ directory.")
            return False
    
    print(f"✅ Found YOLO model at {weights_path}")
    
    # Create a basic config file if it doesn't exist
    config_path = models_dir / "config.yaml"
    if not config_path.exists():
        config_content = """# YOLO Model Configuration for P&ID Symbols
model_path: "yolov5s.pt"
confidence_threshold: 0.5
iou_threshold: 0.45

# Symbol classes (ISA-5.1)
symbol_classes:
  - pump
  - valve_manual
  - valve_control
  - instrument_bubble
  - tank
  - heat_exchanger
  - compressor
  - filter
  - separator
  - reactor
"""
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"✅ Created configuration file at {config_path}")
    
    print("\nYOLO model is ready to use!")
    print("\nTo run the server:")
    print("1. Execute: python -m uvicorn backend.main:app --reload --port 8000")
    print("2. The API will automatically use your YOLO model for symbol detection")
    
    return True

if __name__ == "__main__":
    print("YOLO Model Initialization")
    print("=" * 30)
    initialize_yolo()
