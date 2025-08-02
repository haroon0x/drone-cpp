#include "utils.hpp"
#include <iostream>
#include <fstream>


constexpr int FRAME_WIDTH = 640;
constexpr int FRAME_HEIGHT = 480;


void calculate_offset(const Person& person, int& offset_x, int& offset_y) {
    int center_x = FRAME_WIDTH / 2;
    int center_y = FRAME_HEIGHT / 2;
    
    offset_x = person.x - center_x;
    offset_y = person.y - center_y;
    
}

void store_coordinates(double latitude, double longitude) {
    std::ofstream outfile("gps_coordinates.txt", std::ios_base::app); 
    if (outfile.is_open()) {
        outfile << "Latitude: " << latitude << ", Longitude: " << longitude << std::endl;
        outfile.close();
    } else {
        std::cerr << "Unable to open file for writing." << std::endl;
    }
}

int main() {
    Person detected_person = { 300, 250 }; 
    int offset_x, offset_y;
    
    calculate_offset(detected_person, offset_x, offset_y);
    
    std::cout << "Offset X: " << offset_x << std::endl;
    std::cout << "Offset Y: " << offset_y << std::endl;

    // Placeholder for fetching actual GPS coordinates
    double latitude = 47.397742;
    double longitude = 8.545594;

    if (abs(offset_x) < 10 && abs(offset_y) < 10) {
        store_coordinates(latitude, longitude);
        std::cout << "Person centered, coordinates stored." << std::endl;
    }
    
    return 0;
}