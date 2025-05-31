import os
import sys
import re
import pytest

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from load_stations_zipcodes import load_stations_zipcodes, ZIPCODES_NORMALS_STATIONS

def test_load_stations_zipcodes():
    """Test that stations are loaded correctly from the file."""
    # Make sure the file exists
    assert os.path.exists(ZIPCODES_NORMALS_STATIONS), \
        f"Test data file {ZIPCODES_NORMALS_STATIONS} does not exist"
    
    # Load the stations
    stations = load_stations_zipcodes()
    
    # Check that we have the expected number of stations
    assert len(stations) == 9794, \
        f"Expected 9794 stations, but got {len(stations)}"
    
    # Check that each station has an ID and a valid zipcode
    for station_id, station in stations.items():
        # Check station ID
        assert station.station_id is not None, \
            f"Station {station_id} has no ID set"
        assert station.station_id == station_id, \
            f"Station ID mismatch: {station.station_id} != {station_id}"
        
        # Check zipcode
        assert station.zipcode is not None, \
            f"Station {station_id} has no zipcode set"
        assert re.match(r'^\d{5}$', station.zipcode), \
            f"Station {station_id} has invalid zipcode: {station.zipcode}"

def test_station_count_matches_file():
    """Verify that the number of stations matches the number of unique station IDs in the file."""
    # Count unique station IDs in the file
    unique_ids = set()
    valid_lines = 0
    
    with open(ZIPCODES_NORMALS_STATIONS, 'r') as file:
        for line in file:
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 2:
                    station_id = parts[0]
                    zipcode = parts[1]
                    # Only count lines with valid zipcodes
                    if re.match(r'^\d{5}$', zipcode):
                        unique_ids.add(station_id)
                        valid_lines += 1
    
    # Load the stations
    stations = load_stations_zipcodes()
    
    # Check that the number of stations matches the number of unique IDs
    assert len(stations) == len(unique_ids), \
        f"Number of stations ({len(stations)}) doesn't match unique IDs in file ({len(unique_ids)})"
    
    # Print some stats for debugging
    print(f"Total valid lines in file: {valid_lines}")
    print(f"Unique station IDs with valid zipcodes: {len(unique_ids)}")
    print(f"Stations loaded: {len(stations)}")
