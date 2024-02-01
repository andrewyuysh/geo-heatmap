from datetime import datetime
import json
import pandas as pd
import numpy as np
from tqdm import tqdm

RADIUS_OF_EARTH_M = 6378137

def load_data(file_path='Records.json'):
    """streamJSON, ZIP, GPX, KML not impl"""
    with open(file_path) as json_file:
        data = json.load(json_file)
    ret = []
    key_timestamp = 'timestampMs' if 'timestampMs' in data["locations"][0] else 'timestamp'
    for loc in data["locations"]:
        if "latitudeE7" not in loc or "longitudeE7" not in loc:
            continue
        coords = (round(loc["latitudeE7"] / 1e7, 6),
                round(loc["longitudeE7"] / 1e7, 6))
        timestamp = loc[key_timestamp] 
        if timestamp[-1] != 'Z': print(timestamp)
        timestamp = datetime.fromisoformat(timestamp[:-1])
        ret.append({'lat': coords[0], 'long': coords[1], 'time': timestamp})
    return pd.DataFrame(ret)

def distance(lat1, long1, lat2, long2):
    lat1_rad = np.radians(lat1)
    long1_rad = np.radians(long1)
    lat2_rad = np.radians(lat2)
    long2_rad = np.radians(long2)

    # Haversine formula components
    dlat = lat2_rad - lat1_rad
    dlon = long2_rad - long1_rad
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # Distance calculation
    return RADIUS_OF_EARTH_M * c