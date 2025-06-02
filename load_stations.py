from load_stations_zipcodes import load_stations_zipcodes
from load_stations_daily_temp import load_stations_daily_temp
from load_stations_monthly_precip import load_stations_monthly_precip

def load_stations():
    """
    Load stations from zipcode, temperature, and precipitation data sources and combine them.
    
    Returns:
        dict: Dictionary mapping station IDs to Station objects with combined data
    """
    # Load stations from all data sources
    zipcode_stations = load_stations_zipcodes()
    temp_stations = load_stations_daily_temp()
    precip_stations = load_stations_monthly_precip()
    
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
    
    # Process precipitation stations
    for station_id, precip_station in precip_stations.items():
        if station_id in combined_stations:
            # Station exists in combined dataset - add precipitation data to the existing station
            combined_stations[station_id].avg_rainy_days_per_month = precip_station.avg_rainy_days_per_month
            
            # If location data is missing in the combined station but available in the precip station, add it
            if (combined_stations[station_id].latitude is None and precip_station.latitude is not None):
                combined_stations[station_id].latitude = precip_station.latitude
            
            if (combined_stations[station_id].longitude is None and precip_station.longitude is not None):
                combined_stations[station_id].longitude = precip_station.longitude
        else:
            # Station only exists in precipitation dataset - add it to the combined set
            combined_stations[station_id] = precip_station
    
    return combined_stations

if __name__ == "__main__":
    # Load combined stations
    stations = load_stations()
    
    # Count stations with different types of data
    total_stations = len(stations)
    stations_with_zipcode = sum(1 for station in stations.values() if station.zipcode is not None)
    stations_with_temp = sum(1 for station in stations.values() if station.avg_daily_max_temperature is not None)
    stations_with_precip = sum(1 for station in stations.values() if station.avg_rainy_days_per_month)  # Empty list evaluates to False
    stations_with_both_temp_precip = sum(1 for station in stations.values() 
                           if station.avg_daily_max_temperature is not None and
                              station.avg_rainy_days_per_month)
    stations_with_all = sum(1 for station in stations.values() 
                           if station.zipcode is not None and 
                              station.avg_daily_max_temperature is not None and
                              station.avg_rainy_days_per_month)
    
    # Print summary
    print(f"Loaded {total_stations} total stations")
    print(f"  - {stations_with_zipcode} stations with zipcode data")
    print(f"  - {stations_with_temp} stations with temperature data")
    print(f"  - {stations_with_precip} stations with precipitation data")
    print(f"  - {stations_with_both_temp_precip} stations with both temperature and precipitation data")
    print(f"  - {stations_with_all} stations with zipcode, temperature, and precipitation data")    
    # Print a few examples of combined stations
    print("\nSample stations:")
    for i, (station_id, station) in enumerate(list(stations.items())[:3]):
        zipcode_info = f"Zipcode: {station.zipcode}" if station.zipcode else "No zipcode data"
        temp_info = "Has temperature data" if hasattr(station, 'avg_daily_max_temperature') and station.avg_daily_max_temperature else "No temperature data"
        precip_info = "Has precipitation data" if hasattr(station, 'avg_rainy_days_per_month') and station.avg_rainy_days_per_month else "No precipitation data"
        print(f"Station {i+1}: {station_id} - {zipcode_info}, {temp_info}, {precip_info}")
