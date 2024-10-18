import random
import math
from django.conf import settings

def generate_random_location(latitude, longitude, radius=settings.RANDOM_LOCATION_RADIUS):
    """
    Generate a random location within a radius (in meters) around a given lat/long.
    """

    #convert decimal.Decimal to float
    latitude = float(latitude)
    longitude = float(longitude)

    # 1 radius = 111 Km
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

def move_towards(current_lat, current_lng, target_lat, target_lng, distance_meters = settings.DRIVER_SPEED):
    """
    Move the current location towards the target location at a fixed distance.
    
    Parameters:
    current_lat, current_lng - starting latitude and longitude
    target_lat, target_lng - target latitude and longitude
    distance_meters - distance to move in meters
    """
    # Convert meters to degrees (approximation, varies by location)
    meters_per_degree = 111000  # Approximate conversion at the equator
    speed = distance_meters / meters_per_degree  # Convert distance to degrees

    # Calculate the deltas
    delta_lat = target_lat - current_lat
    delta_lng = target_lng - current_lng
    total_distance = math.sqrt(delta_lat ** 2 + delta_lng ** 2)

    if total_distance < speed:
        return target_lat, target_lng  # Stop when close enough
    else:
        ratio = speed / total_distance
        new_lat = current_lat + ratio * delta_lat
        new_lng = current_lng + ratio * delta_lng
        return new_lat, new_lng
