import math
from src import config
from src.drone_controller import VelocityCommand



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




def get_person_center_x(person: PersonBoundingBox):
    return (person.x_min + person.x_max) / 2

def get_person_center_y(person: PersonBoundingBox):
    return (person.y_min + person.y.max) / 2

def calculate_offset(person: PersonBoundingBox):
    frame_center_x = config.FRAME_WIDTH / 2
    frame_center_y = config.FRAME_HEIGHT / 2
    
    person_center_x = get_person_center_x(person)
    person_center_y = get_person_center_y(person)
    
    offset_x = person_center_x - frame_center_x
    offset_y = person_center_y - frame_center_y
    
    is_centered = (abs(offset_x) <= config.CENTERING_THRESHOLD_X and 
                   abs(offset_y) <= config.CENTERING_THRESHOLD_Y)
    
    return Offset(offset_x, offset_y, is_centered)

def calculate_velocity_command(offset: Offset):
    if offset.is_centered:
        return VelocityCommand(0.0, 0.0, 0.0)
    
    east_m_s = max(-config.MAX_VELOCITY, 
                   min(config.MAX_VELOCITY, 
                       offset.x * config.VELOCITY_SCALING_FACTOR))
    
    north_m_s = max(-config.MAX_VELOCITY, 
                    min(config.MAX_VELOCITY, 
                        -offset.y * config.VELOCITY_SCALING_FACTOR))
    
    return VelocityCommand(north_m_s, east_m_s, 0.0)


if __name__ == '__main__':
    # Example usage: Set config values for independent testing
    config.FRAME_WIDTH = 640
    config.FRAME_HEIGHT = 480
    config.CENTERING_THRESHOLD_X = 10
    config.CENTERING_THRESHOLD_Y = 10
    config.MAX_VELOCITY = 2.0
    config.VELOCITY_SCALING_FACTOR = 0.01

    mock_person = PersonBoundingBox(300, 200, 340, 280, 0.9)

    offset = calculate_offset(mock_person)
    print(f"Offset: x={offset.x}, y={offset.y}, centered={offset.is_centered}")

    velocity_command = calculate_velocity_command(offset)
    print(f"Velocity Command: N={velocity_command.north_m_s} m/s, E={velocity_command.east_m_s} m/s, D={velocity_command.down_m_s} m/s")

    mock_centered_person = PersonBoundingBox(315, 235, 325, 245, 0.95)

    centered_offset = calculate_offset(mock_centered_person)
    print(f"Centered Offset: x={centered_offset.x}, y={centered_offset.y}, centered={centered_offset.is_centered}")

    centered_velocity_command = calculate_velocity_command(centered_offset)
    print(f"Centered Velocity Command: N={centered_velocity_command.north_m_s} m/s, E={centered_velocity_command.east_m_s} m/s, D={centered_velocity_command.down_m_s} m/s")