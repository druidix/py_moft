#! /usr/bin/env python3
"""
This script uses the OpenSky API to get the current state of all aircraft in the U.S.
# U.S. bounding box (min_lat, max_lat, min_lon, max_lon) in WGS84
(24.52, 49.38, -124.77, -66.95)
It will print the state of all aircraft to the console.
"""

import requests
import sys
import os

US_BBOX = (24.52, 49.38, -124.77, -66.95)
OPENSKY_NETWORK_URL = "https://opensky-network.org/api/states/all"
PAGE_SIZE = 20


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


def wait_for_key() -> None:
    """
    Pause until the user presses a key.
    Uses single-key capture when stdin is a TTY, with a safe Enter fallback.
    """
    if not sys.stdin.isatty():
        return

    print("\nPress any key for next page (q to quit)...", end="", flush=True)

    if os.name == "nt":
        import msvcrt

        key = msvcrt.getch()
        print()
        if key.lower() == b"q":
            raise KeyboardInterrupt
        return

    import tty
    import termios

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        print()
        if key.lower() == "q":
            raise KeyboardInterrupt
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def print_paginated(data: list, page_size: int = PAGE_SIZE) -> None:
    total = len(data)
    if total == 0:
        print("No aircraft data returned.")
        return

    total_pages = (total + page_size - 1) // page_size
    for page_index in range(total_pages):
        start = page_index * page_size
        end = min(start + page_size, total)
        print(f"\n=== Page {page_index + 1}/{total_pages} | Records {start + 1}-{end} of {total} ===")

        for row_index, row in enumerate(data[start:end], start=start + 1):
            print(f"{row_index:>5}: {row}")

        if page_index < total_pages - 1:
            wait_for_key()


def main() -> None:
    aircraft_data = get_aircraft_data(US_BBOX)
    print(f">>>Bounding Box with coordinates: {US_BBOX}<<<")
    print(f">>>{len(aircraft_data)} entries total<<<")
    print_paginated(aircraft_data)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
