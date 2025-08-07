import time
from src.drone_controller import DroneController


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

    drone.start_person_detection_and_communication()

if __name__ == "__main__":
    main()
