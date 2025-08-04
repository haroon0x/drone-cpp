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
add_executable(drone_client src/drone_client.cpp src/communication.cpp src/storage.cpp)
target_link_libraries(drone_client PRIVATE MAVSDK::mavsdk)

# Platform-specific libraries for networking
if(WIN32)
    target_link_libraries(drone_client PRIVATE ws2_32)
endif()

# Add common compiler flags and definitions
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(drone_client PRIVATE -Wall -Wextra -Wpedantic)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    target_compile_options(drone_client PRIVATE /W4)
endif()

target_compile_definitions(drone_client PRIVATE
    $<$<CONFIG:Debug>:DEBUG_BUILD>
)

# Installation (optional)
install(TARGETS drone_client
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Building drone_cpp project")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "MAVSDK Found: ${MAVSDK_FOUND}")