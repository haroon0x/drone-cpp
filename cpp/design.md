# 📄 design.md — Person-Centered GPS Location Tracking via Drone

## 🧠 Objective

Build a **C++ MAVSDK** application for a **scout drone** that performs the following tasks:

- **Detects a person** using an external YOLOv8 model
- **Centers** the person in the camera frame by adjusting the drone's **horizontal position** only (no altitude change)
- Once centered, **fetches the GPS coordinates** of the drone's position
- **Transmits coordinates to base station** (with local storage as backup)

---

## 🏗️ System Architecture

### 1. Person Detection (External YOLOv8 Module)
- Processes camera feed and detects persons
- Returns bounding box coordinates: `[x_min, y_min, x_max, y_max]`
- Calculates person center: `person_center_x = (x_min + x_max) / 2`, `person_center_y = (y_min + y_max) / 2`

### 2. Offset Calculation (C++)
Use the bounding box from YOLO to calculate deviation from frame center:

```cpp
offset_x = person_center_x - frame_center_x;
offset_y = person_center_y - frame_center_y;
```

**Centering Logic:**
- If `abs(offset_x) > THRESHOLD_X` or `abs(offset_y) > THRESHOLD_Y` → trigger drone movement
- If within threshold → trigger GPS capture and transmission

### 3. Drone Control (C++ MAVSDK)

**Core Responsibilities:**
- Connect to drone using MAVSDK System
- Use Telemetry plugin to fetch real-time GPS coordinates
- Use Offboard plugin to send horizontal velocity commands for centering

**Movement Strategy:**
- Calculate proportional velocity based on offset magnitude
- Send velocity commands in NED (North-East-Down) frame
- Maintain current altitude (no vertical movement)

**On Successful Centering:**
- Capture current GPS coordinates (latitude, longitude, altitude)
- Transmit to base station via communication link
- Store locally as backup

---

## 🔧 Implementation Details

### File Structure
```
drone-cpp/
├── CMakeLists.txt
├── include/
│   └── utils.hpp
├── src/
│   ├── offset.cpp          # Offset calculation and centering logic
│   └── transmit.cpp        # GPS transmission to base station
└── data/
    └── gps_coordinates.txt # Local backup storage
```

### Key Parameters
- **Frame dimensions:** 640x480 pixels
- **Centering threshold:** ±10 pixels
- **Movement velocity:** Proportional to offset (max 2 m/s)
- **GPS precision:** 6 decimal places minimum

### Communication Protocol
- **Base Station Interface:** TCP/UDP socket or MAVLink protocol
- **Message Format:** JSON or custom binary format
- **Retry Logic:** 3 attempts with exponential backoff
- **Fallback:** Local storage if transmission fails

---

## 🎯 Success Criteria

1. **Detection Accuracy:** Person successfully detected and tracked
2. **Centering Precision:** Person centered within ±10 pixel threshold
3. **GPS Accuracy:** Coordinates captured with <3m accuracy
4. **Transmission Reliability:** >95% successful transmission rate
5. **Response Time:** Complete cycle (detect → center → transmit) <5 seconds

