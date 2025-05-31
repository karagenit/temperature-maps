from station import Station

DAILY_TMAX_NORMAL_FILE = 'noaa/dly-tmax-normal.txt'

def load_stations_daily_temp():
    """
    Load daily maximum temperature data from the dly-tmax-normal.txt file.
    
    Returns:
        dict: Dictionary mapping station IDs to Station objects with temperature data
    """
    stations = {}
    
    try:
        with open(DAILY_TMAX_NORMAL_FILE, 'r') as file:
            for line in file:
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Parse the line
                parts = line.strip().split()
                if len(parts) >= 33:  # Station ID, month, and 31 days of data
                    station_id = parts[0]
                    month = int(parts[1]) - 1  # Convert to 0-based index (0-11)
                    
                    # Create a new Station object if we haven't seen this station before
                    if station_id not in stations:
                        station = Station()
                        station.station_id = station_id
                        # Initialize temperature data structure (12 months, 31 days each)
                        station.avg_daily_max_temperature = [[None for _ in range(31)] for _ in range(12)]
                        stations[station_id] = station
                    
                    # Process temperature data for each day of the month
                    for day in range(31):
                        temp_str = parts[day + 2]  # +2 because parts[0] is station_id and parts[1] is month
                        
                        # Check if it's a special value (-8888)
                        if temp_str.startswith('-8888'):
                            stations[station_id].avg_daily_max_temperature[month][day] = None
                        else:
                            # Extract the numeric part (ignoring the flag character)
                            numeric_part = temp_str.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                            try:
                                # Convert to float and divide by 10 (data is in tenths of degrees)
                                temp_value = float(numeric_part) / 10.0
                                stations[station_id].avg_daily_max_temperature[month][day] = temp_value
                            except ValueError:
                                # If conversion fails, store None
                                stations[station_id].avg_daily_max_temperature[month][day] = None
    
    except FileNotFoundError:
        print(f"Error: File '{DAILY_TMAX_NORMAL_FILE}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return stations

if __name__ == "__main__":
    # Example usage
    temp_stations = load_stations_daily_temp()
    print(f"Loaded temperature data for {len(temp_stations)} stations")
    
    # Print sample of the data for the first station
    if temp_stations:
        sample_station_id = next(iter(temp_stations))
        sample_station = temp_stations[sample_station_id]
        print(f"Sample data for station {sample_station_id}:")
        
        # Print January temperatures (first 10 days)
        print("January temperatures (first 10 days):")
        jan_temps = sample_station.avg_daily_max_temperature[0][:10]
        for day, temp in enumerate(jan_temps, 1):
            print(f"  Day {day}: {temp}°F")
