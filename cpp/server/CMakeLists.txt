cmake_minimum_required(VERSION 3.10.2)

project(base_station_server)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_executable(base_station_server base_station_server.cpp)

# Platform-specific libraries for networking
if(WIN32)
    target_link_libraries(base_station_server PRIVATE ws2_32)
endif()

# Add common compiler flags and definitions
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(base_station_server PRIVATE -Wall -Wextra -Wpedantic)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    target_compile_options(base_station_server PRIVATE /W4)
endif()

target_compile_definitions(base_station_server PRIVATE
    $<$<CONFIG:Debug>:DEBUG_BUILD>
)

# Installation (optional)
install(TARGETS base_station_server
    RUNTIME DESTINATION bin
)

# Print build information
message(STATUS "Building base_station_server project")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
