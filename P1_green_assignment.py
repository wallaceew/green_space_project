# Importing libraries
%matplotlib inline
import numpy as np
import rasterio as rio
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from rasterio.features import rasterize
import folium
import rasterstats
from mpl_toolkits.axes_grid1 import make_axes_locatable
from rasterio.features import rasterize



# Adding functions to begin work

# Function for loading raster data
def load_raster(file_path):
    """
    Load a raster file and return the data and affine transformation.
    
    Parameters:
    file_path (str): Path to the raster file.
    
    Returns:
    tuple: A tuple containing the raster data array and the affine transformation.
    """
    with rio.open(file_path) as src:
        return src.read(1), src.transform

# Function for rasterizing wards
def rasterize_wards(df, landcover_shape, landcover_transform):
     """
    Converts ward boundaries into a raster format.

    Parameters:
    df (GeoDataFrame): A GeoDataFrame containing the ward boundaries.
    landcover_shape (tuple): The dimensions of the output raster (height, width).
    landcover_transform (Affine): The affine transformation to align the raster with the landcover data.

    Returns:
    ndarray: A numpy array representing the rasterized ward boundaries.
    """
    wards_shapes = list(zip(df['geometry'], df['WARDNUMBER']))
    return rasterize(shapes=wards_shapes, fill=0, out_shape=landcover_shape,
                     transform=landcover_transform, dtype=np.uint8)

# Function for displaying rasterised wards - using cmap to allow user to select colour of their choice
def display_rasterized_wards(wards_mask, cmap='viridis'):
    """
    Display a visual representation of the rasterized wards.

    Parameters:
    wards_mask (ndarray): A numpy array where each pixel value represents a ward. 
                          The array is a rasterized version of the ward boundaries.
    cmap (str): The colour map to use for displaying the rasterized wards. Default is 'viridis'.
    """
    fig, ax = plt.subplots(1, 1)
    im = ax.imshow(wards_mask, cmap=cmap)
    fig.colorbar(im)
    plt.show()

# Get a list of all available colormaps
colormaps = plt.colormaps()

# Print the list of colourmaps
print("Available colourmaps:")
for cmap in colormaps:
    print(cmap)

# Load the landcover raster - opened using the 'load_raster' function to read raster data and its affine transformation 
landcover, affine_tfm = load_raster("C:/EGM722/egm722/green_space_project/raster/LCM2015_LP.tif")
# 'landcover' now holds the land cover data from the raster, while 'affine_tfm' holds the affine transformation info

# Opening the DEM GeoTIFF file using rasterio
# 'With' statement makes sure the file is closed properly after processing
with rio.open('C:/EGM722/egm722/green_space_project/ASTGTM/ASTGTMV003_N53W003_dem.tif') as dataset:
    # Reading the first band of the dataset into 'dem' - first band is the elevation data
    dem = dataset.read(1)
    # Extracting affine transformation matrix of dataset
    # Matrix can be used to convert between pixel and spatial coordinates (i.e. row/column to latitude/longitude)
    affine_dem = dataset.transform

# Loading the wards shapefile
df = gpd.read_file("C:/EGM722/egm722/green_space_project/data_files/Lwards.shp")

# Rasterizing the wards
# 'rasterize_wards' function converts vector data to raster format - 'df' is the geodataframe with the ward boundaries
# landcover.shape provides the dimensions of the output raster, affine_tfm ensures spatial alignment with the landcover raster
wards_mask = rasterize_wards(df, landcover.shape, affine_tfm)

# Visualising the rasterized output using 'display_rasterized_wards' function 
# 'wards_mask' contains the rasterized data and 'cmap' specifies colour for map visualisation - in this case, pink
display_rasterized_wards(wards_mask, cmap='pink')


# Further exploring the DEM
# Displaying a visualisation of two specific wards - City Centre North (ccnorth) and City Centre South (ccsouth)
# Creates a boolean mask (ccnorth_and_ccsouth) where condition 'True' is assigned to ward 12 and ward 13, while 'False' is assigned to other wards
# np.logical combines these two conditions - map can then be displayed as before with only the two wards showing
ccnorth_and_ccsouth = np.logical_or(wards_mask == 12, wards_mask == 13)


# Troubleshooting - error (IndexError: boolean index did not match indexed array along dimension 0; dimension is 3601 but corresponding boolean dimension is 660)
# Resizing the boolean mask to match the shape of the DEM array
ccnorth_and_ccsouth_resized = np.resize(ccnorth_and_ccsouth, dem.shape)

# Index the dem array using the resized boolean mask to select elevation values corresponding to 'True' values in the mask
NS_elevation = dem[ccnorth_and_ccsouth_resized]

# Plotting City Centre North and City Centre South
# Creates a new figure (fig) and axis (ax) for the new subplot
fig, ax = plt.subplots(1, 1)
# Displays boolean mask that represents city centre north and south (ax.imshow) while specifying pink colouring for map output
ax.imshow(ccnorth_and_ccsouth, cmap='pink')
# Show the plot
plt.show()

# Print the mean elevation - calculating mean and setting up an output statement to display the result ({:.2f} m) 
# Using NS_elevation - the values selected earlier from the mask that represent the specified wards of interest
print('Mean elevation: {:.2f} m'.format(NS_elevation.mean()))

# The above has allowed us to get to know the area and data better, setting us up for further exploration of the cities green spaces







# zonal statistics using rasterstats



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
liverpool_wards = gpd.read_file('C:/EGM722/egm722/green_space_project/data_files/wards.shp').to_crs(crs)

# inspect data 
print(liverpool_wards)

# Define a function to count unique elements of an array
def count_unique(array, names, nodata=0):
    """
    Count unique elements of an array.
    
    Parameters:
    array (ndarray): Input array.
    names (list): List of names corresponding to array values.
    nodata (int): Nodata value (default is 0).
    
    Returns:
    dict: Dictionary containing counts of unique elements.
    """
    count_dict = dict()
    for val in np.unique(array):
        if val == nodata:
            continue
        count_dict[names[val]] = np.count_nonzero(array == val)
    return count_dict

# Get counts of unique landcover classes in Liverpool
landcover_count = count_unique(landcover, landcover_names)

# Calculate percentage area covered by each landcover class in Liverpool
total_pixels = np.count_nonzero(landcover != 0)  # Total non-zero pixels (excluding nodata)
percentage_area = {key: (value / total_pixels) * 100 for key, value in landcover_count.items()}

print(percentage_area)  # Show the results


# Use rasterstats to get zonal statistics for Liverpool wards
liverpool_stats = rasterstats.zonal_stats(liverpool_wards,  # Liverpool wards shapefile
                                          landcover,  # Liverpool landcover raster
                                          affine=affine_tfm,  # Geotransform of the raster
                                          categorical=True,  # Categorical data
                                          category_map=landcover_names,  # Mapping of categories
                                          nodata=0)  # Nodata value of the raster

print(liverpool_stats[0])  # Show zonal statistics for the first Liverpool ward

# Plotting the processed data with an overlay of the ward boundaries to see where different land cover is most prominent 
# Plot the Liverpool wards with boundaries
fig, ax = plt.subplots(figsize=(10, 10))
liverpool_wards.plot(ax=ax, color='none', edgecolor='black')

# Overlay the land cover raster on top of the wards
im = ax.imshow(landcover, cmap='terrain', extent=(xmin, xmax, ymin, ymax), alpha=0.5)

# Add a colourbar for the land cover raster
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(im, cax=cax)
cbar.set_label('Land Cover Class')

# Add legend for land cover classes
classes = ['Broadleaf woodland', 'Coniferous woodland', 'Arable and Horticulture', 'Improved grassland', 
           'Semi-natural grassland', 'Mountain, heath, bog', 'Saltwater', 'Freshwater', 'Coastal', 
           'Built-up areas and gardens', 'Neutral Grassland', 'Calcareous Grassland', 'Acid Grassland', 
           'Heather', 'Heather grassland', 'Fen, Marsh and Swamp', 'Bog', 'Inland Rock', 'Urban', 
           'Suburban', 'Supra-littoral Rock', 'Supra-littoral Sediment', 'Littoral Rock']
cbar.set_ticks(range(len(classes)))
cbar.set_ticklabels(classes)

# Set title and axis labels
ax.set_title('Land Cover Map of Liverpool with Wards')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Show the plot
plt.show()




# Creating an interactive map centered on Liverpool using folium
m = folium.Map(location=map_center, zoom_start=12)

# Adding the bus stop choropleth layer
folium.Choropleth(
    geo_data=wards_gdf,
    name='Bus Stops per Ward',
    data=wards_gdf,
    columns=['wardname', 'bus_stop_count'],
    key_on='feature.properties.wardname',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Bus Stops per Ward',
    highlight=True,
    smooth_factor=0
).add_to(m)

# Add wards layer
folium.GeoJson(
    wards_gdf,
    name='Wards',
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.6
    },
    tooltip='wardname'
).add_to(m)

# Adding the parks layer
folium.GeoJson(
    parks_gdf,
    name='Parks',
    style_function=lambda x: {
        'fillColor': 'green',
        'color': 'green',
        'weight': 1,
        'fillOpacity': 0.6
    },
    tooltip='Name'
).add_to(m)

# Add landuse layer
folium.GeoJson(
    landuse_gdf,
    name='Land Use',
    style_function=lambda x: {
        'fillColor': 'gray' if x['properties']['landuse'] == 'urban areas' else
                     'khaki' if x['properties']['landuse'] == 'agricultural' else
                     'palegreen' if x['properties']['landuse'] == 'natural vegetation' else
                     'green' if x['properties']['landuse'] == 'parks' else
                     'darkgreen',  # for vegetated areas
        'color': 'gray' if x['properties']['landuse'] == 'urban areas' else
                 'khaki' if x['properties']['landuse'] == 'agricultural' else
                 'palegreen' if x['properties']['landuse'] == 'natural vegetation' else
                 'green' if x['properties']['landuse'] == 'parks' else
                 'darkgreen',
        'weight': 1,
        'fillOpacity': 0.6
    },
    tooltip=folium.features.GeoJsonTooltip(fields=['landuse'])
).add_to(m)

# Add water layer
folium.GeoJson(
    water_gdf,
    name='Water Bodies',
    style_function=lambda x: {
        'fillColor': 'blue',
        'color': 'blue',
        'weight': 1,
        'fillOpacity': 0.6
    }
).add_to(m)

# Add bus stops layer
for idx, row in bus_stops_gdf.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],  # Latitude and Longitude
        radius=2,  # Adjust the size of the circle marker as needed
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=1,
        tooltip='Bus Stop'
    ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Display the map
m