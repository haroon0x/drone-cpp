import time
from src.drone_controller import DroneController, GPSCoordinates, VelocityCommand
from src.offset import get_person_detection, calculate_offset, calculate_velocity_command
from src.communication import BaseStationCommunicator

def transmit_coordinates_to_base(coords: GPSCoordinates):
    """Transmits the given GPS coordinates to the base station."""
    communicator = BaseStationCommunicator()
    return communicator.transmit_coordinates(coords)

def scan_for_person(drone: DroneController):
    """
    Scans for a person, centers the drone on them, and returns their GPS coordinates.
    """
    print("Scanning for a person...")
    # In a real scenario, this would involve a search pattern.
    # For now, we'll just assume a person is detected immediately.
    person = get_person_detection()
    if not person:
        print("No person detected.")
        return None

    print("Person detected. Centering...")
    person_centered = False
    start_time = time.time()
    timeout = 30  # 30-second timeout for centering

    while not person_centered and (time.time() - start_time) < timeout:
        offset = calculate_offset(person)
        
        if offset.is_centered:
            print("Person centered.")
            drone.send_velocity_command(VelocityCommand(0.0, 0.0, 0.0))
            time.sleep(0.5)
            person_centered = True
        else:
            vel_cmd = calculate_velocity_command(offset)
            drone.send_velocity_command(vel_cmd)
            time.sleep(0.1)
            person = get_person_detection()

    if not person_centered:
        print("Failed to center on the person within the timeout.")
        return None

    print("Capturing GPS coordinates...")
    return drone.get_current_gps()

def main():
    """
    Main function for the scout drone.
    Connects to the drone, scans for a person, and sends their location.
    """
    print("Scout drone initiated.")
    drone = DroneController()
    if not drone.connect():
        return

    if not drone.start_offboard_mode():
        return

    # The drone should take off and fly to a certain altitude first.
    # This is a simplified placeholder.
    print("Taking off and starting scan...")
    
    # For now, we'll just wait a bit before scanning.
    time.sleep(5)

    coordinates = scan_for_person(drone)

    if coordinates:
        print(f"GPS Captured: Lat: {coordinates.latitude_deg}, Lon: {coordinates.longitude_deg}")
        print("Transmitting coordinates to base station...")
        if transmit_coordinates_to_base(coordinates):
            print("Coordinates transmitted successfully.")
        else:
            print("Failed to transmit coordinates.")
    else:
        print("Could not get coordinates for the person.")

    drone.stop_offboard_mode()
    print("Scout drone mission finished.")

if __name__ == "__main__":
    main()
