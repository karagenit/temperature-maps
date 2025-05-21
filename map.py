import geopandas as gpd
import matplotlib.pyplot as plt

def create_basic_zipcode_map():
    # Load the zipcode shapefile
    print("Loading zipcode shapefile...")
    zipcode_gdf = gpd.read_file('cb_2020_us_zcta520_500k/cb_2020_us_zcta520_500k.shp')
    
    # Print basic information about the data
    print(f"Loaded {len(zipcode_gdf)} zipcodes")
    print(f"Columns in the shapefile: {zipcode_gdf.columns.tolist()}")
    
    # Simplify the geometry to reduce file size
    # The tolerance parameter controls the level of simplification
    print("Simplifying geometry for SVG output...")
    simplified_gdf = zipcode_gdf.copy()
    simplified_gdf['geometry'] = simplified_gdf['geometry'].simplify(tolerance=0.01)
    
    # Create a simple plot with zipcode outlines for PNG (high detail)
    print("Creating high-resolution PNG map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    zipcode_gdf.plot(
        ax=ax,
        edgecolor='lightgray',
        facecolor='none',
        linewidth=0.1
    )
    
    # Set the boundaries to focus on the US (excluding most of the empty space)
    # These coordinates roughly cover the continental US plus Alaska and Hawaii
    ax.set_xlim(-180, -65)  # Longitude from Alaska to East Coast
    ax.set_ylim(15, 75)     # Latitude from below Hawaii to above Alaska
    
    ax.set_title('US ZIP Code Boundaries', fontsize=15)
    ax.set_axis_off()
    
    # Save the high-resolution PNG
    png_output = 'us_zipcodes_map.png'
    print(f"Saving high-resolution map to {png_output}...")
    plt.savefig(png_output, dpi=600, bbox_inches='tight')
    plt.close()
    
    # Create a simplified plot for SVG
    print("Creating simplified SVG map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    simplified_gdf.plot(
        ax=ax,
        edgecolor='lightgray',
        facecolor='none',
        linewidth=0.1
    )
    
    # Apply the same boundaries to the SVG map
    ax.set_xlim(-180, -65)
    ax.set_ylim(15, 75)
    
    ax.set_title('US ZIP Code Boundaries (Simplified)', fontsize=15)
    ax.set_axis_off()
    
    # Save the simplified SVG
    svg_output = 'us_zipcodes_map_simplified.svg'
    print(f"Saving simplified map to {svg_output}...")
    plt.savefig(svg_output, format='svg', bbox_inches='tight')
    
    print("Maps created successfully!")

if __name__ == "__main__":
    create_basic_zipcode_map()
