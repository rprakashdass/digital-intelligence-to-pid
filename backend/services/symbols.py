import cv2
import numpy as np
import os
from typing import List, Tuple, Dict, Any
from backend.models import Node, BoundingBox, Issue
import uuid

# --- Globals for Template Matching ---
TEMPLATES = {}
TEMPLATE_DIR = "data/templates"
DEFAULT_THRESHOLD = 0.7

# List of supported ISA-5.1 symbols
SUPPORTED_SYMBOLS = [
    "pump",
    "valve_manual",
    "valve_control",
    "instrument_bubble",
    "tank"
]

def load_templates():
    """
    Load symbol templates from the data/templates directory.
    Only loads supported symbols defined in SUPPORTED_SYMBOLS.
    """
    if not os.path.isdir(TEMPLATE_DIR):
        print(f"Warning: Template directory not found at '{TEMPLATE_DIR}'.")
        return

    for filename in os.listdir(TEMPLATE_DIR):
        if filename.endswith(".png"):
            template_name = os.path.splitext(filename)[0]
            # Only load supported symbols
            if template_name in SUPPORTED_SYMBOLS:
                path = os.path.join(TEMPLATE_DIR, filename)
                template_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if template_img is not None:
                    TEMPLATES[template_name] = template_img
                    print(f"Loaded template: {template_name}")
            # else:
            #     print(f"Skipping unsupported symbol template: {template_name}")

# Load templates on module import
load_templates()

def non_max_suppression(boxes: List[Tuple[int, int, int, int]], scores: List[float], overlapThresh: float) -> List[int]:
    """
    Simple non-maximum suppression to remove overlapping bounding boxes.
    """
    if len(boxes) == 0:
        return []

    pick = []
    x1 = np.array([b[0] for b in boxes])
    y1 = np.array([b[1] for b in boxes])
    x2 = np.array([b[0] + b[2] for b in boxes])
    y2 = np.array([b[1] + b[3] for b in boxes])
    
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(scores)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))

    return pick


def detect_symbols(image_path: str, threshold: float = DEFAULT_THRESHOLD) -> Dict[str, Any]:
    """
    Detects symbols in an image using template matching.
    Returns both detected symbols as nodes and issues for unknown symbols.
    """
    img_rgb = cv2.imread(image_path)
    if img_rgb is None:
        print(f"Error: Could not read image at {image_path}")
        return {"nodes": [], "issues": []}
    
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    
    all_detections = []
    all_scores = []
    all_boxes = []
    issues = []

    # Perform template matching for supported symbols
    for name, template in TEMPLATES.items():
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        
        loc = np.where(res >= threshold)
        scores = res[loc]

        for pt, score in zip(zip(*loc[::-1]), scores):
            box = (pt[0], pt[1], w, h)
            all_boxes.append(box)
            all_scores.append(score)
            all_detections.append({
                "name": name,
                "box": box,
                "score": score
            })
    
    # Apply basic contour detection to find possible unknown symbols
    # This is a simplified approach to detect potential symbols not in our template set
    edges = cv2.Canny(img_gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    min_contour_area = 400  # Minimum area to consider as a potential symbol
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_contour_area:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check if this contour overlaps significantly with any template match
            is_known = False
            for box in all_boxes:
                box_x, box_y, box_w, box_h = box
                # Calculate intersection
                x_overlap = max(0, min(x + w, box_x + box_w) - max(x, box_x))
                y_overlap = max(0, min(y + h, box_y + box_h) - max(y, box_y))
                overlap_area = x_overlap * y_overlap
                
                if overlap_area > 0.5 * min(area, box_w * box_h):
                    is_known = True
                    break
            
            if not is_known:
                # Create an issue for this unknown symbol
                issue_id = str(uuid.uuid4())
                issues.append(Issue(
                    id=f"issue_{issue_id}",
                    severity="warn",
                    message=f"Unknown symbol detected at coordinates ({x}, {y}). Not matching any supported symbol templates.",
                    targetId=None  # No target ID since it's not in our graph
                ))

    if not all_boxes:
        return {"nodes": [], "issues": issues}

    # Apply Non-Maximum Suppression
    picked_indices = non_max_suppression(all_boxes, all_scores, 0.4)
    
    final_nodes: List[Node] = []
    for i, idx in enumerate(picked_indices):
        detection = all_detections[idx]
        box = detection['box']
        
        # Determine node kind based on symbol type
        symbol_type = detection["name"]
        if symbol_type == "pump":
            kind = "equipment"
        elif symbol_type == "tank":
            kind = "equipment"
        elif symbol_type == "valve_manual" or symbol_type == "valve_control":
            kind = "equipment"
        elif symbol_type == "instrument_bubble":
            kind = "instrument"
        else:
            kind = "unknown"
        
        # Flag low confidence detections
        if detection["score"] < 0.8:
            issue_id = str(uuid.uuid4())
            issues.append(Issue(
                id=f"issue_{issue_id}",
                severity="info",
                message=f"Low confidence detection ({detection['score']:.2f}) for {symbol_type} at coordinates ({box[0]}, {box[1]}).",
                targetId=f"symbol_{i}"
            ))
        
        node = Node(
            id=f"symbol_{i}",
            kind=kind,
            type=symbol_type,
            bbox=BoundingBox(x=box[0], y=box[1], w=box[2], h=box[3]),
            confidence=detection["score"]
        )
        final_nodes.append(node)

    return {"nodes": final_nodes, "issues": issues}
