"""
Change Detection module for Remote Sensing Data Analyzer
Provides functions for detecting and visualizing changes between images
"""

import numpy as np
from skimage import feature, transform, filters, segmentation, color
import matplotlib.pyplot as plt

def detect_image_changes(image1, image2, method="diff", threshold=0.1):
    """
    Detect changes between two images
    
    Parameters:
    ----------
    image1 : ndarray
        First image (baseline)
    image2 : ndarray
        Second image (comparison)
    method : str
        Method for change detection ('diff', 'ratio', 'regression')
    threshold : float
        Threshold for change detection (0-1)
    
    Returns:
    -------
    change_map : ndarray
        Binary map indicating changed areas
    change_magnitude : ndarray
        Magnitude of changes normalized to 0-1
    """
    # Ensure images are same size and grayscale
    if image1.shape != image2.shape:
        raise ValueError("Input images must have the same dimensions")
    
    if len(image1.shape) > 2:
        # For multi-band images, average across bands
        if len(image1.shape) == 3:
            img1_gray = np.mean(image1, axis=2)
            img2_gray = np.mean(image2, axis=2)
        else:
            raise ValueError("Input images must be 2D or 3D arrays")
    else:
        img1_gray = image1
        img2_gray = image2
    
    # Normalize inputs to 0-1
    img1_norm = (img1_gray - np.min(img1_gray)) / (np.max(img1_gray) - np.min(img1_gray) + 1e-8)
    img2_norm = (img2_gray - np.min(img2_gray)) / (np.max(img2_gray) - np.min(img2_gray) + 1e-8)
    
    if method == "diff":
        # Simple difference method
        change_magnitude = np.abs(img2_norm - img1_norm)
        
    elif method == "ratio":
        # Ratio method (handles illumination changes better)
        # Add small constant to avoid division by zero
        epsilon = 1e-8
        ratio = (img2_norm + epsilon) / (img1_norm + epsilon)
        log_ratio = np.log(ratio)
        change_magnitude = np.abs(log_ratio)
        
        # Normalize change magnitude to 0-1
        change_magnitude = (change_magnitude - np.min(change_magnitude)) / (np.max(change_magnitude) - np.min(change_magnitude) + 1e-8)
        
    elif method == "regression":
        # Linear regression method
        # Flatten arrays for regression
        x = img1_norm.flatten()
        y = img2_norm.flatten()
        
        # Perform linear regression
        from sklearn.linear_model import LinearRegression
        regr = LinearRegression()
        regr.fit(x.reshape(-1, 1), y)
        
        # Predicted values
        y_pred = regr.predict(x.reshape(-1, 1)).reshape(img1_norm.shape)
        
        # Residuals as change magnitude
        change_magnitude = np.abs(img2_norm - y_pred)
        
        # Normalize change magnitude to 0-1
        change_magnitude = (change_magnitude - np.min(change_magnitude)) / (np.max(change_magnitude) - np.min(change_magnitude) + 1e-8)
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Apply threshold to get binary change map
    change_map = change_magnitude > threshold
    
    # Clean up small noise in the change map
    from scipy import ndimage
    change_map = ndimage.binary_opening(change_map, structure=np.ones((3, 3)))
    change_map = ndimage.binary_closing(change_map, structure=np.ones((3, 3)))
    
    return change_map, change_magnitude

def create_change_rgb(image1, image2, change_map):
    """
    Create a RGB visualization of changes between two images
    
    Parameters:
    ----------
    image1 : ndarray
        First image (baseline)
    image2 : ndarray
        Second image (comparison)
    change_map : ndarray
        Binary map indicating changed areas
    
    Returns:
    -------
    rgb_result : ndarray
        RGB visualization where red indicates changes
    """
    # Ensure images are grayscale
    if len(image1.shape) > 2:
        img1_gray = np.mean(image1, axis=2)
        img2_gray = np.mean(image2, axis=2)
    else:
        img1_gray = image1
        img2_gray = image2
    
    # Normalize to 0-1
    img1_norm = (img1_gray - np.min(img1_gray)) / (np.max(img1_gray) - np.min(img1_gray) + 1e-8)
    img2_norm = (img2_gray - np.min(img2_gray)) / (np.max(img2_gray) - np.min(img2_gray) + 1e-8)
    
    # Create RGB image with grayscale image as background (both channels)
    h, w = img1_norm.shape
    rgb_result = np.zeros((h, w, 3), dtype=np.float32)
    
    # Use the second image as background
    rgb_result[:, :, 0] = img2_norm  # Red
    rgb_result[:, :, 1] = img2_norm  # Green
    rgb_result[:, :, 2] = img2_norm  # Blue
    
    # Highlight changes in red
    rgb_result[change_map, 0] = 1.0  # Full red
    rgb_result[change_map, 1] = 0.0  # No green
    rgb_result[change_map, 2] = 0.0  # No blue
    
    return rgb_result

def cluster_changes(change_map, change_magnitude, min_size=10):
    """
    Cluster changed pixels into regions
    
    Parameters:
    ----------
    change_map : ndarray
        Binary map indicating changed areas
    change_magnitude : ndarray
        Magnitude of changes normalized to 0-1
    min_size : int
        Minimum size of a change cluster to be considered
    
    Returns:
    -------
    labeled_changes : ndarray
        Labeled image where each change region has a unique label
    num_changes : int
        Number of distinct change regions
    change_stats : list
        Statistics for each change region
    """
    from scipy import ndimage
    from skimage import measure
    
    # Label connected components
    labeled_changes, num_changes = ndimage.label(change_map)
    
    # Filter small regions
    filtered_labels = np.zeros_like(labeled_changes)
    filtered_changes = []
    next_label = 1
    
    regions = measure.regionprops(labeled_changes)
    for region in regions:
        if region.area >= min_size:
            # Keep regions larger than min_size
            mask = labeled_changes == region.label
            filtered_labels[mask] = next_label
            
            # Calculate statistics for this region
            mean_magnitude = np.mean(change_magnitude[mask])
            max_magnitude = np.max(change_magnitude[mask])
            
            filtered_changes.append({
                'label': next_label,
                'area': region.area,
                'centroid': region.centroid,
                'mean_magnitude': mean_magnitude,
                'max_magnitude': max_magnitude,
                'bbox': region.bbox
            })
            
            next_label += 1
    
    return filtered_labels, len(filtered_changes), filtered_changes

def analyze_changes(image1, image2, change_stats):
    """
    Analyze the nature of changes between two images
    
    Parameters:
    ----------
    image1 : ndarray
        First image (baseline)
    image2 : ndarray
        Second image (comparison)
    change_stats : list
        Statistics for each change region
    
    Returns:
    -------
    change_analysis : list
        Analysis for each change region
    """
    # Convert to grayscale if needed
    if len(image1.shape) > 2:
        img1_gray = np.mean(image1, axis=2)
        img2_gray = np.mean(image2, axis=2)
    else:
        img1_gray = image1
        img2_gray = image2
    
    change_analysis = []
    
    for stat in change_stats:
        # Extract region bounding box
        y_min, x_min, y_max, x_max = stat['bbox']
        
        # Get region in both images
        region1 = img1_gray[y_min:y_max, x_min:x_max]
        region2 = img2_gray[y_min:y_max, x_min:x_max]
        
        # Calculate texture features for both regions
        texture1 = feature.graycomatrix(
            (region1 * 255).astype(np.uint8),
            distances=[1],
            angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
            levels=8,
            symmetric=True,
            normed=True
        )
        
        texture2 = feature.graycomatrix(
            (region2 * 255).astype(np.uint8),
            distances=[1],
            angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
            levels=8,
            symmetric=True,
            normed=True
        )
        
        # Extract features
        contrast1 = feature.graycoprops(texture1, 'contrast')[0, 0]
        homogeneity1 = feature.graycoprops(texture1, 'homogeneity')[0, 0]
        energy1 = feature.graycoprops(texture1, 'energy')[0, 0]
        
        contrast2 = feature.graycoprops(texture2, 'contrast')[0, 0]
        homogeneity2 = feature.graycoprops(texture2, 'homogeneity')[0, 0]
        energy2 = feature.graycoprops(texture2, 'energy')[0, 0]
        
        # Calculate mean intensity change
        mean_intensity1 = np.mean(region1)
        mean_intensity2 = np.mean(region2)
        intensity_change = mean_intensity2 - mean_intensity1
        
        # Determine change type based on features
        change_type = "Unknown"
        change_confidence = 0.0
        
        if contrast2 > contrast1 * 1.5:
            # Significant increase in contrast often indicates new structures
            change_type = "New structure"
            change_confidence = min(1.0, (contrast2 / contrast1 - 1.0) / 2.0)
        elif contrast1 > contrast2 * 1.5:
            # Significant decrease in contrast often indicates structure removal
            change_type = "Structure removal"
            change_confidence = min(1.0, (contrast1 / contrast2 - 1.0) / 2.0)
        elif intensity_change > 0.2:
            # Significant increase in brightness could be clearing or growth
            if energy2 > energy1 * 1.3:
                change_type = "Land clearing"
                change_confidence = min(1.0, intensity_change * 2.0)
            else:
                change_type = "Vegetation growth"
                change_confidence = min(1.0, intensity_change * 2.0)
        elif intensity_change < -0.2:
            # Significant decrease in brightness could be flooding or shadows
            if homogeneity2 > homogeneity1 * 1.3:
                change_type = "Water/flooding"
                change_confidence = min(1.0, abs(intensity_change) * 2.0)
            else:
                change_type = "Shadowing"
                change_confidence = min(1.0, abs(intensity_change) * 2.0)
        else:
            # Small changes in texture without major intensity shifts
            change_type = "Subtle change"
            change_confidence = 0.5
        
        analysis = {
            'label': stat['label'],
            'area': stat['area'],
            'intensity_change': intensity_change,
            'texture_change': {
                'contrast': contrast2 - contrast1,
                'homogeneity': homogeneity2 - homogeneity1,
                'energy': energy2 - energy1
            },
            'change_type': change_type,
            'confidence': change_confidence,
            'centroid': stat['centroid']
        }
        
        change_analysis.append(analysis)
    
    return change_analysis

def generate_change_report(image1, image2, change_analysis):
    """
    Generate a report describing the changes between two images
    
    Parameters:
    ----------
    image1 : ndarray
        First image (baseline)
    image2 : ndarray
        Second image (comparison)
    change_analysis : list
        Analysis for each change region
    
    Returns:
    -------
    report : str
        Markdown formatted report
    """
    report = """# Change Detection Report

## Summary

"""
    
    if len(change_analysis) == 0:
        report += "No significant changes detected between the images.\n"
        return report
    
    # Count change types
    change_types = {}
    total_area = 0
    
    for change in change_analysis:
        change_type = change['change_type']
        if change_type not in change_types:
            change_types[change_type] = {
                'count': 0,
                'area': 0,
                'confidence': 0
            }
        
        change_types[change_type]['count'] += 1
        change_types[change_type]['area'] += change['area']
        change_types[change_type]['confidence'] += change['confidence']
        total_area += change['area']
    
    # Calculate average confidence per type
    for change_type in change_types:
        if change_types[change_type]['count'] > 0:
            change_types[change_type]['confidence'] /= change_types[change_type]['count']
    
    # Add summary info
    report += f"Found **{len(change_analysis)}** significant changes covering approximately **{total_area}** pixels.\n\n"
    report += "## Change Types\n\n"
    
    for change_type, stats in change_types.items():
        percentage = (stats['area'] / total_area) * 100 if total_area > 0 else 0
        confidence = stats['confidence'] * 100
        report += f"- **{change_type}**: {stats['count']} regions ({percentage:.1f}% of changes, {confidence:.1f}% confidence)\n"
    
    # Add detailed analysis for the largest changes
    report += "\n## Major Changes\n\n"
    
    # Sort by area (largest first)
    sorted_changes = sorted(change_analysis, key=lambda x: x['area'], reverse=True)
    
    # Report up to 5 largest changes
    for i, change in enumerate(sorted_changes[:5]):
        report += f"### Change {i+1}\n\n"
        report += f"- **Type**: {change['change_type']} (Confidence: {change['confidence']*100:.1f}%)\n"
        report += f"- **Size**: {change['area']} pixels\n"
        report += f"- **Location**: Row {int(change['centroid'][0])}, Column {int(change['centroid'][1])}\n"
        
        # Add details based on type
        if change['change_type'] == "New structure":
            report += "- **Characteristics**: Significant increase in contrast and edge features\n"
        elif change['change_type'] == "Structure removal":
            report += "- **Characteristics**: Significant decrease in contrast and edge features\n"
        elif change['change_type'] == "Land clearing":
            report += "- **Characteristics**: Increase in brightness and uniformity\n"
        elif change['change_type'] == "Vegetation growth":
            report += "- **Characteristics**: Increase in brightness with maintained texture\n"
        elif change['change_type'] == "Water/flooding":
            report += "- **Characteristics**: Decrease in brightness with increased uniformity\n"
    
    # Add recommendations
    report += "\n## Recommendations\n\n"
    
    has_new_structures = "New structure" in change_types
    has_clearing = "Land clearing" in change_types
    has_water = "Water/flooding" in change_types
    
    if has_new_structures:
        report += "- Consider field verification of detected new structures for urban development monitoring\n"
    
    if has_clearing:
        report += "- Areas with land clearing should be monitored for potential erosion or further development\n"
    
    if has_water:
        report += "- Water/flooding regions should be evaluated for potential impact on surrounding areas\n"
    
    report += "- Consider using higher resolution imagery to better characterize detected changes\n"
    report += "- For improved accuracy, calibrate images for atmospheric conditions before change detection\n"
    
    return report