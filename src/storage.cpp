#include "../include/utils.hpp"
#include <iostream>
#include <fstream>
#include <iomanip>

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
