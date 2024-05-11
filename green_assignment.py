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

# generate matplotlib handles to create a legend of each of the features we put in our map.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = [] # create an empty list
    for ii in range(len(labels)): # for each label and color pair that we're given, make an empty box to pass to our legend
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[ii % lc], edgecolor=edge, alpha=alpha))
    return handles

# create a scale bar of length 20 km in the upper right corner of the map
# adapted this question: https://stackoverflow.com/q/32333870
# answered by SO user Siyh: https://stackoverflow.com/a/35705477
def scale_bar(ax, location=(0.92, 0.95)):
    x0, x1, y0, y1 = ax.get_extent() # get the current extent of the axis
    sbx = x0 + (x1 - x0) * location[0] # get the lower left x coordinate of the scale bar
    sby = y0 + (y1 - y0) * location[1] # get the lower left y coordinate of the scale bar

    ax.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=ax.projection) # plot a thick black line, 20 km long
    ax.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=ax.projection) # plot a smaller black line from 0 to 10 km long
    ax.plot([sbx-10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=ax.projection) # plot a white line from 10 to 20 km

    ax.text(sbx, sby-5000, '20 km', transform=ax.projection, fontsize=8) # add a label at 20 km
    ax.text(sbx-12500, sby-5000, '10 km', transform=ax.projection, fontsize=8) # add a label at 10 km
    ax.text(sbx-24500, sby-5000, '0 km', transform=ax.projection, fontsize=8) # add a label at 0 km

    return ax

# Loading the Liverpool data
liverpool_wards = gpd.read_file('C:/EGM722/egm722/green_space_project/data_files/wards.shp')
liverpool_water = gpd.read_file('C:/EGM722/egm722/green_space_project/data_files/Water_liverpool.shp')
liverpool_landuse = gpd.read_file('C:/EGM722/egm722/green_space_project/data_files/Landuse_liverpool.shp')

# Inspect the data by showing the first ten rows 
liverpool_wards.head(10)

# check the CRS of the wards dataset
liverpool_wards.crs 

# create a Universal Transverse Mercator reference system to transform our data
li_utm = ccrs.UTM(30)  # 30 is the UTM zone that Liverpool falls in


# create a cartopy CRS representation of the CRS associated with the wards dataset
ccrs.CRS(liverpool_wards.crs) 

# create an 8x8 figure (page size in inches) and an axes object in the figure using Liverpool UTM projection where data can be plotted
myFig = plt.figure(figsize=(8, 8))  
ax = plt.axes(projection=li_utm)  

# adding the wards outline of Liverpool using cartopy's ShapelyFeature
wards_feature = ShapelyFeature(liverpool_wards['geometry'], ni_utm, edgecolor='k', facecolor='w')
ax.add_feature(wards_feature) # add the features we've created to the map.

# zooming to the area of interest using the boundary of the wards shapefile features and reordering coordinates for presentation
xmin, ymin, xmax, ymax = liverpool_wards.total_bounds 
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=ni_utm) 




# zonal statistics using rasterstats

# importing libraries
%matplotlib inline

import numpy as np
import rasterio as rio
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterstats

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

names = [n.title() for n in df['wardname']] # getting a list of ward names using a list comprehension formatted with str.title() for lowercase
