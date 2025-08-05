
import socket
import json
import time

BASE_STATION_IP = "127.0.0.1"
BASE_STATION_PORT = 8080
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_MS = 1000

class BaseStationCommunicator:
    def __init__(self, ip=BASE_STATION_IP, port=BASE_STATION_PORT):
        self.server_ip = ip
        self.server_port = port

    def create_gps_message(self, coords):
        message = {
            "message_type": "gps_coordinates",
            "timestamp": int(time.time() * 1000),
            "latitude": coords.latitude_deg,
            "longitude": coords.longitude_deg,
            "altitude": coords.relative_altitude_m
        }
        return json.dumps(message)

    def transmit_coordinates(self, coords):
        message = self.create_gps_message(coords)
        base_delay = 0.5  # 500ms initial delay
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2.0)  # 2-second timeout for connection
                    sock.connect((self.server_ip, self.server_port))
                    sock.sendall(message.encode('utf-8'))
                    print("Successfully transmitted coordinates.")
                    return True
            except ConnectionRefusedError:
                delay = base_delay * (2 ** attempt)
                print(f"Connection refused. Retrying in {delay:.1f}s...")
                time.sleep(delay)
            except Exception as e:
                print(f"An error occurred during transmission: {e}")
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
        
        print("Failed to transmit coordinates after all attempts.")
        return False

    def transmit_payload_dropped_status(self, dropped: bool):
        message = {
            "message_type": "payload_status",
            "timestamp": int(time.time() * 1000),
            "dropped": dropped
        }
        message = json.dumps(message)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_ip, self.server_port))
                sock.sendall(message.encode('utf-8'))
                print("Successfully transmitted payload status.")
                return True
        except Exception as e:
            print(f"Failed to transmit payload status: {e}")
            return False

    def receive_coordinates(self):
        print("Waiting to receive coordinates...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
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
                    from src.drone_controller import GPSCoordinates
                    return GPSCoordinates(
                        latitude_deg=message["latitude"],
                        longitude_deg=message["longitude"],
                        absolute_altitude_m=message["altitude"],
                        relative_altitude_m=message["altitude"]
                    )
                return None
