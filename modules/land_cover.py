"""
Land Cover Classification module for Remote Sensing Data Analyzer
Provides functions for classifying different land cover types in satellite imagery
"""

import numpy as np
from skimage import feature, segmentation, measure, color
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def classify_land_cover(image, num_classes=5):
    """
    Perform land cover classification using K-means clustering
    
    Parameters:
    ----------
    image : ndarray
        Input image as a 2D or 3D numpy array
    num_classes : int
        Number of land cover classes to identify
    
    Returns:
    -------
    classified_image : ndarray
        Classified image with each pixel assigned to a class
    class_colors : ndarray
        Color map for the classes
    """
    # Reshape the image for clustering
    if len(image.shape) == 2:
        # For grayscale images, add a channel dimension
        features = image.reshape(-1, 1)
    else:
        # For RGB or multispectral images, reshape to [pixels, bands]
        height, width, bands = image.shape
        features = image.reshape(-1, bands)
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=num_classes, random_state=42)
    labels = kmeans.fit_predict(features)
    
    # Reshape labels back to image dimensions
    if len(image.shape) == 2:
        height, width = image.shape
        classified = labels.reshape(height, width)
    else:
        height, width, _ = image.shape
        classified = labels.reshape(height, width)
    
    # Create a color map for visualization
    class_colors = plt.cm.viridis(np.linspace(0, 1, num_classes))
    
    return classified, class_colors

def detect_water_bodies(image, threshold=0.2):
    """
    Detect water bodies in satellite imagery using thresholding
    
    Parameters:
    ----------
    image : ndarray
        Input image as a 2D numpy array (grayscale)
    threshold : float
        Threshold value for water detection (0-1)
    
    Returns:
    -------
    water_mask : ndarray
        Binary mask where water bodies are marked as True
    """
    # Water typically appears dark in most satellite bands
    water_mask = image < threshold
    
    # Apply some morphological operations to clean up the mask
    from scipy import ndimage
    water_mask = ndimage.binary_opening(water_mask, structure=np.ones((3, 3)))
    water_mask = ndimage.binary_closing(water_mask, structure=np.ones((5, 5)))
    
    return water_mask

def detect_vegetation(red_band, nir_band, ndvi_threshold=0.3):
    """
    Detect vegetation using NDVI thresholding
    
    Parameters:
    ----------
    red_band : ndarray
        Red band of the satellite image
    nir_band : ndarray
        Near-infrared band of the satellite image
    ndvi_threshold : float
        NDVI threshold for vegetation detection
    
    Returns:
    -------
    vegetation_mask : ndarray
        Binary mask where vegetation is marked as True
    """
    # Compute NDVI
    ndvi = (nir_band - red_band) / (nir_band + red_band + 1e-8)  # Avoid division by zero
    
    # Create vegetation mask
    vegetation_mask = ndvi > ndvi_threshold
    
    return vegetation_mask

def detect_urban_areas(image, window_size=15, threshold=0.15):
    """
    Detect urban areas using texture analysis
    
    Parameters:
    ----------
    image : ndarray
        Input grayscale image
    window_size : int
        Size of the window for texture calculation
    threshold : float
        Threshold for urban area detection
    
    Returns:
    -------
    urban_mask : ndarray
        Binary mask where urban areas are marked as True
    """
    # Ensure input is grayscale
    if len(image.shape) > 2:
        gray_img = np.mean(image, axis=2)
    else:
        gray_img = image
    
    # Normalize to 0-1
    gray_img = (gray_img - np.min(gray_img)) / (np.max(gray_img) - np.min(gray_img) + 1e-8)
    
    # Alternative texture detection using gradient-based approach
    from skimage import filters
    
    # Use gradient magnitude as a texture measure
    texture_response = np.zeros_like(gray_img)
    
    # Calculate gradients using Sobel operator
    grad_x = filters.sobel_h(gray_img)
    grad_y = filters.sobel_v(gray_img)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    
    # Apply different scales of gradient-based texture detection
    for sigma in [0.5, 1.0, 2.0]:
        # Calculate gradients at different scales
        grad_x_scaled = filters.gaussian(grad_x, sigma=sigma)
        grad_y_scaled = filters.gaussian(grad_y, sigma=sigma)
        grad_mag_scaled = np.sqrt(grad_x_scaled**2 + grad_y_scaled**2)
        
        # Add to texture response
        texture_response += grad_mag_scaled
    
    # Normalize texture response
    texture_response = (texture_response - np.min(texture_response)) / (np.max(texture_response) - np.min(texture_response) + 1e-8)
    
    # Calculate local standard deviation (another texture measure)
    from scipy.ndimage import uniform_filter, generic_filter
    
    def local_std_dev(values):
        return np.std(values)
    
    texture = generic_filter(gray_img, local_std_dev, size=window_size)
    texture = (texture - np.min(texture)) / (np.max(texture) - np.min(texture) + 1e-8)
    
    # Combine texture measures (weighted average)
    urban_score = 0.6 * texture_response + 0.4 * texture
    
    # Apply threshold to get urban mask
    urban_mask = urban_score > threshold
    
    # Clean up the mask
    from scipy import ndimage
    urban_mask = ndimage.binary_opening(urban_mask, structure=np.ones((3, 3)))
    urban_mask = ndimage.binary_closing(urban_mask, structure=np.ones((5, 5)))
    
    return urban_mask

def analyze_frequency_patterns(fft_magnitude, threshold_percentile=90):
    """
    Analyze patterns in the frequency domain to identify repetitive structures
    
    Parameters:
    ----------
    fft_magnitude : ndarray
        Magnitude of the Fourier transform
    threshold_percentile : int
        Percentile threshold for peak detection
    
    Returns:
    -------
    pattern_info : dict
        Information about detected frequency patterns
    """
    # Find peaks in the frequency domain that may correspond to repetitive patterns
    threshold = np.percentile(fft_magnitude, threshold_percentile)
    peaks = fft_magnitude > threshold
    
    # Exclude the DC component (center of FFT)
    center_y, center_x = fft_magnitude.shape[0] // 2, fft_magnitude.shape[1] // 2
    window_size = 3
    peaks[center_y-window_size:center_y+window_size+1, center_x-window_size:center_x+window_size+1] = False
    
    # Label connected components
    labeled_peaks, num_peaks = measure.label(peaks, return_num=True)
    
    # Calculate properties of each peak
    peak_properties = []
    if num_peaks > 0:
        regions = measure.regionprops(labeled_peaks)
        for region in regions:
            cy, cx = region.centroid
            # Convert to coordinates relative to center
            rel_y, rel_x = cy - center_y, cx - center_x
            # Calculate distance from center and angle
            distance = np.sqrt(rel_y**2 + rel_x**2)
            angle = np.arctan2(rel_y, rel_x) * 180 / np.pi
            
            # Calculate wavelength (spatial period) based on distance from center
            # The relationship is: wavelength = image_size / distance
            avg_size = (fft_magnitude.shape[0] + fft_magnitude.shape[1]) / 2
            wavelength = avg_size / distance if distance > 0 else float('inf')
            
            peak_properties.append({
                'distance': distance,
                'angle': angle,
                'wavelength': wavelength,
                'area': region.area,
                'intensity': np.mean(fft_magnitude[region.coords[:, 0], region.coords[:, 1]])
            })
    
    pattern_info = {
        'num_patterns': num_peaks,
        'peak_properties': peak_properties
    }
    
    return pattern_info

def visualize_land_cover(classified_image, class_colors, title="Land Cover Classification"):
    """
    Create a colored visualization of the classified land cover
    
    Parameters:
    ----------
    classified_image : ndarray
        Classified image with class labels
    class_colors : ndarray
        Color map for the classes
    title : str
        Title for the visualization
    
    Returns:
    -------
    colored_image : ndarray
        RGB visualization of the classified image
    """
    # Create a colored image from the classification
    colored_image = np.zeros((*classified_image.shape, 4))
    for i in range(len(class_colors)):
        mask = classified_image == i
        for j in range(4):  # RGBA
            colored_image[..., j][mask] = class_colors[i][j]
    
    # Convert to RGB
    rgb_image = color.rgba2rgb(colored_image)
    
    return rgb_image

def compute_land_cover_statistics(classified_image, num_classes):
    """
    Compute statistics about land cover classification
    
    Parameters:
    ----------
    classified_image : ndarray
        Classified image with class labels
    num_classes : int
        Number of land cover classes
    
    Returns:
    -------
    stats : dict
        Dictionary with statistics about each class
    """
    total_pixels = classified_image.size
    stats = {}
    
    for i in range(num_classes):
        class_pixels = np.sum(classified_image == i)
        percentage = (class_pixels / total_pixels) * 100
        stats[f'Class {i+1}'] = {
            'pixel_count': int(class_pixels),
            'percentage': round(percentage, 2)
        }
    
    return stats