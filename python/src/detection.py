import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

def scan_for_person(frame):
    """
    Scans a given frame for the presence of a person using YOLOv8.

    Args:
        frame (numpy.ndarray): The image frame to scan.

    Returns:
        tuple: A tuple containing:
            - bool: True if a person is detected, False otherwise.
            - numpy.ndarray: The frame with detections annotated.
    """
    results = model(frame)
    person_detected = False
    annotated_frame = results[0].plot()

    # Iterate through detection results to find 'person' (class ID 0 in COCO dataset)
    for r in results:
        for c in r.boxes.cls:
            if model.names[int(c)] == 'person':
                person_detected = True
                break
        if person_detected:
            break
            
    return person_detected, annotated_frame


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

    while True:
        success, frame = cap.read()

        if not success:
            print("Error: Could not read frame from video stream.")
            break

        person_found, annotated_frame = scan_for_person(frame)

        if person_found:
            print("Person detected!")
        else:
            print("No person detected.")

        cv2.imshow("YOLOv8 Inference", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
