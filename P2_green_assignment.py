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