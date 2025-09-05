#!/usr/bin/env python3
"""
Setup script for YOLO-based P&ID symbol detection.
This script configures the system to use an existing YOLO model file.
"""

import os
import sys
import requests
from pathlib import Path

def setup_yolo_models():
    """Set up YOLO models for P&ID symbol detection."""
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    print("Setting up YOLO models for P&ID symbol detection...")
    print("=" * 50)
    
    # Check if model exists
    weights_path = models_dir / "yolov5s.pt"
    
    if weights_path.exists():
        print(f"✅ Found existing YOLO model at {weights_path}")
        print("Using existing model for symbol detection.")
    else:
        print(f"❌ No model found at {weights_path}")
        print("Please place your YOLO model file (yolov5s.pt) in the models/ directory.")
    
    # Create a sample configuration file
    config_path = models_dir / "config.yaml"
    if not config_path.exists():
        config_content = """# YOLO Model Configuration for P&ID Symbols
# This file contains configuration for YOLO-based symbol detection

# Model settings
model_path: "yolov5s.pt"  # Path to your existing model
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
        print(f"Created configuration file at {config_path}")
    else:
        print(f"✅ Configuration file already exists at {config_path}")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Start the backend server with 'python -m uvicorn backend.main:app --reload'")
    print("2. Use POST /models/load to load your model")
    print("3. Run analysis with POST /analyze or POST /run/graph")

def create_sample_dataset():
    """Create a sample dataset structure for training."""
    
    print("Model training is not needed since you already have a .pt file.")
    print("Using existing model from the models/ directory.")

if __name__ == "__main__":
    print("YOLO Setup for P&ID Symbol Detection")
    print("=" * 40)
    print("Using existing YOLOv5 model in models/yolov5s.pt")
    
    if len(sys.argv) > 1 and sys.argv[1] == "dataset":
        create_sample_dataset()
    else:
        setup_yolo_models()
