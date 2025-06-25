# Weather Data Mapping

A Python-based project for visualizing weather data across the continental United States using NOAA weather station data. Creates comfort maps based on temperature and precipitation patterns, displayed on grid-based visualizations of the US.

## Overview

This project combines weather station data from NOAA with geographic data to create visual maps showing:
- Temperature comfort scores across the continental US
- Precipitation patterns and "rainy days" statistics  
- Combined comfort scores factoring in both temperature and rainfall preferences
- Grid-based visualizations for performance and clarity

The project emphasizes areas with mild temperatures (around 72°F optimal) and higher precipitation, as these are considered more comfortable climates.

## Setup

### Prerequisites
- Python 3.13
- Virtual environment support

### Installation

1. Set up Python virtual environment:
```bash
python3 -m venv ~/python/venv
source ~/python/venv/bin/activate
```

2. Install dependencies:
```bash
pip install geopandas matplotlib pandas numpy scipy shapely pyproj
```

3. Ensure you have the required data files:
   - NOAA weather data in `noaa/` directory
   - Census shapefiles in `census/` directory

## Usage

### Running Tests
```bash
pytest
```

### Creating Maps
Run the individual map generation scripts:
```bash
python map_grid_temperature.py
python map_grid_precipitation.py 
python map_grid_comfort.py
```

## Python Scripts

### Data Loading Scripts
- **`station.py`** - Core Station class for weather station data with properties for coordinates, temperature, and precipitation data
- **`load_stations_zipcodes.py`** - Loads weather station location data from NOAA zipcodes-normals-stations.txt file
- **`load_stations_daily_temp.py`** - Loads daily maximum temperature normals from NOAA dly-tmax-normal.txt file  
- **`load_stations_monthly_precip.py`** - Loads monthly precipitation data from individual CSV files in normals-monthly/ directory
- **`load_stations.py`** - Combines all data sources into unified station objects with temperature, precipitation, and location data

### Mapping and Visualization Scripts
- **`map_grid.py`** - Core grid generation and state boundary mapping functionality using equal-area projection for accurate grid cells
- **`map_grid_temperature.py`** - Creates temperature comfort maps on a grid, with 72°F as optimal temperature
- **`map_grid_precipitation.py`** - Creates precipitation maps showing average rainy days per month across grid cells
- **`map_grid_comfort.py`** - Combines temperature and precipitation data into overall comfort score maps
- **`map_zipcode_comfort.py`** - Legacy zipcode-based comfort mapping (replaced by more efficient grid approach)

### Data Structure

The project uses a grid-based approach rather than zipcode boundaries for better performance and visual clarity:
- Continental US divided into configurable grid cells (default 20 mile spacing)
- Each grid cell colored based on nearest weather station data
- Uses KD-tree spatial indexing for efficient nearest-neighbor searches
- Caches computed grids for faster subsequent runs

### Output

Generated maps are saved to the `output/` directory in PNG and SVG formats. The maps show:
- Blue areas: Higher comfort scores (cooler temperatures, more precipitation)
- Red/yellow areas: Lower comfort scores (hotter temperatures, less precipitation)

## Data Sources

- **NOAA Climate Normals**: Historical weather averages (1981-2010 period)
  - Daily temperature maxima from ~7,500 weather stations
  - Monthly precipitation data from ~9,800 weather stations
- **US Census Bureau**: State boundary shapefiles for mapping

## Development Notes

- Large data files in `noaa/` directory should be handled carefully to avoid excessive API token usage
- Grid-based approach chosen over county/zipcode mapping for better performance and visual consistency
- Uses equal-area projection to ensure grid cells maintain consistent size across the map
- KD-tree spatial indexing significantly improves performance for nearest-neighbor station lookups

## Testing

Test files are located in the `tests/` directory and use pytest:
- `test_station.py` - Tests for Station class functionality
- `test_load_stations_zipcodes.py` - Tests for zipcode data loading
