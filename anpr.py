import cv2
import re
from paddleocr import PaddleOCR

# ==========================================
# INITIALIZE OCR
# ==========================================
ocr = PaddleOCR(use_angle_cls=True)

# ==========================================
# OCR FUNCTION
# ==========================================
def perform_ocr_on_image(frame, coordinates):

    x1, y1, x2, y2 = map(int, coordinates)

    # Crop plate region
    cropped_img = frame[y1:y2, x1:x2]

    if cropped_img.size == 0:
        return ""

    # OCR
    results = ocr.ocr(cropped_img)

    detected_texts = []

    if results and len(results) > 0:

        for res in results[0]:

            text = res[1][0]
            confidence = res[1][1]

            # Remove symbols
            text = re.sub(r'[\W]', '', text)

            # Replace O with 0
            text = text.replace("O", "0")

            # Confidence filtering
            if confidence > 0.6:

                detected_texts.append(text)

    final_text = " ".join(detected_texts)

    return final_text