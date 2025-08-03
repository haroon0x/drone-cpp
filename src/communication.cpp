#include "../include/communication.hpp"

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

BaseStationCommunicator::BaseStationCommunicator(const std::string& ip, int port)
    : server_ip(ip), server_port(port) {
#ifdef _WIN32
    winsock_initialized = false;
#endif
    initialize_networking();
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