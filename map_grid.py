import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
from shapely.geometry import LineString, MultiLineString, box
from shapely.ops import unary_union

def create_state_boundary_map_with_grid():
    """
    Create a map showing the boundaries of the continental US states
    with a 40-mile grid overlay that only appears inside the US boundaries.
    Uses an equal-area projection to ensure grid cells are square.
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
    
    # Create a 20-mile grid overlay
    # Convert 20 miles to meters (1 mile = 1609.34 meters)
    grid_spacing_meters = 20 * 1609.34
    
    # Create grid lines
    x_grid = np.arange(minx, maxx + grid_spacing_meters, grid_spacing_meters)
    y_grid = np.arange(miny, maxy + grid_spacing_meters, grid_spacing_meters)
    
    print("Generating and clipping grid lines to US boundary...")
    
    # Create vertical grid lines and clip them to the US boundary
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
    
    # Create horizontal grid lines and clip them to the US boundary
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
    
    ax.set_title('Continental US State Boundaries with 40-Mile Grid', fontsize=15)
    ax.set_axis_off()
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save the map
    output_file = 'output/map_grid.png'
    print(f"Saving grid map to {output_file}...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    print("Grid map created successfully!")

if __name__ == "__main__":
    create_state_boundary_map_with_grid()