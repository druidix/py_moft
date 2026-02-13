#! /usr/bin/env python3
"""
This script uses the OpenSky API to get the current state of all aircraft in the U.S.
# U.S. bounding box (min_lat, max_lat, min_lon, max_lon) in WGS84
(24.52, 49.38, -124.77, -66.95)
It will print the state of all aircraft to the console.
"""

import requests
import json

US_BBOX = (24.52, 49.38, -124.77, -66.95)
OPENSKY_NETWORK_URL = "https://opensky-network.org/api/states/all"


def get_aircraft_data(bbox: tuple[float, float, float, float]) -> dict:
    """
    Get the current state of all aircraft in the U.S.
    """
    params = {
        "bbox": ",".join(str(coord) for coord in bbox),
    }
    response = requests.get(OPENSKY_NETWORK_URL, params=params)
    if response.status_code == 200:
        return response.json()["states"]
    else:
        raise Exception(f"Failed to get aircraft data: {response.status_code} {response.text}")


"""Driver code"""
aircraft_data = get_aircraft_data(US_BBOX)
# print(aircraft_data)
print ('>>>Bounding Box with coordinates: ' + str(US_BBOX) + '<<<')
print('>>>' + str(len(aircraft_data)) + ' entries total<<<')