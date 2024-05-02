# allows the figure to be interactive
%matplotlib inline

# Import necessary libraries
import geopandas as gpd
import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely.ops import unary_union
from shapely.geometry.polygon import Polygon
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# make plotting interactive 
plt.ion() 

