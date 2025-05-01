"""
Topography Analysis module for Remote Sensing Data Analyzer
Provides functions for detecting and analyzing hills, mountains, and terrain features
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import filters, morphology, feature, exposure

def detect_hills_mountains(image, min_height=0.2, slope_threshold=0.15, smoothing_sigma=1.0):
    """
    Detect hills and mountains in satellite imagery based on brightness gradients
    
    Parameters:
    ----------
    image : ndarray
        Input grayscale image (assumed to be elevation/brightness related)
    min_height : float
        Minimum relative height/brightness to consider as hills (0-1)
    slope_threshold : float
        Minimum slope threshold to identify hills and mountains
    smoothing_sigma : float
        Amount of smoothing to apply
    
    Returns:
    -------
    hills_mask : ndarray
        Binary mask of detected hills and mountains
    height_estimate : ndarray
        Estimate of relative height (0-1)
    """
    # Ensure input is grayscale and normalize to 0-1
    if len(image.shape) > 2:
        gray_img = np.mean(image, axis=2)
    else:
        gray_img = image.copy()
        
    # Normalize
    gray_img = (gray_img - np.min(gray_img)) / (np.max(gray_img) - np.min(gray_img) + 1e-8)
    
    # Apply smoothing to reduce noise
    smoothed_img = ndimage.gaussian_filter(gray_img, sigma=smoothing_sigma)
    
    # Calculate gradients (slopes)
    grad_x = filters.sobel_h(smoothed_img)
    grad_y = filters.sobel_v(smoothed_img)
    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    # Identify areas with significant slope and minimum height
    hills_mask = (gradient_magnitude > slope_threshold) & (smoothed_img > min_height)
    
    # Clean up mask with morphological operations
    hills_mask = morphology.remove_small_objects(hills_mask, min_size=20)
    hills_mask = morphology.binary_closing(hills_mask, morphology.disk(3))
    
    # Create a relative height estimate (higher values = higher elevation)
    # Use both brightness and local texture for better height estimation
    height_estimate = smoothed_img.copy()
    
    # Identify potential ridges using ridge detection
    ridges = feature.ridge_detection(smoothed_img, sigma=1.0)
    
    # Enhance height estimate by accounting for ridge intensity
    height_estimate[ridges > 0] = height_estimate[ridges > 0] * 1.2
    
    # Normalize back to 0-1
    height_estimate = np.clip(height_estimate, 0, 1)
    
    return hills_mask, height_estimate

def classify_terrain(image, num_classes=5):
    """
    Classify terrain into different elevation/topography classes
    
    Parameters:
    ----------
    image : ndarray
        Input grayscale image
    num_classes : int
        Number of terrain classes to identify
    
    Returns:
    -------
    terrain_classes : ndarray
        Classified image with class labels
    terrain_visualization : ndarray
        RGB visualization of terrain classes
    """
    # Ensure input is grayscale and normalize to 0-1
    if len(image.shape) > 2:
        gray_img = np.mean(image, axis=2)
    else:
        gray_img = image.copy()
        
    # Normalize
    gray_img = (gray_img - np.min(gray_img)) / (np.max(gray_img) - np.min(gray_img) + 1e-8)
    
    # Apply smoothing
    smoothed_img = ndimage.gaussian_filter(gray_img, sigma=1.0)
    
    # Simple thresholding-based terrain classification
    # This assumes higher intensity = higher elevation
    # For more sophisticated classification, consider using clustering algorithms
    terrain_classes = np.zeros_like(smoothed_img, dtype=np.uint8)
    
    for i in range(num_classes):
        lower = i / num_classes
        upper = (i + 1) / num_classes
        terrain_classes[(smoothed_img >= lower) & (smoothed_img < upper)] = i
        
    # Handle the upper boundary case
    terrain_classes[smoothed_img >= (num_classes-1)/num_classes] = num_classes - 1
    
    # Create a color visualization using a terrain colormap
    # Use colors that represent different elevations
    terrain_colors = plt.cm.terrain(np.linspace(0, 1, num_classes))
    
    terrain_visualization = np.zeros((*terrain_classes.shape, 3))
    for i in range(num_classes):
        mask = terrain_classes == i
        for j in range(3):  # RGB
            terrain_visualization[..., j][mask] = terrain_colors[i][j]
    
    return terrain_classes, terrain_visualization

def detect_ridges_valleys(image, sigma=1.0, threshold=0.05):
    """
    Detect ridges and valleys in elevation data
    
    Parameters:
    ----------
    image : ndarray
        Input grayscale image
    sigma : float
        Scale parameter for ridge detection
    threshold : float
        Ridge detection threshold
    
    Returns:
    -------
    ridges : ndarray
        Binary mask of detected ridges
    valleys : ndarray
        Binary mask of detected valleys
    """
    # Ensure input is grayscale and normalize to 0-1
    if len(image.shape) > 2:
        gray_img = np.mean(image, axis=2)
    else:
        gray_img = image.copy()
        
    # Normalize
    gray_img = (gray_img - np.min(gray_img)) / (np.max(gray_img) - np.min(gray_img) + 1e-8)
    
    # Apply smoothing to reduce noise
    smoothed_img = ndimage.gaussian_filter(gray_img, sigma=sigma)
    
    # Apply ridge detection
    ridges = feature.ridge_detection(smoothed_img, sigma=sigma)[0] > threshold
    
    # For valleys, invert the image and detect ridges
    inverted_img = 1.0 - smoothed_img
    valleys = feature.ridge_detection(inverted_img, sigma=sigma)[0] > threshold
    
    # Clean up with morphological operations
    ridges = morphology.remove_small_objects(ridges, min_size=10)
    valleys = morphology.remove_small_objects(valleys, min_size=10)
    
    return ridges, valleys

def create_terrain_visualization(image, hills_mask, ridges, valleys):
    """
    Create a visualization of detected terrain features
    
    Parameters:
    ----------
    image : ndarray
        Original input image
    hills_mask : ndarray
        Binary mask of hills and mountains
    ridges : ndarray
        Binary mask of ridges
    valleys : ndarray
        Binary mask of valleys
    
    Returns:
    -------
    visualization : ndarray
        RGB visualization with terrain features highlighted
    """
    # Ensure input is suitable for RGB visualization
    if len(image.shape) == 2:
        background = np.stack([image] * 3, axis=-1)
    elif len(image.shape) == 3 and image.shape[2] == 3:
        background = image.copy()
    else:
        # Default to grayscale if unknown format
        gray = np.mean(image, axis=2) if len(image.shape) > 2 else image
        background = np.stack([gray] * 3, axis=-1)
    
    # Create visualization image
    visualization = background.copy()
    
    # Highlight hills/mountains with amber overlay
    visualization[hills_mask, 0] = np.minimum(1.0, visualization[hills_mask, 0] * 0.7 + 0.5)  # Red
    visualization[hills_mask, 1] = np.minimum(1.0, visualization[hills_mask, 1] * 0.7 + 0.3)  # Green
    visualization[hills_mask, 2] = np.minimum(1.0, visualization[hills_mask, 2] * 0.5)        # Blue
    
    # Highlight ridges with white
    visualization[ridges, 0] = 1.0  # Red
    visualization[ridges, 1] = 1.0  # Green
    visualization[ridges, 2] = 1.0  # Blue
    
    # Highlight valleys with blue
    visualization[valleys, 0] = 0.0  # Red
    visualization[valleys, 1] = 0.5  # Green
    visualization[valleys, 2] = 1.0  # Blue
    
    return visualization

def analyze_terrain_features(image):
    """
    Analyze terrain features and provide statistical summary
    
    Parameters:
    ----------
    image : ndarray
        Input image
    
    Returns:
    -------
    analysis : dict
        Dictionary containing terrain analysis results
    """
    # Detect hills and mountains
    hills_mask, height_estimate = detect_hills_mountains(image)
    
    # Detect ridges and valleys
    ridges, valleys = detect_ridges_valleys(image)
    
    # Calculate terrain ruggedness index (TRI)
    # TRI is a measure of elevation difference between adjacent cells
    if len(image.shape) > 2:
        gray_img = np.mean(image, axis=2)
    else:
        gray_img = image.copy()
    
    # Normalize
    gray_img = (gray_img - np.min(gray_img)) / (np.max(gray_img) - np.min(gray_img) + 1e-8)
    
    # Calculate TRI using 3x3 neighborhood standard deviation
    tri = ndimage.generic_filter(gray_img, np.std, size=3)
    
    # Analyze hill/mountain features
    hill_percentage = np.sum(hills_mask) / hills_mask.size * 100
    hill_area_pixels = np.sum(hills_mask)
    
    # Analyze ridges
    ridge_percentage = np.sum(ridges) / ridges.size * 100
    ridge_length_pixels = np.sum(ridges)
    
    # Analyze valleys
    valley_percentage = np.sum(valleys) / valleys.size * 100
    valley_length_pixels = np.sum(valleys)
    
    # Calculate terrain roughness statistics
    mean_tri = np.mean(tri)
    max_tri = np.max(tri)
    
    # Terrain elevation statistics
    mean_elevation = np.mean(height_estimate)
    max_elevation = np.max(height_estimate)
    min_elevation = np.min(height_estimate)
    elevation_range = max_elevation - min_elevation
    
    # Assemble the analysis dictionary
    analysis = {
        'hill_percentage': hill_percentage,
        'hill_area_pixels': hill_area_pixels,
        'ridge_percentage': ridge_percentage,
        'ridge_length_pixels': ridge_length_pixels,
        'valley_percentage': valley_percentage,
        'valley_length_pixels': valley_length_pixels,
        'terrain_ruggedness_index': {
            'mean': mean_tri,
            'max': max_tri
        },
        'elevation_statistics': {
            'mean': mean_elevation,
            'max': max_elevation,
            'min': min_elevation,
            'range': elevation_range
        }
    }
    
    # Add terrain classification
    terrain_classes, _ = classify_terrain(image)
    class_distribution = {}
    
    for i in range(np.max(terrain_classes) + 1):
        class_count = np.sum(terrain_classes == i)
        class_percentage = class_count / terrain_classes.size * 100
        class_distribution[f'class_{i}'] = {
            'pixels': int(class_count),
            'percentage': float(class_percentage)
        }
    
    analysis['terrain_classification'] = class_distribution
    
    return analysis

def generate_terrain_report(image, analysis):
    """
    Generate a markdown report for terrain analysis
    
    Parameters:
    ----------
    image : ndarray
        Original image
    analysis : dict
        Terrain analysis results from analyze_terrain_features
    
    Returns:
    -------
    report : str
        Markdown formatted report
    """
    # Start with report header
    report = """# Terrain Analysis Report

## Topographic Features Summary

"""
    
    # Add hill/mountain information
    report += f"### Hills and Mountains\n"
    report += f"- **Coverage:** {analysis['hill_percentage']:.2f}% of the image\n"
    report += f"- **Area:** {analysis['hill_area_pixels']} pixels\n\n"
    
    # Add ridge information
    report += f"### Ridges\n"
    report += f"- **Coverage:** {analysis['ridge_percentage']:.2f}% of the image\n"
    report += f"- **Total Length:** Approximately {analysis['ridge_length_pixels']} pixels\n\n"
    
    # Add valley information
    report += f"### Valleys\n"
    report += f"- **Coverage:** {analysis['valley_percentage']:.2f}% of the image\n"
    report += f"- **Total Length:** Approximately {analysis['valley_length_pixels']} pixels\n\n"
    
    # Add terrain ruggedness information
    report += f"## Terrain Ruggedness\n"
    report += f"- **Mean Ruggedness Index:** {analysis['terrain_ruggedness_index']['mean']:.4f}\n"
    report += f"- **Maximum Ruggedness:** {analysis['terrain_ruggedness_index']['max']:.4f}\n\n"
    
    # Add elevation statistics
    report += f"## Elevation Statistics\n"
    report += f"- **Mean Relative Elevation:** {analysis['elevation_statistics']['mean']:.4f}\n"
    report += f"- **Elevation Range:** {analysis['elevation_statistics']['range']:.4f}\n"
    report += f"- **Minimum Elevation:** {analysis['elevation_statistics']['min']:.4f}\n"
    report += f"- **Maximum Elevation:** {analysis['elevation_statistics']['max']:.4f}\n\n"
    
    # Add terrain classification results
    report += f"## Terrain Classification\n"
    report += f"The image area is classified into {len(analysis['terrain_classification'])} terrain types:\n\n"
    
    # Create a sorted list of terrain classes
    class_items = sorted(analysis['terrain_classification'].items(), 
                         key=lambda x: int(x[0].split('_')[1]))
    
    for class_name, stats in class_items:
        # Convert class names to more intuitive descriptions
        class_index = int(class_name.split('_')[1])
        class_count = len(class_items)
        
        if class_count == 5:  # For 5-class classification
            if class_index == 0:
                terrain_type = "Lowlands/Water"
            elif class_index == 1:
                terrain_type = "Plains/Flatlands"
            elif class_index == 2:
                terrain_type = "Low Hills/Plateaus"
            elif class_index == 3:
                terrain_type = "Hills/Highland"
            else:
                terrain_type = "Mountains/Peaks"
        else:  # For other classifications
            if class_index == 0:
                terrain_type = "Lowest Elevation"
            elif class_index == class_count - 1:
                terrain_type = "Highest Elevation"
            else:
                terrain_type = f"Mid-Elevation (Level {class_index})"
        
        report += f"- **{terrain_type}:** {stats['percentage']:.2f}% ({stats['pixels']} pixels)\n"
    
    # Add interpretation section
    report += f"\n## Interpretation\n\n"
    
    # Interpret ruggedness
    if analysis['terrain_ruggedness_index']['mean'] < 0.05:
        report += "- The terrain is generally **flat with minimal variations**.\n"
    elif analysis['terrain_ruggedness_index']['mean'] < 0.1:
        report += "- The terrain has **gentle variations** with moderate topography.\n"
    else:
        report += "- The terrain is **rough with significant elevation changes**.\n"
    
    # Interpret elevation distribution
    if analysis['hill_percentage'] < 10:
        report += "- The area is **predominantly low-lying** with few elevated features.\n"
    elif analysis['hill_percentage'] < 30:
        report += "- The area has a **mix of flat and elevated terrain**.\n"
    else:
        report += "- The area is **dominated by hills and elevated terrain**.\n"
    
    # Interpret ridge and valley density
    ridge_valley_sum = analysis['ridge_percentage'] + analysis['valley_percentage']
    if ridge_valley_sum < 5:
        report += "- The terrain has **few defined ridges and valleys**.\n"
    elif ridge_valley_sum < 15:
        report += "- The terrain has a **moderate network of ridges and valleys**.\n"
    else:
        report += "- The terrain has a **dense network of ridges and valleys**.\n"
    
    return report