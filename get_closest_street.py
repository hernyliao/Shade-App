import numpy as np
import math
from data import get_data
from streets import get_streets

def find_centerpoint(house):
    coordinates = house.coordinates
    latitudes = [pos[1] for pos in coordinates[0]]
    longitudes = [pos[0] for pos in coordinates[0]]
    latitude = sum(latitudes) / len(latitudes)
    longitude = sum(longitudes) / len(longitudes)
    
    return (longitude, latitude)

def house_with_street(house, streets):

    centerpoint = find_centerpoint(house)

    closest_dist = 100000000
    closest_street_index = 0
    closest_street = 0

    dist = []

    for i, street in enumerate(streets):
        for points in street.coordinates:
            for point in points:
                # print(f"Point, {point}, centerpoint: {centerpoint}")
                dist.append(get_dist(centerpoint, point))
                recent_dist = dist[-1]
                # print(min_dist)
                # print(closest_dist)
                if recent_dist <= closest_dist:
                    closest_dist = recent_dist
                    closest_street_index = i
                    closest_street = street

    print(recent_dist)

    streets[closest_street_index].selected = True
    print("LEN STREETS: ", len(streets))

    print(closest_street_index)

    return closest_street_index
                    
def get_dist(a, b):
    # print(f"a: {a}, b: {b}")

    if isinstance(a, list) and isinstance(b, list):
        return math.sqrt((a[0][0] - b[0][0]) ** 2 + (a[0][1] - b[0][1]) ** 2)
    elif isinstance(a, int) and isinstance(b, int):
        return math.sqrt(a ** 2 + b ** 2)
    elif isinstance(a, tuple) and isinstance(b, list):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    