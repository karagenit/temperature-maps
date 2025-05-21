import geopandas as gpd
import matplotlib.pyplot as plt

def create_basic_zipcode_map():
    # Load the zipcode shapefile
    print("Loading zipcode shapefile...")
    zipcode_gdf = gpd.read_file('cb_2020_us_zcta520_500k/cb_2020_us_zcta520_500k.shp')
    
    # Print basic information about the data
    print(f"Loaded {len(zipcode_gdf)} zipcodes")
    print(f"Columns in the shapefile: {zipcode_gdf.columns.tolist()}")
    
    # Create a simple plot with zipcode outlines
    print("Creating map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot with very light gray outlines and no fill
    zipcode_gdf.plot(
        ax=ax,
        edgecolor='lightgray',
        facecolor='none',
        linewidth=0.1
    )
    
    # Set title and remove axes
    ax.set_title('US ZIP Code Boundaries', fontsize=15)
    ax.set_axis_off()
    
    # Save the map as SVG
    output_file = 'us_zipcodes_map.svg'
    print(f"Saving map to {output_file}...")
    plt.savefig(output_file, format='svg', bbox_inches='tight')
    
    print("Map created successfully!")

if __name__ == "__main__":
    create_basic_zipcode_map()
