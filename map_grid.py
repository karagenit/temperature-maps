import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import LineString, MultiLineString, box, Polygon
from shapely.ops import unary_union

def create_state_boundary_map_with_grid(grid_spacing_miles=20, return_grid_cells=False):
    """
    Create a map showing the boundaries of the continental US states
    with a grid overlay that only appears inside the US boundaries.
    Uses an equal-area projection to ensure grid cells are square.
    
    Args:
        grid_spacing_miles (int): Grid spacing in miles
        return_grid_cells (bool): If True, return grid cells that intersect with the US boundary
        
    Returns:
        tuple: (plt, grid_cells, us_boundary, projected_states) if return_grid_cells is True,
               otherwise just plt
    """
    print("Loading state shapefile...")
    
    # Load the state shapefile
    states_gdf = gpd.read_file('census/cb_2024_us_state_500k/cb_2024_us_state_500k.shp')
    
    # Filter to include only the continental US (lower 48 states)
    # Exclude Alaska (02), Hawaii (15), Puerto Rico (72), and other territories
    continental_states = states_gdf[~states_gdf['STATEFP'].isin(['02', '15', '72', '60', '66', '69', '78'])]
    
    print(f"Loaded {len(continental_states)} continental US states")
    
    # Project to an equal-area projection suitable for the US
    # Albers Equal Area projection is commonly used for US maps
    # EPSG:5070 is the Albers Equal Area projection for the contiguous United States
    projected_states = continental_states.to_crs(epsg=5070)
    
    # Create a single geometry representing the entire continental US
    us_boundary = unary_union(projected_states.geometry)
    
    # Get the bounds of the US in the projected coordinate system (in meters)
    minx, miny, maxx, maxy = us_boundary.bounds
    
    # Create the map
    print("Creating state boundary map with grid overlay...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot state boundaries
    projected_states.plot(
        linewidth=0.8,
        edgecolor='black',
        facecolor='white',
        ax=ax
    )
    
    # Convert miles to meters (1 mile = 1609.34 meters)
    grid_spacing_meters = grid_spacing_miles * 1609.34
    
    # Create grid coordinates
    x_grid = np.arange(minx, maxx + grid_spacing_meters, grid_spacing_meters)
    y_grid = np.arange(miny, maxy + grid_spacing_meters, grid_spacing_meters)
    
    print("Generating grid cells within US...")
    
    # If we need to return grid cells, store them here
    grid_cells = []
    
    # Create grid cells and lines - TODO takes a while, maybe can optimize or cache results?
    for i in range(len(x_grid) - 1):
        for j in range(len(y_grid) - 1):
            # Create a grid cell
            cell = box(x_grid[i], y_grid[j], x_grid[i+1], y_grid[j+1])
            
            # Check if the cell intersects with the US boundary
            if cell.intersects(us_boundary):
                # Get the intersection of the cell with the US boundary
                cell_in_us = cell.intersection(us_boundary)
                
                # Skip if the intersection is too small
                if cell_in_us.area < 0.1 * cell.area:
                    continue
                
                if return_grid_cells:
                    grid_cells.append(cell_in_us)

    print("Generating and clipping X-grid lines to US boundary...")
    
    # Draw grid lines
    for x in x_grid:
        line = LineString([(x, miny), (x, maxy)])
        # Clip the line to the US boundary
        if line.intersects(us_boundary):
            clipped_line = line.intersection(us_boundary)
            
            # The intersection could be a single LineString or a MultiLineString
            if isinstance(clipped_line, LineString):
                ax.plot(*clipped_line.xy, color='grey', linestyle='-', linewidth=0.5, alpha=0.7)
            elif isinstance(clipped_line, MultiLineString):
                for segment in clipped_line.geoms:
                    ax.plot(*segment.xy, color='grey', linestyle='-', linewidth=0.5, alpha=0.7)
    
    print("Generating and clipping Y-grid lines to US boundary...")
    
    for y in y_grid:
        line = LineString([(minx, y), (maxx, y)])
        # Clip the line to the US boundary
        if line.intersects(us_boundary):
            clipped_line = line.intersection(us_boundary)
            
            # The intersection could be a single LineString or a MultiLineString
            if isinstance(clipped_line, LineString):
                ax.plot(*clipped_line.xy, color='grey', linestyle='-', linewidth=0.5, alpha=0.7)
            elif isinstance(clipped_line, MultiLineString):
                for segment in clipped_line.geoms:
                    ax.plot(*segment.xy, color='grey', linestyle='-', linewidth=0.5, alpha=0.7)
    
    ax.set_title(f'Continental US State Boundaries with {grid_spacing_miles}-Mile Grid', fontsize=15)
    ax.set_axis_off()

    if return_grid_cells:
        return plt, grid_cells, us_boundary, projected_states
    else:
        return plt

if __name__ == "__main__":
    plt = create_state_boundary_map_with_grid()

    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save the map
    output_file = 'output/map_grid.png'
    print(f"Saving grid map to {output_file}...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print("Grid map created successfully!")