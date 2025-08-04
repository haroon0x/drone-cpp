import time
import csv
import os
from src.drone_controller import DroneController, GPSCoordinates, VelocityCommand
from src.offset import get_person_detection, calculate_offset, calculate_velocity_command
from src.communication import BaseStationCommunicator

def format_gps(coord):
    return f"{coord:.8f}"

def store_coordinates_locally(coords: GPSCoordinates):
    file_exists = os.path.isfile("gps_coordinates.csv")
    with open("gps_coordinates.csv", "a", newline="") as csvfile:
        fieldnames = ["timestamp_ms", "latitude", "longitude", "altitude_m"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            "timestamp_ms": int(time.time() * 1000),
            "latitude": format_gps(coords.latitude_deg),
            "longitude": format_gps(coords.longitude_deg),
            "altitude_m": f"{coords.relative_altitude_m:.3f}"
        })
    print("Coordinates stored locally.")
    return True

def transmit_coordinates_to_base(coords: GPSCoordinates):
    communicator = BaseStationCommunicator()
    return communicator.transmit_coordinates(coords)

def main():
    print("Starting Person-Centered GPS Tracking System (pymavlink)...")

    drone = DroneController()
    if not drone.connect():
        return

    if not drone.start_offboard_mode():
        return

    person = get_person_detection()
    person_centered = False
    
    start_time = time.time()
    timeout = 20
    cycle_start_time = time.time()

    print("\nStarting centering loop...")
    while not person_centered and (time.time() - start_time) < timeout:
        offset = calculate_offset(person)
        
        if offset.is_centered:
            print("Person is centered. Halting movement.")
            drone.send_velocity_command(VelocityCommand(0.0, 0.0, 0.0))
            time.sleep(0.5)

            print("Capturing GPS coordinates...")
            coords = drone.get_current_gps()
            
            if coords:
                cycle_time = time.time() - cycle_start_time
                print(f"Cycle time (detect to capture): {cycle_time:.2f}s")
                print(f"GPS Captured: Lat: {format_gps(coords.latitude_deg)}, Lon: {format_gps(coords.longitude_deg)}")
                
                store_coordinates_locally(coords)
                transmit_coordinates_to_base(coords)
            else:
                print("Failed to retrieve GPS coordinates.")
            
            person_centered = True
        else:
            vel_cmd = calculate_velocity_command(offset)
            drone.send_velocity_command(vel_cmd)
            time.sleep(0.1)
            person = get_person_detection()

    drone.stop_offboard_mode()

    if person_centered:
        print("\nMission completed successfully!")
    else:
        print(f"\nCentering failed. Timeout of {timeout}s reached.")

if __name__ == "__main__":
    main()
