import pandas as pd
import math
from datetime import datetime
import pytz
from pysolar.solar import get_altitude, get_azimuth

def calculate_shade(df, data, current_time=None):
    for feature in data['features']:
        geometry = feature.get('geometry')
        if geometry is None:
            latitude = 34.0522
            longitude = -118.2437

        coordinates = geometry.get('coordinates')
        if coordinates is None:
            latitude = 34.0522
            longitude = -118.2437

        if geometry.get('type') == 'Polygon':
            latitudes = [pos[1] for pos in coordinates[0]]
            longitudes = [pos[0] for pos in coordinates[0]]
            latitude = sum(latitudes) / len(latitudes)
            longitude = sum(longitudes) / len(longitudes)

        elif geometry.get('type') == 'MultiPolygon':
            for index in range(len(coordinates)):
                latitudes = [pos[1] for pos in coordinates[index][0]]
                longitudes = [pos[0] for pos in coordinates[index][0]]
                latitude = sum(latitudes) / len(latitudes)
                longitude = sum(longitudes) / len(longitudes)

    # Get the current time if not provided
    if current_time is None:
        timezone = pytz.timezone('America/Los_Angeles')
        current_time = datetime.now(timezone)

    # Get the sun altitude angle
    sun_altitude = get_altitude(latitude, longitude, current_time)
    sun_azimuth = get_azimuth(latitude, longitude, current_time)

    # Conversion factor from feet to degrees (approximate)
    feet_to_degrees = 1 / 364000

    # Calculate the shadow length for each building in degrees
    df['shadow_length'] = ((df['height']) * feet_to_degrees) / math.tan(math.radians(sun_altitude))
    df['type'] = df['geometry_type'] # Assign the type of the geometry to the dataframe

    # Calculate the shadow coordinates
    shadow_coordinates = []
    for row in df.itertuples():
        shadow_coords = calculate_shadow_coordinates(row.coordinates, row.type, row.shadow_length, sun_azimuth)
        shadow_coordinates.append([shadow_coords])
    df['shadow_coordinates'] = shadow_coordinates
    
    df = pd.DataFrame(df, columns=['shadow_coordinates', 'type'])
    return df

def calculate_shadow_coordinates(coordinates, type, shadow_length, sun_azimuth):
    # Calculate the direction of the shadow based on the sun's position (180 degrees opposite)
    shadow_direction = (sun_azimuth + 180) % 360

    # Convert the shadow direction to radians
    shadow_direction_rad = math.radians(shadow_direction)
    shadow_coords = []
    if type == 'MultiPolygon':  # Check if it's a MultiPolygon
        for polygon in coordinates:
            polygon_shadow_coords = []
            for pos in polygon[0]:
                shadow_x = pos[0] + shadow_length * math.cos(shadow_direction_rad)
                shadow_y = pos[1] + shadow_length * math.sin(shadow_direction_rad)
                polygon_shadow_coords.append([shadow_x, shadow_y])
            shadow_coords.append(polygon_shadow_coords)
    elif type == 'Polygon':  # It's a Polygon
        for pos in coordinates[0]:
            shadow_x = pos[0] + shadow_length * math.cos(shadow_direction_rad)
            shadow_y = pos[1] + shadow_length * math.sin(shadow_direction_rad)
            shadow_coords.append([shadow_x, shadow_y])
    # print(len(shadow_coords))
    return shadow_coords