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

# Person detection and centering settings
CENTERING_TIMEOUT = 30  # seconds

# Frame dimensions for person detection
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Centering thresholds in pixels
CENTERING_THRESHOLD_X = 10
CENTERING_THRESHOLD_Y = 10

# Velocity control for centering
MAX_VELOCITY = 2.0  # m/s
VELOCITY_SCALING_FACTOR = 0.01

# GPS navigation settings                               │
GPS_REACHED_TOLERANCE_M = 2.0 

# Base station communication settings
BASE_STATION_IP = "127.0.0.1"
BASE_STATION_PORT = 8080
MAX_RETRY_ATTEMPTS = 3
BASE_RETRY_DELAY_S = 0.5 