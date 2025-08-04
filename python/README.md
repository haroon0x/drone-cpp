# Person-Centered GPS Tracking Drone

This project contains the Python application for controlling a drone to detect a person, center them in the camera frame, and transmit their GPS coordinates to a base station.

## Project Overview

The application uses `pymavlink` to communicate with a drone's flight controller. It is designed to be run in a simulated environment (SITL) for testing or deployed on a physical drone.

The core logic is as follows:
1.  **Connect** to the drone using the connection URL specified in `src/config.py`.
2.  **Arm** the drone and set it to `GUIDED` mode.
3.  **Detect a person** (currently simulated) and calculate the offset from the camera's center.
4.  **Send velocity commands** to the drone to center it on the person.
5.  Once centered, **capture the drone's GPS coordinates**.
6.  **Transmit** the coordinates to a base station and **store them locally** in `gps_coordinates.csv`.

## Getting Started

### 1. Prerequisites

-   Python 3.12+
-   `uv` (or `pip`) for package management
-   A MAVLink-compatible flight simulator (like SITL) or a physical drone.

### 2. Setup

**a. Clone the repository:**
```bash
git clone <repository_url>
cd drone-cpp/python
```

**b. Create and activate a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**c. Install the required dependencies:**
```bash
uv pip install -r requirements.txt
```

### 3. Configuration

The drone's connection URL is configured in `src/config.py`.

-   **For a SITL simulator (default):**
    ```python
    CONNECTION_URL = "udp:127.0.0.1:14540"
    ```

-   **For a physical drone via telemetry radio:**
    Update the `CONNECTION_URL` to match your device's serial port.
    ```python
    # Example for Linux
    CONNECTION_URL = "/dev/ttyUSB0"

    # Example for Windows
    CONNECTION_URL = "COM3"
    ```

### 4. Running the Application

**a. Start your simulator or connect your drone.**

**b. Run the main application:**
```bash
python main.py
```

The application will then connect to the drone, perform the centering mission, and print the results to the console.

## Project Structure

-   `main.py`: The main entry point for the application.
-   `src/`: Contains the core source code.
    -   `config.py`: Configuration settings (e.g., connection URL).
    -   `drone_controller.py`: Handles all communication with the drone.
    -   `offset.py`: Logic for calculating the centering offset and velocity commands.
    -   `communication.py`: Manages TCP communication with the base station.
-   `design.md`: The project's technical design and future work.
-   `requirements.txt`: A list of Python dependencies.
