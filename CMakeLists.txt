cmake_minimum_required(VERSION 3.10.2)

project(drone_cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Find required packages
find_package(MAVSDK REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Add executables
add_executable(drone_client src/offset.cpp src/communication.cpp)
target_link_libraries(drone_client PRIVATE MAVSDK::mavsdk)

add_executable(base_station_server base_station_server.cpp)

# Platform-specific libraries for networking
if(WIN32)
    target_link_libraries(drone_client PRIVATE ws2_32)
    target_link_libraries(base_station_server PRIVATE ws2_32)
endif()

# Add common compiler flags and definitions
foreach(target drone_client base_station_server)
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
    elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        target_compile_options(${target} PRIVATE /W4)
    endif()

    target_compile_definitions(${target} PRIVATE
        $<$<CONFIG:Debug>:DEBUG_BUILD>
    )
endforeach()

# Installation (optional)
install(TARGETS drone_client base_station_server
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Building drone_cpp project")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "MAVSDK Found: ${MAVSDK_FOUND}")
