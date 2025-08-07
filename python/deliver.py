import time
from src.drone_controller import DroneController, GPSCoordinates
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

    # Define multiple delivery locations
    # These would typically come from a mission plan or base station
    delivery_locations = [
        GPSCoordinates(latitude_deg=35.6895, longitude_deg=139.6917, absolute_altitude_m=config.DEFAULT_TAKEOFF_ALTITUDE_DELIVER, relative_altitude_m=config.DEFAULT_TAKEOFF_ALTITUDE_DELIVER),
        GPSCoordinates(latitude_deg=35.6890, longitude_deg=139.6920, absolute_altitude_m=config.DEFAULT_TAKEOFF_ALTITUDE_DELIVER, relative_altitude_m=config.DEFAULT_TAKEOFF_ALTITUDE_DELIVER),
        # Add more locations as needed
    ]

    # 1. Take off (if not already airborne)
    # Assuming drone is already at a safe altitude or will take off to DEFAULT_TAKEOFF_ALTITUDE_DELIVER
    # if not drone.takeoff(config.DEFAULT_TAKEOFF_ALTITUDE_DELIVER):
    #     print("Takeoff failed. Exiting.")
    #     return


    # 2. Execute the multi-location delivery sequence
    drone.delivery_sequence(delivery_locations)

    # 3. After all deliveries, return to base or land
    print("\nAll delivery locations processed. Initiating return to base or final landing.")
    # Example: Land at current position after mission
    if not drone.land():
        print("Failed to land the drone after mission.")
        return

    print("Delivery mission complete.")

if __name__ == "__main__":
    main()

