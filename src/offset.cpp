#include "utils.hpp"
#include <mavsdk/mavsdk.h>
#include <mavsdk/plugins/telemetry/telemetry.h>
#include <mavsdk/plugins/offboard/offboard.h>
#include <iostream>
#include <fstream>
#include <chrono>
#include <thread>
#include <cmath>
#include <iomanip>

using namespace mavsdk;

// TODO: Replace with actual YOLOv8 detection logic

PersonBoundingBox get_person_detection() {
    // Simulate a person detection
    return {200, 150, 280, 300, 0.85f};
}

// Helper function implementations
int get_person_center_x(const PersonBoundingBox& person) {
    return (person.x_min + person.x_max) / 2;
}

int get_person_center_y(const PersonBoundingBox& person) {
    return (person.y_min + person.y_max) / 2;
}

Offset calculate_offset(const PersonBoundingBox& person) {
    int frame_center_x = FRAME_WIDTH / 2;
    int frame_center_y = FRAME_HEIGHT / 2;
    
    int person_center_x = get_person_center_x(person);
    int person_center_y = get_person_center_y(person);
    
    Offset offset;
    offset.x = person_center_x - frame_center_x;
    offset.y = person_center_y - frame_center_y;
    
  
    offset.is_centered = (std::abs(offset.x) <= CENTERING_THRESHOLD_X && 
                         std::abs(offset.y) <= CENTERING_THRESHOLD_Y);
    
    return offset;
}

VelocityCommand calculate_velocity_command(const Offset& offset) {
    VelocityCommand cmd;
    
    if (offset.is_centered) {
        
        cmd.north_m_s = 0.0f;
        cmd.east_m_s = 0.0f;
        cmd.down_m_s = 0.0f;
        return cmd;
    }
    
    // Calculate proportional velocity based on offset
    // Note: In NED frame, positive North is forward, positive East is right
    // We need to map screen coordinates to NED frame
    
    // X offset (horizontal) maps to East velocity
    cmd.east_m_s = std::max(-MAX_VELOCITY, 
                            std::min(MAX_VELOCITY, 
                                   offset.x * VELOCITY_SCALING_FACTOR));
    
    // Y offset (vertical) maps to North velocity (inverted because screen Y increases downward)
    cmd.north_m_s = std::max(-MAX_VELOCITY, 
                             std::min(MAX_VELOCITY, 
                                    -offset.y * VELOCITY_SCALING_FACTOR));
    
    cmd.down_m_s = 0.0f; // No vertical movement
    
    return cmd;
}

bool store_coordinates_locally(const GPSCoordinates& coords) {
    std::ofstream outfile("data/gps_coordinates.txt", std::ios_base::app);
    if (!outfile.is_open()) {
        std::cerr << "Error: Unable to open local storage file." << std::endl;
        return false;
    }
    
    outfile << std::fixed << std::setprecision(8)
            << "Timestamp: " << coords.timestamp_ms
            << ", Lat: " << coords.latitude
            << ", Lon: " << coords.longitude
            << ", Alt: " << coords.altitude << " m"
            << std::endl;
    
    outfile.close();
    std::cout << "GPS coordinates stored locally." << std::endl;
    return true;
}

class DroneController {
private:
    std::shared_ptr<s> system;
    std::shared_ptr<Telemetry> telemetry;
    std::shared_ptr<Offboard> offboard;
    bool is_connected;
    
public:
    DroneController() : is_connected(false) {}
    
    bool connect(const std::string& connection_url = "udp://:14540") {
        Mavsdk mavsdk{Mavsdk::Configuration{Mavsdk::ComponentType::GroundStation}};
        
        ConnectionResult connection_result = mavsdk.add_any_connection(connection_url);
        if (connection_result != ConnectionResult::Success) {
            std::cerr << "Connection failed: " << connection_result << std::endl;
            return false;
        }
        
        std::cout << "Waiting to discover system..." << std::endl;
        auto prom = std::promise<std::shared_ptr<s>>{};
        auto fut = prom.get_future();
        
        Mavsdk::NewSystemHandle handle = mavsdk.subscribe_on_new_system([&mavsdk, &prom, &handle]() {
            auto system = mavsdk.systems().back();
            if (system->has_autopilot()) {
                mavsdk.unsubscribe_on_new_system(handle);
                prom.set_value(system);
            }
        });
        
        if (fut.wait_for(std::chrono::seconds(3)) == std::future_status::timeout) {
            std::cerr << "No autopilot found." << std::endl;
            return false;
        }
        
        system = fut.get();
        telemetry = std::make_shared<Telemetry>(system);
        offboard = std::make_shared<Offboard>(system);
        
        is_connected = true;
        std::cout << "Connected to drone successfully." << std::endl;
        return true;
    }
    
    GPSCoordinates get_current_gps() {
        GPSCoordinates coords = {0, 0, 0, 0};
        
        if (!is_connected) {
            std::cerr << "Error: Not connected to drone." << std::endl;
            return coords;
        }
        
        auto position = telemetry->position();
        coords.latitude = position.latitude_deg;
        coords.longitude = position.longitude_deg;
        coords.altitude = position.relative_altitude_m;
        
        // Get current timestamp
        auto now = std::chrono::system_clock::now();
        coords.timestamp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()).count();
        
        return coords;
    }
    
    bool send_velocity_command(const VelocityCommand& cmd) {
        if (!is_connected) {
            std::cerr << "Error: Not connected to drone." << std::endl;
            return false;
        }
        
        Offboard::VelocityNedYaw velocity_command{};
        velocity_command.north_m_s = cmd.north_m_s;
        velocity_command.east_m_s = cmd.east_m_s;
        velocity_command.down_m_s = cmd.down_m_s;
        velocity_command.yaw_deg = NAN; // Keep current yaw
        
        auto result = offboard->set_velocity_ned(velocity_command);
        if (result != Offboard::Result::Success) {
            std::cerr << "Failed to send velocity command: " << result << std::endl;
            return false;
        }
        
        return true;
    }
    
    bool start_offboard_mode() {
        if (!is_connected) return false;
        
       
        VelocityCommand zero_cmd = {0.0f, 0.0f, 0.0f};
        send_velocity_command(zero_cmd);
        
        auto result = offboard->start();
        if (result != Offboard::Result::Success) {
            std::cerr << "Failed to start offboard mode: " << result << std::endl;
            return false;
        }
        
        std::cout << "Offboard mode started successfully." << std::endl;
        return true;
    }
    
    bool stop_offboard_mode() {
        if (!is_connected) return false;
        
        auto result = offboard->stop();
        return (result == Offboard::Result::Success);
    }
};

int main() {
    std::cout << "Starting Person-Centered GPS Tracking System..." << std::endl;
    
    // Initialize drone controller
    DroneController drone;
    if (!drone.connect()) {
        std::cerr << "Failed to connect to drone. Exiting." << std::endl;
        return -1;
    }
    
    // Start offboard mode for position control
    if (!drone.start_offboard_mode()) {
        std::cerr << "Failed to start offboard mode. Exiting." << std::endl;
        return -1;
    }
    
    // TODO: Replace with actual YOLO detection pipeline
    PersonBoundingBox person = get_person_detection();

    bool person_centered = false;

    while (!person_centered) {
        // Calculate offset from frame center
        Offset offset = calculate_offset(person);

        std::cout << "Offset from center: X=" << offset.x << ", Y=" << offset.y << std::endl;
        std::cout << "Person centered: " << (offset.is_centered ? "YES" : "NO") << std::endl;

        if (offset.is_centered) {
            // Person is centered, capture GPS coordinates
            std::cout << "\n🎯 Person is centered! Capturing GPS coordinates..." << std::endl;

            GPSCoordinates coords = drone.get_current_gps();
            std::cout << std::fixed << std::setprecision(8)
                      << "GPS Coordinates captured:" << std::endl
                      << "  Latitude: " << coords.latitude << "°" << std::endl
                      << "  Longitude: " << coords.longitude << "°" << std::endl
                      << "  Altitude: " << coords.altitude << " m" << std::endl;

            // Store coordinates locally
            if (store_coordinates_locally(coords)) {
                std::cout << "✅ Coordinates stored locally." << std::endl;
            }

            // Transmit coordinates to base station
            if (transmit_coordinates_to_base(coords)) {
                std::cout << "✅ Coordinates transmitted to base station." << std::endl;
            } else {
                std::cerr << "❌ Failed to transmit coordinates to base station." << std::endl;
            }

            person_centered = true;
        } else {
            // Calculate and send velocity command to center the drone
            VelocityCommand vel_cmd = calculate_velocity_command(offset);

            std::cout << "Sending velocity command:" << std::endl
                      << "  North: " << vel_cmd.north_m_s << " m/s" << std::endl
                      << "  East: " << vel_cmd.east_m_s << " m/s" << std::endl
                      << "  Down: " << vel_cmd.down_m_s << " m/s" << std::endl;

            if (drone.send_velocity_command(vel_cmd)) {
                std::cout << "✅ Velocity command sent successfully." << std::endl;
            } else {
                std::cerr << "❌ Failed to send velocity command." << std::endl;
            }

            // Wait for drone to move (in real implementation, this would be based on actual movement)
            std::this_thread::sleep_for(std::chrono::seconds(2));

            // Get the next simulated detection
            person = get_person_detection();
        }
    }
    
    // Stop offboard mode
    drone.stop_offboard_mode();
    
    if (person_centered) {
        std::cout << "\n🎉 Mission completed successfully!" << std::endl;
    } else {
        std::cout << "\n⚠️ Person centering failed after all attempts." << std::endl;
    }
    
    return 0;
}