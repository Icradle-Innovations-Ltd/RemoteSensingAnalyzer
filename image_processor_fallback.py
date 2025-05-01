import numpy as np
from PIL import Image
import io
import os
import cv2
import utils

# Try to import rasterio, but provide fallback if not available
try:
    import rasterio
    from rasterio.plot import reshape_as_image
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    print("Warning: rasterio not available, using fallback for GeoTIFF processing")

def process_upload(uploaded_file):
    """
    Process an uploaded file based on its type.
    
    Parameters:
    ----------
    uploaded_file : UploadedFile
        The file uploaded through Streamlit
    
    Returns:
    -------
    image_data : ndarray
        The loaded image data
    is_geotiff : bool
        Whether the uploaded file is a GeoTIFF
    bands : list
        List of band names if GeoTIFF, None otherwise
    """
    # Get file extension
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Check if it's a GeoTIFF
    is_geotiff = file_extension in ['.tif', '.tiff']
    
    if is_geotiff and RASTERIO_AVAILABLE:
        # Process GeoTIFF with rasterio
        byte_data = uploaded_file.getvalue()
        with rasterio.open(io.BytesIO(byte_data)) as src:
            # Read all bands
            image_data = src.read()
            
            # Get band descriptions (if available)
            bands = [src.descriptions[i-1] if src.descriptions[i-1] else f"Band {i}" 
                    for i in range(1, src.count + 1)]
            
            # Reshape for easier band manipulation
            image_data = reshape_as_image(image_data)
            
            return image_data, is_geotiff, bands
    elif is_geotiff:
        # Fallback for GeoTIFF without rasterio
        try:
            # Try to open with PIL
            image = Image.open(uploaded_file)
            
            # Convert to numpy array
            image_data = np.array(image)
            
            # Assume it's a single-band image
            bands = ["Band 1"]
            if len(image_data.shape) == 3:
                bands = [f"Band {i+1}" for i in range(image_data.shape[2])]
            
            return image_data, is_geotiff, bands
        except Exception as e:
            # If PIL fails, return a placeholder image with error message
            print(f"Error processing GeoTIFF: {e}")
            # Create a small grayscale image with text
            image_data = np.zeros((100, 400), dtype=np.uint8)
            # Add text using OpenCV
            cv2.putText(image_data, "GeoTIFF processing requires rasterio", 
                       (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1)
            return image_data, is_geotiff, ["Error"]
    else:
        # Process regular image file (JPG, PNG)
        image = Image.open(uploaded_file)
        
        # Convert to numpy array
        image_data = np.array(image)
        
        # Get band information (RGB or grayscale)
        bands = None
        if len(image_data.shape) == 3 and image_data.shape[2] == 3:
            bands = ["Red", "Green", "Blue"]
        
        return image_data, is_geotiff, bands

def preprocess_image(image_data):
    """
    Preprocess image data for FFT analysis.
    
    Parameters:
    ----------
    image_data : ndarray
        The input image data
    
    Returns:
    -------
    preprocessed : ndarray
        Preprocessed grayscale image as float32 in range [0, 1]
    """
    # Check if image is already grayscale
    if len(image_data.shape) == 2:
        # Already grayscale
        grayscale = image_data
    elif len(image_data.shape) == 3:
        # Check if it's RGB or has more bands
        if image_data.shape[2] == 3:
            # Convert RGB to grayscale
            grayscale = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
        elif image_data.shape[2] > 3:
            # For multi-band images, just take the first band
            grayscale = image_data[:, :, 0]
        else:
            # Single channel image stored in 3D array
            grayscale = image_data[:, :, 0]
    else:
        raise ValueError("Unexpected image format")
    
    # Resize if image is too large (for better performance)
    resized, _ = utils.resize_if_large(grayscale, max_dimension=1024)
    
    # Normalize to [0, 1] range
    preprocessed = utils.normalize_image(resized)
    
    return preprocessed.astype(np.float32)

def extract_band(image_data, band_index):
    """
    Extract a specific band from multi-band image data.
    
    Parameters:
    ----------
    image_data : ndarray
        Multi-band image data
    band_index : int
        Index of the band to extract
    
    Returns:
    -------
    band : ndarray
        Extracted band as a 2D array
    """
    # Check if image has multiple bands
    if len(image_data.shape) < 3:
        # Single band image, just return it
        return image_data
    
    # Check if band index is valid
    if band_index >= image_data.shape[2]:
        raise ValueError(f"Band index {band_index} out of range for image with {image_data.shape[2]} bands")
    
    # Extract the specified band
    band = image_data[:, :, band_index]
    
    # Normalize to [0, 1] range
    band_normalized = utils.normalize_image(band)
    
    return band_normalized