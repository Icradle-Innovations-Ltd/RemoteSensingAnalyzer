"""
Time Series Analysis module for Remote Sensing Data Analyzer
Provides functions for analyzing temporal changes in satellite imagery
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy import ndimage, stats
import itertools

def calculate_ndvi_change(ndvi_t1, ndvi_t2):
    """
    Calculate change in NDVI between two time points
    
    Parameters:
    ----------
    ndvi_t1 : ndarray
        NDVI image at time 1
    ndvi_t2 : ndarray
        NDVI image at time 2
    
    Returns:
    -------
    change_map : ndarray
        Map of NDVI changes
    """
    # Ensure images are same size
    if ndvi_t1.shape != ndvi_t2.shape:
        raise ValueError("Input images must have the same dimensions")
    
    # Calculate change (t2 - t1)
    change_map = ndvi_t2 - ndvi_t1
    
    return change_map

def create_change_visualization(change_map, threshold=0.1):
    """
    Create a visualization of changes with color coding
    
    Parameters:
    ----------
    change_map : ndarray
        Map of changes between two time points
    threshold : float
        Threshold for significant change
    
    Returns:
    -------
    change_rgb : ndarray
        RGB visualization of changes (green=increase, red=decrease, black=no change)
    """
    # Create RGB image
    h, w = change_map.shape
    change_rgb = np.zeros((h, w, 3), dtype=np.float32)
    
    # Green for increase
    increase_mask = change_map > threshold
    change_rgb[increase_mask, 1] = np.clip(np.abs(change_map[increase_mask]) * 5, 0, 1)
    
    # Red for decrease
    decrease_mask = change_map < -threshold
    change_rgb[decrease_mask, 0] = np.clip(np.abs(change_map[decrease_mask]) * 5, 0, 1)
    
    # Gray for no change
    no_change_mask = np.abs(change_map) <= threshold
    change_rgb[no_change_mask, :] = 0.5
    
    return change_rgb

def detect_sudden_changes(time_series, threshold=2.0):
    """
    Detect sudden changes in a time series of images
    
    Parameters:
    ----------
    time_series : list
        List of images representing the same area at different times
    threshold : float
        Threshold for determining significant change (in standard deviations)
    
    Returns:
    -------
    change_points : list
        Indices of time points where sudden changes occur
    change_magnitude : ndarray
        Magnitude of change at each point
    """
    # Convert to numpy array if not already
    time_series = np.array(time_series)
    
    # Calculate difference between consecutive frames
    diffs = np.diff(time_series, axis=0)
    
    # Calculate mean and std of differences
    mean_diff = np.mean(diffs, axis=0)
    std_diff = np.std(diffs, axis=0)
    
    # Identify points with changes greater than threshold standard deviations
    change_points = []
    change_magnitude = np.zeros_like(time_series[0])
    
    for i in range(len(diffs)):
        # Z-score of difference
        z_score = np.abs((diffs[i] - mean_diff) / (std_diff + 1e-10))
        
        # If any pixel exceeds threshold, mark as change point
        if np.any(z_score > threshold):
            change_points.append(i + 1)  # Index in original time series
            change_magnitude = np.maximum(change_magnitude, z_score)
    
    return change_points, change_magnitude

def analyze_trend(time_series, dates=None):
    """
    Analyze trend in a time series of images
    
    Parameters:
    ----------
    time_series : list
        List of images representing the same area at different times
    dates : list
        List of datetime objects corresponding to each image
    
    Returns:
    -------
    slope : ndarray
        Slope of linear trend for each pixel
    p_value : ndarray
        P-value for trend significance
    """
    # Convert to numpy array if not already
    time_series = np.array(time_series)
    
    # Create time axis
    if dates is None:
        time_axis = np.arange(len(time_series))
    else:
        # Convert dates to numerical values (days since first date)
        first_date = dates[0]
        time_axis = np.array([(date - first_date).days for date in dates])
    
    # Reshape time series for linear regression
    n_times, h, w = time_series.shape
    time_axis_2d = np.repeat(time_axis[:, np.newaxis], h * w, axis=1)
    y_values = time_series.reshape(n_times, -1)
    
    # Calculate slope and p-value for each pixel
    slope = np.zeros((h, w))
    p_value = np.zeros((h, w))
    
    for i in range(h * w):
        if np.all(np.isfinite(y_values[:, i])):
            result = stats.linregress(time_axis, y_values[:, i])
            slope.flat[i] = result.slope
            p_value.flat[i] = result.pvalue
    
    return slope, p_value

def create_trend_visualization(slope, p_value, significance=0.05):
    """
    Create visualization of trend analysis
    
    Parameters:
    ----------
    slope : ndarray
        Slope of linear trend
    p_value : ndarray
        P-value for trend significance
    significance : float
        Significance threshold for p-value
    
    Returns:
    -------
    trend_rgb : ndarray
        RGB visualization of trends (red=negative trend, green=positive trend,
        intensity based on slope magnitude, transparency based on significance)
    """
    # Create RGBA image
    h, w = slope.shape
    trend_rgb = np.zeros((h, w, 4), dtype=np.float32)
    
    # Scale slope to 0-1 range for color intensity
    abs_slope = np.abs(slope)
    max_slope = np.percentile(abs_slope[np.isfinite(abs_slope)], 95)
    norm_slope = np.clip(abs_slope / max_slope, 0, 1)
    
    # Green for positive trend
    pos_mask = (slope > 0)
    trend_rgb[pos_mask, 1] = norm_slope[pos_mask]
    
    # Red for negative trend
    neg_mask = (slope < 0)
    trend_rgb[neg_mask, 0] = norm_slope[neg_mask]
    
    # Alpha based on significance (more transparent when less significant)
    significant = (p_value < significance)
    trend_rgb[:, :, 3] = 0.3  # Base transparency
    trend_rgb[significant, 3] = 1.0  # Fully opaque for significant trends
    
    return trend_rgb

def calculate_seasonal_metrics(time_series, dates):
    """
    Calculate seasonal metrics for time series data
    
    Parameters:
    ----------
    time_series : list
        List of images representing the same area at different times
    dates : list
        List of datetime objects corresponding to each image
    
    Returns:
    -------
    metrics : dict
        Dictionary containing seasonal metrics (amplitude, phase, etc.)
    """
    # Convert to numpy array if not already
    time_series = np.array(time_series)
    
    # Extract month information from dates
    months = np.array([date.month for date in dates])
    
    # Calculate metrics per month
    unique_months = range(1, 13)  # 1-12
    monthly_means = {}
    
    for month in unique_months:
        indices = np.where(months == month)[0]
        if len(indices) > 0:
            monthly_means[month] = np.mean(time_series[indices], axis=0)
    
    # Calculate amplitude (max - min over the year)
    if len(monthly_means) > 1:
        monthly_data = np.array([monthly_means[m] for m in monthly_means.keys()])
        amplitude = np.max(monthly_data, axis=0) - np.min(monthly_data, axis=0)
        
        # Calculate month of maximum
        month_indices = np.array(list(monthly_means.keys()))
        max_month_idx = np.argmax(monthly_data, axis=0)
        phase = np.zeros_like(max_month_idx, dtype=np.float32)
        
        # Convert to valid indices
        valid_indices = np.where(np.isfinite(amplitude))
        for i, j in zip(*valid_indices):
            phase[i, j] = month_indices[max_month_idx[i, j]]
    else:
        amplitude = np.zeros_like(time_series[0])
        phase = np.zeros_like(time_series[0])
    
    metrics = {
        'amplitude': amplitude,
        'phase': phase,
        'monthly_means': monthly_means
    }
    
    return metrics

def create_seasonal_visualization(metrics):
    """
    Create visualization of seasonal metrics
    
    Parameters:
    ----------
    metrics : dict
        Dictionary containing seasonal metrics from calculate_seasonal_metrics
    
    Returns:
    -------
    season_rgb : ndarray
        RGB visualization of seasonal patterns
    """
    amplitude = metrics['amplitude']
    phase = metrics['phase']
    
    # Create HSV image (hue = phase/month, saturation = 1, value = amplitude)
    h, w = amplitude.shape
    hsv = np.zeros((h, w, 3), dtype=np.float32)
    
    # Normalize amplitude for brightness
    max_amp = np.percentile(amplitude[np.isfinite(amplitude)], 95)
    norm_amplitude = np.clip(amplitude / max_amp, 0, 1)
    
    # Normalize phase to 0-1 range for hue (1-12 months to 0-1)
    norm_phase = (phase - 1) / 12.0
    
    # Set HSV values
    hsv[:, :, 0] = norm_phase  # Hue
    hsv[:, :, 1] = 1.0  # Saturation
    hsv[:, :, 2] = norm_amplitude  # Value
    
    # Convert HSV to RGB
    from matplotlib.colors import hsv_to_rgb
    rgb = hsv_to_rgb(hsv)
    
    return rgb


def generate_time_series_report(metrics, changes=None):
    """
    Generate a report based on time series analysis
    
    Parameters:
    ----------
    metrics : dict
        Dictionary containing seasonal metrics
    changes : dict, optional
        Dictionary containing change detection results
    
    Returns:
    -------
    report : str
        Markdown formatted report
    """
    report = """# Time Series Analysis Report

## Seasonal Patterns

"""
    
    # Add seasonal information
    if np.any(metrics['amplitude'] > 0):
        max_amp_loc = np.unravel_index(np.argmax(metrics['amplitude']), metrics['amplitude'].shape)
        max_amp = metrics['amplitude'][max_amp_loc]
        max_amp_month = int(metrics['phase'][max_amp_loc])
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        report += f"""The analysis reveals strong seasonal patterns in the data:

- Maximum amplitude: {max_amp:.3f}
- Peak month: {month_names[max_amp_month-1]} (month {max_amp_month})
- The intensity of seasonal variation is represented by brightness in the visualization

"""
    else:
        report += "No significant seasonal patterns detected in the time series.\n\n"
    
    # Add change information if available
    if changes and 'change_points' in changes and len(changes['change_points']) > 0:
        report += """## Detected Changes

Significant changes were detected at the following time points:

"""
        for i, point in enumerate(changes['change_points']):
            report += f"- Change point {i+1}: at time index {point}\n"
        
        report += """
These changes may indicate:
- Sudden land cover conversions
- Extreme weather events
- Agricultural harvesting or planting activities
- Urban development projects

"""
    
    # Add recommendations
    report += """## Recommendations

Based on the time series analysis:

1. For areas with strong seasonality, consider:
   - Planning observations around peak months
   - Adjusting baselines to account for seasonal variation

2. For areas with significant changes:
   - Collect ground truth data to verify the nature of changes
   - Consider monitoring these areas more frequently

3. For future analysis:
   - Increase the temporal resolution of observations
   - Combine with climate data to correlate changes with environmental factors
"""
    
    return report