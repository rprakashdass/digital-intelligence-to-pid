import pytesseract
from PIL import Image
import numpy as np
import cv2
from typing import List
import os
import sys
from backend.models import Text, BoundingBox

# --- Tesseract Configuration ---
# Try multiple common Tesseract installation paths on Windows
tesseract_paths = [
    r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
    r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
    # Add any other possible installation paths here
]

# Check for environment variable override first
if os.environ.get('TESSERACT_PATH'):
    pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_PATH')
    print(f"Using Tesseract from environment variable: {pytesseract.pytesseract.tesseract_cmd}")
else:
    # Try to find Tesseract in common locations
    tesseract_found = False
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"Found Tesseract at: {path}")
            tesseract_found = True
            break
    
    if not tesseract_found:
        print("WARNING: Tesseract executable not found. Using mock OCR mode with empty results.")
        
        # Define a mock OCR function that returns empty results
        def mock_ocr_image(image_path, **kwargs):
            print(f"MOCK OCR: Would process {image_path}")
            return []
        
        # Replace the actual OCR function with our mock
        ocr_image = mock_ocr_image

def ocr_image(image_path: str, use_easyocr: bool = False) -> List[Text]:
    """
    Performs OCR on an image and returns a list of text blocks.
    - Tries to correct for vertical text by rotating the image.
    - Uses enhanced preprocessing for engineering diagrams.
    """
    if use_easyocr:
        try:
            import easyocr
            reader = easyocr.Reader(['en'])
            results = reader.readtext(image_path)
            
            texts = []
            for i, (bbox, text, conf) in enumerate(results):
                if conf > 0.3:  # Minimum confidence threshold
                    x = int(min(bbox[0][0], bbox[3][0]))
                    y = int(min(bbox[0][1], bbox[1][1]))
                    w = int(max(bbox[1][0], bbox[2][0]) - x)
                    h = int(max(bbox[2][1], bbox[3][1]) - y)
                    
                    texts.append(
                        Text(
                            id=f"text_{i}",
                            content=text,
                            bbox=BoundingBox(x=x, y=y, w=w, h=h)
                        )
                    )
            return texts
        except ImportError:
            print("EasyOCR not installed, falling back to pytesseract.")
            pass

    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return []

    # --- Enhanced Preprocessing for OCR in Engineering Diagrams ---
    # Convert to OpenCV BGR
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    
    # Scale up small images for better OCR
    h, w = gray.shape[:2]
    scale = 1.0
    if max(h, w) < 1500:
        scale = 2000.0 / max(h, w)  # Increased scale for better resolution
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Enhanced image processing pipeline
    # 1. Noise reduction
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # 2. Adaptive thresholding (better for varying lighting conditions)
    adaptive_thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # 3. Morphological operations to enhance text regions
    # Remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    opening = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Connect nearby text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))  # horizontal kernel
    connected = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    # 4. Invert back to black text on white background for OCR
    pre = cv2.bitwise_not(connected)
    
    # Save preprocessing result for debugging if needed
    # debug_path = os.path.join(os.path.dirname(image_path), "ocr_debug.png")
    # cv2.imwrite(debug_path, pre)
    
    # Back to PIL for pytesseract
    pre_pil = Image.fromarray(pre)

    # --- Improved Pytesseract OCR with Multiple Configurations ---
    def _safe_confs(vals):
        confs = []
        for v in vals:
            try:
                confs.append(float(v))
            except Exception:
                pass
        return [c for c in confs if c > -1]
    
    # Try multiple PSM (Page Segmentation Modes) to improve results for engineering diagrams
    psm_modes = [
        # PSM 6: Assume a single uniform block of text (default)
        {"mode": 6, "desc": "Single uniform block"},
        # PSM 3: Fully automatic page segmentation without OCR
        {"mode": 3, "desc": "Auto page segmentation"},
        # PSM 11: Sparse text - Find as much text as possible, no specific order
        {"mode": 11, "desc": "Sparse text detection"},
        # PSM 4: Assume a single column of text of variable sizes
        {"mode": 4, "desc": "Single column variable size"}
    ]
    
    # For engineering diagrams, allow more characters
    char_whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_/(),.[]{}:;%$&+=<>"
    
    # Try normal and rotated orientations
    orientations = [
        {"angle": 0, "desc": "normal"},
        {"angle": 90, "desc": "rotated 90°"},
        {"angle": -90, "desc": "rotated -90°"}  # Sometimes text can be rotated the other way
    ]
    
    # Initialize variables to track the best results
    best_texts = []
    best_conf = 0
    best_config = {"psm": 0, "orientation": "none"}
    
    # Try each combination of PSM mode and orientation
    for psm in psm_modes:
        for orient in orientations:
            # Create the configuration for tesseract
            tesseract_cfg = f"--oem 3 --psm {psm['mode']} -c preserve_interword_spaces=1"
            tesseract_cfg += f" -c tessedit_char_whitelist={char_whitelist}"
            
            # Rotate the image if needed
            if orient["angle"] != 0:
                curr_img = pre_pil.rotate(orient["angle"], expand=True)
            else:
                curr_img = pre_pil
                
            # Run OCR
            try:
                data = pytesseract.image_to_data(curr_img, output_type=pytesseract.Output.DICT, config=tesseract_cfg)
                
                # Calculate confidence
                confs = _safe_confs(data['conf'])
                avg_conf = np.mean(confs) if confs else 0
                
                # Count recognized words with good confidence
                good_words = sum(1 for conf in confs if conf > 60)
                
                # If this configuration is better than the previous best, save it
                if good_words > 0 and (good_words > len(best_texts) or 
                                       (good_words == len(best_texts) and avg_conf > best_conf)):
                    best_conf = avg_conf
                    best_config = {"psm": psm["mode"], "orientation": orient["desc"]}
                    
                    # Process the results
                    texts = []
                    n_boxes = len(data['level'])
                    for i in range(n_boxes):
                        try:
                            conf_i = float(data['conf'][i])
                        except Exception:
                            conf_i = -1
                            
                        # Only keep results with good confidence and actual content
                        if conf_i > 40 and data['text'][i].strip():
                            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                            
                            # If the image was rotated, transform coordinates back to original orientation
                            if orient["angle"] == 90:
                                img_w, img_h = curr_img.size
                                x, y = y, img_w - (x + w)
                                w, h = h, w
                            elif orient["angle"] == -90:
                                img_w, img_h = curr_img.size
                                x, y = img_h - (y + h), x
                                w, h = h, w
                            
                            # Scale back if we upscaled
                            if scale != 1.0:
                                x = int(x / scale)
                                y = int(y / scale)
                                w = int(w / scale)
                                h = int(h / scale)
                                
                            texts.append(
                                Text(
                                    id=f"text_{i}",
                                    content=data['text'][i],
                                    bbox=BoundingBox(x=x, y=y, w=w, h=h)
                                )
                            )
                    
                    best_texts = texts
            except Exception as e:
                print(f"OCR error with PSM {psm['mode']}, orientation {orient['desc']}: {e}")
                continue
    
    print(f"Best OCR config - PSM: {best_config['psm']}, Orientation: {best_config['orientation']}, Found {len(best_texts)} text elements")
    
    # If no text was found with any configuration, try the original image without preprocessing
    if not best_texts:
        print("No text found with preprocessing, trying original image...")
        try:
            # Try with the original image at PSM 11 (sparse text)
            original_img = Image.open(image_path).convert('L')  # Convert to grayscale
            data = pytesseract.image_to_data(
                original_img, 
                output_type=pytesseract.Output.DICT, 
                config="--oem 3 --psm 11"
            )
            
            # Process results
            texts = []
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                try:
                    conf_i = float(data['conf'][i])
                except Exception:
                    conf_i = -1
                    
                if conf_i > 40 and data['text'][i].strip():
                    texts.append(
                        Text(
                            id=f"text_{i}",
                            content=data['text'][i],
                            bbox=BoundingBox(
                                x=data['left'][i],
                                y=data['top'][i],
                                w=data['width'][i],
                                h=data['height'][i]
                            )
                        )
                    )
            
            if texts:
                print(f"Found {len(texts)} text elements with original image")
                best_texts = texts
        except Exception as e:
            print(f"Error with original image OCR: {e}")
    
    # Try to merge nearby text boxes that likely belong together (e.g. for tags split across multiple detections)
    merged_texts = merge_text_boxes(best_texts)
    
    return merged_texts

def merge_text_boxes(texts: List[Text], max_distance: int = 15) -> List[Text]:
    """
    Merges nearby text boxes that likely belong to the same text element.
    This is useful for tags that may be split across multiple OCR detections.
    """
    if not texts:
        return []
    
    # Sort texts by y-coordinate (top to bottom)
    sorted_texts = sorted(texts, key=lambda t: t.bbox.y)
    
    merged = []
    skip_indices = set()
    
    for i, text1 in enumerate(sorted_texts):
        if i in skip_indices:
            continue
            
        current_text = text1
        current_content = text1.content
        current_bbox = text1.bbox
        
        # Check for nearby texts
        for j, text2 in enumerate(sorted_texts[i+1:], i+1):
            if j in skip_indices:
                continue
                
            # Check if text2 is close to the right of text1
            is_horizontal = (
                abs(text2.bbox.y - current_bbox.y) < max_distance and
                abs(text2.bbox.x - (current_bbox.x + current_bbox.w)) < max_distance * 2
            )
            
            # Check if text2 is directly below text1
            is_vertical = (
                abs(text2.bbox.x - current_bbox.x) < max_distance and
                abs(text2.bbox.y - (current_bbox.y + current_bbox.h)) < max_distance
            )
            
            if is_horizontal or is_vertical:
                # Merge the text content
                if is_horizontal:
                    current_content += " " + text2.content
                else:  # is_vertical
                    current_content += "\n" + text2.content
                
                # Update the bounding box to encompass both
                x_min = min(current_bbox.x, text2.bbox.x)
                y_min = min(current_bbox.y, text2.bbox.y)
                x_max = max(current_bbox.x + current_bbox.w, text2.bbox.x + text2.bbox.w)
                y_max = max(current_bbox.y + current_bbox.h, text2.bbox.y + text2.bbox.h)
                
                current_bbox = BoundingBox(
                    x=x_min,
                    y=y_min,
                    w=x_max - x_min,
                    h=y_max - y_min
                )
                
                skip_indices.add(j)
        
        # Create the merged text element
        merged.append(
            Text(
                id=f"merged_{i}",
                content=current_content.strip(),
                bbox=current_bbox
            )
        )
    
    return merged
