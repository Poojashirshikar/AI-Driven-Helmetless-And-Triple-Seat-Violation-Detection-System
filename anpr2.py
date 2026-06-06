import os
import sys
from pathlib import Path
from paddleocr import PaddleOCR
import re
from datetime import datetime
from sqldb1 import insert_license_plate
from sqldb1 import is_similar_plate

# File Path Setup
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))

# Suppress Logging for Cleaner Output
from ultralytics.utils import LOGGER
LOGGER.setLevel(50)
import logging
logging.getLogger("ppocr").setLevel(logging.ERROR)  # Suppress debug logs

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True)


def perform_ocr_on_image(frame, coordinates):
    """Perform OCR on a given image region and return detected text with violation details."""
    
    x, y, w, h = map(int, coordinates)
    cropped_img = frame[y:h, x:w]  # Crop the plate region
    
    # Perform OCR
    results = ocr.ocr(cropped_img, det=True, rec=True, cls=False)
    
    detected_texts = []
    if results and isinstance(results, list) and len(results) > 0 and results[0]:
        for res in results[0]:
            text = res[1][0]  # Extracted text
            confidence = res[1][1]  # Confidence score
            pattern = re.compile('[\W]')
            text = pattern.sub('', text)
            text = text.replace("???", "").strip()
            text = text.replace("O", "0").strip()
            text = text.replace("粤", "").strip()
            if confidence > 0.7 and text not in {".", "?"}:
                detected_texts.append(text)

    # Join detected texts
    current_text = " ".join(detected_texts)

    from integrated import violation_type_global

    if current_text:
        if not is_similar_plate(current_text):
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            insert_license_plate(start_time, end_time, current_text, violation_type_global)

    return current_text   
 


