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
            - list: A list of bounding boxes for detected persons. Each bounding box is a
              tuple of (x_min, y_min, x_max, y_max, confidence).
            - numpy.ndarray: The frame with detections annotated.
    """
    results = model(frame)
    persons = []
    annotated_frame = results[0].plot()

    # Iterate through detection results to find 'person' (class ID 0 in COCO dataset)
    for r in results:
        for i, c in enumerate(r.boxes.cls):
            if model.names[int(c)] == 'person':
                # Get the bounding box coordinates and confidence
                bbox = r.boxes.xyxy[i].cpu().numpy()
                confidence = r.boxes.conf[i].cpu().numpy()
                persons.append((bbox[0], bbox[1], bbox[2], bbox[3], float(confidence)))

    return persons, annotated_frame


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

        persons, annotated_frame = scan_for_person(frame)

        if persons:
            print(f"Detected {len(persons)} person(s).")
            for person in persons:
                print(f"  - BBox: {person}")
        else:
            print("No person detected.")

        cv2.imshow("YOLOv8 Inference", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()