"""
Satellite Orbit Visualization module for Remote Sensing Data Analyzer
Provides functions for visualizing satellite orbits and data collection paths
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import streamlit as st
from datetime import datetime, timedelta
import io
import math

# Common satellite parameters (simplified orbital elements)
SATELLITE_CATALOG = {
    "Landsat-8": {
        "inclination": 98.2,  # degrees
        "altitude": 705,  # km
        "period": 99,  # minutes
        "launch_date": "2013-02-11",
        "sensor_resolution": 30,  # meters
        "swath_width": 185,  # km
        "color": "#1E88E5",  # blue
    },
    "Sentinel-2": {
        "inclination": 98.5,  # degrees
        "altitude": 786,  # km
        "period": 100.7,  # minutes
        "launch_date": "2015-06-23",
        "sensor_resolution": 10,  # meters
        "swath_width": 290,  # km
        "color": "#43A047",  # green
    },
    "MODIS (Terra)": {
        "inclination": 98.1,  # degrees
        "altitude": 705,  # km
        "period": 99,  # minutes
        "launch_date": "1999-12-18",
        "sensor_resolution": 250,  # meters
        "swath_width": 2330,  # km
        "color": "#FFA000",  # amber
    },
    "MODIS (Aqua)": {
        "inclination": 98.1,  # degrees
        "altitude": 705,  # km
        "period": 99,  # minutes
        "launch_date": "2002-05-04",
        "sensor_resolution": 250,  # meters
        "swath_width": 2330,  # km
        "color": "#26A69A",  # teal
    },
    "Sentinel-1": {
        "inclination": 98.2,  # degrees
        "altitude": 693,  # km
        "period": 98.6,  # minutes
        "launch_date": "2014-04-03",
        "sensor_resolution": 5,  # meters
        "swath_width": 250,  # km
        "color": "#7E57C2",  # deep purple
    },
    "Planet SkySat": {
        "inclination": 97.4,  # degrees
        "altitude": 500,  # km
        "period": 94.6,  # minutes
        "launch_date": "2016-09-16",
        "sensor_resolution": 0.5,  # meters
        "swath_width": 8,  # km
        "color": "#D81B60",  # pink
    }
}

def calculate_orbit_path(satellite_name, num_points=100, duration_hours=2):
    """
    Calculate orbit path points for a satellite
    
    Parameters:
    ----------
    satellite_name : str
        Name of the satellite from the catalog
    num_points : int
        Number of points to calculate for the path
    duration_hours : float
        Duration of the orbit simulation in hours
    
    Returns:
    -------
    latitude : ndarray
        Array of latitude points
    longitude : ndarray
        Array of longitude points
    altitude : ndarray
        Array of altitude points
    time_points : ndarray
        Array of time points (in minutes)
    """
    if satellite_name not in SATELLITE_CATALOG:
        raise ValueError(f"Satellite {satellite_name} not found in catalog")
    
    satellite = SATELLITE_CATALOG[satellite_name]
    
    # Orbital parameters
    inclination = satellite["inclination"] * np.pi / 180  # convert to radians
    altitude = satellite["altitude"]
    period = satellite["period"]
    
    # Earth parameters
    earth_radius = 6371  # km
    
    # Time points
    max_minutes = duration_hours * 60
    time_points = np.linspace(0, max_minutes, num_points)
    
    # Calculate orbit
    latitude = np.zeros(num_points)
    longitude = np.zeros(num_points)
    altitude_points = np.ones(num_points) * altitude
    
    for i, t in enumerate(time_points):
        # Calculate position in orbit
        orbit_angle = (t % period) / period * 2 * np.pi
        
        # Calculate latitude (varies with inclination)
        latitude[i] = np.sin(orbit_angle) * np.sin(inclination) * 90
        
        # Calculate longitude (complete Earth rotation in approximately 24 hours)
        # Plus position in orbit projected onto equator
        longitude[i] = ((t / (24 * 60)) * 360 + 
                        np.cos(orbit_angle) * np.cos(inclination) * 180) % 360
        
        # Convert longitude from 0-360 to -180 to 180
        if longitude[i] > 180:
            longitude[i] -= 360
    
    return latitude, longitude, altitude_points, time_points

def create_orbit_animation(satellite_name, ground_track=True, duration_hours=4, fps=10):
    """
    Create an animation of a satellite's orbit
    
    Parameters:
    ----------
    satellite_name : str
        Name of the satellite from the catalog
    ground_track : bool
        Whether to show the ground track
    duration_hours : float
        Duration of the orbit simulation in hours
    fps : int
        Frames per second for the animation
    
    Returns:
    -------
    animation_html : str
        HTML containing the animation, ready to be displayed in Streamlit
    satellite_info : dict
        Information about the satellite
    """
    if satellite_name not in SATELLITE_CATALOG:
        raise ValueError(f"Satellite {satellite_name} not found in catalog")
    
    satellite = SATELLITE_CATALOG[satellite_name]
    
    # Calculate number of points based on duration and desired smoothness
    num_points = duration_hours * 60 * fps  # 1 point per second
    
    # Calculate orbit
    lat, lon, alt, time_points = calculate_orbit_path(
        satellite_name, num_points, duration_hours
    )
    
    # Create figure with Earth
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create Earth sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    earth_radius = 6371  # km
    
    x = earth_radius * np.outer(np.cos(u), np.sin(v))
    y = earth_radius * np.outer(np.sin(u), np.sin(v))
    z = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Plot Earth with a lighter color and some transparency
    earth = ax.plot_surface(x, y, z, color='lightblue', alpha=0.3, 
                           edgecolor='none', zorder=1)
    
    # Convert lat/lon to 3D coordinates
    x_vals = np.zeros(num_points)
    y_vals = np.zeros(num_points)
    z_vals = np.zeros(num_points)
    
    for i in range(num_points):
        # Convert lat/lon/alt to 3D coordinates
        r = earth_radius + alt[i]
        lat_rad = lat[i] * np.pi / 180
        lon_rad = lon[i] * np.pi / 180
        
        x_vals[i] = r * np.cos(lat_rad) * np.cos(lon_rad)
        y_vals[i] = r * np.cos(lat_rad) * np.sin(lon_rad)
        z_vals[i] = r * np.sin(lat_rad)
    
    # Plot the entire orbit path as a reference
    ax.plot(x_vals, y_vals, z_vals, color=satellite['color'], alpha=0.3, 
           linewidth=1, linestyle='dashed', zorder=2)
    
    # Create satellite point object that will be updated in animation
    satellite_point, = ax.plot([x_vals[0]], [y_vals[0]], [z_vals[0]], 
                             'o', color=satellite['color'], markersize=7, zorder=3)
    
    # Create ground track point
    if ground_track:
        ground_x = earth_radius * np.cos(lat[0] * np.pi / 180) * np.cos(lon[0] * np.pi / 180)
        ground_y = earth_radius * np.cos(lat[0] * np.pi / 180) * np.sin(lon[0] * np.pi / 180)
        ground_z = earth_radius * np.sin(lat[0] * np.pi / 180)
        
        ground_point, = ax.plot([ground_x], [ground_y], [ground_z], 
                               'o', color='red', markersize=5, zorder=4)
        
        # Line connecting satellite to ground
        connection_line, = ax.plot([x_vals[0], ground_x], [y_vals[0], ground_y], 
                                  [z_vals[0], ground_z], color='red', 
                                  linestyle='dotted', linewidth=1, alpha=0.5, zorder=2)
    
    # Ground track path
    ground_track_line, = ax.plot([], [], [], color='red', linewidth=1, alpha=0.7, zorder=2)
    ground_track_points = np.zeros((0, 3))
    
    # Title with time display
    start_time = datetime.now()
    title = ax.set_title(f"Satellite: {satellite_name} - Time: {start_time.strftime('%H:%M:%S')}")
    
    # Set axis limits
    max_range = earth_radius + max(alt) + 500
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # Equal aspect ratio
    ax.set_box_aspect([1, 1, 1])
    
    # Remove axis labels for cleaner look
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    
    # Add information text
    text_info = (
        f"Satellite: {satellite_name}\n"
        f"Altitude: {satellite['altitude']} km\n"
        f"Inclination: {satellite['inclination']}°\n"
        f"Period: {satellite['period']} minutes\n"
        f"Resolution: {satellite['sensor_resolution']} m"
    )
    fig.text(0.02, 0.95, text_info, transform=fig.transFigure, fontsize=9, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    # Animation update function
    def update(frame):
        # Update satellite position
        satellite_point.set_data([x_vals[frame]], [y_vals[frame]])
        satellite_point.set_3d_properties([z_vals[frame]])
        
        # Update ground track if enabled
        if ground_track:
            # Calculate ground point position (nadir point)
            ground_x = earth_radius * np.cos(lat[frame] * np.pi / 180) * np.cos(lon[frame] * np.pi / 180)
            ground_y = earth_radius * np.cos(lat[frame] * np.pi / 180) * np.sin(lon[frame] * np.pi / 180)
            ground_z = earth_radius * np.sin(lat[frame] * np.pi / 180)
            
            # Initialize ground_point if not defined in first frame
            if 'ground_point' not in locals():
                ground_point.set_data([ground_x], [ground_y])
                ground_point.set_3d_properties([ground_z])
            else:
                ground_point.set_data([ground_x], [ground_y])
                ground_point.set_3d_properties([ground_z])
            
            # Initialize connection_line if not defined in first frame
            if 'connection_line' not in locals():
                connection_line.set_data([x_vals[frame], ground_x], [y_vals[frame], ground_y])
                connection_line.set_3d_properties([z_vals[frame], ground_z])
            else:
                connection_line.set_data([x_vals[frame], ground_x], [y_vals[frame], ground_y])
                connection_line.set_3d_properties([z_vals[frame], ground_z])
            
            # Update ground track path (last 50 points)
            nonlocal ground_track_points
            new_point = np.array([[ground_x, ground_y, ground_z]])
            ground_track_points = np.append(ground_track_points, new_point, axis=0)
            
            # Keep only the last 100 points for the track
            if len(ground_track_points) > 100:
                ground_track_points = ground_track_points[-100:]
                
            ground_track_line.set_data(ground_track_points[:, 0], ground_track_points[:, 1])
            ground_track_line.set_3d_properties(ground_track_points[:, 2])
        
        # Update time display
        time_elapsed = timedelta(minutes=time_points[frame])
        current_time = start_time + time_elapsed
        title.set_text(f"Satellite: {satellite_name} - Time: {current_time.strftime('%H:%M:%S')}")
        
        return satellite_point, title
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=range(0, num_points, int(num_points/(fps*duration_hours))), 
                          interval=1000/fps, blit=False)
    
    # Save animation to HTML
    animation_html = anim.to_jshtml()
    
    # Extract satellite info for display
    satellite_info = {
        "name": satellite_name,
        "inclination": satellite["inclination"],
        "altitude": satellite["altitude"],
        "period": satellite["period"],
        "launch_date": satellite["launch_date"],
        "sensor_resolution": satellite["sensor_resolution"],
        "swath_width": satellite["swath_width"],
        "color": satellite["color"]
    }
    
    return animation_html, satellite_info

def calculate_coverage_area(satellite_name, location=None):
    """
    Calculate the potential coverage area of a satellite when passing over a location
    
    Parameters:
    ----------
    satellite_name : str
        Name of the satellite from the catalog
    location : tuple, optional
        (latitude, longitude) of the point of interest
    
    Returns:
    -------
    coverage_info : dict
        Information about the coverage
    """
    if satellite_name not in SATELLITE_CATALOG:
        raise ValueError(f"Satellite {satellite_name} not found in catalog")
    
    satellite = SATELLITE_CATALOG[satellite_name]
    
    # Default to middle of the US if no location provided
    if location is None:
        location = (39.8283, -98.5795)  # Center of the US
    
    # Calculate coverage radius
    swath_width = satellite["swath_width"]  # km
    
    # Calculate how long the satellite will be in view (simplified calculation)
    altitude = satellite["altitude"]  # km
    earth_radius = 6371  # km
    
    # Calculate angular coverage (in radians)
    angular_coverage = math.atan(swath_width / (2 * altitude))
    
    # Calculate ground distance coverage (km)
    ground_coverage_radius = earth_radius * angular_coverage
    
    # Calculate time in view (assuming overhead pass)
    # This is a simplified calculation
    orbital_velocity = 2 * math.pi * (earth_radius + altitude) / (satellite["period"] * 60)  # km/s
    time_in_view = 2 * ground_coverage_radius / orbital_velocity  # seconds
    
    coverage_info = {
        "satellite": satellite_name,
        "location": location,
        "swath_width": swath_width,
        "ground_coverage_radius": ground_coverage_radius,
        "time_in_view": time_in_view,
        "orbital_velocity": orbital_velocity
    }
    
    return coverage_info

def create_coverage_map(satellite_name, location=None, map_width=800, map_height=500):
    """
    Create a map showing the coverage area of a satellite
    
    Parameters:
    ----------
    satellite_name : str
        Name of the satellite from the catalog
    location : tuple, optional
        (latitude, longitude) of the point of interest
    map_width : int
        Width of the map in pixels
    map_height : int
        Height of the map in pixels
    
    Returns:
    -------
    fig : matplotlib.figure.Figure
        The coverage map figure
    coverage_info : dict
        Information about the coverage
    """
    if satellite_name not in SATELLITE_CATALOG:
        raise ValueError(f"Satellite {satellite_name} not found in catalog")
    
    # Get coverage information
    coverage_info = calculate_coverage_area(satellite_name, location)
    
    location = coverage_info["location"]
    swath_width = coverage_info["swath_width"]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(map_width/100, map_height/100))
    
    # Create a simple world map background
    # This is a placeholder - a real implementation would use cartopy or other mapping library
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.grid(alpha=0.3)
    
    # Plot the location
    ax.plot(location[1], location[0], 'ro', markersize=8)
    
    # Plot the coverage area (simplified as a circle)
    # This is a simplified visualization and does not account for Earth's curvature
    coverage_circle = plt.Circle(
        (location[1], location[0]), 
        swath_width/111,  # Convert km to degrees (approx)
        color=SATELLITE_CATALOG[satellite_name]["color"],
        alpha=0.3
    )
    ax.add_patch(coverage_circle)
    
    # Plot the satellite ground track
    lat, lon, _, _ = calculate_orbit_path(satellite_name, 1000, 4)
    ax.plot(lon, lat, color=SATELLITE_CATALOG[satellite_name]["color"], 
           alpha=0.7, linewidth=1)
    
    # Add information text
    sat = SATELLITE_CATALOG[satellite_name]
    ax.set_title(f"Coverage Map for {satellite_name}")
    
    info_text = (
        f"Swath Width: {swath_width} km\n"
        f"Resolution: {sat['sensor_resolution']} m\n"
        f"Altitude: {sat['altitude']} km\n"
        f"Location: {location[0]:.2f}°, {location[1]:.2f}°"
    )
    ax.text(0.02, 0.02, info_text, transform=ax.transAxes, fontsize=9,
           verticalalignment='bottom', horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    # Set axis labels
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")
    
    return fig, coverage_info

def display_satellite_info_table(satellites=None):
    """
    Generate a table with satellite information
    
    Parameters:
    ----------
    satellites : list of str, optional
        List of satellite names to include, if None, include all
    
    Returns:
    -------
    table_html : str
        HTML formatted table with satellite information
    """
    if satellites is None:
        satellites = list(SATELLITE_CATALOG.keys())
    
    # Filter to include only satellites in the catalog
    satellites = [sat for sat in satellites if sat in SATELLITE_CATALOG]
    
    # Create table headers
    headers = ["Satellite", "Altitude (km)", "Inclination (°)", "Period (min)", 
              "Resolution (m)", "Swath Width (km)", "Launch Date"]
    
    # Create table rows
    rows = []
    for sat_name in satellites:
        sat = SATELLITE_CATALOG[sat_name]
        row = [
            sat_name,
            str(sat["altitude"]),
            str(sat["inclination"]),
            str(sat["period"]),
            str(sat["sensor_resolution"]),
            str(sat["swath_width"]),
            sat["launch_date"]
        ]
        rows.append(row)
    
    # Generate HTML table
    table_html = "<table style='width:100%; border-collapse: collapse;'>\n"
    
    # Add headers
    table_html += "<tr style='background-color: #f2f2f2;'>\n"
    for header in headers:
        table_html += f"<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>{header}</th>\n"
    table_html += "</tr>\n"
    
    # Add rows
    for i, row in enumerate(rows):
        style = "background-color: #f9f9f9;" if i % 2 == 0 else ""
        table_html += f"<tr style='{style}'>\n"
        for cell in row:
            table_html += f"<td style='padding: 8px; text-align: left; border: 1px solid #ddd;'>{cell}</td>\n"
        table_html += "</tr>\n"
    
    table_html += "</table>"
    
    return table_html

def get_satellite_list():
    """
    Get the list of available satellites
    
    Returns:
    -------
    satellites : list
        List of satellite names
    """
    return list(SATELLITE_CATALOG.keys())