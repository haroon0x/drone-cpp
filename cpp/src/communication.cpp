#include "../include/communication.hpp"
#include <map>

// Configuration loading function
std::map<std::string, std::string> load_config(const std::string& filename) {
    std::map<std::string, std::string> config;
    std::ifstream file(filename);
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream is_line(line);
        std::string key;
        if (std::getline(is_line, key, '=')) {
            std::string value;
            if (std::getline(is_line, value)) {
                config[key] = value;
            }
        }
    }
    return config;
}

bool BaseStationCommunicator::initialize_networking() {
#ifdef _WIN32
    if (winsock_initialized) return true;
    
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        std::cerr << "WSAStartup failed: " << result << std::endl;
        return false;
    }
    winsock_initialized = true;
#endif
    return true;
}

void BaseStationCommunicator::cleanup_networking() {
#ifdef _WIN32
    if (winsock_initialized) {
        WSACleanup();
        winsock_initialized = false;
    }
#endif
}

BaseStationCommunicator::BaseStationCommunicator() {
#ifdef _WIN32
    winsock_initialized = false;
#endif
    initialize_networking();

    // Load configuration
    auto config = load_config("config.conf");
    server_ip = config["BASE_STATION_IP"];
    server_port = std::stoi(config["BASE_STATION_PORT"]);
}

BaseStationCommunicator::~BaseStationCommunicator() {
    cleanup_networking();
}

std::string BaseStationCommunicator::create_gps_message(const GPSCoordinates& coords) {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(8);
    oss << "{"
        << "\"message_type\":\"gps_coordinates\","
        << "\"timestamp\":