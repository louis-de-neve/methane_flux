import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from matplotlib.patheffects import withStroke
from matplotlib.patches import Polygon
from geopy.distance import geodesic
import math
import numpy as np

# test

# Refactored base map components
def base_map(landfill_coords, sewage_coords, sample_coords):
    fig, ax = setup_map(sample_coords)
    plot_sampling_point(ax, sample_coords)
    plot_highlighted_polygons(ax)
    plot_landfill_and_sewage_points(ax, landfill_coords, sewage_coords)
    draw_distance_and_bearing(ax, landfill_coords, sample_coords)
    draw_distance_and_bearing(ax, sewage_coords, sample_coords)
    add_gridlines_and_compass(ax)
    add_legend()
    
    return fig, ax

def setup_map(sample_coords, zoom_level=18):
    google_satellite = cimgt.GoogleTiles(style='satellite', cache=True)
    fig, ax = plt.subplots(figsize=(18, 18), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([sample_coords[0] - 0.005, sample_coords[0] + 0.015,
                   sample_coords[1] - 0.008, sample_coords[1] + 0.012], crs=ccrs.PlateCarree())
    ax.add_image(google_satellite, zoom_level)
    return fig, ax

def plot_sampling_point(ax, sample_coords):
    ax.plot(sample_coords[0], sample_coords[1], marker='*', color='yellow', markersize=50, markeredgewidth=2, 
            markeredgecolor='black', transform=ccrs.PlateCarree(), label='Sampling point')
    text = ax.text(sample_coords[0] + 0.001, sample_coords[1], "Sampling point", 
                   transform=ccrs.PlateCarree(), fontsize=24, color='white', fontweight='bold')
    text.set_path_effects([withStroke(linewidth=3, foreground='black')])

def plot_highlighted_polygons(ax):
    polygon_coords = [
        (0.1425, 52.2485), (0.1470, 52.2470), (0.1435, 52.2435),
        (0.1510, 52.2410), (0.1500, 52.2380), (0.1370, 52.2430)
    ]
    water_treatment_coords = [
        (0.1560, 52.2365), (0.1520, 52.2320), (0.1575, 52.2305), (0.1615, 52.2350)
    ]
    
    highlight_polygon = Polygon(polygon_coords, closed=True, edgecolor='red', facecolor='none', linewidth=4,
                                linestyle='--', label='Landfill Area')
    water_treatment_polygon = Polygon(water_treatment_coords, closed=True, edgecolor='blue', facecolor='none',
                                      linewidth=4, linestyle='--', label='Sewage plant')
    ax.add_patch(highlight_polygon)
    ax.add_patch(water_treatment_polygon)

def plot_landfill_and_sewage_points(ax, landfill_coords, sewage_coords):
    ax.plot(landfill_coords[0], landfill_coords[1], marker='*', color='red', markersize=40, markeredgewidth=2,
            markeredgecolor='black', transform=ccrs.PlateCarree(), label='Landfill source')
    ax.plot(sewage_coords[0], sewage_coords[1], marker='*', color='blue', markersize=40, markeredgewidth=2,
            markeredgecolor='black', transform=ccrs.PlateCarree(), label='Sewage source')

def calculate_initial_compass_bearing(pointA, pointB):
    lat1, lat2 = map(math.radians, [pointA[0], pointB[0]])
    diffLong = math.radians(pointB[1] - pointA[1])
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(diffLong)
    initial_bearing = math.degrees(math.atan2(x, y))
    return (initial_bearing + 360) % 360

def draw_distance_and_bearing(ax, point1_coords, point2_coords):
    distance = geodesic((point1_coords[1], point1_coords[0]), (point2_coords[1], point2_coords[0])).km
    bearing = calculate_initial_compass_bearing((point1_coords[1], point1_coords[0]),
                                                (point2_coords[1], point2_coords[0]))
    ax.plot([point1_coords[0], point2_coords[0]], [point1_coords[1], point2_coords[1]],
            color='white', linestyle=':', linewidth=3, transform=ccrs.PlateCarree())
    ax.text((point1_coords[0] + point2_coords[0]) / 2, (point1_coords[1] + point2_coords[1]) / 2,
            f"{distance:.3f} km, {bearing:.1f}°", transform=ccrs.PlateCarree(), fontsize=16,
            color='white', fontweight='bold').set_path_effects([withStroke(linewidth=3, foreground='black')])

def add_gridlines_and_compass(ax):
    gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree(), linewidth=2, color='black', alpha=0.7, linestyle='--')
    gl.xlabel_style = {'size': 15, 'color': 'black', 'weight': 'bold'}
    gl.ylabel_style = {'size': 15, 'color': 'black', 'weight': 'bold'}
    
    ax.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.85),
                arrowprops=dict(facecolor='white', edgecolor='black', linewidth=3, width=10, headwidth=30, headlength=30),
                ha='center', va='center', fontsize=30, color='white', xycoords='axes fraction',
                path_effects=[withStroke(linewidth=5, foreground='black')])

def add_legend():
    plt.legend(loc='upper right', fontsize=20)






# Function to add wind direction arrows
def add_wind_direction(ax, wind_angle):
    # Determine the wind vector components
    wind_angle_rad = np.deg2rad(wind_angle + 180)  # Adjust to reflect direction wind is coming from
    u = np.sin(wind_angle_rad)  # Eastward component
    v = np.cos(wind_angle_rad)  # Northward component

    # Get the current longitude and latitude range from the plot
    lon_min, lon_max = ax.get_xlim()
    lat_min, lat_max = ax.get_ylim()

    # Adjust the grid to ensure arrows do not plot near the edge
    buffer_lon = (lon_max - lon_min) * 0.1  # 10% buffer on longitude
    buffer_lat = (lat_max - lat_min) * 0.1  # 10% buffer on latitude
    lon_min += buffer_lon
    lon_max -= buffer_lon
    lat_min += buffer_lat
    lat_max -= buffer_lat

    # Generate a grid of points over the map for arrows
    x = np.linspace(lon_min, lon_max, 8)  # Longitude range divided into 8 points (slightly denser)
    y = np.linspace(lat_min, lat_max, 7)  # Latitude range divided into 7 points (increased density vertically)
    lons, lats = np.meshgrid(x, y)

    # Select every other arrow for plotting
    lons = lons[::2, ::2]
    lats = lats[::2, ::2]
    
    # Add arrows to the map with lighter teal color and thicker black outline
    ax.quiver(lons, lats, u, v, transform=ax.projection, color='#80cbc4', edgecolor='white', linewidth=2.0, scale=10, label='Wind direction')

    ax.legend(fontsize=20)
    
    return ax.figure, ax


# Function to add plume contours to an existing Cartopy figure
def add_plume_contours(fig, ax, lon, lat, concentration_data, x, y, z, z_height=10, levels=10, theta_deg=0):
    """
    Adds contours of concentration data to an existing figure.

    Parameters:
        fig: matplotlib Figure instance of the base map
        ax: cartopy GeoAxes instance to which the contours are added
        lon: float, Longitude of the Gaussian plume source
        lat: float, Latitude of the Gaussian plume source
        concentration_data: 3D numpy array, concentration data from the Gaussian plume model
        x, y, z: 1D numpy arrays, spatial coordinates corresponding to concentration_data
        z_height: float, height at which to extract concentration data for plotting (default 10 m)
        levels: List of contour levels to plot or integer for automatic levels (default 10)
        theta_deg: float, wind angle in degrees (default 0 degrees)
    """
    from matplotlib.colors import LogNorm
    from matplotlib.ticker import LogLocator

    # Extract the concentration data at the specified height
    z_index = (np.abs(z - z_height)).argmin()
    concentration_at_height = concentration_data[:, :, z_index]

    min_value = 1e-15
    max_value = concentration_at_height.max()
    # Create logarithmic levels using np.logspace
    num_levels = 10  # Adjust this for more or fewer levels
    levels = np.logspace(np.log10(min_value), np.log10(max_value), num_levels)
    #concentration_at_height[concentration_at_height < 1e-15] = np.nan

    # Convert lon and lat to the projection's coordinate system
    proj = ccrs.TransverseMercator(central_longitude=lon, central_latitude=lat)
    origin_xy = proj.transform_point(lon, lat, ccrs.PlateCarree())

    # Shift and rotate the grid
    x_shifted = x[:, :, 0] + origin_xy[0]
    y_shifted = y[:, :, 0] + origin_xy[1]
    theta_deg = (theta_deg + 90)
    theta_deg = 360 - theta_deg   # Reverse the angle to match the wind direction

    theta = np.radians(theta_deg)  # Rotation angle in radians

    x_rotated = np.cos(theta) * x_shifted - np.sin(theta) * y_shifted
    y_rotated = np.sin(theta) * x_shifted + np.cos(theta) * y_shifted

    # Add filled contour plot of the concentration with transparency
    contour = ax.contourf(
        x_rotated, y_rotated, concentration_at_height,
        levels=levels, transform=proj, cmap='viridis', alpha=0.6, norm=LogNorm(vmin=min_value, vmax=max_value))

    ## Define a custom position for the colorbar that is 0.8 times the height of the plot with extra padding
    bbox = ax.get_position()
    cbar_ax = fig.add_axes([bbox.x1 + 0.1, bbox.y0 + 0.1, 0.02, 0.8 * (bbox.y1 - bbox.y0)])  # [left, bottom, width, height]
    
    # Create the colorbar using the defined position
    cbar = fig.colorbar(contour, cax=cbar_ax)
    cbar.ax.tick_params(labelsize=18, width=2)  # Increase the font size and set bold tick labels
    cbar_ticks = [1e-15, 1e-13, 1e-11, 1e-9, 1e-7, 1e-5, 1e-3, max_value]  # Set ticks in range from 1e-15 to 1e-3
    cbar.set_ticks(cbar_ticks)
    cbar.set_ticklabels([f"{tick:.0e}" for tick in cbar_ticks])  # Use scientific notation labels

    cbar.ax.set_ylabel('Log Concentration (g/m^3)', fontsize=20, fontweight='bold')  # Increase the font size and make the label bold

    # Convert x_rotated and y_rotated back to lon/lat in PlateCarree projection using the ax projection
    lonlat_coords = ax.projection.transform_points(proj, x_rotated, y_rotated)

    # Extract longitude and latitude
    plume_lons = lonlat_coords[:, :, 0]
    plume_lats = lonlat_coords[:, :, 1]
    plume_data = (plume_lons, plume_lats, concentration_at_height)


    return fig, ax, plume_data
