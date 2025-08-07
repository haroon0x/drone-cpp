import socket
import json
import time
from src import config
from src.shared import GPSCoordinates

class BaseStationCommunicator:
    def __init__(self, ip=config.BASE_STATION_IP, port=config.BASE_STATION_PORT):
        self.server_ip = ip
        self.server_port = port

    def _transmit_message(self, message):
        """Handles the core logic of transmitting a message with retries."""
        message_json = json.dumps(message)
        for attempt in range(config.MAX_RETRY_ATTEMPTS):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2.0)  # 2-second timeout for connection
                    sock.connect((self.server_ip, self.server_port))
                    sock.sendall(message_json.encode('utf-8'))
                    print(f"Successfully transmitted message of type '{message.get('message_type', 'unknown')}'.")
                    return True
            except socket.timeout:
                print(f"Connection timed out. Retrying...")
            except ConnectionRefusedError:
                delay = config.BASE_RETRY_DELAY_S * (2 ** attempt)
                print(f"Connection refused. Retrying in {delay:.1f}s...")
                time.sleep(delay)
            except socket.gaierror as e:
                print(f"Address-related error connecting to server: {e}")
                # No retry for this, as it's a configuration issue
                return False
            except Exception as e:
                delay = config.BASE_RETRY_DELAY_S * (2 ** attempt)
                print(f"An unexpected error occurred during transmission: {e}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
        
        print(f"Failed to transmit message after {config.MAX_RETRY_ATTEMPTS} attempts.")
        return False

    def create_gps_message(self, coords: GPSCoordinates):
        return {
            "message_type": "gps_coordinates",
            "timestamp": int(time.time() * 1000),
            "latitude": coords.latitude_deg,
            "longitude": coords.longitude_deg,
            "altitude": coords.relative_altitude_m
        }

    def transmit_coordinates(self, coords: GPSCoordinates):
        message = self.create_gps_message(coords)
        return self._transmit_message(message)

    def transmit_payload_dropped_status(self, dropped: bool):
        message = {
            "message_type": "payload_status",
            "timestamp": int(time.time() * 1000),
            "dropped": dropped
        }
        return self._transmit_message(message)

    def transmit_person_detected_status(self, detected: bool):
        message = {
            "message_type": "person_detection_status",
            "timestamp": int(time.time() * 1000),
            "detected": detected
        }
        return self._transmit_message(message)

    def receive_coordinates(self, timeout=30.0):
        print("Waiting to receive coordinates...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.bind((self.server_ip, self.server_port))
                sock.listen()
                conn, addr = sock.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if not data:
                        return None
                    message = json.loads(data.decode('utf-8'))
                    if message.get("message_type") == "gps_coordinates":
                        return GPSCoordinates(
                            latitude_deg=message["latitude"],
                            longitude_deg=message["longitude"],
                            absolute_altitude_m=message["altitude"],
                            relative_altitude_m=message["altitude"]
                        )
                    return None
            except socket.timeout:
                print("Timed out waiting for a connection.")
                return None
            except Exception as e:
                print(f"An error occurred while receiving coordinates: {e}")
                return None