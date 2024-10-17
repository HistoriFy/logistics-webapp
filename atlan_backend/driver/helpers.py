import random
import math

def generate_random_location(latitude, longitude, radius=2000):
    """
    Generate a random location within a radius (in meters) around a given lat/long.
    """
    radius_in_degrees = radius / 111000  # Convert meters to degrees
    u = random.random()
    v = random.random()
    w = radius_in_degrees * math.sqrt(u)
    t = 2 * math.pi * v
    delta_lat = w * math.cos(t)
    delta_long = w * math.sin(t) / math.cos(math.radians(latitude))
    
    new_latitude = latitude + delta_lat
    new_longitude = longitude + delta_long
    return new_latitude, new_longitude


def move_towards(current_lat, current_lng, target_lat, target_lng, speed=0.007207):
    """
    Move the current location towards the target location at a fixed speed.
    """
    delta_lat = target_lat - current_lat
    delta_lng = target_lng - current_lng
    distance = math.sqrt(delta_lat ** 2 + delta_lng ** 2)
    
    if distance < speed:
        return target_lat, target_lng  # Stop when close enough
    else:
        ratio = speed / distance
        new_lat = current_lat + ratio * delta_lat
        new_lng = current_lng + ratio * delta_lng
        return new_lat, new_lng
