"""
Railways Detection module for Remote Sensing Data Analyzer
Provides functions for detecting and analyzing railway infrastructure
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import filters, morphology, feature, exposure, transform, color, segmentation

def detect_railways(image, direction_tolerance=30, min_length=20, threshold=0.7):
    """
    Detect railways in satellite imagery using line detection and directional filtering
    
    Parameters:
    ----------
    image : ndarray
        Input grayscale image
    direction_tolerance : float
        Tolerance in degrees for line direction clustering
    min_length : int
        Minimum length of a line to be considered a railway
    threshold : float
        Threshold for line detection
    
    Returns:
    -------
    railways_mask : ndarray
        Binary mask of detected railways
    properties : dict
        Dictionary containing railway properties
    """
    # Ensure input is grayscale and normalize to 0-1
    if len(image.shape) > 2:
        gray_img = np.mean(image, axis=2)
    else:
        gray_img = image.copy()
        
    # Normalize
    gray_img = (gray_img - np.min(gray_img)) / (np.max(gray_img) - np.min(gray_img) + 1e-8)
    
    # Enhance contrast to make lines more visible
    enhanced = exposure.equalize_adapthist(gray_img)
    
    # Apply edge detection
    edges = feature.canny(enhanced, sigma=1.0, low_threshold=0.1, high_threshold=0.2)
    
    # Apply Hough transform to detect lines
    tested_angles = np.linspace(-np.pi/2, np.pi/2, 180, endpoint=False)
    h, theta, d = transform.hough_line(edges, theta=tested_angles)
    
    # Extract line segments
    railway_segments = []
    railways_mask = np.zeros_like(gray_img, dtype=bool)
    origin = np.array((0, 0))
    
    # Find peaks in the Hough transform
    peak_threshold = threshold * np.max(h)
    hspace, angles, dists = transform.hough_line_peaks(h, theta, d, 
                                                    threshold=peak_threshold,
                                                    min_angle=10,  # Minimum angle separation in degrees
                                                    min_distance=10)  # Minimum distance between lines
    
    # Group lines by similar directions
    grouped_lines = {}
    
    for _, angle, dist in zip(hspace, angles, dists):
        # Convert angle to degrees
        angle_deg = np.degrees(angle) % 180
        
        # Find the group this line belongs to
        assigned_group = False
        for direction, group in grouped_lines.items():
            # Check if the angle is within tolerance of an existing group
            if min(abs(angle_deg - direction), abs(180 - abs(angle_deg - direction))) < direction_tolerance:
                group.append((angle, dist))
                assigned_group = True
                break
        
        # If no matching group, create a new one
        if not assigned_group:
            grouped_lines[angle_deg] = [(angle, dist)]
    
    # Process each group of lines
    for direction, lines in grouped_lines.items():
        group_mask = np.zeros_like(gray_img, dtype=bool)
        
        for angle, dist in lines:
            # Calculate line endpoints
            cos_theta = np.cos(angle)
            sin_theta = np.sin(angle)
            x0 = dist * cos_theta
            y0 = dist * sin_theta
            
            # Calculate line length based on image dimensions
            length = np.sqrt(gray_img.shape[0]**2 + gray_img.shape[1]**2)
            
            # Calculate endpoints
            x1 = int(x0 + length * (-sin_theta))
            y1 = int(y0 + length * (cos_theta))
            x2 = int(x0 - length * (-sin_theta))
            y2 = int(y0 - length * (cos_theta))
            
            # Draw the line on the mask
            rr, cc = np.array(np.linspace(y1, y2, 1000)), np.array(np.linspace(x1, x2, 1000))
            valid_indices = (rr >= 0) & (rr < gray_img.shape[0]) & (cc >= 0) & (cc < gray_img.shape[1])
            rr, cc = rr[valid_indices].astype(int), cc[valid_indices].astype(int)
            
            if len(rr) > min_length:
                group_mask[rr, cc] = True
                railway_segments.append({
                    'angle_deg': direction,
                    'length_pixels': len(rr),
                    'start': (y1, x1),
                    'end': (y2, x2)
                })
        
        # Combine with overall mask
        railways_mask = railways_mask | group_mask
    
    # Clean up the mask - remove small objects and close small gaps
    railways_mask = morphology.remove_small_objects(railways_mask, min_size=min_length)
    railways_mask = morphology.binary_dilation(railways_mask, morphology.disk(1))
    railways_mask = morphology.remove_small_holes(railways_mask, area_threshold=100)
    railways_mask = morphology.binary_erosion(railways_mask, morphology.disk(1))
    
    # Calculate properties
    total_length = sum(segment['length_pixels'] for segment in railway_segments)
    
    properties = {
        'segments': railway_segments,
        'total_length_pixels': total_length,
        'segment_count': len(railway_segments),
        'coverage_percentage': np.sum(railways_mask) / railways_mask.size * 100
    }
    
    # Identify main directions (if any)
    if railway_segments:
        # Get angles and lengths
        angles = [segment['angle_deg'] for segment in railway_segments]
        lengths = [segment['length_pixels'] for segment in railway_segments]
        
        # Calculate weighted average angle (weighted by length)
        weighted_sum = sum(angle * length for angle, length in zip(angles, lengths))
        total_length = sum(lengths)
        
        if total_length > 0:
            main_direction = weighted_sum / total_length
        else:
            main_direction = None
            
        properties['main_direction_degrees'] = main_direction
        
    return railways_mask, properties

def create_railway_visualization(image, railways_mask):
    """
    Create a visualization of detected railways
    
    Parameters:
    ----------
    image : ndarray
        Original input image
    railways_mask : ndarray
        Binary mask of detected railways
    
    Returns:
    -------
    visualization : ndarray
        RGB visualization with railways highlighted
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
    
    # Create visualization with railways highlighted in red
    visualization = background.copy()
    
    # Create a dilated mask for better visibility
    display_mask = morphology.binary_dilation(railways_mask, morphology.disk(2))
    
    # Highlight railways in magenta for visibility
    visualization[display_mask, 0] = 1.0  # Red
    visualization[display_mask, 1] = 0.0  # Green
    visualization[display_mask, 2] = 1.0  # Blue
    
    return visualization

def detect_rail_intersections(railways_mask):
    """
    Detect railway intersections in the railways mask
    
    Parameters:
    ----------
    railways_mask : ndarray
        Binary mask of detected railways
    
    Returns:
    -------
    intersections : ndarray
        Binary mask of detected intersections
    intersection_points : list
        List of (y, x) coordinates of intersection points
    """
    # Create a kernel for detecting intersections
    kernel = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ], dtype=np.uint8)
    
    # Count neighbors for each point
    neighbor_count = ndimage.convolve(railways_mask.astype(np.uint8), kernel, mode='constant')
    
    # Points with more than 2 neighbors on the railway mask are likely intersections
    intersections = (neighbor_count > 2) & railways_mask
    
    # Remove nearby intersections (keep only one per local area)
    labeled, num = ndimage.label(intersections)
    intersection_points = []
    
    # Get centroid of each intersection region
    for i in range(1, num + 1):
        region = labeled == i
        y, x = ndimage.center_of_mass(region)
        intersection_points.append((int(y), int(x)))
    
    return intersections, intersection_points

def analyze_railway_network(railways_mask, properties):
    """
    Analyze railway network and provide statistical summary
    
    Parameters:
    ----------
    railways_mask : ndarray
        Binary mask of detected railways
    properties : dict
        Dictionary containing railway properties from detect_railways
    
    Returns:
    -------
    analysis : dict
        Dictionary containing railway network analysis results
    """
    # Detect intersections (potential stations or junctions)
    intersections, intersection_points = detect_rail_intersections(railways_mask)
    
    # Calculate segment lengths
    segment_lengths = [segment['length_pixels'] for segment in properties['segments']]
    
    # Calculate length statistics
    if segment_lengths:
        avg_segment_length = sum(segment_lengths) / len(segment_lengths)
        max_segment_length = max(segment_lengths)
        min_segment_length = min(segment_lengths)
    else:
        avg_segment_length = 0
        max_segment_length = 0
        min_segment_length = 0
    
    # Create the analysis dictionary
    analysis = {
        'network_length_pixels': properties['total_length_pixels'],
        'segment_count': properties['segment_count'],
        'intersection_count': len(intersection_points),
        'coverage_percentage': properties['coverage_percentage'],
        'segment_statistics': {
            'average_length': avg_segment_length,
            'max_length': max_segment_length,
            'min_length': min_segment_length
        }
    }
    
    # Add main direction if available
    if 'main_direction_degrees' in properties:
        analysis['main_direction_degrees'] = properties['main_direction_degrees']
    
    # Calculate network density (length per unit area)
    total_area = railways_mask.size
    if total_area > 0:
        network_density = properties['total_length_pixels'] / total_area
    else:
        network_density = 0
        
    analysis['network_density'] = network_density
    
    # Calculate connectivity metrics
    if len(intersection_points) > 0 and properties['segment_count'] > 0:
        # Beta index: ratio of links to nodes
        beta_index = properties['segment_count'] / len(intersection_points)
        analysis['connectivity'] = {
            'beta_index': beta_index,
            'intersection_density': len(intersection_points) / total_area * 10000  # per 10,000 pixels
        }
    
    return analysis

def generate_railway_report(image, analysis):
    """
    Generate a markdown report for railway analysis
    
    Parameters:
    ----------
    image : ndarray
        Original image
    analysis : dict
        Railway analysis results
    
    Returns:
    -------
    report : str
        Markdown formatted report
    """
    # Start with report header
    report = """# Railway Network Analysis Report

## Network Summary

"""
    
    # Add general information
    report += f"- **Total Railway Length:** {analysis['network_length_pixels']:.1f} pixels\n"
    report += f"- **Number of Segments:** {analysis['segment_count']}\n"
    report += f"- **Number of Intersections:** {analysis['intersection_count']}\n"
    report += f"- **Coverage Area:** {analysis['coverage_percentage']:.2f}% of the image\n"
    
    # Add main direction if available
    if 'main_direction_degrees' in analysis:
        # Convert to compass directions for better interpretability
        angle = analysis['main_direction_degrees']
        compass_direction = ""
        
        if angle is not None:
            # Convert angle to 0-180 range
            angle = angle % 180
            
            if 0 <= angle < 22.5 or 157.5 <= angle < 180:
                compass_direction = "East-West"
            elif 22.5 <= angle < 67.5:
                compass_direction = "Northeast-Southwest"
            elif 67.5 <= angle < 112.5:
                compass_direction = "North-South"
            else:  # 112.5 <= angle < 157.5
                compass_direction = "Northwest-Southeast"
                
            report += f"- **Main Direction:** {compass_direction} ({angle:.1f}°)\n"
    
    # Add network density
    report += f"- **Network Density:** {analysis['network_density'] * 10000:.4f} per 10,000 pixels\n\n"
    
    # Add segment statistics
    report += f"## Segment Statistics\n\n"
    report += f"- **Average Segment Length:** {analysis['segment_statistics']['average_length']:.1f} pixels\n"
    report += f"- **Maximum Segment Length:** {analysis['segment_statistics']['max_length']:.1f} pixels\n"
    report += f"- **Minimum Segment Length:** {analysis['segment_statistics']['min_length']:.1f} pixels\n\n"
    
    # Add connectivity metrics if available
    if 'connectivity' in analysis:
        report += f"## Network Connectivity\n\n"
        report += f"- **Beta Index:** {analysis['connectivity']['beta_index']:.2f} (links per node)\n"
        report += f"- **Intersection Density:** {analysis['connectivity']['intersection_density']:.4f} per 10,000 pixels\n\n"
    
    # Add interpretation section
    report += f"## Interpretation\n\n"
    
    # Interpret network complexity
    if analysis['segment_count'] < 3:
        report += "- The railway network is **simple with few segments**.\n"
    elif analysis['segment_count'] < 10:
        report += "- The railway network has **moderate complexity**.\n"
    else:
        report += "- The railway network is **complex with many segments**.\n"
    
    # Interpret connectivity
    if 'connectivity' in analysis:
        beta = analysis['connectivity']['beta_index']
        if beta < 1:
            report += "- The network has **poor connectivity** with more isolated segments than connections.\n"
        elif beta < 1.5:
            report += "- The network has **moderate connectivity** with sufficient connections between segments.\n"
        else:
            report += "- The network has **good connectivity** with multiple alternate routes.\n"
    
    # Interpret coverage
    if analysis['coverage_percentage'] < 1:
        report += "- Railways cover a **very small portion** of the analyzed area.\n"
    elif analysis['coverage_percentage'] < 5:
        report += "- Railways have **moderate coverage** across the analyzed area.\n"
    else:
        report += "- Railways have **extensive coverage** throughout the analyzed area.\n"
    
    return report