# Drone connection settings

# For SITL (Software In The Loop) simulator, use 'udp:127.0.0.1:14540'
# For a physical drone via telemetry radio, use something like '/dev/ttyUSB0' (Linux) or 'COM3' (Windows)
CONNECTION_URL = "udp:127.0.0.1:14540"

# Default takeoff altitude in meters
DEFAULT_TAKEOFF_ALTITUDE_SCOUT = 60
DEFAULT_TAKEOFF_ALTITUDE_DELIVER = 10

# Enable or disable video display for person detection
ENABLE_VIDEO_DISPLAY = False

# Payload release servo settings
PAYLOAD_SERVO_CHANNEL = 8  # Example: Servo connected to output channel 8
PAYLOAD_SERVO_OPEN_PWM = 1900 # PWM value for open/release
PAYLOAD_SERVO_CLOSED_PWM = 1100 # PWM value for closed/hold
