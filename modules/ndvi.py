import numpy as np
import utils

def compute_ndvi(red_band, nir_band):
    """
    Compute Normalized Difference Vegetation Index (NDVI) from red and near-infrared bands.
    
    Parameters:
    ----------
    red_band : ndarray
        Red band (typically band 3 in Landsat)
    nir_band : ndarray
        Near-infrared band (typically band 4 in Landsat)
    
    Returns:
    -------
    ndvi : ndarray
        NDVI values normalized to [0, 1] range
    """
    # Ensure inputs are in float format for division
    red = red_band.astype(np.float32)
    nir = nir_band.astype(np.float32)
    
    # Avoid division by zero by adding a small epsilon
    epsilon = 1e-10
    
    # NDVI formula: (NIR - Red) / (NIR + Red)
    ndvi = (nir - red) / (nir + red + epsilon)
    
    # NDVI values are typically in the range [-1, 1]
    # Convert to [0, 1] range for visualization
    ndvi_normalized = (ndvi + 1) / 2
    
    return ndvi_normalized

def colorize_ndvi(ndvi):
    """
    Apply a colormap to NDVI values for better visualization.
    
    Parameters:
    ----------
    ndvi : ndarray
        NDVI values in range [0, 1]
    
    Returns:
    -------
    colored_ndvi : ndarray
        RGB representation of NDVI values
    """
    # Create an empty RGB image
    h, w = ndvi.shape
    colored_ndvi = np.zeros((h, w, 3), dtype=np.float32)
    
    # Define color ranges for NDVI values:
    # 0.0-0.25 (low vegetation): brown to light brown
    # 0.25-0.5 (moderate vegetation): light green
    # 0.5-0.75 (high vegetation): medium green
    # 0.75-1.0 (very high vegetation): dark green
    
    # Low vegetation (browns)
    mask = (ndvi >= 0.0) & (ndvi < 0.25)
    factor = ndvi[mask] / 0.25  # Normalized factor from 0 to 1 within this range
    colored_ndvi[mask, 0] = 0.6 - 0.2 * factor  # R: decrease from 0.6 to 0.4
    colored_ndvi[mask, 1] = 0.4 - 0.1 * factor  # G: decrease from 0.4 to 0.3
    colored_ndvi[mask, 2] = 0.2 - 0.1 * factor  # B: decrease from 0.2 to 0.1
    
    # Moderate vegetation (light green)
    mask = (ndvi >= 0.25) & (ndvi < 0.5)
    factor = (ndvi[mask] - 0.25) / 0.25
    colored_ndvi[mask, 0] = 0.4 - 0.3 * factor  # R: decrease from 0.4 to 0.1
    colored_ndvi[mask, 1] = 0.6 + 0.1 * factor  # G: increase from 0.6 to 0.7
    colored_ndvi[mask, 2] = 0.1 + 0.1 * factor  # B: increase from 0.1 to 0.2
    
    # High vegetation (medium green)
    mask = (ndvi >= 0.5) & (ndvi < 0.75)
    factor = (ndvi[mask] - 0.5) / 0.25
    colored_ndvi[mask, 0] = 0.1 - 0.05 * factor  # R: decrease from 0.1 to 0.05
    colored_ndvi[mask, 1] = 0.7 + 0.1 * factor   # G: increase from 0.7 to 0.8
    colored_ndvi[mask, 2] = 0.2 - 0.1 * factor   # B: decrease from 0.2 to 0.1
    
    # Very high vegetation (dark green)
    mask = (ndvi >= 0.75)
    factor = (ndvi[mask] - 0.75) / 0.25
    colored_ndvi[mask, 0] = 0.05 - 0.05 * factor  # R: decrease from 0.05 to 0
    colored_ndvi[mask, 1] = 0.8 - 0.2 * factor    # G: decrease from 0.8 to 0.6
    colored_ndvi[mask, 2] = 0.1 - 0.05 * factor   # B: decrease from 0.1 to 0.05
    
    return colored_ndvi
