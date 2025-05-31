from load_stations_zipcodes import load_stations_zipcodes
from load_stations_daily_temp import load_stations_daily_temp

def load_stations():
    """
    Load stations from both zipcode and temperature data sources and combine them.
    
    Returns:
        dict: Dictionary mapping station IDs to Station objects with combined data
    """
    # Load stations from both data sources
    zipcode_stations = load_stations_zipcodes()
    temp_stations = load_stations_daily_temp()
    
    # Start with all zipcode stations
    combined_stations = zipcode_stations.copy()
    
    # Process temperature stations
    for station_id, temp_station in temp_stations.items():
        if station_id in combined_stations:
            # Station exists in both datasets - add temperature data to the existing station
            combined_stations[station_id].avg_daily_max_temperature = temp_station.avg_daily_max_temperature
        else:
            # Station only exists in temperature dataset - add it to the combined set
            combined_stations[station_id] = temp_station
    
    return combined_stations

if __name__ == "__main__":
    # Load combined stations
    stations = load_stations()
    
    # Count stations with different types of data
    total_stations = len(stations)
    stations_with_zipcode = sum(1 for station in stations.values() if station.zipcode is not None)
    stations_with_temp = sum(1 for station in stations.values() if station.avg_daily_max_temperature is not None)
    stations_with_both = sum(1 for station in stations.values() 
                           if station.zipcode is not None and station.avg_daily_max_temperature is not None)
    
    # Print summary
    print(f"Loaded {total_stations} total stations")
    print(f"  - {stations_with_zipcode} stations with zipcode data")
    print(f"  - {stations_with_temp} stations with temperature data")
    print(f"  - {stations_with_both} stations with both zipcode and temperature data")
    
    # Print a few examples of combined stations
    print("\nSample stations:")
    for i, (station_id, station) in enumerate(list(stations.items())[:3]):
        zipcode_info = f"Zipcode: {station.zipcode}" if station.zipcode else "No zipcode data"
        temp_info = "Has temperature data" if station.avg_daily_max_temperature else "No temperature data"
        print(f"Station {i+1}: {station_id} - {zipcode_info}, {temp_info}")
