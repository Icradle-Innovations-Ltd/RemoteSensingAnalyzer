import numpy as np
from scipy import ndimage

def create_filter_mask(shape, filter_params):
    """
    Create a frequency domain filter mask based on the specified filter parameters.
    
    Parameters:
    ----------
    shape : tuple
        Shape of the FFT array (height, width)
    filter_params : dict
        Dictionary containing filter parameters:
        - 'type': 'Low-pass', 'High-pass', or 'Band-stop'
        - 'cutoff_radius': Radius for low-pass or high-pass filters
        - 'inner_radius', 'outer_radius': Radii for band-stop filter
        - 'gaussian_tapering': Boolean for whether to apply Gaussian tapering
    
    Returns:
    -------
    mask : ndarray
        2D array with same shape as input, containing the filter mask
    """
    rows, cols = shape
    
    # Create a coordinate grid
    y, x = np.ogrid[:rows, :cols]
    
    # Calculate center coordinates
    center_y, center_x = rows // 2, cols // 2
    
    # Calculate distance from center for each point
    distance_from_center = np.sqrt((y - center_y)**2 + (x - center_x)**2)
    
    # Initialize mask
    mask = np.zeros((rows, cols), dtype=np.float32)
    
    # Create filter based on type
    filter_type = filter_params.get('type', 'Low-pass')
    
    if filter_type == 'Low-pass':
        cutoff_radius = filter_params.get('cutoff_radius', rows//4)
        
        # Create the basic mask (1 inside circle, 0 outside)
        mask = distance_from_center <= cutoff_radius
        
        # Apply Gaussian tapering if requested
        if filter_params.get('gaussian_tapering', False):
            sigma = cutoff_radius / 3  # Adjust sigma for smoother transition
            gaussian_mask = np.exp(-(distance_from_center**2) / (2 * sigma**2))
            mask = mask * gaussian_mask
        
    elif filter_type == 'High-pass':
        cutoff_radius = filter_params.get('cutoff_radius', rows//4)
        
        # Create the basic mask (0 inside circle, 1 outside)
        mask = distance_from_center > cutoff_radius
        
        # Apply Gaussian tapering if requested
        if filter_params.get('gaussian_tapering', False):
            sigma = cutoff_radius / 3  # Adjust sigma for smoother transition
            gaussian_mask = 1 - np.exp(-(distance_from_center**2) / (2 * sigma**2))
            mask = mask * gaussian_mask
    
    elif filter_type == 'Band-stop':
        inner_radius = filter_params.get('inner_radius', rows//8)
        outer_radius = filter_params.get('outer_radius', rows//4)
        
        # Create the basic mask (1 outside the band, 0 within the band)
        mask = np.logical_or(distance_from_center < inner_radius, 
                             distance_from_center > outer_radius)
        
        # Apply Gaussian tapering if requested
        if filter_params.get('gaussian_tapering', False):
            # Create a gradual transition at both edges of the band
            inner_sigma = inner_radius / 3
            outer_sigma = outer_radius / 3
            
            # Gaussian weight for inner edge (1 at center, decreasing outward)
            inner_weight = np.exp(-(distance_from_center**2) / (2 * inner_sigma**2))
            
            # Gaussian weight for outer edge (0 at center, increasing outward)
            outer_weight = 1 - np.exp(-(distance_from_center**2) / (2 * outer_sigma**2))
            
            # Apply weights to create gradual transition
            band_region = np.logical_and(distance_from_center >= inner_radius, 
                                         distance_from_center <= outer_radius)
            transition_mask = np.ones_like(mask, dtype=np.float32)
            transition_mask[band_region] = 0
            
            # Apply gaussian transition at boundaries
            transition_region = np.logical_and(
                distance_from_center >= inner_radius - inner_sigma*2,
                distance_from_center <= inner_radius + inner_sigma*2
            )
            transition_mask[transition_region] = 1 - inner_weight[transition_region]
            
            transition_region = np.logical_and(
                distance_from_center >= outer_radius - outer_sigma*2,
                distance_from_center <= outer_radius + outer_sigma*2
            )
            transition_mask[transition_region] = outer_weight[transition_region]
            
            mask = transition_mask
    
    # Convert boolean to float for multiplication with complex FFT
    if mask.dtype == bool:
        mask = mask.astype(np.float32)
    
    return mask

def apply_filter(fft_shifted, filter_mask):
    """
    Apply a frequency domain filter to the shifted FFT of an image and 
    transform back to the spatial domain.
    
    Parameters:
    ----------
    fft_shifted : ndarray
        Shifted FFT of the input image (complex values)
    filter_mask : ndarray
        Filter mask to apply (same shape as fft_shifted)
    
    Returns:
    -------
    filtered_image : ndarray
        Filtered image in spatial domain, normalized to [0, 1]
    """
    # Apply filter mask to the FFT
    filtered_fft = fft_shifted * filter_mask
    
    # Shift back
    filtered_fft_shifted = np.fft.ifftshift(filtered_fft)
    
    # Inverse FFT
    inverse_fft = np.fft.ifft2(filtered_fft_shifted)
    
    # Get the magnitude (absolute value) of the complex result
    filtered_image = np.abs(inverse_fft)
    
    # Normalize to [0, 1] range for display
    filtered_image_normalized = (filtered_image - filtered_image.min()) / (filtered_image.max() - filtered_image.min())
    
    return filtered_image_normalized
