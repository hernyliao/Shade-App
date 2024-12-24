import os
import json
import pandas as pd

def get_all_streets():
    # Get the base path (assuming this script is in the same directory as the file)
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data', 'Street Centerline.json')

    # Open and load the Json file
    with open(file_path) as f:
        data = json.load(f)

    # print(data)
    # Normalize the Json data. Assuming the 'features' key contains the list of geographical data.
    df = pd.json_normalize(data, record_path=['features'])
    # df = df[['properties.stname', 'properties.zip_r', 'geometry.coordinates']]

    return df, data

def get_streets(name):
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data', name + '_Street_List.json')

    with open(file_path) as f:
        data = json.load(f)

    df = pd.json_normalize(data, record_path=['features'])
    df = df[['geometry.coordinates', 'properties.stname', 'properties.zip_r']]
    df = df.rename(columns={'geometry.coordinates': 'coordinates', 'properties.stname': 'street_name', 'properties.zip_r': 'zip'})
    return df, data

# df, data = get_all_streets()
# pd.set_option('display.max_columns', None)
# print(df.info())
# print(df.head())