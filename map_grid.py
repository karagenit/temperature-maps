import geopandas as gpd
import matplotlib.pyplot as plt
import os

def create_state_boundary_map():
    """
    Create a map showing the boundaries of the continental US states.
    """
    print("Loading state shapefile...")
    
    # Load the state shapefile
    states_gdf = gpd.read_file('census/cb_2024_us_state_500k/cb_2024_us_state_500k.shp')
    
    # Filter to include only the continental US (lower 48 states)
    # Exclude Alaska (02), Hawaii (15), Puerto Rico (72), and other territories
    continental_states = states_gdf[~states_gdf['STATEFP'].isin(['02', '15', '72', '60', '66', '69', '78'])]
    
    print(f"Loaded {len(continental_states)} continental US states")
    
    # Create the map
    print("Creating state boundary map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot state boundaries
    continental_states.plot(
        linewidth=0.8,
        edgecolor='black',
        facecolor='white',
        ax=ax
    )
    
    # Set the boundaries to focus only on the continental US
    ax.set_xlim(-125, -66)
    ax.set_ylim(24, 50)
    
    ax.set_title('Continental US State Boundaries', fontsize=15)
    ax.set_axis_off()
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save the map
    output_file = 'output/map_states.png'
    print(f"Saving state boundary map to {output_file}...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    print("State boundary map created successfully!")

if __name__ == "__main__":
    create_state_boundary_map()
