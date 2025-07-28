cmake_minimum_required(VERSION 3.10.2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project(drone_functions)

add_executable( drone_functions
    offset
)

find_package(MAVSDK REQUIRED)
find_package(OPENCV REQUIRED)
target_link_libraries(offset
    MAVSDK::mavsdk
)
