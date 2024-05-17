

# zonal statistics using rasterstats

# importing libraries
%matplotlib inline

import numpy as np
import rasterio as rio
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterstats
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
# import rasterize from rasterio features 
from rasterio.features import rasterize
import pandas as pd
import geopandas as gpd
import folium


# DEM work - rasterising wards dataset to produce dem of Liverpool wards

# Load the landcover raster
with rio.open("C:/EGM722/egm722/green_space_project/raster/LCM2015_LP.tif") as src:
    landcover = src.read(1)
    affine_tfm = src.transform

#Open DEM GeoTIFF file using rasterio
# 'with' statement ensures that the file is closed after reading 
with rio.open('C:/EGM722/egm722/green_space_project/ASTGTM/ASTGTMV003_N53W003_dem.tif') as dataset:
    # read first band of the DEM file (1) which contains the elevation data
    dem = dataset.read(1)
    # get the affine transformation matrix of the DEM raster - matrix defines the mapping from pixel to geographic coordinates
    affine_dem = src.transform

# Load the wards shapefile
df = gpd.read_file("C:/EGM722/egm722/green_space_project/data_files/Lwards.shp")








# obtained data LCM data for Liverpool to rasterise and create land cover map
# find all names of land cover using metadata of LCM.tif online 

# define the landcover class names in a list
names = ['Broadleaf woodland', 'Coniferous woodland', 'Arable and Horticulture', 'Improved grassland', 
         'Semi-natural grassland', 'Mountain, heath, bog', 'Saltwater', 'Freshwater', 'Coastal', 
         'Built-up areas and gardens', 'Neutral Grassland', 'Calcareous Grassland', 'Acid Grassland', 
         'Heather', 'Heather grassland', 'Fen, Marsh and Swamp', 'Bog', 'Inland Rock', 'Urban', 
         'Suburban', 'Supra-littoral Rock', 'Supra-littoral Sediment', 'Littoral Rock']

values = range(1, 24)  # Get numbers from 1-23, corresponding to the landcover values

# Create a dictionary of landcover value/name pairs
landcover_names = dict(zip(values, names))

# Load the Liverpool landuse raster data
with rio.open('C:/EGM722/egm722/green_space_project/raster/LCM2015_Liverpool.tif') as dataset:
    xmin, ymin, xmax, ymax = dataset.bounds
    crs = dataset.crs
    landcover = dataset.read(1)
    affine_tfm = dataset.transform

# Load the Liverpool wards shapefile
wards = gpd.read_file('C:/EGM722/egm722/green_space_project/data_files/wards.shp').to_crs(crs)

# inspect data 
print(wards)

# getting rid of spaces in ward names 

data = {
    'wardname': ['Aigburth', 'Childwall', 'Church', 'City Centre North', 'City Centre South', 'Clubmoor East', 'Clubmoor West', 'County', 'Croxteth', 'Croxteth Country Park', 'Dingle', 'Allerton', 'Edge Hill', 'Everton East', 'Everton North', 'Everton West', 'Fazakerley East', 'Fazakerley North', 'Fazakerley West', 'Festival Gardens', 'Garston', 'Gateacre', 'Anfield', 'Grassendale & Cressington', 'Greenbank Park', 'Kensington & Fairfield', 'Kirkdale East', 'Kirkdale West', 'Knotty Ash & Dovecot Park', 'Mossley Hill', 'Much Woolton & Hunts Cross', 'Norris Green', 'Old Swan East', 'Arundel', 'Old Swan West', 'Orrell Park', 'Penny Lane', 'Princes Park', 'Sandfield Park', 'Sefton Park', 'Smithdown', 'Speke', 'Springwood', 'St Michaels', 'Belle Vale', 'Stoneycroft', 'Toxteth', 'Tuebrook Breckside Park', 'Tuebrook Larkhill', 'Vauxhall', 'Walton', 'Waterfront North', 'Waterfront South', 'Wavertree Garden Suburb', 'Wavertree Village', 'Broadgreen', 'West Derby Deysbrook', 'West Derby Leyfield', 'West Derby Muirhead', 'Woolton Village', 'Yew Tree', 'Brownlow Hill', 'Calderstones', 'Canning']
              }

# creating data frame from data to edit wardname column
df = pd.DataFrame(data)

# replace spaces in 'wardname' with underscore
df['wardname'] = df['wardname'].str.replace(" ", "_")

print(df)

# Define a function to count unique landcover classes
def count_unique(array, names, nodata=0):
    '''
    Count the unique elements of an array.

    :param array: Input array
    :param names: a dict of key/value pairs that map raster values to a name
    :param nodata: nodata value to ignore in the counting

    :returns count_dict: a dictionary of unique values and counts
    '''
    count_dict = dict()  # Create the output dict
    for val in np.unique(array):  # Iterate over the unique values for the raster
        if val == nodata:  # If the value is equal to our nodata value, move on to the next one
            continue
        count_dict[names[val]] = np.count_nonzero(array == val)
    return count_dict  # Return the now-populated output dict


# Check unique values in the Liverpool landuse raster
unique_values = np.unique(landcover)

# Compare unique values with keys in the landcover_names dictionary
missing_values = [val for val in unique_values if val not in landcover_names.keys()]

# Display missing values
if missing_values:
    print("The following values are missing from the landcover_names dictionary:", missing_values)
else:
    print("All unique values in the landcover raster are accounted for in the landcover_names dictionary.")

# Update the landcover_names dictionary to include missing values
for missing_val in missing_values:
    landcover_names[missing_val] = f"Unknown_{missing_val}"

# Count unique landcover classes in the Liverpool landuse raster
landcover_count = count_unique(landcover, landcover_names)
print(landcover_count)  # Show the results

# Getting a list of ward names using a list comprehension formatted with str.title() for lowercase
names = [n.title() for n in df['wardname']] 
#Printing a list of ward names to inspect the data
print(names) 

# Add landcover stats to the wards table
short_names = ['broadleaf', 'coniferous', 'arable', 'imp_grass', 'nat_grass',
               'mountain', 'saltwater', 'freshwater', 'coastal', 'built_up',
               'neutral_grass', 'calcareous_grass', 'acid_grass', 'heather',
               'heather_grass', 'fen_marsh_swamp', 'bog', 'inland_rock', 'urban',
               'suburban', 'supra_littoral_rock', 'supra_littoral_sediment', 'littoral_rock']
short_dict = dict(zip(names, short_names))
