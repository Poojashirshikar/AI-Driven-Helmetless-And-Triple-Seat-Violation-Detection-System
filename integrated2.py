import cv2
from ultralytics import YOLO

# ==========================================
# LOAD YOLO MODELS
# ==========================================
motorcycle_model = YOLO('weights/motorcycle.pt')
helmet_model = YOLO('weights/helmet.pt')

CONFIDENCE_THRESHOLD = 0.5

# ==========================================
# DETECT VIOLATIONS
# ==========================================
def detect_violations(frame):

    motorcycle_results = motorcycle_model(frame)

    for result in motorcycle_results:

        boxes = result.boxes.xyxy
        classes = result.boxes.cls

        for box, cls in zip(boxes, classes):

            x1, y1, x2, y2 = map(int, box)

            # ==========================================
            # MOTORCYCLE / TRIPLE SEAT LABEL
            # ==========================================
            if int(cls) == 0:
                label = "Two Wheeler"
                color = (255, 165, 0)
            else:
                label = "Triple Seat"
                color = (0, 0, 255)

            # Draw Motorcycle Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

            # ==========================================
            # CROP MOTORCYCLE REGION
            # ==========================================
            motorcycle_region = frame[y1:y2, x1:x2]

            if motorcycle_region.size == 0:
                continue

            # ==========================================
            # HELMET DETECTION
            # ==========================================
            helmet_results = helmet_model(motorcycle_region)

            no_helmet_detected = False

            for helmet_result in helmet_results:

                for helmet_box, helmet_class, confidence in zip(
                    helmet_result.boxes.xyxy,
                    helmet_result.boxes.cls,
                    helmet_result.boxes.conf
                ):

                    if confidence < CONFIDENCE_THRESHOLD:
                        continue

                    hx1, hy1, hx2, hy2 = map(int, helmet_box)

                    # ==========================================
                    # HELMET LABEL
                    # ==========================================
                    if int(helmet_class) == 0:
                        helmet_label = "Helmet"
                        helmet_color = (0, 255, 0)
                    else:
                        helmet_label = "No Helmet"
                        helmet_color = (0, 0, 255)
                        no_helmet_detected = True

                    # ==========================================
                    # DRAW HELMET BOX
                    # ==========================================
                    cv2.rectangle(
                        frame,
                        (x1 + hx1, y1 + hy1),
                        (x1 + hx2, y1 + hy2),
                        helmet_color,
                        2
                    )

                    cv2.putText(
                        frame,
                        helmet_label,
                        (x1 + hx1, y1 + hy1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        helmet_color,
                        2
                    )

            # ==========================================
            # VIOLATION DISPLAY
            # ==========================================
            if no_helmet_detected:

                cv2.rectangle(
                    frame,
                    (x1, y2 + 5),
                    (x1 + 220, y2 + 45),
                    (0, 0, 255),
                    -1
                )

                cv2.putText(
                    frame,
                    "HELMET VIOLATION",
                    (x1 + 10, y2 + 32),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

            # ==========================================
            # TRIPLE SEAT VIOLATION
            # ==========================================
            if int(cls) == 1:

                cv2.rectangle(
                    frame,
                    (x1, y2 + 50),
                    (x1 + 220, y2 + 90),
                    (0, 0, 255),
                    -1
                )

                cv2.putText(
                    frame,
                    "TRIPLE SEAT VIOLATION",
                    (x1 + 10, y2 + 78),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                

    return frame