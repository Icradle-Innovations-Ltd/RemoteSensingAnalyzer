"""
Directional Filtering module for Remote Sensing Data Analyzer
Provides functions for detecting and analyzing directional patterns in satellite imagery
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, rotate

def create_directional_filter(shape, direction=0, width=20, strength=1.0):
    """
    Create a directional filter in the frequency domain
    
    Parameters:
    ----------
    shape : tuple
        Shape of the FFT array (height, width)
    direction : float
        Direction angle in degrees (0-360)
    width : float
        Angular width of the filter in degrees
    strength : float
        Filter strength (0-1)
    
    Returns:
    -------
    filter_mask : ndarray
        Directional filter mask
    """
    h, w = shape
    y, x = np.ogrid[:h, :w]
    
    # Center coordinates
    center_y, center_x = h // 2, w // 2
    
    # Convert coordinates to polar
    y_coord = y - center_y
    x_coord = x - center_x
    
    # Calculate radius and angle for each point
    radius = np.sqrt(y_coord**2 + x_coord**2)
    angle = np.arctan2(y_coord, x_coord) * 180 / np.pi
    
    # Convert angle to 0-360 range
    angle = (angle + 360) % 360
    
    # Create the directional filter
    # First create a wedge-shaped mask in the direction
    direction_min = (direction - width/2) % 360
    direction_max = (direction + width/2) % 360
    
    if direction_min < direction_max:
        direction_mask = np.logical_and(angle >= direction_min, angle <= direction_max)
    else:
        # Handle angle wrapping around 360
        direction_mask = np.logical_or(angle >= direction_min, angle <= direction_max)
    
    # Add the perpendicular direction (180 degrees opposite)
    perp_direction_min = (direction + 180 - width/2) % 360
    perp_direction_max = (direction + 180 + width/2) % 360
    
    if perp_direction_min < perp_direction_max:
        perp_mask = np.logical_and(angle >= perp_direction_min, angle <= perp_direction_max)
    else:
        # Handle angle wrapping around 360
        perp_mask = np.logical_or(angle >= perp_direction_min, angle <= perp_direction_max)
    
    # Combine the two directions
    combined_mask = np.logical_or(direction_mask, perp_mask)
    
    # Start with a mask of zeros
    filter_mask = np.zeros(shape)
    
    # Set the directional component
    filter_mask[combined_mask] = strength
    
    # Apply Gaussian tapering for smoother transitions
    filter_mask = gaussian_filter(filter_mask, sigma=1.0)
    
    # Ensure the filter values are in range [0, strength]
    filter_mask = filter_mask / np.max(filter_mask) * strength
    
    return filter_mask

def directional_analysis(fft_magnitude, num_directions=8, threshold_percentile=90):
    """
    Analyze directional patterns in the frequency domain
    
    Parameters:
    ----------
    fft_magnitude : ndarray
        Magnitude of the FFT of an image
    num_directions : int
        Number of directions to analyze
    threshold_percentile : int
        Percentile threshold for peak detection
    
    Returns:
    -------
    directional_info : dict
        Information about directional patterns
    """
    h, w = fft_magnitude.shape
    center_y, center_x = h // 2, w // 2
    
    # Create circular mask to exclude extreme high frequencies
    y, x = np.ogrid[:h, :w]
    radius = np.sqrt((y - center_y)**2 + (x - center_x)**2)
    max_radius = min(h, w) // 2
    circle_mask = radius <= max_radius
    
    # Apply mask to FFT magnitude
    masked_fft = fft_magnitude.copy()
    masked_fft[~circle_mask] = 0
    
    # Calculate directional energy
    direction_energy = {}
    direction_peaks = {}
    angle_step = 180 / num_directions
    
    for i in range(num_directions):
        angle = i * angle_step
        
        # Create directional mask with narrow width
        dir_mask = create_directional_filter((h, w), direction=angle, width=angle_step, strength=1.0)
        
        # Apply mask to FFT magnitude and calculate energy
        dir_energy = np.sum(masked_fft * dir_mask)
        direction_energy[angle] = dir_energy
        
        # Find peaks in this direction
        threshold = np.percentile(masked_fft * dir_mask, threshold_percentile)
        peaks = np.where((masked_fft * dir_mask) > threshold)
        
        if len(peaks[0]) > 0:
            # Calculate frequency of peaks (distance from center)
            peak_distances = np.sqrt((peaks[0] - center_y)**2 + (peaks[1] - center_x)**2)
            
            # Get the top 5 peaks
            top_indices = np.argsort(masked_fft[peaks])[-5:]
            
            peak_info = []
            for idx in top_indices:
                y_peak, x_peak = peaks[0][idx], peaks[1][idx]
                dist = np.sqrt((y_peak - center_y)**2 + (x_peak - center_x)**2)
                peak_info.append({
                    'distance': dist,
                    'position': (y_peak, x_peak),
                    'spatial_freq': dist / max_radius,  # Normalized spatial frequency
                    'magnitude': masked_fft[y_peak, x_peak]
                })
                
            direction_peaks[angle] = peak_info
    
    # Find the dominant directions (top 3)
    sorted_directions = sorted(direction_energy.items(), key=lambda x: x[1], reverse=True)
    dominant_directions = sorted_directions[:3]
    
    # Calculate direction strengths as percentages
    total_energy = sum(direction_energy.values())
    direction_strength = {angle: energy / total_energy for angle, energy in direction_energy.items()}
    
    # Determine pattern type based on direction distribution
    pattern_type = "isotropic"  # Default, no strong directional pattern
    
    if dominant_directions[0][1] > 2 * dominant_directions[1][1]:
        # One dominant direction, much stronger than others
        pattern_type = "strongly_directional"
    elif dominant_directions[0][1] > 1.5 * dominant_directions[1][1]:
        # One moderately dominant direction
        pattern_type = "directional"
    elif dominant_directions[0][1] > 1.5 * dominant_directions[2][1]:
        # Two dominant perpendicular directions, grid pattern
        opposite_angle = (dominant_directions[1][0] + 90) % 180
        if abs(dominant_directions[0][0] - opposite_angle) < 20:
            pattern_type = "grid"
        else:
            pattern_type = "bidirectional"
    
    # Compile results
    directional_info = {
        'energy_by_direction': direction_energy,
        'strength_by_direction': direction_strength,
        'dominant_directions': [{'angle': angle, 'energy': energy} for angle, energy in dominant_directions],
        'pattern_type': pattern_type,
        'direction_peaks': direction_peaks
    }
    
    return directional_info

def enhance_directional_features(image, direction, width=30, strength=0.8):
    """
    Enhance features in a specific direction using frequency domain filtering
    
    Parameters:
    ----------
    image : ndarray
        Input image as a 2D numpy array
    direction : float
        Direction angle in degrees (0-360)
    width : float
        Angular width of the filter in degrees
    strength : float
        Enhancement strength (0-1)
    
    Returns:
    -------
    enhanced_image : ndarray
        Image with enhanced directional features
    """
    from scipy.fftpack import fft2, ifft2, fftshift, ifftshift
    
    # Ensure image is 2D
    if len(image.shape) > 2:
        raise ValueError("Input image must be a 2D array")
    
    # Compute FFT
    fft = fft2(image)
    fft_shifted = fftshift(fft)
    
    # Create directional filter
    h, w = image.shape
    dir_filter = create_directional_filter((h, w), direction=direction, width=width, strength=strength)
    
    # Apply filter (enhance the specified direction)
    # The filter increases values in the specified direction
    enhanced_fft = fft_shifted * (1 + dir_filter)
    
    # Inverse FFT
    enhanced_shifted = ifftshift(enhanced_fft)
    enhanced_image = np.real(ifft2(enhanced_shifted))
    
    # Normalize to [0, 1]
    enhanced_image = (enhanced_image - np.min(enhanced_image)) / (np.max(enhanced_image) - np.min(enhanced_image))
    
    return enhanced_image

def suppress_directional_noise(image, direction, width=30, strength=0.8):
    """
    Suppress noise in a specific direction using frequency domain filtering
    
    Parameters:
    ----------
    image : ndarray
        Input image as a 2D numpy array
    direction : float
        Direction angle in degrees (0-360) to suppress
    width : float
        Angular width of the filter in degrees
    strength : float
        Suppression strength (0-1)
    
    Returns:
    -------
    filtered_image : ndarray
        Image with suppressed directional noise
    """
    from scipy.fftpack import fft2, ifft2, fftshift, ifftshift
    
    # Ensure image is 2D
    if len(image.shape) > 2:
        raise ValueError("Input image must be a 2D array")
    
    # Compute FFT
    fft = fft2(image)
    fft_shifted = fftshift(fft)
    
    # Create directional filter
    h, w = image.shape
    dir_filter = create_directional_filter((h, w), direction=direction, width=width, strength=strength)
    
    # Apply filter (suppress the specified direction)
    # The filter decreases values in the specified direction
    filtered_fft = fft_shifted * (1 - dir_filter)
    
    # Inverse FFT
    filtered_shifted = ifftshift(filtered_fft)
    filtered_image = np.real(ifft2(filtered_shifted))
    
    # Normalize to [0, 1]
    filtered_image = (filtered_image - np.min(filtered_image)) / (np.max(filtered_image) - np.min(filtered_image))
    
    return filtered_image

def visualize_directional_analysis(image, directional_info):
    """
    Visualize directional analysis results
    
    Parameters:
    ----------
    image : ndarray
        Original image
    directional_info : dict
        Output from directional_analysis function
    
    Returns:
    -------
    fig : matplotlib.figure.Figure
        Figure with visualizations
    """
    # Create the figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot the original image
    axes[0, 0].imshow(image, cmap='gray')
    axes[0, 0].set_title('Original Image')
    axes[0, 0].axis('off')
    
    # Plot the directional energy distribution as a polar plot
    ax_polar = fig.add_subplot(222, projection='polar')
    angles = np.array(list(directional_info['energy_by_direction'].keys())) * np.pi / 180
    energy = np.array(list(directional_info['energy_by_direction'].values()))
    
    # Duplicate the first point to close the circle
    angles = np.append(angles, angles[0])
    energy = np.append(energy, energy[0])
    
    # Normalize energy for better visualization
    energy = energy / np.max(energy)
    
    ax_polar.plot(angles, energy)
    ax_polar.fill(angles, energy, alpha=0.3)
    ax_polar.set_title('Directional Energy Distribution')
    ax_polar.set_xticks(np.arange(0, 2*np.pi, np.pi/4))
    ax_polar.set_xticklabels(['0°', '45°', '90°', '135°', '180°', '225°', '270°', '315°'])
    
    # Plot enhanced image for the dominant direction
    if len(directional_info['dominant_directions']) > 0:
        dominant_angle = directional_info['dominant_directions'][0]['angle']
        enhanced = enhance_directional_features(image, dominant_angle)
        axes[1, 0].imshow(enhanced, cmap='gray')
        axes[1, 0].set_title(f'Enhanced Features at {dominant_angle}°')
        axes[1, 0].axis('off')
    
    # Plot information about the directional analysis
    axes[1, 1].axis('off')
    info_text = f"Pattern Type: {directional_info['pattern_type']}\n\n"
    info_text += "Dominant Directions:\n"
    
    for i, dir_info in enumerate(directional_info['dominant_directions']):
        angle = dir_info['angle']
        strength = dir_info['energy']
        info_text += f"{i+1}. {angle}° (Strength: {strength:.2f})\n"
    
    axes[1, 1].text(0.05, 0.95, info_text, transform=axes[1, 1].transAxes, 
                  fontsize=12, verticalalignment='top')
    
    plt.tight_layout()
    return fig