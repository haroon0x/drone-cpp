cmake_minimum_required(VERSION 3.10.2)

project(drone_functions)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(MAVSDK REQUIRED)

# Create directories if they don't exist
file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/data)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Add executables
add_executable(drone_functions offset.cpp)
target_link_libraries(drone_functions
    MAVSDK::mavsdk
)

add_executable(transmit_location transmit.cpp)
target_link_libraries(transmit_location
    MAVSDK::mavsdk
)

# Platform-specific libraries for networking
if(WIN32)
    target_link_libraries(transmit_location ws2_32)
endif()

# Set output directory
set_target_properties(drone_functions transmit_location PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin
)

# Custom target to create necessary directories
add_custom_target(create_dirs ALL
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_SOURCE_DIR}/data
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_SOURCE_DIR}/bin
    COMMENT "Creating necessary directories"
)

# Make executables depend on directory creation
add_dependencies(drone_functions create_dirs)
add_dependencies(transmit_location create_dirs)

# Installation (optional)
install(TARGETS drone_functions transmit_location
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Building drone_functions project")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "MAVSDK Found: ${MAVSDK_FOUND}")

# Add compiler flags for better debugging and warnings
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(drone_functions PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(transmit_location PRIVATE -Wall -Wextra -Wpedantic)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    target_compile_options(drone_functions PRIVATE /W4)
    target_compile_options(transmit_location PRIVATE /W4)
endif()

# Add compile definitions
target_compile_definitions(drone_functions PRIVATE
    $<$<CONFIG:Debug>:DEBUG_BUILD>
)
target_compile_definitions(transmit_location PRIVATE
    $<$<CONFIG:Debug>:DEBUG_BUILD>
)