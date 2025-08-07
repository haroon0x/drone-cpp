
from pymavlink import mavutil
import time
from src import config
from src.communication import BaseStationCommunicator
from src.detection import scan_for_person
import cv2

class GPSCoordinates:
    def __init__(self, latitude_deg, longitude_deg, absolute_altitude_m, relative_altitude_m):
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.absolute_altitude_m = absolute_altitude_m
        self.relative_altitude_m = relative_altitude_m

class VelocityCommand:
    def __init__(self, north_m_s, east_m_s, down_m_s):
        self.north_m_s = north_m_s
        self.east_m_s = east_m_s
        self.down_m_s = down_m_s

class DroneController:
    def __init__(self):
        self.connection_url = config.CONNECTION_URL
        self.master = None
        self.is_connected = False
        self.communicator = BaseStationCommunicator()

    def connect(self):
        try:
            print(f"Connecting to drone on {self.connection_url}...")
            self.master = mavutil.mavlink_connection(self.connection_url, autoreconnect=True)
            self.master.wait_heartbeat(timeout=5)
            print(f"Heartbeat from system (system {self.master.target_system} component {self.master.target_component})")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def _wait_for_ack(self, command_name, timeout=3):
        try:
            ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
            if ack and ack.command == command_name and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                return True
            print(f"Command {mavutil.mavlink.enums['MAV_CMD'][command_name].name} was not accepted.")
            return False
        except Exception as e:
            print(f"Error waiting for ACK: {e}")
            return False

    def get_current_gps(self):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")
        
        msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if not msg:
            print("Failed to get GPS data.")
            return None
            
        return GPSCoordinates(
            msg.lat / 1e7,
            msg.lon / 1e7,
            msg.alt / 1000.0,
            msg.relative_alt / 1000.0
        )

    def send_velocity_command(self, cmd: VelocityCommand):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")
            
        self.master.mav.set_position_target_local_ned_send(
            0, 
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111000111, 
            0, 0, 0,
            cmd.north_m_s, cmd.east_m_s, cmd.down_m_s,
            0, 0, 0, 
            0, 0)

    def start_offboard_mode(self):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        mode = 'GUIDED'
        if mode not in self.master.mode_mapping():
            print(f"GUIDED mode is not supported.")
            return False

        mode_id = self.master.mode_mapping()[mode]
        
        print("Arming vehicle...")
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
        
        if not self._wait_for_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM):
            return False
        print("Vehicle armed.")

        print(f"Setting mode to {mode}...")
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id)

        if not self._wait_for_ack(mavutil.mavlink.MAV_CMD_DO_SET_MODE):
             return False
        print(f"Mode set to {mode}.")
        return True

    def takeoff(self, altitude: float):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        print(f"Attempting to takeoff to {altitude} meters...")
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, altitude)
        
        # Wait for the drone to reach the target altitude
        start_time = time.time()
        timeout = 60  # seconds
        target_reached = False

        while time.time() - start_time < timeout:
            msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
            if msg:
                current_altitude = msg.relative_alt / 1000.0
                print(f"Current altitude: {current_altitude:.2f}m / Target: {altitude}m")
                if current_altitude >= altitude * 0.95: # Within 5% of target altitude
                    print(f"Reached takeoff altitude of {altitude} meters.")
                    target_reached = True
                    break
            time.sleep(0.5) # Check every half second

        if not target_reached:
            print("Takeoff timed out or failed to reach target altitude.")
            return False
        return True

    def goto_location(self, coords: GPSCoordinates, ground_speed: float = 5.0):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        print(f"Going to Lat: {coords.latitude_deg}, Lon: {coords.longitude_deg}, Alt: {coords.absolute_altitude_m}...")
        
        # Send the MAVLink command to set the target location
        self.master.mav.set_position_target_global_int_send(
            0,  # time_boot_ms (not used)
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # Frame
            0b0000111111111000,  # type_mask (only position enabled)
            int(coords.latitude_deg * 1e7), # lat_int
            int(coords.longitude_deg * 1e7), # lon_int
            coords.absolute_altitude_m, # alt
            0, 0, 0, # vx, vy, vz
            0, 0, 0, # afx, afy, afz
            0, 0) # yaw, yaw_rate

        # Monitor drone's position until it reaches the target or times out
        start_time = time.time()
        timeout = 120  # seconds (2 minutes for travel)
        target_tolerance = 0.00001 # Roughly 1 meter in lat/lon degrees
        
        while time.time() - start_time < timeout:
            current_gps = self.get_current_gps()
            if current_gps:
                # Calculate Euclidean distance (simplified for small distances)
                distance = ((current_gps.latitude_deg - coords.latitude_deg)**2 + \
                            (current_gps.longitude_deg - coords.longitude_deg)**2)**0.5
                
                print(f"Distance to target: {distance:.6f} degrees")
                if distance < target_tolerance:
                    print("Reached target location.")
                    return True
            time.sleep(1) # Check position every second

        print("Goto location timed out or failed to reach target.")
        return False

    def start_person_detection_and_communication(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open video stream for person detection.")
            return

        print("Starting person detection and communication...")
        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame for person detection. Exiting.")
                break

            person_detected, annotated_frame = scan_for_person(frame)
            self.communicator.transmit_person_detected_status(person_detected)

            if person_detected:
                current_gps = self.get_current_gps()
                if current_gps:
                    print(f"Person detected at drone's current GPS: Lat: {current_gps.latitude_deg}, Lon: {current_gps.longitude_deg}")
                    self.communicator.transmit_coordinates(current_gps)
                else: 
                    print("Not able to get the drone's current GPS coordinates")
            if config.ENABLE_VIDEO_DISPLAY:
                cv2.imshow("Person Detection", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                # In headless mode, provide a way to stop the loop, e.g., a simple time limit or external signal
                # For now, we'll just break after a short delay to avoid an infinite loop in a non-interactive environment
                time.sleep(0.1) # Small delay to prevent busy-waiting
                # In a real production scenario, you'd want a more robust exit condition,
                # such as listening for a signal or a message from the base station.
                # For demonstration, we'll assume the script will be managed externally.
                pass
        
        cap.release()
        cv2.destroyAllWindows()



