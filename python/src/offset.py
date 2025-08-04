import math

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CENTERING_THRESHOLD_X = 10
CENTERING_THRESHOLD_Y = 10
MAX_VELOCITY = 2.0  # m/s
VELOCITY_SCALING_FACTOR = 0.01

class PersonBoundingBox:
    def __init__(self, x_min, y_min, x_max, y_max, confidence):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.confidence = confidence

class Offset:
    def __init__(self, x, y, is_centered):
        self.x = x
        self.y = y
        self.is_centered = is_centered

class VelocityCommand:
    def __init__(self, north_m_s, east_m_s, down_m_s):
        self.north_m_s = north_m_s
        self.east_m_s = east_m_s
        self.down_m_s = down_m_s

def get_person_detection():
    # Simulate a person detection
    return PersonBoundingBox(200, 150, 280, 300, 0.85)

def get_person_center_x(person: PersonBoundingBox):
    return (person.x_min + person.x_max) / 2

def get_person_center_y(person: PersonBoundingBox):
    return (person.y_min + person.y_max) / 2

def calculate_offset(person: PersonBoundingBox):
    frame_center_x = FRAME_WIDTH / 2
    frame_center_y = FRAME_HEIGHT / 2
    
    person_center_x = get_person_center_x(person)
    person_center_y = get_person_center_y(person)
    
    offset_x = person_center_x - frame_center_x
    offset_y = person_center_y - frame_center_y
    
    is_centered = (abs(offset_x) <= CENTERING_THRESHOLD_X and 
                   abs(offset_y) <= CENTERING_THRESHOLD_Y)
    
    return Offset(offset_x, offset_y, is_centered)

def calculate_velocity_command(offset: Offset):
    if offset.is_centered:
        return VelocityCommand(0.0, 0.0, 0.0)
    
    east_m_s = max(-MAX_VELOCITY, 
                   min(MAX_VELOCITY, 
                       offset.x * VELOCITY_SCALING_FACTOR))
    
    north_m_s = max(-MAX_VELOCITY, 
                    min(MAX_VELOCITY, 
                        -offset.y * VELOCITY_SCALING_FACTOR))
    
    return VelocityCommand(north_m_s, east_m_s, 0.0)