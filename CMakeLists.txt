cmake_minimum_required(VERSION 3.10.2)

project(drone_functions)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(MAVSDK REQUIRED)


add_executable(drone_functions offset.cpp)
target_link_libraries(drone_functions
    MAVSDK::mavsdk
)

add_executable(transmit_location transmit.cpp)
target_link_libraries(transmit_location
    MAVSDK::mavsdk
)
