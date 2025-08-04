#pragma once

#include "utils.hpp"
#include <string>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <thread>
#include <chrono>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
#else
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

// Base station configuration
constexpr const char* BASE_STATION_IP = "127.0.0.1";
constexpr int BASE_STATION_PORT = 8080;
constexpr int MAX_RETRY_ATTEMPTS = 3;
constexpr int RETRY_DELAY_MS = 1000;

class BaseStationCommunicator {
private:
    std::string server_ip;
    int server_port;
    
#ifdef _WIN32
    bool winsock_initialized;
#endif
    
    bool initialize_networking();
    void cleanup_networking();
    std::string create_gps_message(const GPSCoordinates& coords);
    bool send_tcp_message(const std::string& message);

public:
    BaseStationCommunicator(const std::string& ip = BASE_STATION_IP, int port = BASE_STATION_PORT);
    ~BaseStationCommunicator();
    
    bool transmit_coordinates(const GPSCoordinates& coords);
};
