# drone-cpp


# 🚁 Drone Person-Centered GPS Tracking System

A C++ MAVSDK-based application that automatically centers a drone on a detected person and transmits the GPS coordinates to a base station.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   YOLOv8 Model  │───▶│  Offset Calc &   │───▶│  Base Station   │
│ (Person Detect) │    │  Drone Control   │    │ Communication   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Local GPS Storage│
                       │    (Backup)      │
                       └──────────────────┘
```

## 📁 Project Structure

```
drone-cpp/
├── CMakeLists.txt              # Build configuration
├── README.md                   # This file
├── design.md                   # Detailed design document
├── .gitignore                  # Git ignore rules
├── include/
│   └── utils.hpp              # Header with structs and function declarations
├── src/
│   ├── offset.cpp             # Main person centering logic
│   └── transmit.cpp           # GPS transmission to base station
├── data/
│   └── gps_coordinates.txt    # Local GPS storage (created at runtime)
└── bin/                       # Compiled executables (created at build)
    ├── drone_functions        # Main centering application
    └── transmit_location      # Transmission test application
```

## 🛠️ Prerequisites

### System Requirements
- **OS**: Windows 10+ or Linux (Ubuntu 18.04+)
- **Compiler**: GCC 7+, Clang 6+, or MSVC 2019+
- **CMake**: Version 3.10.2 or higher
- **MAVSDK**: Latest stable version

### Hardware Requirements
- Compatible drone (PX4 or ArduPilot autopilot)
- Companion computer (Raspberry Pi, NVIDIA Jetson, etc.)
- Camera for person detection
- Network connection for base station communication

### Software Dependencies

#### MAVSDK Installation

**Ubuntu/Linux:**
```bash
# Install from package manager (recommended)
sudo apt update
sudo apt install libmavsdk-dev

# Or build from source
git clone https://github.com/mavlink/MAVSDK.git
cd MAVSDK
cmake -Bbuild -H. -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
sudo cmake --build build --target install
```

**Windows:**
```powershell
# Using vcpkg (recommended)
vcpkg install mavsdk

# Or download pre-built binaries from MAVSDK releases
```

## 🔧 Building the Project

### Clone and Build
```bash
git clone <your-repo-url>
cd drone-cpp

# Create build directory
mkdir build && cd build

# Configure and build
cmake ..
cmake --build .

# Or use make on Linux
make -j$(nproc)
```

### Build Outputs
After successful build, you'll find:
- `bin/drone_functions` - Main person centering application
- `bin/transmit_location` - Base station transmission test
- `data/` - Directory for GPS coordinate storage

## 🚀 Usage

### 1. Configure Base Station
Edit the base station settings in `transmit.cpp`:
```cpp
constexpr const char* BASE_STATION_IP = "192.168.1.100";  // Your base station IP
constexpr int BASE_STATION_PORT = 8080;                   // Your base station port
```

### 2. Run Person Centering System
```bash
# Connect drone via USB or network
./bin/drone_functions

# Or specify custom connection
./bin/drone_functions udp://192.168.1.10:14540
```

### 3. Test Base Station Communication
```bash
# Test transmission without drone
./bin/transmit_location
```

## 📊 Configuration Parameters

### Frame and Detection Settings
```cpp
constexpr int FRAME_WIDTH = 640;                    // Camera frame width
constexpr int FRAME_HEIGHT = 480;                   // Camera frame height
constexpr int CENTERING_THRESHOLD_X = 10;           // Centering tolerance (pixels)
constexpr int CENTERING_THRESHOLD_Y = 10;           // Centering tolerance (pixels)
```

### Movement Parameters
```cpp
constexpr float MAX_VELOCITY = 2.0f;                // Maximum drone speed (m/s)
constexpr float VELOCITY_SCALING_FACTOR = 0.01f;    // Pixel-to-velocity conversion
```

### Communication Settings
```cpp
constexpr int MAX_RETRY_ATTEMPTS = 3;               // Transmission retry limit
constexpr int RETRY_DELAY_MS = 1000;                // Delay between retries
```

## 🔌 Integration with YOLOv8

The system expects person detection data in this format:

```cpp
PersonBoundingBox person = {
    .x_min = 200,        // Left edge of bounding box
    .y_min = 150,        // Top edge of bounding box  
    .x_max = 400,        // Right edge of bounding box
    .y_max = 350,        // Bottom edge of bounding box
    .confidence = 0.85f  // Detection confidence (0.0-1.0)
};
```

### Integration Steps:
1. **Replace simulation data** in `offset.cpp` with real YOLO detections
2. **Add camera interface** (OpenCV, GStreamer, etc.)
3. **Implement YOLO inference** pipeline
4. **Add detection filtering** (confidence threshold, person class only)

## 📡 Base Station Protocol

### Message Format (JSON)
```json
{
    "message_type": "gps_coordinates",
    "timestamp": 1674123456789,
    "latitude": 47.39774200,
    "longitude": 8.54559400,
    "altitude": 123.45
}
```

### Expected Response
Base station should respond with acknowledgment:
```json
{
    "status": "received",
    "message_id": "12345"
}
```

## 🐛 Troubleshooting

### Common Issues

**1. MAVSDK Connection Failed**
```bash
# Check drone connection
ls /dev/ttyACM*  # Linux
# or
ls /dev/ttyUSB*  # Linux

# Test with QGroundControl first
```

**2. Build Errors**
```bash
# Ensure MAVSDK is properly installed
pkg-config --cflags --libs mavsdk

# Check CMake can find MAVSDK
cmake .. -DCMAKE_VERBOSE_MAKEFILE=ON
```

**3. Network Transmission Failed**
```bash
# Test base station connectivity
telnet 192.168.1.100 8080

# Check firewall settings
sudo ufw allow 8080  # Linux
```

**4. Permission Denied (Linux)**
```bash
# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER
# Logout and login again
``