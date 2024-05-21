# Import necessary libraries
import os
import earthaccess  # For accessing and downloading earth access data
import shapely  # For handling geometric objects
import rasterio  # For reading and writing raster data
import geopandas as gpd  # For handling geospatial data
import numpy as np
import matplotlib.pyplot as plt  # For plotting data
from pyproj import Proj, transform  # For transforming coordinate systems
from osgeo import gdal  # For handling and converting geospatial data formats

# Load ward boundaries shapefile and convert to WGS84 coordinate reference system (CRS)
wards = gpd.read_file('C:/EGM722/egm722/green_space_project/data_files/wardsPolygon.shp').to_crs(epsg=4326)

# Create a single polygon from the ward boundaries to define the search area
outline = wards['geometry'].unary_union
search_area = outline.minimum_rotated_rectangle  # Get the minimum bounding rectangle
search_area = shapely.geometry.polygon.orient(search_area, sign=1)  # Ensure the polygon vertices are in a counter-clockwise order

# Log-in and search for datasets using earthaccess
earthaccess.login(strategy='interactive', persist=True)
datasets = earthaccess.search_datasets(
    keyword='vegetation indices',  # Search for vegetation indices datasets
    polygon=search_area.exterior.coords  # Use the search area defined above
)

# Select the first dataset from the search results
dataset = datasets[0]
ds_name = dataset.get_umm('ShortName')  # Get the short name of the dataset

# Search for data granules within the dataset and the search area
results = earthaccess.search_data(
    short_name=ds_name,
    polygon=search_area.exterior.coords,
    count=10  # Limit the search to the first 10 results
)

# Create a directory for the dataset if it doesn't exist
os.makedirs(ds_name, exist_ok=True)