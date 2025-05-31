from station import Station

ZIPCODES_NORMALS_STATIONS = 'noaa/zipcodes-normals-stations.txt'

def load_stations_zipcodes():
    """
    Load stations from the zipcodes-normals-stations.txt file.
    
    Returns:
        dict: Dictionary mapping station IDs to Station objects
    """
    stations = {}
    
    try:
        with open(ZIPCODES_NORMALS_STATIONS, 'r') as file:
            for line in file:
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Parse the line
                parts = line.strip().split()
                if len(parts) >= 1:
                    station_id = parts[0]
                    
                    # Create a new Station object if we haven't seen this station before
                    if station_id not in stations:
                        station = Station()
                        station.station_id = station_id
                        stations[station_id] = station
                
    except FileNotFoundError:
        print(f"Error: File '{ZIPCODES_NORMALS_STATIONS}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return stations

if __name__ == "__main__":
    # Example usage
    stations = load_stations_zipcodes()
    print(f"Loaded {len(stations)} unique stations")
    
    # Print first few stations as a sample
    for i, (station_id, station) in enumerate(list(stations.items())[:5]):
        print(f"Station {i+1}: {station_id}")
