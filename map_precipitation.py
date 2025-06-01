import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import Point, Polygon
from matplotlib.colors import LinearSegmentedColormap
from load_stations_monthly_precip import load_stations_monthly_precip
from map_grid import create_state_boundary_map_with_grid
from pyproj import Transformer
import subprocess

def create_precipitation_map(grid_spacing_miles=20):
    """
    Create a map showing precipitation data across the continental US using a grid.
    Each grid cell is colored based on the average precipitation score of stations within it.
    
    Args:
        grid_spacing_miles (int): Grid spacing in miles
        
    Returns:
        matplotlib.pyplot: The plot object with the precipitation map
    """
    print("Loading precipitation data from stations...")
    stations = load_stations_monthly_precip()
    print(f"Loaded precipitation data for {len(stations)} stations")
    
    # Get the map, grid cells, and other data from map_grid
    plt, grid_cells, us_boundary, projected_states = create_state_boundary_map_with_grid(
        grid_spacing_miles=grid_spacing_miles, 
        return_grid_cells=True
    )
    
    print(f"Generated {len(grid_cells)} grid cells that intersect with the US boundary")
    
    # Create a transformer to convert from lat/lon to the projected CRS
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)
    
    # Calculate precipitation scores for each grid cell
    print("Calculating precipitation scores for each grid cell...")
    grid_cell_scores = []
    
    # Pre-compute all station points in the projected coordinate system
    # Store as tuples of (station_id, station, point) sorted by X coordinate
    station_data = []
    for station_id, station in stations.items():
        if station.latitude is not None and station.longitude is not None:
            # Transform station coordinates to the projected CRS
            station_x, station_y = transformer.transform(station.longitude, station.latitude)
            point = Point(station_x, station_y)
            station_data.append((station_id, station, point, station_x))
    
    # Sort by X coordinate for faster spatial filtering
    station_data.sort(key=lambda x: x[3])
    
    print(f"\nPre-computed coordinates for {len(station_data)} stations")
    
    for i, cell in enumerate(grid_cells, 1):
        # Update progress
        print(f"\rCalculating precipitation scores: {i}/{len(grid_cells)} cells", end='')
        
        # Get cell bounds
        cell_minx, cell_miny, cell_maxx, cell_maxy = cell.bounds
        
        # Find stations within this grid cell's X range using binary search
        # Find the first station with x >= cell_minx
        left = 0
        right = len(station_data) - 1
        start_idx = len(station_data)
        
        while left <= right:
            mid = (left + right) // 2
            if station_data[mid][3] < cell_minx:
                left = mid + 1
            else:
                start_idx = mid
                right = mid - 1
        
        # Find stations within this grid cell
        stations_in_cell = []
        
        # Only check stations with x coordinates within the cell's x range
        idx = start_idx
        while idx < len(station_data) and station_data[idx][3] <= cell_maxx:
            _, station, point, _ = station_data[idx]
            
            # Check if the station is within the cell
            if cell.contains(point):
                stations_in_cell.append(station)
            
            idx += 1
        
        # Calculate average precipitation score if there are stations in the cell
        if stations_in_cell:
            avg_precip_score = sum(station.get_precipitation_score() for station in stations_in_cell) / len(stations_in_cell)
            grid_cell_scores.append((cell, avg_precip_score))
    
    # Print newline after completion
    print()    
    print(f"Found {len(grid_cell_scores)} grid cells with precipitation data")
    
    # Find the range of precipitation scores
    if grid_cell_scores:
        min_score = min(score for _, score in grid_cell_scores)
        max_score = max(score for _, score in grid_cell_scores)
        print(f"Precipitation score range: {min_score:.2f} to {max_score:.2f}")
        
        # Create a custom colormap: blue for high precipitation, yellow for low
        colors = [(1, 1, 0.7), (0.7, 0.9, 1), (0, 0.5, 1)]  # Yellow to light blue to dark blue
        cmap = LinearSegmentedColormap.from_list('precipitation_cmap', colors)
        
        # Get the current axes
        ax = plt.gca()
        
        # Plot grid cells with colors based on precipitation scores
        for cell, score in grid_cell_scores:
            # Normalize the score between 0 and 1
            normalized_score = (score - min_score) / (max_score - min_score) if max_score > min_score else 0.5
            color = cmap(normalized_score)
            
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
        
        # Create a colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(min_score, max_score))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
        cbar.set_label('Precipitation Score (higher = more rainy days)')
    
    ax.set_title(f'Continental US Precipitation Map ({grid_spacing_miles}-Mile Grid)', fontsize=15)
    
    return plt

if __name__ == "__main__":
    plt = create_precipitation_map()
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save the map
    output_file = 'output/map_grid_precip.png'
    print(f"Saving precipitation map to {output_file}...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    print("Precipitation map created successfully!")
    subprocess.run(["open", output_file])
