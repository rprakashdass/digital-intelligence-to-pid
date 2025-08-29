import cv2
import numpy as np
import os
from typing import List, Tuple
from ..models import Node, BoundingBox

# --- Globals for Template Matching ---
TEMPLATES = {}
TEMPLATE_DIR = "data/templates"
DEFAULT_THRESHOLD = 0.7

def load_templates():
    """
    Load symbol templates from the data/templates directory.
    """
    if not os.path.isdir(TEMPLATE_DIR):
        print(f"Warning: Template directory not found at '{TEMPLATE_DIR}'.")
        return

    for filename in os.listdir(TEMPLATE_DIR):
        if filename.endswith(".png"):
            template_name = os.path.splitext(filename)[0]
            path = os.path.join(TEMPLATE_DIR, filename)
            template_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if template_img is not None:
                TEMPLATES[template_name] = template_img
                print(f"Loaded template: {template_name}")

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


def detect_symbols(image_path: str, threshold: float = DEFAULT_THRESHOLD) -> List[Node]:
    """
    Detects symbols in an image using template matching.
    """
    img_rgb = cv2.imread(image_path)
    if img_rgb is None:
        print(f"Error: Could not read image at {image_path}")
        return []
    
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    
    all_detections = []
    all_scores = []
    all_boxes = []

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

    if not all_boxes:
        return []

    # Apply Non-Maximum Suppression
    picked_indices = non_max_suppression(all_boxes, all_scores, 0.4)
    
    final_nodes: List[Node] = []
    for i, idx in enumerate(picked_indices):
        detection = all_detections[idx]
        box = detection['box']
        
        node = Node(
            id=f"symbol_{i}",
            kind="equipment" if "pump" in detection["name"] else "instrument",
            type=detection["name"],
            bbox=BoundingBox(x=box[0], y=box[1], w=box[2], h=box[3]),
            confidence=detection["score"]
        )
        final_nodes.append(node)

    return final_nodes
