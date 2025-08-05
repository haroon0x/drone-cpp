import time
from src.drone_controller import DroneController, GPSCoordinates, VelocityCommand
from src.offset import get_person_detection, calculate_offset, calculate_velocity_command
from src.communication import BaseStationCommunicator

def get_target_coordinates() -> GPSCoordinates:
    """Receives GPS coordinates from the base station."""
    communicator = BaseStationCommunicator()
    return communicator.receive_coordinates()

def fly_to_target(drone: DroneController, target_coords: GPSCoordinates):
    """Flies the drone to the target GPS coordinates."""
    print(f"Flying to target: Lat: {target_coords.latitude_deg}, Lon: {target_coords.longitude_deg}")
    # This is a simplified placeholder for GPS-based navigation.
    # In a real implementation, you would use MAVLink commands to guide the drone.
    # For now, we'll just simulate the flight time.
    time.sleep(10)
    print("Arrived at target location.")

def center_and_drop_payload(drone: DroneController):
    """
    Centers the drone on a person and drops the payload.
    """
    person = get_person_detection()
    if not person:
        print("No person detected at the target location.")
        return False

    print("Person detected. Centering for payload drop...")
    person_centered = False
    start_time = time.time()
    timeout = 30

    while not person_centered and (time.time() - start_time) < timeout:
        offset = calculate_offset(person)
        
        if offset.is_centered:
            print("Person centered. Dropping payload.")
            drone.send_velocity_command(VelocityCommand(0.0, 0.0, 0.0))
            # Placeholder for payload drop mechanism
            time.sleep(2) 
            print("Payload dropped.")
            return True
        else:
            vel_cmd = calculate_velocity_command(offset)
            drone.send_velocity_command(vel_cmd)
            time.sleep(0.1)
            person = get_person_detection()

    print("Failed to center for payload drop.")
    return False

def main():
    """
    Main function for the delivery drone.
    Waits for coordinates, flies to the location, and drops the payload.
    """
    print("Delivery drone initiated.")
    drone = DroneController()
    if not drone.connect():
        return

    if not drone.start_offboard_mode():
        return

    print("Waiting for target coordinates from base station...")
    target_coords = get_target_coordinates()

    if not target_coords:
        print("Failed to receive target coordinates.")
        drone.stop_offboard_mode()
        return

    fly_to_target(drone, target_coords)
    
    if center_and_drop_payload(drone):
        print("Delivery mission successful.")
        # Notify base station of successful delivery
        communicator = BaseStationCommunicator()
        communicator.transmit_payload_dropped_status(True)
    else:
        print("Delivery mission failed.")
        communicator = BaseStationCommunicator()
        communicator.transmit_payload_dropped_status(False)

    drone.stop_offboard_mode()
    print("Delivery drone mission finished.")

if __name__ == "__main__":
    main()
