import os
import json
from data import get_all_data

name = 'Westwood'

def filter_zone(data):
    lat_min = 34.05
    lat_max = 34.08
    lon_min = -118.45
    lon_max = -118.42

    def is_in_zone(feature):
        geometry = feature.get('geometry')
        if geometry is None:
            return False

        coordinates = geometry.get('coordinates')
        if coordinates is None:
            return False

        if geometry['type'] == 'Polygon':
            for pos in coordinates:
                for lon, lat in pos:
                    if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                        return True
        elif geometry['type'] == 'MultiPolygon':
            for polygon in coordinates:
                for pos in polygon:
                    for lon, lat in pos:
                        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                            return True
        return False

    features = [feature for feature in data['features'] if is_in_zone(feature)]
    data = {
        'borders': {
            'lat_min': lat_min,
            'lat_max': lat_max,
            'lon_min': lon_min,
            'lon_max': lon_max
        },
        'features': features
    }
    return data

def save_data(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    df, data = get_all_data()
    data = filter_zone(data)
    output_file = os.path.join(os.path.dirname(__file__), 'data', name + '_Building_List.json')
    save_data(data, output_file)
    print(f"Filtered data saved to {output_file}")