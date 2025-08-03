#pragma once

#include <string>

Offset calculate_offset(const PersonBoundingBox& person);
VelocityCommand calculate_velocity_command(const Offset& offset);
bool store_coordinates_locally(const GPSCoordinates& coords);
bool transmit_coordinates_to_base(const GPSCoordinates& coords);
int get_person_center_x(const PersonBoundingBox& person);
int get_person_center_y(const PersonBoundingBox& person);

// Frame configuration
constexpr int FRAME_WIDTH = 640;
constexpr int FRAME_HEIGHT = 480;
constexpr int CENTERING_THRESHOLD_X = 10;
constexpr int CENTERING_THRESHOLD_Y = 10;

// Velocity limits for drone movement (m/s)
constexpr float MAX_VELOCITY = 2.0f;
constexpr float VELOCITY_SCALING_FACTOR = 0.01f; // pixels to m/s conversion

// GPS coordinates structure
struct GPSCoordinates {
    double latitude;
    double longitude;
    double altitude;
    long long timestamp_ms;
};

// Person detection result from YOLO
struct PersonBoundingBox {
    int x_min;
    int y_min;
    int x_max;
    int y_max;
    float confidence;
};

// Calculated offset from frame center
struct Offset {
    int x;
    int y;
    bool is_centered;
};

// Velocity commands for drone movement
struct VelocityCommand {
    float north_m_s;
    float east_m_s;
    float down_m_s;  // Should remain 0 for horizontal-only movement
};

