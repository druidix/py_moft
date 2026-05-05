"""
Flask web UI for py_moft — My Own Flight Tracker.
Run with:  python app.py
Then open: http://localhost:5000
"""

import requests
from flask import Flask, render_template, jsonify
from main import get_flight_results, get_access_token, REQUEST_TIMEOUT_SECONDS

app = Flask(__name__)

# OpenSky state vector field indices
FIELDS = [
    "icao24",        # 0
    "callsign",      # 1
    "country",       # 2
    "time_position", # 3
    "last_contact",  # 4
    "longitude",     # 5
    "latitude",      # 6
    "baro_altitude", # 7
    "on_ground",     # 8
    "velocity",      # 9
    "heading",       # 10
    "vertical_rate", # 11
    "sensors",       # 12
    "geo_altitude",  # 13
    "squawk",        # 14
    "spi",           # 15
    "position_source", # 16
]

# Columns to show in the table (subset of FIELDS)
DISPLAY_COLUMNS = [
    "callsign",
    "country",
    "baro_altitude",
    "velocity",
    "heading",
    "vertical_rate",
    "latitude",
    "longitude",
    "on_ground",
    "icao24",
]


def parse_aircraft(raw_states: list) -> list[dict]:
    """Convert raw OpenSky state vectors into named dicts."""
    aircraft = []
    for state in raw_states:
        if state is None:
            continue
        row = {}
        for i, field in enumerate(FIELDS):
            row[field] = state[i] if i < len(state) else None
        # Clean up callsign whitespace
        if row["callsign"]:
            row["callsign"] = row["callsign"].strip()
        # Round numeric fields for readability
        for field in ("baro_altitude", "geo_altitude", "velocity",
                      "heading", "vertical_rate", "latitude", "longitude"):
            if row[field] is not None:
                row[field] = round(row[field], 1)
        aircraft.append(row)
    return aircraft


@app.route("/")
def index():
    error = None
    aircraft = []
    count = 0
    try:
        raw = get_flight_results()
        aircraft = parse_aircraft(raw or [])
        count = len(aircraft)
    except Exception as e:
        error = str(e)

    return render_template(
        "index.html",
        aircraft=aircraft,
        columns=DISPLAY_COLUMNS,
        count=count,
        error=error,
    )


@app.route("/api/flights")
def api_flights():
    """JSON endpoint — useful for future JS-driven refresh."""
    try:
        raw = get_flight_results()
        return jsonify({"ok": True, "data": parse_aircraft(raw or [])})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


OPENSKY_METADATA_URL = "https://opensky-network.org/api/metadata/aircraft/icao"


@app.route("/api/aircraft/<icao24>")
def api_aircraft_metadata(icao24):
    try:
        token = get_access_token()
        response = requests.get(
            f"{OPENSKY_METADATA_URL}/{icao24}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code == 200:
            return jsonify({"ok": True, "data": response.json()})
        if response.status_code == 404:
            return jsonify({"ok": True, "data": None})
        return jsonify({"ok": False, "error": f"HTTP {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
