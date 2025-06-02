import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import Point, Polygon
from matplotlib.colors import LinearSegmentedColormap
from load_stations_monthly_precip import load_stations_monthly_precip
from map_grid import create_state_boundary_map_with_grid
from pyproj import Transformer
import subprocess
from scipy.spatial import KDTree

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
    
    # Calculate precipitation scores for each grid cell
    print("Calculating precipitation scores for each grid cell...")
    grid_cell_scores = []
    cells_without_stations = []
    
    # Convert grid spacing from miles to meters (for the projected CRS)
    # Assuming 1 mile = 1609.34 meters
    grid_spacing_meters = grid_spacing_miles * 1609.34
    
    for i, cell in enumerate(grid_cells, 1):
        # Update progress
        print(f"\rCalculating precipitation scores: {i}/{len(grid_cells)} cells", end='')
        
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
        
        # Calculate average precipitation score if there are stations in the cell
        if stations_in_cell:
            avg_precip_score = sum(station.get_precipitation_score() for station in stations_in_cell) / len(stations_in_cell)
            grid_cell_scores.append((cell, avg_precip_score))
        else:
            cells_without_stations.append(cell)
    
    # Print newline after completion
    print()    
    print(f"Found {len(grid_cell_scores)} grid cells with precipitation data")
    print(f"{len(cells_without_stations)}/{len(grid_cells)} cells are missing precipitation data")
    
    # Find the range of precipitation scores
    if grid_cell_scores:
        # Get all scores
        all_scores = [score for _, score in grid_cell_scores]
        
        # Calculate the actual min and max for reference
        actual_min = min(all_scores)
        actual_max = max(all_scores)
        
        # Calculate 5th and 95th percentiles for better color distribution
        min_score = np.percentile(all_scores, 5)
        max_score = np.percentile(all_scores, 95)
        
        print(f"Actual precipitation score range: {actual_min:.2f} to {actual_max:.2f}")
        print(f"Using color scale range (5th-95th percentile): {min_score:.2f} to {max_score:.2f}")
        
        # Create a custom colormap: white for no precipitation, dark blue for high
        colors = [(1, 1, 1), (0.7, 0.9, 1), (0, 0.3, 0.8)]  # White to light blue to dark blue
        cmap = LinearSegmentedColormap.from_list('precipitation_cmap', colors)
        
        # Get the current axes
        ax = plt.gca()
        
        # First, plot cells without stations in light red
        for cell in cells_without_stations:
            if isinstance(cell, Polygon):
                x, y = cell.exterior.xy
                ax.fill(x, y, color=(1, 0.8, 0.8), alpha=0.7, edgecolor='none')  # Light red
            else:  # MultiPolygon
                for polygon in cell.geoms:
                    x, y = polygon.exterior.xy
                    ax.fill(x, y, color=(1, 0.8, 0.8), alpha=0.7, edgecolor='none')  # Light red
        
        # Plot grid cells with colors based on precipitation scores
        for cell, score in grid_cell_scores:
            # Clip the score to the percentile range
            clipped_score = max(min_score, min(score, max_score))
            
            # Normalize the score between 0 and 1
            normalized_score = (clipped_score - min_score) / (max_score - min_score) if max_score > min_score else 0.5
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
        
        # Create a colorbar for precipitation data
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(min_score, max_score))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
        cbar.set_label('Precipitation Score (higher = more rainy days)')
        
        # Add a legend for cells without data
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=(1, 0.8, 0.8), alpha=0.7, label='No Station Data')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
    
    ax.set_title(f'Continental US Precipitation Map ({grid_spacing_miles}-Mile Grid)', fontsize=15)
    
    return plt

if __name__ == "__main__":
    plt = create_precipitation_map(grid_spacing_miles=20)
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save the map
    output_file = 'output/map_grid_precip.png'
    print(f"Saving precipitation map to {output_file}...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    print("Precipitation map created successfully!")
    subprocess.run(["open", output_file])
