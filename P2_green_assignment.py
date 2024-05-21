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

# Download the data granules
downloaded_files = earthaccess.download(results, ds_name)

# Define a function to convert HDF files to GeoTIFF format
def hdf_to_geotiff(hdf_file, output_dir):
    """
    Convert an HDF file to GeoTIFF format.

    Parameters:
        hdf_file (str): Path to the input HDF file.
        output_dir (str): Directory where the output GeoTIFF file will be saved.

    Returns:
        str: Path to the output GeoTIFF file.
    """
    hdf_ds = gdal.Open(hdf_file)  # Open the HDF file
    subdataset = hdf_ds.GetSubDatasets()[0][0]  # Get the first subdataset
    output_file = os.path.join(output_dir, os.path.basename(hdf_file).replace('.hdf', '.tif'))  # Define the output file path
    gdal.Translate(output_file, subdataset, format='GTiff')  # Convert the subdataset to GeoTIFF format
    return output_file  # Return the path to the output GeoTIFF file

# Convert all downloaded HDF files to GeoTIFF format
hdf_files = [file for file in os.listdir(ds_name) if file.endswith('.hdf')]
output_dir = 'C:\\EGM722\\egm722\\green_space_project\\preprocessed_geotiffs'
os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

geotiff_files = []
for hdf_file in hdf_files:
    geotiff_file = hdf_to_geotiff(os.path.join(ds_name, hdf_file), output_dir)
    geotiff_files.append(geotiff_file)


# Merge the GeoTIFF files into a single dataset
merged_output_path = 'C:\\EGM722\\egm722\\green_space_project\\merged_dataset.tif'
src_files_to_merge = [rasterio.open(file) for file in geotiff_files]
merged_dataset, merged_transform = rasterio.merge.merge(src_files_to_merge)
merged_crs = src_files_to_merge[0].crs  # Get the CRS of the merged dataset

# Write the merged dataset to a new GeoTIFF file
with rasterio.open(merged_output_path, 'w', driver='GTiff',
                   height=merged_dataset.shape[1], width=merged_dataset.shape[2],
                   count=1, dtype=merged_dataset.dtype,
                   crs=merged_crs, transform=merged_transform) as dst:
    dst.write(merged_dataset[0], 1)

# Define Liverpool's bounding box in WGS84 (EPSG:4326) coordinates
liverpool_bbox_wgs84 = {'left': -3.1, 'right': -2.7, 'bottom': 53.30, 'top': 53.55}

# Open the merged dataset to read the data
with rasterio.open(merged_output_path) as src:
    data = src.read(1)  # Read the first band
    crs = src.crs  # Get the CRS of the dataset
    extent = src.bounds  # Get the extent of the dataset
