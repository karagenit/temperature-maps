import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import cKDTree
import time

def create_temperature_map():
    start_time = time.time()
    
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
    
    # Step 6: Fill in missing temperature data
    print("Filling in missing temperature data...")
    
    # Project the data to a coordinate system that preserves distances
    # EPSG:3857 is Web Mercator, commonly used for web maps
    projected_gdf = merged_gdf.copy()
    projected_gdf = projected_gdf.to_crs(epsg=3857)
    
    # Make a copy with only zip codes that have temperature data
    has_temp = projected_gdf[projected_gdf['temperature'].notna()].copy()
    
    # Get zip codes missing temperature data
    missing_temp = projected_gdf[projected_gdf['temperature'].isna()].copy()
    print(f"Found {len(missing_temp)} zip codes with missing temperature data")
    
    # First pass: Fill in using adjacent zip codes
    fill_start = time.time()
    filled_count = 0
    
    # Create a spatial index for faster adjacency checks
    has_temp_sindex = has_temp.sindex
    
    for idx, missing_zip in missing_temp.iterrows():
        # Use spatial index to find potential adjacent zip codes
        possible_matches_idx = list(has_temp_sindex.query(missing_zip.geometry, predicate='touches'))
        if possible_matches_idx:
            adjacent_zips = has_temp.iloc[possible_matches_idx]
            if not adjacent_zips.empty:
                projected_gdf.loc[idx, 'temperature'] = adjacent_zips['temperature'].mean()
                filled_count += 1
    
    print(f"Filled {filled_count} zip codes using adjacent zip codes in {time.time() - fill_start:.2f} seconds")
    
    # Update has_temp to include newly filled values
    has_temp = projected_gdf[projected_gdf['temperature'].notna()].copy()
    
    # Second pass: For any still missing, use nearest zip code with KDTree (much faster)
    still_missing = projected_gdf[projected_gdf['temperature'].isna()]
    if len(still_missing) > 0:
        print(f"Finding nearest neighbors for {len(still_missing)} remaining zip codes...")
        nn_start = time.time()
        
        # Extract centroids for all zip codes with temperature data
        has_temp_centroids = np.array([(p.x, p.y) for p in has_temp.geometry.centroid])
        
        # Build KDTree for fast nearest neighbor lookup
        tree = cKDTree(has_temp_centroids)
        
        # Extract centroids for all missing zip codes
        missing_centroids = np.array([(p.x, p.y) for p in still_missing.geometry.centroid])
        
        # Find nearest neighbors for all missing zip codes at once
        distances, indices = tree.query(missing_centroids, k=1)
        
        # Apply the temperatures from nearest neighbors
        for i, idx in enumerate(still_missing.index):
            nearest_idx = has_temp.index[indices[i]]
            projected_gdf.loc[idx, 'temperature'] = has_temp.loc[nearest_idx, 'temperature']
        
        print(f"Filled all remaining zip codes using nearest neighbor approach in {time.time() - nn_start:.2f} seconds")
    
    # Transfer the filled temperature values back to the original GeoDataFrame
    merged_gdf['temperature'] = projected_gdf['temperature']
    
    # Step 7: Create a custom colormap (blue to white to red)
    cmap = LinearSegmentedColormap.from_list('temp_cmap', ['blue', 'white', 'red'])
    
    # Step 8: Create the map
    print("Creating temperature map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot zipcodes with temperature data
    merged_gdf.plot(
        column='temperature',
        cmap=cmap,
        linewidth=0.1,
        edgecolor='gray',
        ax=ax,
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
    
    print(f"Temperature maps created successfully in {time.time() - start_time:.2f} seconds!")

if __name__ == "__main__":
    create_temperature_map()
