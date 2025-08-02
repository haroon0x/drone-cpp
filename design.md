# 📄 design.md — Person-Centered GPS Location Tracking via Drone

## 🧠 Objective

Build a **C++ MAVSDK** application for a **scout drone** that performs the following tasks:

- **Detects a person** using an external YOLOv8 model.
- **Centers** the person in the camera frame by adjusting the drone's **horizontal position** only (no altitude change).
- Once centered, **fetches the GPS coordinates** of the drone's position.
- **Stores the coordinates locally** (no need to send to base station for now).

---


### 2. Offset Handling (C++)

Use the bounding box from YOLO to calculate:

cpp
Copy
Edit
offset_x = person_center_x - frame_center_x;
offset_y = person_center_y - frame_center_y;
If the offset is within a threshold → trigger location capture.


- Receives `offset_x` and `offset_y` values from the YOLOv8 module.
- Compares offset to a defined threshold:
If outside the threshold → triggers Offboard control to nudge the drone horizontally.

If within the threshold → triggers GPS capture.


3. MAVSDK Integration (C++)
Core Responsibilities:
Connect to the drone using MAVSDK System.

Use:

Telemetry plugin to fetch real-time GPS coordinates.

Offboard plugin to send horizontal velocity commands to center the drone.

On successful centering:

Log current GPS coordinates (latitude, longitude, optionally altitude) to a local file.



