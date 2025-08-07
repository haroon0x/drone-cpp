import time
from src.drone_controller import DroneController
from src.communication import BaseStationCommunicator
from src import config

def main():
    """
    Main function for the delivery drone.
    Orchestrates the multi-location delivery mission.
        - Waits for coordinates, flies to the location, detect the person, centers the person and then drops the payload.

    """
    print("Delivery drone initiated.")

    drone = DroneController()
    communicator = BaseStationCommunicator()

    if not drone.connect():
        print("Failed to connect to drone. Exiting.")
        return

    if not drone.start_offboard_mode():
        print("Failed to set offboard mode. Exiting.")
        return

    # Main mission loop
    while True:
        print("\nWaiting for next delivery location from base station...")
        target_gps = communicator.receive_coordinates()

        if not target_gps:
            print("No coordinates received or an error occurred. Mission complete or standing by.")
            break

        print(f"Received new target: Lat: {target_gps.latitude_deg}, Lon: {target_gps.longitude_deg}")

        # 1. Navigate to the target GPS coordinates
        if not drone.goto_gps_coordinates(target_gps):
            print(f"Failed to navigate to the delivery location. Skipping to next.")
            continue

        # 2. Start the centering and payload drop sequence
        print("Reached delivery location. Starting final approach and payload drop.")
        drone.center_on_person_and_drop_payload()

    # 3. After all deliveries, return to base or land
    print("\nDelivery mission finished. Returning to home.")
    if not drone.return_to_home():
        print("Failed to initiate Return to Launch (RTL).")

    print("Delivery mission complete.")

if __name__ == "__main__":
    main()