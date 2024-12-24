import os
import pandas as pd
import json

def get_data(name):
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data', name + '_Building_List.json')

    with open(file_path) as f:
        data = json.load(f)

    df = pd.json_normalize(data, record_path=['features'])
    df = df[['geometry.coordinates', 'properties.HEIGHT', 'properties.ELEV', 'geometry.type']]
    df = df.rename(columns={'geometry.coordinates': 'coordinates', 'properties.HEIGHT': 'height', 'properties.ELEV': 'elevation', 'geometry.type': 'geometry_type'})
    return df, data

def get_all_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data', 'Full_Building_List_Compact.json')

    with open(file_path) as f:
        data = json.load(f)

    df = pd.json_normalize(data, record_path=['features'])
    df = df[['geometry.coordinates', 'properties.HEIGHT', 'properties.ELEV', 'geometry.type']]
    df = df.rename(columns={'geometry.coordinates': 'coordinates', 'properties.HEIGHT': 'height', 'properties.ELEV': 'elevation', 'geometry.type': 'geometry_type'})
    return df, data