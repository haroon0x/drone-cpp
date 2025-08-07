
from pymavlink import mavutil
import time
import math
from src import config
from src.communication import BaseStationCommunicator
from src.detection import scan_for_person
from src.offset import PersonBoundingBox, calculate_offset, calculate_velocity_command
import cv2

from src.shared import GPSCoordinates

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

    def takeoff(self, altitude_m):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        print(f"Taking off to {altitude_m}m...")
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, altitude_m)

        if not self._wait_for_ack(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF):
            print("Failed to acknowledge takeoff command.")
            return False

        # Wait for the drone to reach the target altitude
        while True:
            msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if msg:
                relative_alt = msg.relative_alt / 1000.0
                print(f"Current altitude: {relative_alt:.2f}m")
                if relative_alt >= altitude_m * 0.95:
                    print("Reached target altitude.")
                    return True
            time.sleep(1)

    def release_payload(self):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        print(f"Releasing payload on servo channel {config.PAYLOAD_SERVO_CHANNEL}...")
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
            config.PAYLOAD_SERVO_CHANNEL,  # servo number
            config.PAYLOAD_SERVO_OPEN_PWM,  # PWM value for open
            0, 0, 0, 0, 0) # Unused parameters
        
        if not self._wait_for_ack(mavutil.mavlink.MAV_CMD_DO_SET_SERVO):
            print("Failed to acknowledge payload release command.")
            return False
        print("Payload release command sent.")
        self.communicator.transmit_payload_dropped_status(True)
        return True

    def goto_gps_coordinates(self, target_gps: GPSCoordinates, tolerance_m=1.0, timeout=120):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        print(f"Navigating to Lat: {target_gps.latitude_deg}, Lon: {target_gps.longitude_deg}, Alt: {target_gps.relative_altitude_m}m...")

        # Send MAV_CMD_NAV_WAYPOINT command
        self.master.mav.send(
            mavutil.mavlink.MAVLink_set_position_target_global_int_message(
                10,  # time_boot_ms (not used here)
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                0b0000111111111000,  # Position, altitude, and yaw valid
                int(target_gps.latitude_deg * 1e7),
                int(target_gps.longitude_deg * 1e7),
                target_gps.relative_altitude_m,
                0, 0, 0, 0, 0, 0, 0, 0  # No velocity, acceleration, or yaw rate
            )
        )

        start_time = time.time()
        while time.time() - start_time < timeout:
            current_gps = self.get_current_gps()
            if current_gps:
                # Simple Euclidean distance check (approximation for small distances)
                # More accurate would be haversine formula
                distance = math.sqrt(
                    ((current_gps.latitude_deg - target_gps.latitude_deg) * 111319.9)**2 + 
                    ((current_gps.longitude_deg - target_gps.longitude_deg) * 111319.9 * math.cos(math.radians(current_gps.latitude_deg)))**2 + 
                    ((current_gps.relative_altitude_m - target_gps.relative_altitude_m))**2
                )
                
                print(f"Distance to target: {distance:.2f}m")
                if distance < tolerance_m:
                    print("Reached target GPS coordinates.")
                    return True
            time.sleep(1) # Check every second

        print("Navigation to GPS coordinates timed out.")
        return False

    def land(self):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        print("Initiating landing sequence...")
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0) # All params 0 for current position
        
        # Wait for the drone to land (simplified check)
        start_time = time.time()
        timeout = 120 # seconds
        while time.time() - start_time < timeout:
            msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
            if msg and msg.relative_alt / 1000.0 < 0.5: # Landed if relative altitude is very low
                print("Drone has landed.")
                return True
            time.sleep(1)
        print("Landing timed out or failed.")
        return False

    def return_to_home(self):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")

        print("Initiating Return To Launch (RTL) sequence...")
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0)
        
        if not self._wait_for_ack(mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH):
            print("Failed to acknowledge RTL command.")
            return False
        print("RTL command sent. Drone should be returning to home.")
        return True

    def center_on_person_and_drop_payload(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open video stream for delivery sequence.")
            return

        print("Starting delivery sequence...")
        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame for delivery sequence. Exiting.")
                break

            persons, annotated_frame = scan_for_person(frame)

            if persons:
                # Assume the largest bounding box is the target
                target_person = max(persons, key=lambda p: (p[2] - p[0]) * (p[3] - p[1]))
                person_bbox = PersonBoundingBox(*target_person)
                
                offset = calculate_offset(person_bbox)

                if offset.is_centered:
                    print("Person centered. Releasing payload.")
                    self.release_payload()
                    time.sleep(2) # Wait for payload to drop
                    print("Payload released. Mission for this location is complete.")
                    break
                else:
                    velocity_cmd = calculate_velocity_command(offset)
                    print(f"Adjusting position. Velocity command: N={velocity_cmd.north_m_s:.2f}, E={velocity_cmd.east_m_s:.2f}")
                    self.send_velocity_command(velocity_cmd)
            else:
                # If no person is detected, hover in place
                print("No person detected. Hovering.")
                self.send_velocity_command(VelocityCommand(0, 0, 0))

            if config.ENABLE_VIDEO_DISPLAY:
                cv2.imshow("Delivery Sequence", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        
        cap.release()
        cv2.destroyAllWindows()

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



