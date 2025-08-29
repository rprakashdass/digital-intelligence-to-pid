import pytesseract
from PIL import Image
import numpy as np
from typing import List
from ..models import Text, BoundingBox

# --- Tesseract Configuration ---
# On Windows, you may need to set the path to the Tesseract executable.
# Update this path if you installed Tesseract in a different location.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_image(image_path: str, use_easyocr: bool = False) -> List[Text]:
    """
    Performs OCR on an image and returns a list of text blocks.
    - Tries to correct for vertical text by rotating the image.
    """
    if use_easyocr:
        # Placeholder for EasyOCR integration
        print("EasyOCR not implemented, falling back to pytesseract.")
        pass

    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return []

    # --- Pytesseract OCR ---
    # Get detailed data including text, position, and confidence
    # We run it twice: once normally, once rotated, and take the best result
    # based on average confidence. This is a simple heuristic for vertical text.

    data_normal = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    conf_normal = [int(c) for c in data_normal['conf'] if int(c) > -1]
    avg_conf_normal = np.mean(conf_normal) if conf_normal else 0

    img_rotated = img.rotate(90, expand=True)
    data_rotated = pytesseract.image_to_data(img_rotated, output_type=pytesseract.Output.DICT)
    conf_rotated = [int(c) for c in data_rotated['conf'] if int(c) > -1]
    avg_conf_rotated = np.mean(conf_rotated) if conf_rotated else 0

    data = data_normal
    is_rotated = False
    if avg_conf_rotated > avg_conf_normal:
        data = data_rotated
        is_rotated = True
        print("Used rotated image for OCR based on higher confidence.")

    texts: List[Text] = []
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        # We only care about actual words
        if int(data['conf'][i]) > 60 and data['text'][i].strip():
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            
            if is_rotated:
                # Un-rotate the bounding box coordinates
                img_w, img_h = img_rotated.size
                x, y = y, img_w - (x + w)
                w, h = h, w

            texts.append(
                Text(
                    id=f"text_{i}",
                    content=data['text'][i],
                    bbox=BoundingBox(x=x, y=y, w=w, h=h)
                )
            )
    
    # Simple line aggregation could be added here if needed, but for now, we return words.
    return texts
