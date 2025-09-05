# YOLO Integration for P&ID Symbol Detection

This document explains how to integrate YOLO (You Only Look Once) deep learning models for robust P&ID symbol detection, replacing the template matching approach.

## Overview

The YOLO integration provides:
- **Better accuracy**: Deep learning-based detection vs. template matching
- **Robustness**: Handles variations in drawing styles, rotations, and scales
- **Extensibility**: Easy to add new symbol types through training
- **Fallback support**: Automatically falls back to template matching if YOLO is unavailable

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   P&ID Image   │───▶│  YOLO Detector   │───▶│  Symbol Nodes   │
│                │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Template Matching│
                       │   (Fallback)    │
                       └──────────────────┘
```

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The requirements include:
- `torch` - PyTorch for YOLO inference
- `torchvision` - Computer vision utilities
- `ultralytics` - YOLOv5 implementation
- `requests` - For downloading model weights

### 2. Setup YOLO Models

Run the setup script to download pre-trained weights and create configuration:

```bash
cd backend
python setup_yolo.py
```

This will:
- Create a `models/` directory
- Download YOLOv5s pre-trained weights
- Create sample configuration files
- Set up dataset structure for training

## Usage

### 1. Load a Custom Model

```bash
# Load a trained YOLO model
curl -X POST "http://localhost:8000/models/load" \
     -H "Content-Type: application/json" \
     -d '{
       "model_path": "models/your_trained_model.pt",
       "conf_threshold": 0.6
     }'
```

### 2. Check Model Status

```bash
# Get information about loaded model
curl "http://localhost:8000/models/info"
```

### 3. Run Analysis

```bash
# Upload and analyze P&ID
curl -X POST "http://localhost:8000/upload" \
     -F "file=@your_pid_diagram.png"

# Run complete analysis
curl -X POST "http://localhost:8000/run/graph"
```

## Training Your Own Model

### 1. Prepare Dataset

Create a YOLO-format dataset:

```
dataset/
├── images/
│   ├── train/
│   │   ├── pid_001.png
│   │   ├── pid_002.png
│   │   └── ...
│   └── val/
│       ├── pid_101.png
│       ├── pid_102.png
│       └── ...
├── labels/
│   ├── train/
│   │   ├── pid_001.txt
│   │   ├── pid_002.txt
│   │   └── ...
│   └── val/
│       ├── pid_101.txt
│       ├── pid_102.txt
│       └── ...
└── data.yaml
```

### 2. Label Format

Each label file should contain one line per object:
```
class_id center_x center_y width height
```

Example for a pump at center (100, 150) with size 50x30:
```
0 100 150 50 30
```

### 3. Train the Model

```bash
# Install ultralytics
pip install ultralytics

# Train on your dataset
python -m ultralytics.train \
    data=dataset/data.yaml \
    model=yolov5s.pt \
    epochs=100 \
    imgsz=640 \
    batch=16
```

### 4. Use Trained Model

Copy your trained model to the `models/` directory and load it:

```bash
cp runs/train/exp/weights/best.pt models/pid_symbols.pt

# Load via API
curl -X POST "http://localhost:8000/models/load" \
     -H "Content-Type: application/json" \
     -d '{
       "model_path": "models/pid_symbols.pt",
       "conf_threshold": 0.5
     }'
```

## Supported Symbol Classes

The default YOLO model supports these ISA-5.1 symbols:

| Class ID | Symbol Type | Category |
|----------|-------------|----------|
| 0 | pump | Equipment |
| 1 | valve_manual | Equipment |
| 2 | valve_control | Equipment |
| 3 | instrument_bubble | Instrument |
| 4 | tank | Equipment |
| 5 | heat_exchanger | Equipment |
| 6 | compressor | Equipment |
| 7 | filter | Equipment |
| 8 | separator | Equipment |
| 9 | reactor | Equipment |

## Configuration

### Model Settings

Edit `models/config.yaml`:

```yaml
# Model settings
model_path: "your_model.pt"
confidence_threshold: 0.5
iou_threshold: 0.45

# Symbol classes
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
```

### Training Parameters

```yaml
training:
  epochs: 100
  batch_size: 16
  learning_rate: 0.01
  image_size: 640

augmentation:
  hsv_h: 0.015
  hsv_s: 0.7
  hsv_v: 0.4
  degrees: 0.0  # No rotation for P&ID symbols
  translate: 0.1
  scale: 0.5
  fliplr: 0.5   # Horizontal flip OK
  mosaic: 1.0
```

## Performance Optimization

### 1. GPU Acceleration

```python
# Automatically detected in YOLOSymbolDetector
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

### 2. Model Quantization

```bash
# Quantize model for faster inference
python -m ultralytics.export \
    model=models/pid_symbols.pt \
    format=onnx \
    optimize=True
```

### 3. Batch Processing

For multiple images, modify the detector to process batches:

```python
def detect_symbols_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
    """Process multiple images in batch for better GPU utilization."""
    # Implementation for batch processing
    pass
```

## Troubleshooting

### Common Issues

1. **Model not loading**
   - Check file path and format (.pt or .onnx)
   - Verify PyTorch/ultralytics installation
   - Check GPU memory if using CUDA

2. **Low detection accuracy**
   - Lower confidence threshold
   - Retrain with more diverse data
   - Check class balance in training set

3. **Slow inference**
   - Use smaller model (YOLOv5n instead of YOLOv5l)
   - Enable GPU acceleration
   - Quantize model to INT8

### Debug Mode

Enable debug logging in the YOLO service:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing Pipeline

The YOLO integration seamlessly replaces template matching:

```python
# Old template matching
from .services import symbols
result = symbols.detect_symbols(image_path)

# New YOLO detection (with fallback)
from .services import yolo_symbols
result = yolo_symbols.detect_symbols_yolo(image_path)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/models/info` | GET | Get current model information |
| `/models/load` | POST | Load a custom YOLO model |
| `/analyze` | POST | Run analysis with current model |
| `/run/graph` | POST | Run complete analysis pipeline |

## Future Enhancements

1. **Multi-scale detection**: Handle symbols at different scales
2. **Rotation invariance**: Detect rotated symbols
3. **Ensemble models**: Combine multiple YOLO models
4. **Real-time processing**: Stream processing for live P&ID analysis
5. **Active learning**: Improve model with user feedback

## References

- [YOLOv5 Documentation](https://docs.ultralytics.com/)
- [ISA-5.1 Standard](https://www.isa.org/standards-and-publications/isa-standards)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [Computer Vision Best Practices](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data)
