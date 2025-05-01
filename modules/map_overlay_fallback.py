import io
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Try to import folium, but provide fallback if not available
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Warning: folium not available, using fallback for map overlay")

def create_map_overlay(image, bounds=None, alpha=0.7):
    """
    Create an interactive map with the image overlaid.
    
    Parameters:
    ----------
    image : ndarray
        Image to overlay
    bounds : list
        Geographical bounds [west, south, east, north]
    alpha : float
        Opacity of the overlay (0-1)
    
    Returns:
    -------
    map_html : str
        HTML content of the map
    """
    # If no bounds provided, use a default area (San Francisco Bay Area)
    if bounds is None:
        bounds = [-122.5, 37.7, -122.3, 37.9]  # [west, south, east, north]
    
    if FOLIUM_AVAILABLE:
        # Create a map centered on the bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Convert image to RGB if grayscale
        if len(image.shape) == 2:
            img_rgb = np.stack([image, image, image], axis=2)
        else:
            img_rgb = image
        
        # Normalize to [0, 1] if needed
        if img_rgb.max() > 1.0:
            img_rgb = img_rgb / 255.0
        
        # Convert to 8-bit for PIL
        img_uint8 = (img_rgb * 255).astype(np.uint8)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(img_uint8)
        
        # Create overlay
        folium.raster_layers.ImageOverlay(
            image=pil_img,
            bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
            opacity=alpha,
            name="Image Overlay"
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Convert to HTML
        map_html = m._repr_html_()
        
        return map_html
    else:
        # Fallback: Create a static map using matplotlib
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Convert image to RGB if grayscale
        if len(image.shape) == 2:
            img_rgb = np.stack([image, image, image], axis=2)
        else:
            img_rgb = image
        
        # Normalize to [0, 1] if needed
        if img_rgb.max() > 1.0:
            img_rgb = img_rgb / 255.0
        
        # Plot the image with geographical bounds
        ax.imshow(img_rgb, extent=bounds, alpha=alpha)
        
        # Add grid lines
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add labels
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Image Overlay (Static Map - folium not available)')
        
        # Save to a buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # Create HTML with the image
        map_html = f"""
        <div style="text-align: center;">
            <h3>Static Map (folium not available)</h3>
            <img src="data:image/png;base64,{Image.open(buf).tobytes().hex()}" style="max-width: 100%;">
            <p>Note: Interactive map requires folium package. Using static map as fallback.</p>
        </div>
        """
        
        plt.close(fig)
        return map_html

def plot_overlay_on_map(image, fft_spectrum, filtered_image, bounds=None):
    """
    Create a figure with the original, FFT, and filtered images overlaid on maps.
    
    Parameters:
    ----------
    image : ndarray
        Original image
    fft_spectrum : ndarray
        FFT spectrum
    filtered_image : ndarray
        Filtered image
    bounds : list
        Geographical bounds [west, south, east, north]
    
    Returns:
    -------
    fig : matplotlib.figure.Figure
        Figure with map overlays
    """
    # If no bounds provided, use a default area
    if bounds is None:
        bounds = [-122.5, 37.7, -122.3, 37.9]  # [west, south, east, north]
    
    # Create a figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot original image
    axes[0].imshow(image, cmap='gray', extent=bounds)
    axes[0].set_title("Original Image")
    axes[0].set_xlabel("Longitude")
    axes[0].set_ylabel("Latitude")
    
    # Plot FFT spectrum (center it)
    axes[1].imshow(fft_spectrum, cmap='viridis', extent=bounds)
    axes[1].set_title("FFT Spectrum")
    axes[1].set_xlabel("Longitude")
    axes[1].set_ylabel("Latitude")
    
    # Plot filtered image
    axes[2].imshow(filtered_image, cmap='gray', extent=bounds)
    axes[2].set_title("Filtered Image")
    axes[2].set_xlabel("Longitude")
    axes[2].set_ylabel("Latitude")
    
    # Adjust layout
    fig.tight_layout()
    
    return fig