import os
import csv
from station import Station

MONTHLY_PRECIP_DIR = 'noaa/normals-monthly/'

# TODO would also like to count snowfall days at some point and count those as precipitation
# TODO also might be better to use 0.1" cutoff for rainy days instead.
def load_stations_monthly_precip():
    """
    Load monthly precipitation data from CSV files in the normals-monthly directory.
    Each CSV file represents a station with the filename being the station ID.
    
    Returns:
        dict: Dictionary mapping station IDs to Station objects with precipitation data
    """
    stations = {}
    
    try:
        # Check if directory exists
        if not os.path.isdir(MONTHLY_PRECIP_DIR):
            print(f"Error: Directory '{MONTHLY_PRECIP_DIR}' not found.")
            return stations
        
        # Process each CSV file in the directory
        for filename in os.listdir(MONTHLY_PRECIP_DIR):
            if not filename.endswith('.csv'):
                continue
                
            station_id = os.path.splitext(filename)[0]  # Remove .csv extension to get station ID
            file_path = os.path.join(MONTHLY_PRECIP_DIR, filename)
            
            # Create a new station object
            station = Station()
            station.station_id = station_id
            
            # Initialize precipitation data array (12 months)
            # TODO should probably be None that way we can tell if it's unloaded vs actually zero
            precip_data = [0] * 12
            
            # Read the CSV file
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Get the month (1-based in the CSV, convert to 0-based for our array)
                    try:
                        month = int(row['DATE']) - 1  # DATE column contains the month number
                        
                        # Get the precipitation value
                        if 'MLY-PRCP-AVGNDS-GE050HI' in row:
                            precip_value = row['MLY-PRCP-AVGNDS-GE050HI']
                            
                            # Convert to float if it's a valid number
                            # TODO seems like some of these are -7777 (missing data)? In that case we should skip it as well, though it's not a big deal because later in Station.py there's a validation to make sure it's 0-31
                            if precip_value and precip_value != 'S' and precip_value != 'P':
                                # The data is the sum over 30 years, so divide by 30 to get the average
                                precip_data[month] = float(precip_value) / 30.0
                        
                        # Get latitude and longitude (only need to set once)
                        if month == 0:  # Only process for the first month to avoid redundancy
                            if 'LATITUDE' in row and not station.latitude:
                                try:
                                    station.latitude = row['LATITUDE']
                                except ValueError:
                                    # Skip invalid latitude
                                    pass
                                
                            if 'LONGITUDE' in row and not station.longitude:
                                try:
                                    station.longitude = row['LONGITUDE']
                                except ValueError:
                                    # Skip invalid longitude
                                    pass
                    except (ValueError, IndexError):
                        # Skip rows with invalid data
                        continue
            
            # Set the precipitation data on the station. If any values are invalid or None this will throw exception, so just skip that station
            try:
                station.avg_rainy_days_per_month = precip_data
            except ValueError as e:
                continue
            
            # Add the station to our dictionary
            stations[station_id] = station
    
    except Exception as e:
        print(f"Error loading precipitation data: {e}")
    
    return stations

if __name__ == "__main__":
    # Example usage
    precip_stations = load_stations_monthly_precip()
    print(f"Loaded precipitation data for {len(precip_stations)} stations")
    
    # Print sample of the data for the first station
    if precip_stations:
        sample_station_id = next(iter(precip_stations))
        sample_station = precip_stations[sample_station_id]
        print(f"Sample data for station {sample_station_id}:")
        
        # Print location data
        print(f"  Location: {sample_station.latitude}, {sample_station.longitude}")
        
        # Print monthly precipitation data
        print("Monthly precipitation data (average days with ≥0.5\" rainfall):")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for month_idx, days in enumerate(sample_station.avg_rainy_days_per_month):
            print(f"  {months[month_idx]}: {days:.2f} days")