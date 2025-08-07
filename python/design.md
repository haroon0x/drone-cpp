# Person-Centered GPS Location Tracking via Drone

- **Detects a person** using an external YOLOv8 model
- **Centers** the person in the camera frame by adjusting the drone's **horizontal position** only (no altitude change)
- Once centered, **fetches the GPS coordinates** of the drone's position
- **Transmits coordinates to base station** (with local storage as backup)

---

## 📝 Core Tasks & Implementation

This project is implemented in Python and structured into several core modules:

-   **Drone Controller (`drone_controller.py`):**
    -   **Task:** Manages the connection, state, and movement of the drone.
    -   **Implementation:** Uses `pymavlink` for robust, low-level control. Implements best practices for connecting, arming, setting modes (`GUIDED`), and sending velocity commands while waiting for command acknowledgements.

-   **Centering Logic (`offset.py`):**
    -   **Task:** Calculates the drone's required movement to center a detected person in the camera frame.
    -   **Implementation:** Calculates the pixel offset from the frame center and converts it into a proportional `VelocityCommand` based on the parameters defined in this design document.

-   **Base Station Communication (`communication.py`):**
    -   **Task:** Transmit captured GPS coordinates to a remote base station.
    -   **Implementation:** A TCP client sends JSON-formatted GPS data. Includes a reliable retry mechanism with exponential backoff to handle connection issues.

-   **Main Application (`main.py`):**
    -   **Task:** Orchestrate the entire process from detection to transmission.
    -   **Implementation:** The main loop integrates all modules, manages the centering process, and handles local CSV storage as a fallback.

---

## 🚀 Future Work & Next Steps

1.  **Integrate Real-time YOLOv8 Detection:** Replace the current `get_person_detection()` simulation with a live YOLOv8 model to enable real-world person detection.
2.  **Develop Python Base Station Server:** Create a Python-based TCP server to receive and process the GPS data, making the entire system language-consistent.
3.  **Configuration Management:** Move hardcoded values (e.g., connection URLs, frame dimensions) to an external configuration file (`config.ini`) for easier modification.
4.  **Integration Testing with a Simulator (SITL):** Perform end-to-end testing of the application using a flight simulator to ensure all components work together correctly in a controlled environment before deploying on a physical drone.

---

## Key Parameters

-   **Frame dimensions:** 640x480 pixels
-   **Centering threshold:** ±10 pixels
-   **Movement velocity:** Proportional to offset (max 2 m/s)
-   **GPS precision:** 6 decimal places minimum

## Communication Protocol

-   **Base Station Interface:** TCP/UDP socket or MAVLink protocol
-   **Message Format:** JSON or custom binary format
-   **Retry Logic:** 3 attempts with exponential backoff
-   **Fallback:** Local storage if transmission fails

---

