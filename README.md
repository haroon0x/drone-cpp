# Drone Person-Centered GPS Tracking System

A C++ MAVSDK-based application that automatically centers a drone on a detected person and transmits the GPS coordinates to a base station.

## Components

*   `drone_client`: The main application for the drone.
*   `base_station_server`: A simple server to receive GPS coordinates from the drone.

## How to Build

```bash
mkdir build && cd build
cmake ..
cmake --build .
```

## How to Run

1.  **Start the server:**

    ```bash
    ./build/bin/base_station_server
    ```

2.  **Run the drone client:**

    ```bash
    ./build/bin/drone_client
    ```
