from pymavlink import mavutil
import time

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
    def __init__(self, connection_url="udp:127.0.0.1:14550"):
        self.connection_url = connection_url
        self.master = None
        self.is_connected = False

    def connect(self):
        print(f"Connecting to drone on {self.connection_url}...")
        self.master = mavutil.mavlink_connection(self.connection_url)
        self.master.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (self.master.target_system, self.master.target_component))
        self.is_connected = True
        return True

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
            mode = 'OFFBOARD'
            if mode not in self.master.mode_mapping():
                 print(f"Neither GUIDED nor OFFBOARD modes are supported.")
                 return False

        mode_id = self.master.mode_mapping()[mode]
        
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
        
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        if ack and ack.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("Failed to arm vehicle.")
            return False
        print("Vehicle armed.")

        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id)

        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        if ack and ack.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print(f"Failed to set mode to {mode}.")
            return False
            
        print(f"Mode set to {mode}.")
        return True

    def stop_offboard_mode(self):
        if not self.is_connected:
            raise ConnectionError("Not connected to drone.")
        
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
        
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        if ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("Vehicle disarmed.")
        else:
            print("Failed to disarm vehicle.")