#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <vector>
#include <mutex>
#include <atomic>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
#else
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <signal.h>
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

// Server configuration
constexpr int SERVER_PORT = 8080;
constexpr int MAX_CLIENTS = 10;
constexpr int BUFFER_SIZE = 1024;
constexpr const char* LOG_FILE = "base_station_log.txt";

// GPS coordinate structure (matching your utils.hpp)
struct GPSCoordinates {
    double latitude;
    double longitude;
    double altitude;
    long long timestamp_ms;
    std::string drone_id;
};

class BaseStationServer {
private:
    SOCKET server_socket;
    std::atomic<bool> running;
    std::mutex log_mutex;
    std::vector<std::thread> client_threads;
    int total_connections;
    int successful_receptions;
    
#ifdef _WIN32
    bool winsock_initialized;
#endif

    bool initialize_networking() {
#ifdef _WIN32
        if (winsock_initialized) return true;
        
        WSADATA wsaData;
        int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
        if (result != 0) {
            std::cerr << "❌ WSAStartup failed: " << result << std::endl;
            return false;
        }
        winsock_initialized = true;
        std::cout << "✅ Winsock initialized successfully" << std::endl;
#endif
        return true;
    }
    
    void cleanup_networking() {
#ifdef _WIN32
        if (winsock_initialized) {
            WSACleanup();
            winsock_initialized = false;
        }
#endif
    }
    
    std::string get_current_timestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;
        
        std::ostringstream oss;
        oss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        oss << "." << std::setfill('0') << std::setw(3) << ms.count();
        return oss.str();
    }
    
    void log_message(const std::string& message) {
        std::lock_guard<std::mutex> lock(log_mutex);
        
        std::string timestamp = get_current_timestamp();
        std::string log_entry = "[" + timestamp + "] " + message;
        
        // Print to console
        std::cout << log_entry << std::endl;
        
        // Write to log file
        std::ofstream logfile(LOG_FILE, std::ios_base::app);
        if (logfile.is_open()) {
            logfile << log_entry << std::endl;
            logfile.close();
        }
    }
    
    GPSCoordinates parse_gps_message(const std::string& message) {
        GPSCoordinates coords = {0, 0, 0, 0, "unknown"};
        
        try {
            // Simple JSON parsing (for production, use a proper JSON library)
            size_t lat_pos = message.find("\"latitude\":");
            size_t lon_pos = message.find("\"longitude\":");
            size_t alt_pos = message.find("\"altitude\":");
            size_t time_pos = message.find("\"timestamp\":");
            
            if (lat_pos != std::string::npos) {
                lat_pos += 11; // Skip "latitude":
                size_t lat_end = message.find(",", lat_pos);
                if (lat_end == std::string::npos) lat_end = message.find("}", lat_pos);
                if (lat_end != std::string::npos) {
                    std::string lat_str = message.substr(lat_pos, lat_end - lat_pos);
                    coords.latitude = std::stod(lat_str);
                }
            }
            
            if (lon_pos != std::string::npos) {
                lon_pos += 12; // Skip "longitude":
                size_t lon_end = message.find(",", lon_pos);
                if (lon_end == std::string::npos) lon_end = message.find("}", lon_pos);
                if (lon_end != std::string::npos) {
                    std::string lon_str = message.substr(lon_pos, lon_end - lon_pos);
                    coords.longitude = std::stod(lon_str);
                }
            }
            
            if (alt_pos != std::string::npos) {
                alt_pos += 11; // Skip "altitude":
                size_t alt_end = message.find(",", alt_pos);
                if (alt_end == std::string::npos) alt_end = message.find("}", alt_pos);
                if (alt_end != std::string::npos) {
                    std::string alt_str = message.substr(alt_pos, alt_end - alt_pos);
                    coords.altitude = std::stod(alt_str);
                }
            }
            
            if (time_pos != std::string::npos) {
                time_pos += 12; // Skip "timestamp":
                size_t time_end = message.find(",", time_pos);
                if (time_end == std::string::npos) time_end = message.find("}", time_pos);
                if (time_end != std::string::npos) {
                    std::string time_str = message.substr(time_pos, time_end - time_pos);
                    coords.timestamp_ms = std::stoll(time_str);
                }
            }
            
        } catch (const std::exception& e) {
            log_message("❌ Error parsing GPS message: " + std::string(e.what()));
        }
        
        return coords;
    }
    
    void save_gps_coordinates(const GPSCoordinates& coords, const std::string& client_ip) {
        std::lock_guard<std::mutex> lock(log_mutex);
        
        std::ofstream gps_file("received_gps_coordinates.csv", std::ios_base::app);
        if (gps_file.is_open()) {
            // Write header if file is empty/new
            gps_file.seekp(0, std::ios::end);
            if (gps_file.tellp() == 0) {
                gps_file << "timestamp,client_ip,latitude,longitude,altitude_m,reception_time" << std::endl;
            }
            
            gps_file << std::fixed << std::setprecision(8)
                     << coords.timestamp_ms << ","
                     << client_ip << ","
                     << coords.latitude << ","
                     << coords.longitude << ","
                     << coords.altitude << ","
                     << get_current_timestamp() << std::endl;
            gps_file.close();
            
            log_message("💾 GPS coordinates saved to CSV file");
        }
    }
    
    void handle_client(SOCKET client_socket, const std::string& client_ip) {
        char buffer[BUFFER_SIZE];
        std::string client_info = "Client[" + client_ip + "]";
        
        log_message("🤝 " + client_info + " connected successfully");
        
        try {
            // Set receive timeout
            struct timeval timeout;
            timeout.tv_sec = 30;  // 30 seconds timeout
            timeout.tv_usec = 0;
            
#ifdef _WIN32
            DWORD timeout_ms = 30000;
            setsockopt(client_socket, SOL_SOCKET, SO_RCVTIMEO, 
                      (const char*)&timeout_ms, sizeof(timeout_ms));
#else
            setsockopt(client_socket, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
#endif
            
            while (running) {
                memset(buffer, 0, BUFFER_SIZE);
                int bytes_received = recv(client_socket, buffer, BUFFER_SIZE - 1, 0);
                
                if (bytes_received > 0) {
                    buffer[bytes_received] = '\0';
                    std::string message(buffer);
                    
                    log_message("📥 " + client_info + " sent: " + message);
                    
                    // Parse GPS coordinates
                    GPSCoordinates coords = parse_gps_message(message);
                    
                    if (coords.latitude != 0 || coords.longitude != 0) {
                        log_message("📍 GPS Coordinates received:");
                        log_message("   Latitude: " + std::to_string(coords.latitude) + "°");
                        log_message("   Longitude: " + std::to_string(coords.longitude) + "°");
                        log_message("   Altitude: " + std::to_string(coords.altitude) + " m");
                        log_message("   Timestamp: " + std::to_string(coords.timestamp_ms));
                        
                        // Save coordinates
                        save_gps_coordinates(coords, client_ip);
                        successful_receptions++;
                        
                        // Send acknowledgment
                        std::string ack_message = "{\"status\":\"success\",\"message\":\"GPS coordinates received\"}";
                        send(client_socket, ack_message.c_str(), ack_message.length(), 0);
                        log_message("✅ " + client_info + " acknowledged successfully");
                        
                        // Display summary statistics
                        log_message("📊 Total connections: " + std::to_string(total_connections) + 
                                   ", Successful receptions: " + std::to_string(successful_receptions));
                        
                    } else {
                        // Invalid GPS data
                        std::string error_message = "{\"status\":\"error\",\"message\":\"Invalid GPS data\"}";
                        send(client_socket, error_message.c_str(), error_message.length(), 0);
                        log_message("⚠️ " + client_info + " sent invalid GPS data");
                    }
                    
                } else if (bytes_received == 0) {
                    log_message("👋 " + client_info + " disconnected gracefully");
                    break;
                } else {
                    log_message("❌ " + client_info + " receive error or timeout");
                    break;
                }
            }
            
        } catch (const std::exception& e) {
            log_message("❌ Exception handling " + client_info + ": " + e.what());
        }
        
        closesocket(client_socket);
        log_message("🔌 " + client_info + " connection closed");
    }
    
public:
    BaseStationServer() : running(false), total_connections(0), successful_receptions(0) {
#ifdef _WIN32
        winsock_initialized = false;
#endif
        server_socket = INVALID_SOCKET;
    }
    
    ~BaseStationServer() {
        stop();
        cleanup_networking();
    }
    
    bool start() {
        if (!initialize_networking()) {
            return false;
        }
        
        // Create socket
        server_socket = socket(AF_INET, SOCK_STREAM, 0);
        if (server_socket == INVALID_SOCKET) {
            log_message("❌ Failed to create server socket");
            return false;
        }
        
        // Enable address reuse
        int opt = 1;
#ifdef _WIN32
        setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));
#else
        setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif
        
        // Bind to port
        sockaddr_in server_addr;
        server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = INADDR_ANY;
        server_addr.sin_port = htons(SERVER_PORT);
        
        if (bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
            log_message("❌ Failed to bind to port " + std::to_string(SERVER_PORT));
            closesocket(server_socket);
            return false;
        }
        
        // Start listening
        if (listen(server_socket, MAX_CLIENTS) == SOCKET_ERROR) {
            log_message("❌ Failed to listen on socket");
            closesocket(server_socket);
            return false;
        }
        
        running = true;
        log_message("🚀 Base Station Server started successfully");
        log_message("📡 Listening on port " + std::to_string(SERVER_PORT));
        log_message("🔗 Maximum concurrent clients: " + std::to_string(MAX_CLIENTS));
        log_message("📁 Logging to: " + std::string(LOG_FILE));
        log_message("💾 GPS data saved to: received_gps_coordinates.csv");
        log_message("⏰ Waiting for drone connections...");
        
        return true;
    }
    
    void run() {
        while (running) {
            sockaddr_in client_addr;
            socklen_t client_len = sizeof(client_addr);
            
            SOCKET client_socket = accept(server_socket, (sockaddr*)&client_addr, &client_len);
            if (client_socket != INVALID_SOCKET) {
                total_connections++;
                
                // Get client IP address
                char client_ip[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, INET_ADDRSTRLEN);
                
                // Handle client in separate thread
                client_threads.emplace_back(&BaseStationServer::handle_client, this, 
                                          client_socket, std::string(client_ip));
                
                // Clean up finished threads
                for (auto it = client_threads.begin(); it != client_threads.end();) {
                    if (it->joinable()) {
                        ++it;
                    } else {
                        it = client_threads.erase(it);
                    }
                }
            }
        }
    }
    
    void stop() {
        if (running) {
            running = false;
            log_message("🛑 Shutting down Base Station Server...");
            
            if (server_socket != INVALID_SOCKET) {
                closesocket(server_socket);
                server_socket = INVALID_SOCKET;
            }
            
            // Wait for all client threads to finish
            for (auto& thread : client_threads) {
                if (thread.joinable()) {
                    thread.join();
                }
            }
            client_threads.clear();
            
            log_message("✅ Base Station Server stopped successfully");
            log_message("📈 Final Statistics:");
            log_message("   Total connections: " + std::to_string(total_connections));
            log_message("   Successful GPS receptions: " + std::to_string(successful_receptions));
        }
    }
    
    void print_status() {
        log_message("📊 Server Status:");
        log_message("   Running: " + std::string(running ? "Yes" : "No"));
        log_message("   Port: " + std::to_string(SERVER_PORT));
        log_message("   Total connections: " + std::to_string(total_connections));
        log_message("   Successful receptions: " + std::to_string(successful_receptions));
        log_message("   Active threads: " + std::to_string(client_threads.size()));
    }
};

// Global server instance for signal handling
BaseStationServer* global_server = nullptr;

#ifndef _WIN32
void signal_handler(int signal) {
    std::cout << "\n🛑 Received signal " << signal << ", shutting down..." << std::endl;
    if (global_server) {
        global_server->stop();
    }
}
#endif

int main() {
    std::cout << "=== 🛰️  Drone Base Station Server ===" << std::endl;
    std::cout << "Starting GPS coordinate reception server..." << std::endl;
    
    BaseStationServer server;
    global_server = &server;
    
#ifndef _WIN32
    // Set up signal handlers for graceful shutdown
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
#endif
    
    if (!server.start()) {
        std::cerr << "❌ Failed to start server. Exiting." << std::endl;
        return -1;
    }
    
    // Start status reporting thread
    std::thread status_thread([&server]() {
        while (true) {
            std::this_thread::sleep_for(std::chrono::minutes(1));
            server.print_status();
        }
    });
    status_thread.detach();
    
    std::cout << "\n💡 Server is running! Press Ctrl+C to stop." << std::endl;
    std::cout << "📋 Commands available while running:" << std::endl;
    std::cout << "   - Send GPS data from drone using your transmit.cpp" << std::endl;
    std::cout << "   - Check base_station_log.txt for detailed logs" << std::endl;
    std::cout << "   - Check received_gps_coordinates.csv for GPS data" << std::endl;
    std::cout << "\n🔗 Waiting for drone connections on port " << SERVER_PORT << "...\n" << std::endl;
    
    try {
        server.run();
    } catch (const std::exception& e) {
        std::cerr << "❌ Server error: " << e.what() << std::endl;
    }
    
    global_server = nullptr;
    std::cout << "\n👋 Base Station Server shutdown complete." << std::endl;
    return 0;
}