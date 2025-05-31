import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import cKDTree
import time
import re
from matplotlib.colors import Normalize

def calculate_comfort_score(temp_f):
    """
    Calculate comfort score based on temperature:
    - 72°F = 40 points (optimal)
    - Points decrease with distance from 72°F
    - 32°F and 92°F = 0 points
    - Higher temperatures lose points faster
    - Temperatures below 32°F or above 92°F continue to lose points at 2 points per degree
    - Scores can go negative
    """
    # if temp_f <= 32:
        # Continue losing points at 2 points per degree below 32°F
        # return 0 - (32 - temp_f) * 2
    if temp_f <= 72:
        # Linear increase from 0 at 32°F to 40 at 72°F
        return (temp_f - 32) * 40 / 40
    # elif temp_f <= 92:
    else:
        # Linear decrease from 40 at 72°F to 0 at 92°F
        return 40 - (temp_f - 72) * 40 / 20
    # else:
        # Continue losing points at 2 points per degree above 92°F
        # return 0 - (temp_f - 92) * 2

def calculate_precipitation_score(station_id, base_dir="noaa/normals-monthly"):
    """
    Calculate precipitation score for a station based on number of rainy days.
    
    Args:
        station_id: The ID of the weather station
        base_dir: Directory containing the station CSV files
        
    Returns:
        The precipitation score (10 points per day with ≥0.5" rainfall)
    """
    try:
        # Construct the path to the station's CSV file
        csv_path = f"{base_dir}/{station_id}.csv"
        
        # Load the CSV file
        df = pd.read_csv(csv_path)
        
        # Check if the required column exists
        if "MLY-PRCP-AVGNDS-GE050HI" not in df.columns:
            # print(f"Warning: Precipitation data not found for station {station_id}")
            return 0
        
        # Sum the number of rainy days across all months
        rainy_days = df["MLY-PRCP-AVGNDS-GE050HI"].sum()
        
        # Calculate score (10 points per rainy day)
        precipitation_score = rainy_days * 10 / 30 # seems like it's total days over 30 years not pure averages (e.g. it'll be 120 for january, impossible)
        
        return precipitation_score
        
    except FileNotFoundError:
        # If the file doesn't exist, return 0 points
        print(f"Warning: CSV file not found for station {station_id}")
        return 0
    except Exception as e:
        # Handle other potential errors
        print(f"Error processing precipitation data for station {station_id}: {e}")
        return 0

def create_comfort_score_map():
    start_time = time.time()
    
    # Step 1: Load and process the temperature data
    print("Loading temperature data...")
    
    # Dictionary to store comfort scores by station ID
    station_scores = {}
    
    # Read the temperature data file from noaa directory
    with open('noaa/dly-tmax-normal.txt', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
                
            station_id = parts[0]
            month = parts[1]
            
            # Initialize station score if not already done
            if station_id not in station_scores:
                station_scores[station_id] = 0
            
            # Process each day's temperature in the month
            for day_idx, temp_str in enumerate(parts[2:33]):  # Skip station and month, process up to 31 days
                # Skip invalid dates (like Feb 30)
                if temp_str == '-8888':
                    continue
                
                # Extract the numeric part and convert to float
                match = re.match(r'(-?\d+)', temp_str)
                if match:
                    temp_value = float(match.group(1)) / 10.0  # Convert from tenths to actual degrees
                    # Calculate and add comfort score for this day
                    score = calculate_comfort_score(temp_value)
                    station_scores[station_id] += score

    # Implement precipitation score calculation here
    print("Loading precipitation data...")
    # for station_id in station_scores:
        # Add precipitation score to the existing temperature-based score
        # precipitation_score = calculate_precipitation_score(station_id)
        # station_scores[station_id] += precipitation_score

    
    print(f"Calculated comfort scores for {len(station_scores)} stations")
    
    # Step 2: Load the station to zipcode mapping from noaa directory
    print("Loading station to zipcode mapping...")
    station_to_zip = {}
    
    with open('noaa/zipcodes-normals-stations.txt', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                station_id = parts[0]
                zipcode = parts[1]
                station_to_zip[station_id] = zipcode
    
    print(f"Loaded zipcode mappings for {len(station_to_zip)} stations")
    
    # Step 3: Create a mapping from zipcode to comfort score
    zipcode_scores = {}
    
    for station_id, score in station_scores.items():
        if station_id in station_to_zip:
            zipcode = station_to_zip[station_id]
            # If multiple stations map to the same zipcode, take the average
            if zipcode in zipcode_scores:
                zipcode_scores[zipcode].append(score)
            else:
                zipcode_scores[zipcode] = [score]
    
    # Calculate average score for each zipcode
    zipcode_avg_scores = {zipcode: np.mean(scores) for zipcode, scores in zipcode_scores.items()}
    
    print(f"Calculated comfort scores for {len(zipcode_avg_scores)} zipcodes")
    
    # Step 4: Load the zipcode shapefile from census directory
    print("Loading zipcode shapefile...")
    zipcode_gdf = gpd.read_file('census/cb_2020_us_zcta520_500k/cb_2020_us_zcta520_500k.shp')
    
    # Step 5: Join score data with zipcode geometries
    # Convert the score dictionary to a DataFrame
    score_df = pd.DataFrame(list(zipcode_avg_scores.items()), columns=['ZCTA5CE20', 'comfort_score'])
    
    # Convert ZCTA5CE20 to string to match the shapefile
    score_df['ZCTA5CE20'] = score_df['ZCTA5CE20'].astype(str)
    
    # Merge with the GeoDataFrame
    merged_gdf = zipcode_gdf.merge(score_df, on='ZCTA5CE20', how='left')
    
    print(f"Merged comfort score data with {merged_gdf['comfort_score'].notna().sum()} zipcodes")
    
    # Step 6: Fill in missing score data
    print("Filling in missing comfort score data...")
    
    # Project the data to a coordinate system that preserves distances
    projected_gdf = merged_gdf.copy()
    projected_gdf = projected_gdf.to_crs(epsg=3857)
    
    # Make a copy with only zip codes that have score data
    has_score = projected_gdf[projected_gdf['comfort_score'].notna()].copy()
    
    # Get zip codes missing score data
    missing_score = projected_gdf[projected_gdf['comfort_score'].isna()].copy()
    print(f"Found {len(missing_score)} zip codes with missing comfort score data")
    
    # First pass: Fill in using adjacent zip codes
    fill_start = time.time()
    filled_count = 0
    
    # Create a spatial index for faster adjacency checks
    has_score_sindex = has_score.sindex
    
    for idx, missing_zip in missing_score.iterrows():
        # Use spatial index to find potential adjacent zip codes
        possible_matches_idx = list(has_score_sindex.query(missing_zip.geometry, predicate='touches'))
        if possible_matches_idx:
            adjacent_zips = has_score.iloc[possible_matches_idx]
            if not adjacent_zips.empty:
                projected_gdf.loc[idx, 'comfort_score'] = adjacent_zips['comfort_score'].mean()
                filled_count += 1
    
    print(f"Filled {filled_count} zip codes using adjacent zip codes in {time.time() - fill_start:.2f} seconds")
    
    # Update has_score to include newly filled values
    has_score = projected_gdf[projected_gdf['comfort_score'].notna()].copy()
    
    # Second pass: For any still missing, use nearest zip code with KDTree
    still_missing = projected_gdf[projected_gdf['comfort_score'].isna()]
    if len(still_missing) > 0:
        print(f"Finding nearest neighbors for {len(still_missing)} remaining zip codes...")
        nn_start = time.time()
        
        # Extract centroids for all zip codes with score data
        has_score_centroids = np.array([(p.x, p.y) for p in has_score.geometry.centroid])
        
        # Build KDTree for fast nearest neighbor lookup
        tree = cKDTree(has_score_centroids)
        
        # Extract centroids for all missing zip codes
        missing_centroids = np.array([(p.x, p.y) for p in still_missing.geometry.centroid])
        
        # Find nearest neighbors for all missing zip codes at once
        distances, indices = tree.query(missing_centroids, k=1)
        
        # Apply the scores from nearest neighbors
        for i, idx in enumerate(still_missing.index):
            nearest_idx = has_score.index[indices[i]]
            projected_gdf.loc[idx, 'comfort_score'] = has_score.loc[nearest_idx, 'comfort_score']
        
        print(f"Filled all remaining zip codes using nearest neighbor approach in {time.time() - nn_start:.2f} seconds")
    
    # Transfer the filled score values back to the original GeoDataFrame
    merged_gdf['comfort_score'] = projected_gdf['comfort_score']
    
    # Step 7: Create a custom colormap for comfort scores
    # Use a diverging colormap centered at 0 for positive and negative scores
    cmap = plt.cm.RdYlGn  # Red (negative) to Yellow (neutral) to Green (positive)
    
    # Step 8: Create the map
    print("Creating comfort score map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Get score range for better color mapping
    score_min = merged_gdf['comfort_score'].min()
    score_max = merged_gdf['comfort_score'].max()
    score_median = merged_gdf['comfort_score'].median()
    
    # Calculate percentiles to exclude extreme outliers
    score_5th = merged_gdf['comfort_score'].quantile(0.03)
    score_95th = merged_gdf['comfort_score'].quantile(0.98)
    
    print(f"Score range: {score_min:.2f} to {score_max:.2f}")
    print(f"Score median: {score_median:.2f}")
    print(f"5th to 95th percentile: {score_5th:.2f} to {score_95th:.2f}")
    
    # Create a custom normalization centered around the median
    # This will make half the data appear red and half appear green
    norm = Normalize(vmin=score_5th, vmax=score_95th)
    
    # Plot zipcodes with comfort score data using the median-centered normalization
    merged_gdf.plot(
        column='comfort_score',
        cmap=cmap,
        linewidth=0.1,
        edgecolor='gray',
        ax=ax,
        legend=True,
        norm=norm,
        legend_kwds={'label': 'Temperature Comfort Score', 'orientation': 'horizontal'}
    )
    
    # Set the boundaries to focus only on the continental US
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    
    ax.set_title('Continental US Temperature Comfort Score\n(Higher = More Days Near 72°F)', fontsize=15)
    ax.set_axis_off()
    
    # Save the map to output directory
    output_file = 'output/continental_us_comfort_score.png'
    print(f"Saving comfort score map to {output_file}...")
    plt.savefig(output_file, dpi=600, bbox_inches='tight')
    
    # Create a simplified version for SVG
    print("Creating simplified SVG comfort score map...")
    simplified_gdf = merged_gdf.copy()
    simplified_gdf['geometry'] = simplified_gdf['geometry'].simplify(tolerance=0.01, preserve_topology=True)
    
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Use the same normalization for the simplified map
    simplified_gdf.plot(
        column='comfort_score',
        cmap=cmap,
        linewidth=0.1,
        edgecolor='gray',
        ax=ax,
        legend=True,
        norm=norm,
        legend_kwds={'label': 'Temperature Comfort Score', 'orientation': 'horizontal'}
    )
    
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    
    ax.set_title('Continental US Temperature Comfort Score\n(Higher = More Days Near 72°F)', fontsize=15)
    ax.set_axis_off()
    
    svg_output = 'output/continental_us_comfort_score_simplified.svg'
    print(f"Saving simplified comfort score map to {svg_output}...")
    plt.savefig(svg_output, format='svg', bbox_inches='tight')
    
    print(f"Comfort score maps created successfully in {time.time() - start_time:.2f} seconds!")

if __name__ == "__main__":
    create_comfort_score_map()
