import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import Point, Polygon
from matplotlib.colors import ListedColormap
from load_stations import load_stations
from map_grid import create_state_boundary_map_with_grid
from pyproj import Transformer
import subprocess
from scipy.spatial import KDTree

def create_comfort_map(grid_spacing_miles=20):
    """
    Create a map showing overall comfort scores across the continental US using a grid.
    Each grid cell is colored based on the average comfort score of stations within it,
    combining both temperature and precipitation data.
    
    Args:
        grid_spacing_miles (int): Grid spacing in miles
        
    Returns:
        matplotlib.pyplot: The plot object with the comfort map
    """
    print("Loading station data...")
    all_stations = load_stations()
    
    # Filter stations to only include those with temperature data, precipitation data, and coordinates
    stations = {
        station_id: station for station_id, station in all_stations.items()
        if station.latitude is not None and 
           station.longitude is not None and 
           station.avg_daily_max_temperature is not None and
           station.avg_rainy_days_per_month  # Make sure precipitation data exists
    }
    
    print(f"Loaded data for {len(stations)} stations with both temperature and precipitation data")
    
    # Get the map, grid cells, and other data from map_grid
    plt, grid_cells, us_boundary, projected_states = create_state_boundary_map_with_grid(
        grid_spacing_miles=grid_spacing_miles, 
        return_grid_cells=True
    )
    
    print(f"Generated {len(grid_cells)} grid cells that intersect with the US boundary")
    
    # Create a transformer to convert from lat/lon to the projected CRS
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)
    
    # Pre-compute all station points in the projected coordinate system
    station_data = []
    station_points = []
    
    for station_id, station in stations.items():
        if station.latitude is not None and station.longitude is not None:
            # Transform station coordinates to the projected CRS
            station_x, station_y = transformer.transform(station.longitude, station.latitude)
            point = Point(station_x, station_y)
            station_data.append((station_id, station, point))
            station_points.append((station_x, station_y))
    
    print(f"\nPre-computed coordinates for {len(station_data)} stations")
    
    # Create KDTree for efficient spatial queries
    if not station_points:
        print("No valid station points found!")
        return plt
        
    kdtree = KDTree(station_points)
    
    # Calculate comfort scores for each grid cell
    print("Calculating comfort scores for each grid cell...")
    grid_cell_scores = []
    cells_with_assigned_stations = 0
    cells_with_nearest_stations = 0
    
    # Convert grid spacing from miles to meters (for the projected CRS)
    # Assuming 1 mile = 1609.34 meters
    grid_spacing_meters = grid_spacing_miles * 1609.34
    
    for i, cell in enumerate(grid_cells, 1):
        # Update progress
        print(f"\rCalculating comfort scores: {i}/{len(grid_cells)} cells", end='')
        
        # Get cell center and bounds
        cell_center_x = (cell.bounds[0] + cell.bounds[2]) / 2
        cell_center_y = (cell.bounds[1] + cell.bounds[3]) / 2
        
        # Query KDTree for stations within the search radius
        # Using the diagonal of the grid cell as the search radius to ensure we capture all stations
        search_radius = np.sqrt(2) * (grid_spacing_meters / 2)
        
        # Find indices of stations within the search radius
        indices = kdtree.query_ball_point([cell_center_x, cell_center_y], search_radius)
        
        # Filter stations that are actually within the cell
        stations_in_cell = []
        for idx in indices:
            _, station, point = station_data[idx]
            if cell.contains(point):
                stations_in_cell.append(station)
        
        # Calculate average comfort score if there are stations in the cell
        if stations_in_cell:
            # Use get_total_score() instead of get_temperature_score()
            avg_comfort_score = sum(station.get_total_score() for station in stations_in_cell) / len(stations_in_cell)
            grid_cell_scores.append((cell, avg_comfort_score))
            cells_with_assigned_stations += 1
        else:
            # Find the closest station to this cell's center
            distance, idx = kdtree.query([cell_center_x, cell_center_y], k=1)
            closest_station = station_data[idx][1]  # Get the station object
            # Use get_total_score() instead of get_temperature_score()
            comfort_score = closest_station.get_total_score()
            grid_cell_scores.append((cell, comfort_score))
            cells_with_nearest_stations += 1
    
    # Print newline after completion
    print()    
    print(f"Found {cells_with_assigned_stations} grid cells with stations inside")
    print(f"Assigned {cells_with_nearest_stations} grid cells to their nearest station")
    print(f"All {len(grid_cells)} cells now have comfort data")
    
    # Find the range of comfort scores
    if grid_cell_scores:
        # Get all scores
        all_scores = [score for _, score in grid_cell_scores]
        
        # Calculate the actual min and max for reference
        actual_min = min(all_scores)
        actual_max = max(all_scores)
        
        # Calculate 2nd and 98th percentiles for better color distribution
        min_score = np.percentile(all_scores, 2)
        max_score = np.percentile(all_scores, 98)
        
        print(f"Actual comfort score range: {actual_min:.2f} to {actual_max:.2f}")
        print(f"Using color scale range (2nd-98th percentile): {min_score:.2f} to {max_score:.2f}")
        
        # Create a list of 7 distinct colors from red to yellow to green
        distinct_colors = [
            (0.8, 0, 0),      # Dark red
            (1.0, 0.2, 0.2),  # Red
            (1.0, 0.5, 0),    # Orange
            (1.0, 1.0, 0),    # Yellow
            (0.7, 1.0, 0),    # Yellow-green
            (0.4, 0.8, 0),    # Light green
            (0, 0.6, 0)       # Green
        ]
        
        # Create a discrete colormap with 7 colors
        cmap = ListedColormap(distinct_colors)
        
        # Get the current axes
        ax = plt.gca()
        
        # Calculate the bin edges for the 7 categories
        score_range = max_score - min_score
        bin_edges = [min_score + (i * score_range / 7) for i in range(8)]
        
        # Plot grid cells with colors based on comfort scores
        for cell, score in grid_cell_scores:
            # Clip the score to the percentile range
            clipped_score = max(min_score, min(score, max_score))
            
            # Determine which bin the score falls into
            bin_index = 0
            for i in range(7):
                if clipped_score >= bin_edges[i] and clipped_score <= bin_edges[i+1]:
                    bin_index = i
                    break
            
            color = distinct_colors[bin_index]
            
            if isinstance(cell, Polygon):
                x, y = cell.exterior.xy
                ax.fill(x, y, color=color, alpha=0.7, edgecolor='none')
            else:  # MultiPolygon
                for polygon in cell.geoms:
                    x, y = polygon.exterior.xy
                    ax.fill(x, y, color=color, alpha=0.7, edgecolor='none')
        
        # Plot state boundaries on top to ensure they're visible
        projected_states.boundary.plot(
            linewidth=0.8,
            edgecolor='black',
            ax=ax
        )
        
        # Create a colorbar for comfort data
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(min_score, max_score))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8, ticks=[(bin_edges[i] + bin_edges[i+1])/2 for i in range(7)])
        cbar.set_label('Overall Comfort Score (higher = more comfortable)')
    
    ax.set_title(f'Continental US Comfort Map (Temperature & Precipitation, {grid_spacing_miles}-Mile Grid)', fontsize=15)
    
    return plt

if __name__ == "__main__":
    plt = create_comfort_map(grid_spacing_miles=10)
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save the map
    output_file = 'output/map_grid_comfort.png'
    print(f"Saving comfort map to {output_file}...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    print("Comfort map created successfully!")
    subprocess.run(["open", output_file])
