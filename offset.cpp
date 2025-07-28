#include <iostream>
#include <fstream>
#include <chrono>
#include <thread>


constexpr int FRAME_WIDTH = 640;
constexpr int FRAME_HEIGHT = 480;

struct Person {
    int x;
    int y;
};

void calculate_offset(const Person& person, int& offset_x, int& offset_y) {
    int center_x = FRAME_WIDTH / 2;
    int center_y = FRAME_HEIGHT / 2;
    
    offset_x = person.x - center_x;
    offset_y = person.y - center_y;
    
}