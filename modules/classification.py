import numpy as np
import cv2
from skimage.feature import graycomatrix, graycoprops

def texture_classification(image):
    """
    Perform texture-based classification on an image using GLCM features.
    
    Parameters:
    ----------
    image : ndarray
        Input grayscale image in range [0, 1]
    
    Returns:
    -------
    classified_image : ndarray
        Classified image with texture regions highlighted
    """
    # Convert to uint8 for GLCM computation
    img_uint8 = (image * 255).astype(np.uint8)
    
    # Define texture parameters
    distances = [1]  # Distance between pixel pairs
    angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]  # Angles to consider
    
    # Calculate texture features in windows
    window_size = 15
    stride = 5
    
    height, width = image.shape
    
    # Create output image (3 channels for visualization)
    classified_image = np.zeros((height, width, 3), dtype=np.float32)
    
    # Calculate texture features at each window position
    for y in range(0, height - window_size, stride):
        for x in range(0, width - window_size, stride):
            # Extract window
            window = img_uint8[y:y+window_size, x:x+window_size]
            
            # Calculate GLCM features
            try:
                glcm = graycomatrix(window, distances=distances, angles=angles, 
                                   levels=8, symmetric=True, normed=True)
                
                # Extract texture properties
                contrast = graycoprops(glcm, 'contrast').mean()
                dissimilarity = graycoprops(glcm, 'dissimilarity').mean()
                homogeneity = graycoprops(glcm, 'homogeneity').mean()
                energy = graycoprops(glcm, 'energy').mean()
                correlation = graycoprops(glcm, 'correlation').mean()
                
                # Classify based on features
                # These thresholds can be adjusted based on specific imagery
                if contrast > 0.5:  # High contrast areas (e.g., boundaries)
                    color = [1.0, 0.0, 0.0]  # Red
                elif energy > 0.3:  # Homogeneous areas (e.g., water bodies)
                    color = [0.0, 0.0, 1.0]  # Blue
                elif homogeneity > 0.8:  # Smooth areas
                    color = [0.0, 1.0, 0.0]  # Green
                elif correlation > 0.5:  # Linearly structured areas
                    color = [1.0, 1.0, 0.0]  # Yellow
                else:  # Default
                    color = [0.5, 0.5, 0.5]  # Gray
                
                # Fill the window area in the output image
                classified_image[y:y+window_size, x:x+window_size] = np.array(color)
            except:
                # In case of GLCM computation error, use a default color
                classified_image[y:y+window_size, x:x+window_size] = [0.5, 0.5, 0.5]
    
    # Overlay classification result on original image
    overlay = image.reshape(height, width, 1).repeat(3, axis=2) * 0.5 + classified_image * 0.5
    
    return overlay

def detect_edges(image):
    """
    Detect edges in an image using Canny edge detection.
    
    Parameters:
    ----------
    image : ndarray
        Input grayscale image in range [0, 1]
    
    Returns:
    -------
    edges : ndarray
        Binary edge map
    """
    # Convert to uint8
    img_uint8 = (image * 255).astype(np.uint8)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(img_uint8, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Normalize to [0, 1]
    edges_normalized = edges.astype(np.float32) / 255.0
    
    return edges_normalized
