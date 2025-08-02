#pragma once

struct Person {
    int x;
    int y;
};

void calculate_offset(const Person& person, int& offset_x, int& offset_y);
