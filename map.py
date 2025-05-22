import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def create_temperature_map():
    # Step 1: Load and process the temperature data
    print("Loading temperature data...")
    
    # Dictionary to store January 1st temperatures by station ID
    station_temps = {}
    
    # Read the temperature data file
    with open('dly-tmax-normal.txt', 'r') as f:
        for line in f:
            parts = line.split()
            station_id = parts[0]
            month = parts[1]
            
            # We only care about January (month 01)
            if month == '01':
                # The first temperature value after the month is January 1st
                # Format is like "875C" where 875 is 87.5°F and C is the flag
                temp_str = parts[2]
                # Extract the numeric part and convert to float
                temp_value = float(temp_str.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) / 10.0  # Convert from tenths to actual degrees
                station_temps[station_id] = temp_value
    
    print(f"Loaded temperatures for {len(station_temps)} stations")
    
    # Step 2: Load the station to zipcode mapping
    print("Loading station to zipcode mapping...")
    station_to_zip = {}
    
    with open('zipcodes-normals-stations.txt', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                station_id = parts[0]
                zipcode = parts[1]
                station_to_zip[station_id] = zipcode
    
    print(f"Loaded zipcode mappings for {len(station_to_zip)} stations")
    
    # Step 3: Create a mapping from zipcode to temperature
    zipcode_temps = {}
    
    for station_id, temp in station_temps.items():
        if station_id in station_to_zip:
            zipcode = station_to_zip[station_id]
            # If multiple stations map to the same zipcode, take the average
            if zipcode in zipcode_temps:
                zipcode_temps[zipcode].append(temp)
            else:
                zipcode_temps[zipcode] = [temp]
    
    # Calculate average temperature for each zipcode
    zipcode_avg_temps = {zipcode: np.mean(temps) for zipcode, temps in zipcode_temps.items()}
    
    print(f"Calculated temperatures for {len(zipcode_avg_temps)} zipcodes")
    
    # Step 4: Load the zipcode shapefile
    print("Loading zipcode shapefile...")
    zipcode_gdf = gpd.read_file('cb_2020_us_zcta520_500k/cb_2020_us_zcta520_500k.shp')
    
    # Step 5: Join temperature data with zipcode geometries
    # Convert the temperature dictionary to a DataFrame
    temp_df = pd.DataFrame(list(zipcode_avg_temps.items()), columns=['ZCTA5CE20', 'temperature'])
    
    # Convert ZCTA5CE20 to string to match the shapefile
    temp_df['ZCTA5CE20'] = temp_df['ZCTA5CE20'].astype(str)
    
    # Merge with the GeoDataFrame
    merged_gdf = zipcode_gdf.merge(temp_df, on='ZCTA5CE20', how='left')
    
    print(f"Merged temperature data with {merged_gdf['temperature'].notna().sum()} zipcodes")
    
    # Step 6: Create a custom colormap (blue to white to red)
    cmap = LinearSegmentedColormap.from_list('temp_cmap', ['blue', 'white', 'red'])
    
    # Step 7: Create the map
    print("Creating temperature map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot zipcodes with temperature data
    merged_gdf.plot(
        column='temperature',
        cmap=cmap,
        linewidth=0.1,
        edgecolor='gray',
        ax=ax,
        missing_kwds={'color': 'lightgray'},
        legend=True,
        legend_kwds={'label': 'Temperature (°F)', 'orientation': 'horizontal'}
    )
    
    # Set the boundaries to focus only on the continental US
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    
    ax.set_title('Continental US January 1st Maximum Temperatures (°F)', fontsize=15)
    ax.set_axis_off()
    
    # Save the map
    output_file = 'continental_us_jan1_temperatures.png'
    print(f"Saving temperature map to {output_file}...")
    plt.savefig(output_file, dpi=600, bbox_inches='tight')
    
    # Create a simplified version for SVG
    print("Creating simplified SVG temperature map...")
    simplified_gdf = merged_gdf.copy()
    simplified_gdf['geometry'] = simplified_gdf['geometry'].simplify(tolerance=0.01)
    
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    simplified_gdf.plot(
        column='temperature',
        cmap=cmap,
        linewidth=0.1,
        edgecolor='gray',
        ax=ax,
        missing_kwds={'color': 'lightgray'},
        legend=True,
        legend_kwds={'label': 'Temperature (°F)', 'orientation': 'horizontal'}
    )
    
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    
    ax.set_title('Continental US January 1st Maximum Temperatures (°F)', fontsize=15)
    ax.set_axis_off()
    
    svg_output = 'continental_us_jan1_temperatures_simplified.svg'
    print(f"Saving simplified temperature map to {svg_output}...")
    plt.savefig(svg_output, format='svg', bbox_inches='tight')
    
    print("Temperature maps created successfully!")

if __name__ == "__main__":
    create_temperature_map()
