import pygame as py
import numpy as np
import pytz
from datetime import datetime
from shapely.geometry import Polygon
import math
import random
from sun import calculate_shade
from data import get_data
from streets import get_streets
from get_closest_street import house_with_street, find_centerpoint

py.init()

WIDTH = 800
HEIGHT = 800

center_x = WIDTH / 2
center_y = HEIGHT / 2

FPS = 60
ZOOM = 1
SHIFT = None

clock = py.time.Clock()
screen = py.display.set_mode([WIDTH, HEIGHT])
py.display.set_caption("Shade Map")
font = py.font.Font(None, 36)

name = 'Westwood Village'
time = (12, 0)

time = np.array(time)

# Define colors
background_color = (20, 20, 20)
house_color = (220, 220, 220)
shadow_color = (255,0,0)
street_color = (0, 255, 0)

time_zone = pytz.timezone('America/Los_Angeles')
manual_time = time_zone.localize(datetime(2023, 12, 23, time[0], time[1]))  # Example: December 21, 2024, 6:00 AM

# Get the building, street, and shadow data
df, data = get_data(name)
street_df, street_data = get_streets(name)
shade_df = calculate_shade(df, data, current_time=manual_time)
    
def get_maxmin(data):
    lon_min, lon_max = float('inf'), float('-inf')
    lat_min, lat_max = float('inf'), float('-inf')

    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            for polygon in feature['geometry']['coordinates']:
                for lon, lat in polygon:
                    lon_min = min(lon_min, lon)
                    lon_max = max(lon_max, lon)
                    lat_min = min(lat_min, lat)
                    lat_max = max(lat_max, lat)
        elif feature['geometry']['type'] == 'MultiPolygon':
            for multipolygon in feature['geometry']['coordinates']:
                for polygon in multipolygon:
                    for lon, lat in polygon:
                        lon_min = min(lon_min, lon)
                        lon_max = max(lon_max, lon)
                        lat_min = min(lat_min, lat)
                        lat_max = max(lat_max, lat)

    return lon_min, lon_max, lat_min, lat_max

lon_min, lon_max, lat_min, lat_max = get_maxmin(data)

# Scale buffer and SHIFT to the size of the map.
buffer = 0.005 * (lon_max - lon_min + lat_max - lat_min)
SHIFT = float((lon_max - lon_min + lat_max - lat_min) * 750)

# Add buffer to the map
lon_min -= buffer
lon_max += buffer
lat_min -= buffer
lat_max += buffer

# Define classes
class House:
    def __init__(self, coordinates, height, elevation, type, selected):
        self.coordinates = coordinates
        self.height = height
        self.meters_sealevel = elevation
        self.type = type
        self.selected = selected

    def draw(self):
        if self.selected:
            color = (0, 0, 200)
        else:
            color = house_color
        if self.type == 'MultiPolygon':  # Check if it's a multipolygon
            for polygon in self.coordinates:
                if len(polygon) >= 3:
                    py.draw.polygon(screen, color, polygon)
        else:  # It's a polygon or courtyard
            if len(self.coordinates[0]) >= 3:
                py.draw.polygon(screen, color, self.coordinates[0])

class Shadow:
    def __init__(self, coordinates, type):
        self.coordinates = coordinates
        self.area = Polygon(self.coordinates[0]).area
        self.type = type

    def draw(self):
        if self.type == 'MultiPolygon':  # Check if it's a multipolygon
            for polygon in self.coordinates:
                if len(polygon) >= 3:
                    py.draw.polygon(screen, shadow_color, polygon)
        else:  # It's a polygon or courtyard
            if len(self.coordinates[0]) >= 3:
                py.draw.polygon(screen, (255 - min(255, math.log(self.area) ** 2 - 150), 0, 0), self.coordinates[0])

class Street: 
    def __init__(self, coordinates, selected):
        self.coordinates = coordinates
        self.selected = selected

    def draw(self):
        if self.selected:
            color = (0, 0, 200)
        else:
            color = street_color
        if len(self.coordinates[0]) >= 2:
            py.draw.lines(screen, color, False, self.coordinates[0], 2)

# Create map objects
map = [
    House(row['coordinates'], row['height'], row['elevation'], row['type'], False) for _, row in df.iterrows()
]

selected_map1 = map[random.randint(1, len(map) - 1)]
selected_map2 = map[random.randint(1, len(map) - 1)]

selected_map1.selected = True
selected_map2.selected = True

shade_map = [
    Shadow(row['shadow_coordinates'], row['type']) for _, row in shade_df.iterrows()
]

street_map = [
    Street(row['coordinates'], False) for _, row in street_df.iterrows()
]

street_map[house_with_street(selected_map1, street_map)].selected = True
street_map[house_with_street(selected_map2, street_map)].selected = True

# Returns the vector and ZOOM based off keypresses
def check_key_press(ZOOM):
    if keys[py.K_a] or keys[py.K_LEFT]:
        vector = (SHIFT, 0)
    elif keys[py.K_d] or keys[py.K_RIGHT]:
        vector = (-SHIFT, 0)
    elif keys[py.K_s] or keys[py.K_DOWN]:
        vector = (0, -SHIFT)
    elif keys[py.K_w] or keys[py.K_UP]:
        vector = (0, SHIFT)
    else:
        vector = (0, 0)

    if ZOOM > 0:
        if keys[py.K_EQUALS]:
            ZOOM += 0.001
        elif keys[py.K_MINUS]:
            ZOOM -= 0.001
        else: # Reset zoom so it doesn't keep zooming in/out
            ZOOM = 1
    return vector, ZOOM

# Update time
def update_time(time):
    time[1] += 1
    if time[1] == 60: # Reset minutes to 0 if it reaches 60
        time[1] = 0 
        time[0] += 1
    time[0] = time[0] % 24 # Reset to 0 if it reaches 24
    return time

# Scale the positions of the houses, streets, and shadows to the map size
def scale_positions(map, shade_map, street_map, lon_min, lon_max, lat_min, lat_max):
    def scale_to_screen(pos, type, lon_min, lon_max, lat_min, lat_max):
        if type == 'MultiPolygon':
            scaled_positions = []
            for polygon in pos:
                scaled_polygon = []
                if isinstance(pos, list) and isinstance(polygon, list):
                    for group in polygon:
                        for pos in group:
                            x = ((pos[0] - lon_min) / (lon_max - lon_min)) * WIDTH
                            y = ((lat_max - pos[1]) / (lat_max - lat_min)) * HEIGHT
                            scaled_polygon.append((float(x), float(y)))
                        scaled_positions.append(scaled_polygon)
            return scaled_positions
        else:
            x = ((pos[0] - lon_min) / (lon_max - lon_min)) * WIDTH
            y = ((lat_max - pos[1]) / (lat_max - lat_min)) * HEIGHT
            return (float(x), float(y))

    for house in map:
        if house.type == 'MultiPolygon':
            scaled_position = scale_to_screen(house.coordinates, house.type, lon_min, lon_max, lat_min, lat_max)
            house.coordinates = scaled_position
        else:  # It's a polygon
            for i, position in enumerate(house.coordinates[0]):
                scaled_position = scale_to_screen(position, house.type, lon_min, lon_max, lat_min, lat_max)
                house.coordinates[0][i] = scaled_position

    for shadow in shade_map:
        if shadow.type == 'MultiPolygon':  # Check if it's a multipolygon
            scaled_position = scale_to_screen(shadow.coordinates, shadow.type, lon_min, lon_max, lat_min, lat_max)
            shadow.coordinates = scaled_position
        else:  # It's a polygon
            for i, position in enumerate(shadow.coordinates[0]):
                scaled_position = scale_to_screen(position, shadow.type, lon_min, lon_max, lat_min, lat_max)
                shadow.coordinates[0][i] = scaled_position
    
    for street in street_map:
        for i, position in enumerate(street.coordinates[0]):
            scaled_position = scale_to_screen(position, None, lon_min, lon_max, lat_min, lat_max)
            street.coordinates[0][i] = scaled_position

scale_positions(map, shade_map, street_map, lon_min, lon_max, lat_min, lat_max)

# Draw the map
def draw_map(map, shade_map, vector, ZOOM):
    center_x = WIDTH / 2
    center_y = HEIGHT / 2

    def apply_movement(position, type, vector, ZOOM, center_x, center_y):
        position = np.array(position)
        if type == 'MultiPolygon':
            for i in range(len(position)):
                position[i][0] += vector[0]
                position[i][1] += vector[1]

                # ZOOM (FROM CENTER)
                position[i][0] -= center_x
                position[i][1] -= center_y

                position[i][0] *= ZOOM
                position[i][1] *= ZOOM

                position[i][0] += center_x
                position[i][1] += center_y
        else:
            position[0] += vector[0]
            position[1] += vector[1]

            # ZOOM (FROM CENTER)
            position[0] -= center_x
            position[1] -= center_y

            position[0] *= ZOOM
            position[1] *= ZOOM

            position[0] += center_x
            position[1] += center_y
        return position

    for shadow in shade_map:
        if shadow.type == 'MultiPolygon':  # Check if it's a multipolygon
            for i, polygon in enumerate(shadow.coordinates):
                shadow.coordinates[i] = apply_movement(polygon, shadow.type, vector, ZOOM, center_x, center_y)
        else: # It's a polygon
            for i, position in enumerate(shadow.coordinates[0]):
                shadow.coordinates[0][i] = apply_movement(position, shadow.type, vector, ZOOM, center_x, center_y)
        shadow.draw()

    for house in map:
        if house.type == 'MultiPolygon': # Check if it's a multipolygon
            for i, polygon in enumerate(house.coordinates):
                house.coordinates[i] = apply_movement(polygon, house.type, vector, ZOOM, center_x, center_y)
        else: # It's a polygon
            for i, position in enumerate(house.coordinates[0]):
                house.coordinates[0][i] = apply_movement(position, house.type, vector, ZOOM, center_x, center_y)
        house.draw()

    for street in street_map:
        for i, position in enumerate(street.coordinates[0]):
            street.coordinates[0][i] = apply_movement(position, None, vector, ZOOM, center_x, center_y)

        street.draw()

# Main loop
running = True
while running:
    keys = py.key.get_pressed()
    pressed = py.mouse.get_pressed()
    vector, ZOOM = check_key_press(ZOOM)

    clock.tick(FPS)
    for event in py.event.get():
        if event.type == py.QUIT or keys[py.K_ESCAPE]:
            running = False

    screen.fill(background_color)
    time = update_time(time)

    # time_font = font.render(f"Time: {time[0]}:{time[1]}", True, background_color, house_color)
    # screen.blit(time_font, (10, HEIGHT - 50))

    draw_map(map, shade_map, vector, ZOOM)
    
    py.display.flip()

py.quit()