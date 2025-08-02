# drone-cpp

A C++ MAVSDK-based application that automatically centers a drone on a detected person and transmits the GPS coordinates to a base station.


🏗️ System Architecture
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