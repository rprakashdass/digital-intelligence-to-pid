import cv2
import numpy as np
import os
import torch
from typing import List, Tuple, Dict, Any, Optional
from backend.models import Node, BoundingBox, Issue
import uuid
import json

class YOLOSymbolDetector:
    """
    YOLO-based symbol detector for P&ID diagrams.
    Supports loading custom trained models and performing inference.
    """
    
    def __init__(self, model_path: Optional[str] = None, conf_threshold: float = 0.5):
        self.model = None
        self.conf_threshold = conf_threshold
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # ISA-5.1 symbol classes
        self.symbol_classes = [
            "pump",
            "valve_manual", 
            "valve_control",
            "instrument_bubble",
            "tank",
            "heat_exchanger",
            "compressor",
            "filter",
            "separator",
            "reactor"
        ]
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """
        Load a YOLO model from path.
        Supports both .pt (PyTorch) and .onnx formats.
        """
        try:
            if model_path.endswith('.pt'):
                # Load PyTorch model
                try:
                    import torch
                    print(f"PyTorch version: {torch.__version__}")
                    print(f"Loading model from {model_path}...")
                    
                    # First try the ultralytics method (newer)
                    try:
                        from ultralytics import YOLO
                        self.model = YOLO(model_path)
                        print("Model loaded using ultralytics YOLO")
                    except (ImportError, Exception) as e:
                        print(f"Ultralytics import failed: {e}, trying torch hub...")
                        # Fallback to torch hub (older method)
                        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, trust_repo=True)
                    
                    self.model.to(self.device)
                    print(f"Model loaded and moved to device: {self.device}")
                    
                    # Prefer class names from model if provided
                    try:
                        names = getattr(self.model, 'names', None)
                        if isinstance(names, dict):
                            # yolov5 stores names as dict index->name
                            self.symbol_classes = [names[i] for i in range(len(names))]
                        elif isinstance(names, list):
                            self.symbol_classes = names
                        print(f"Symbol classes: {self.symbol_classes}")
                    except Exception as e:
                        print(f"Could not get symbol classes from model: {e}")
                        
                    # remember path
                    self.model_path = model_path
                    return True
                except Exception as e:
                    print(f"Error loading PyTorch model: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
                    
            elif model_path.endswith('.onnx'):
                # Load ONNX model (requires onnxruntime)
                try:
                    import onnxruntime as ort
                    print(f"ONNX Runtime version: {ort.__version__}")
                    self.model = ort.InferenceSession(model_path)
                    print(f"Loaded ONNX model from {model_path}")
                    self.model_path = model_path
                    return True
                except ImportError:
                    print("ONNX runtime not available. Install with: pip install onnxruntime")
                    return False
                except Exception as e:
                    print(f"Error loading ONNX model: {e}")
                    return False
            else:
                print(f"Unsupported model format: {model_path}")
                return False
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def detect_symbols(self, image_path: str) -> Dict[str, Any]:
        """
        Detect symbols in an image using YOLO.
        Returns detected symbols as nodes and any issues.
        """
        if self.model is None:
            # Fallback to template matching if no YOLO model loaded
            print("No YOLO model loaded, falling back to template matching")
            return self._fallback_detection(image_path)
        
        try:
            print(f"Reading image from {image_path}")
            img = cv2.imread(image_path)
            if img is None:
                print(f"Error: Could not read image at {image_path}")
                return {"nodes": [], "issues": []}
            
            print(f"Image loaded, shape: {img.shape}")
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Perform YOLO inference
            detections = None
            print("Running YOLO inference...")
            
            try:
                # Check if using ultralytics YOLO
                if hasattr(self.model, 'predict'):
                    # Ultralytics YOLO
                    print("Using ultralytics YOLO predict")
                    results = self.model.predict(img_rgb)
                    boxes = results[0].boxes
                    detections = []
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = box.conf[0].item()
                        cls = box.cls[0].item()
                        detections.append([x1, y1, x2, y2, conf, cls])
                    detections = np.array(detections)
                else:
                    # YOLOv5 PyTorch
                    print("Using YOLOv5 PyTorch model")
                    results = self.model(img_rgb)
                    detections = results.xyxy[0].detach().cpu().numpy()
            except Exception as e:
                print(f"PyTorch inference failed: {e}, trying ONNX...")
                # Try ONNX path
                try:
                    detections = self._run_onnx_inference(img_rgb)
                except Exception as e2:
                    print(f"ONNX inference failed: {e2}")
                    return self._fallback_detection(image_path)
            
            print(f"Inference complete, found {len(detections) if detections is not None else 0} detections")
            
            if detections is None or len(detections) == 0:
                print("No detections found")
                return {"nodes": [], "issues": []}
                
            nodes = []
            issues = []
            
            print("Processing detections...")
            for detection in detections:
                if len(detection) >= 6:  # x1, y1, x2, y2, confidence, class_id
                    x1, y1, x2, y2, confidence, class_id = detection[:6]
                    
                    if confidence >= self.conf_threshold:
                        # Convert coordinates
                        x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                        
                        # Get class name
                        class_id = int(class_id)
                        if class_id < len(self.symbol_classes):
                            symbol_type = self.symbol_classes[class_id]
                        else:
                            symbol_type = f"unknown_{class_id}"
                        
                        # Determine node kind
                        kind = self._get_symbol_kind(symbol_type)
                        
                        # Create node
                        node = Node(
                            id=f"yolo_symbol_{len(nodes)}",
                            kind=kind,
                            type=symbol_type,
                            bbox=BoundingBox(x=x, y=y, w=w, h=h),
                            confidence=float(confidence)
                        )
                        nodes.append(node)
                        
                        # Flag low confidence detections
                        if confidence < 0.7:
                            issue_id = str(uuid.uuid4())
                            issues.append(Issue(
                                id=f"issue_{issue_id}",
                                severity="info",
                                message=f"Low confidence YOLO detection ({confidence:.2f}) for {symbol_type}",
                                targetId=node.id
                            ))
            
            print(f"Found {len(nodes)} symbols")
            
            # Skip unknown symbol detection for now to avoid issues
            # unknown_issues = self._detect_unknown_symbols(img, nodes)
            # issues.extend(unknown_issues)
            
            return {"nodes": nodes, "issues": issues}
            
        except Exception as e:
            print(f"Error during YOLO detection: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_detection(image_path)
    
    def _run_onnx_inference(self, img_rgb: np.ndarray) -> np.ndarray:
        """Run inference using ONNX model."""
        # Preprocess image for ONNX model
        input_size = (640, 640)  # Standard YOLO input size
        img_resized = cv2.resize(img_rgb, input_size)
        img_normalized = img_resized.astype(np.float32) / 255.0
        img_transposed = np.transpose(img_normalized, (2, 0, 1))
        img_batch = np.expand_dims(img_transposed, axis=0)
        
        # Run inference
        input_name = self.model.get_inputs()[0].name
        outputs = self.model.run(None, {input_name: img_batch})
        
        # Process outputs (this may need adjustment based on your ONNX model structure)
        detections = outputs[0]  # Assuming first output contains detections
        return detections
    
    def _get_symbol_kind(self, symbol_type: str) -> str:
        """Determine the kind of symbol based on type."""
        equipment_types = ["pump", "tank", "valve_manual", "valve_control", "heat_exchanger", "compressor", "filter", "separator", "reactor"]
        instrument_types = ["instrument_bubble"]
        
        if symbol_type in equipment_types:
            return "equipment"
        elif symbol_type in instrument_types:
            return "instrument"
        else:
            return "unknown"
    
    def _detect_unknown_symbols(self, img: np.ndarray, known_nodes: List[Node]) -> List[Issue]:
        """Detect potential unknown symbols using contour detection."""
        issues = []
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Edge detection and contour finding
        edges = cv2.Canny(img_gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        min_contour_area = 400
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_contour_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if this contour overlaps with any known symbol
                is_known = False
                for node in known_nodes:
                    bbox = node.bbox
                    # Calculate intersection
                    x_overlap = max(0, min(x + w, bbox.x + bbox.w) - max(x, bbox.x))
                    y_overlap = max(0, min(y + h, bbox.y + bbox.h) - max(y, bbox.y))
                    overlap_area = x_overlap * y_overlap
                    
                    if overlap_area > 0.3 * min(area, bbox.w * bbox.h):
                        is_known = True
                        break
                
                if not is_known:
                    issue_id = str(uuid.uuid4())
                    issues.append(Issue(
                        id=f"issue_{issue_id}",
                        severity="warn",
                        message=f"Unknown symbol detected at coordinates ({x}, {y}). Not recognized by YOLO model.",
                        targetId=None
                    ))
        
        return issues
    
    def _fallback_detection(self, image_path: str) -> Dict[str, Any]:
        """Fallback to template matching if YOLO is not available."""
        try:
            from backend.services.symbols import detect_symbols
            return detect_symbols(image_path)
        except ImportError:
            print("Error importing symbols module, returning empty results")
            return {"nodes": [], "issues": []}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if self.model is None:
            return {"status": "no_model_loaded"}
        
        info = {
            "status": "model_loaded",
            "device": str(self.device),
            "symbol_classes": self.symbol_classes,
            "conf_threshold": self.conf_threshold
        }
        
        if hasattr(self.model, 'names'):
            info["class_names"] = self.model.names
        
        return info

# Global detector instance
yolo_detector = YOLOSymbolDetector()

def detect_symbols_yolo(image_path: str, model_path: Optional[str] = None, conf_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Main function to detect symbols using YOLO.
    If model_path is provided, loads the model first.
    """
    global yolo_detector
    
    try:
        if model_path and model_path != getattr(yolo_detector, 'model_path', None):
            yolo_detector = YOLOSymbolDetector(model_path, conf_threshold)
        
        return yolo_detector.detect_symbols(image_path)
    except Exception as e:
        import traceback
        print(f"Error in YOLO detection: {e}")
        traceback.print_exc()
        # Fallback to template matching
        try:
            from backend.services.symbols import detect_symbols
            return detect_symbols(image_path)
        except Exception as e2:
            print(f"Error in fallback detection: {e2}")
            return {"nodes": [], "issues": []}

def get_yolo_model_info() -> Dict[str, Any]:
    """Get information about the current YOLO model."""
    try:
        return yolo_detector.get_model_info()
    except Exception as e:
        print(f"Error getting YOLO model info: {e}")
        return {"status": "error", "message": str(e)}
