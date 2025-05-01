import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2

def compute_fft(image):
    """
    Compute the 2D FFT of an image and return both the shifted spectrum and 
    the log-scaled magnitude for visualization.
    
    Parameters:
    ----------
    image : ndarray
        Input image as a 2D numpy array
    
    Returns:
    -------
    fft_shifted : ndarray
        Shifted FFT with zero frequency at center (complex values)
    fft_magnitude : ndarray
        Log-scaled magnitude of FFT for visualization
    """
    # Ensure image is properly formatted
    if image.dtype != np.float32 and image.dtype != np.float64:
        image = image.astype(np.float32) / 255.0
    
    # Apply FFT
    fft_result = np.fft.fft2(image)
    
    # Shift the zero frequency component to the center
    fft_shifted = np.fft.fftshift(fft_result)
    
    # Compute the magnitude spectrum (add small constant to avoid log(0))
    fft_magnitude = 20 * np.log10(np.abs(fft_shifted) + 1e-10)
    
    # Normalize magnitude for visualization
    fft_magnitude_normalized = (fft_magnitude - fft_magnitude.min()) / (fft_magnitude.max() - fft_magnitude.min())
    
    return fft_shifted, fft_magnitude_normalized

def create_comparison_figure(original, fft_spectrum, filtered, title="Image Comparison"):
    """
    Create a figure with three subplots showing the original image, 
    FFT spectrum, and filtered result.
    
    Parameters:
    ----------
    original : ndarray
        Original image
    fft_spectrum : ndarray
        FFT magnitude spectrum
    filtered : ndarray
        Filtered image
    title : str
        Figure title
    
    Returns:
    -------
    fig : matplotlib.figure.Figure
        The created figure object
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Original image
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title("Original Image")
    axes[0].axis('off')
    
    # FFT Spectrum
    im = axes[1].imshow(fft_spectrum, cmap='viridis')
    axes[1].set_title("FFT Spectrum")
    axes[1].axis('off')
    fig.colorbar(im, ax=axes[1], shrink=0.8)
    
    # Filtered image
    axes[2].imshow(filtered, cmap='gray')
    axes[2].set_title("Filtered Result")
    axes[2].axis('off')
    
    fig.suptitle(title)
    fig.tight_layout()
    
    return fig

def normalize_image(image):
    """
    Normalize image values to the range [0, 1]
    
    Parameters:
    ----------
    image : ndarray
        Input image
    
    Returns:
    -------
    normalized : ndarray
        Normalized image
    """
    if image.min() == image.max():
        return np.zeros_like(image, dtype=np.float32)
    
    normalized = (image - image.min()) / (image.max() - image.min())
    return normalized

def resize_if_large(image, max_dimension=1024):
    """
    Resize image if any dimension exceeds max_dimension
    
    Parameters:
    ----------
    image : ndarray
        Input image
    max_dimension : int
        Maximum allowed dimension
    
    Returns:
    -------
    resized : ndarray
        Resized image if needed, otherwise original image
    scale_factor : float
        The factor by which the image was scaled
    """
    height, width = image.shape[:2]
    
    # Check if resizing is needed
    if height <= max_dimension and width <= max_dimension:
        return image, 1.0
    
    # Calculate scale factor
    scale_factor = max_dimension / max(height, width)
    
    # Calculate new dimensions
    new_height = int(height * scale_factor)
    new_width = int(width * scale_factor)
    
    # Resize image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return resized, scale_factor

def pil_to_numpy(pil_image):
    """
    Convert PIL Image to numpy array
    
    Parameters:
    ----------
    pil_image : PIL.Image
        Input PIL image
    
    Returns:
    -------
    numpy_image : ndarray
        Numpy array representation of the image
    """
    # Convert to grayscale if it's RGB/RGBA
    if pil_image.mode in ['RGB', 'RGBA']:
        pil_image = pil_image.convert('L')
    
    # Convert to numpy array
    numpy_image = np.array(pil_image).astype(np.float32) / 255.0
    
    return numpy_image
