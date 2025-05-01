import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import os
import time

# Import custom modules
import image_processor
import filters
import utils
from modules import ndvi, classification, map_overlay

# Set page configuration
st.set_page_config(
    page_title="Remote Sensing Data Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a title and description
st.title("🌍 Remote Sensing Data Analyzer")
st.markdown("*Frequency-domain filtering and analysis for satellite imagery*")

# Initialize session state variables if they don't exist
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'preprocessed_image' not in st.session_state:
    st.session_state.preprocessed_image = None
if 'fft_image' not in st.session_state:
    st.session_state.fft_image = None
if 'filtered_image' not in st.session_state:
    st.session_state.filtered_image = None
if 'fft_magnitude' not in st.session_state:
    st.session_state.fft_magnitude = None
if 'fft_shifted' not in st.session_state:
    st.session_state.fft_shifted = None
if 'selected_band' not in st.session_state:
    st.session_state.selected_band = None
if 'is_geotiff' not in st.session_state:
    st.session_state.is_geotiff = False
if 'bands' not in st.session_state:
    st.session_state.bands = None
if 'last_filter_params' not in st.session_state:
    st.session_state.last_filter_params = {}
if 'img_info' not in st.session_state:
    st.session_state.img_info = {}
    
# Sidebar
with st.sidebar:
    st.header("Upload & Controls")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an image (JPG, PNG, or GeoTIFF)", 
                                    type=["jpg", "jpeg", "png", "tif", "tiff"])
    
    # Only show the rest of the controls if an image is uploaded
    if uploaded_file is not None:
        try:
            # Process the uploaded file
            image_data, is_geotiff, bands = image_processor.process_upload(uploaded_file)
            
            # Update session state
            st.session_state.original_image = image_data
            st.session_state.is_geotiff = is_geotiff
            st.session_state.bands = bands
            
            # Band selection for GeoTIFF
            if is_geotiff and bands and len(bands) > 1:
                band_options = list(range(1, len(bands) + 1))
                selected_band = st.selectbox(
                    "Select band to analyze:", 
                    band_options,
                    index=0
                )
                st.session_state.selected_band = selected_band
                
                # Extract the selected band
                preprocessed_img = image_processor.extract_band(image_data, selected_band - 1)
                st.session_state.preprocessed_image = preprocessed_img
                
                # Show band info if available
                if bands and len(bands) >= selected_band:
                    st.info(f"Band {selected_band}: {bands[selected_band - 1]}")
            else:
                # For non-GeoTIFF or single-band GeoTIFF
                preprocessed_img = image_processor.preprocess_image(image_data)
                st.session_state.preprocessed_image = preprocessed_img
                st.session_state.selected_band = 0
            
            # Compute FFT if we have a preprocessed image
            if st.session_state.preprocessed_image is not None:
                fft_shifted, fft_magnitude = utils.compute_fft(st.session_state.preprocessed_image)
                st.session_state.fft_shifted = fft_shifted
                st.session_state.fft_magnitude = fft_magnitude
            
            # Display image info
            img_height, img_width = st.session_state.preprocessed_image.shape
            st.session_state.img_info = {
                "width": img_width,
                "height": img_height,
                "type": "GeoTIFF" if is_geotiff else uploaded_file.type,
                "size_kb": round(len(uploaded_file.getvalue()) / 1024, 2)
            }
            
            # Show image info
            st.subheader("Image Information")
            st.write(f"Dimensions: {img_width} x {img_height}")
            st.write(f"Type: {st.session_state.img_info['type']}")
            st.write(f"Size: {st.session_state.img_info['size_kb']} KB")
            
            # Filter selection
            st.subheader("Filter Selection")
            filter_type = st.radio(
                "Select filter type:",
                ["Low-pass", "High-pass", "Band-stop"]
            )
            
            # Filter parameters
            st.subheader("Filter Parameters")
            
            # Get the smaller dimension for setting max radius
            min_dim = min(img_height, img_width) // 2
            
            # Different sliders based on filter type
            if filter_type == "Low-pass":
                cutoff_radius = st.slider(
                    "Cutoff radius:", 
                    1, min_dim, min_dim // 4,
                    help="Frequencies below this radius will be preserved"
                )
                gaussian_tapering = st.checkbox("Apply Gaussian tapering", 
                                               value=True,
                                               help="Smooths the filter transition to reduce ringing artifacts")
                filter_params = {
                    "type": filter_type,
                    "cutoff_radius": cutoff_radius,
                    "gaussian_tapering": gaussian_tapering
                }
            
            elif filter_type == "High-pass":
                cutoff_radius = st.slider(
                    "Cutoff radius:", 
                    1, min_dim, min_dim // 4,
                    help="Frequencies above this radius will be preserved"
                )
                gaussian_tapering = st.checkbox("Apply Gaussian tapering", 
                                               value=True,
                                               help="Smooths the filter transition to reduce ringing artifacts")
                filter_params = {
                    "type": filter_type,
                    "cutoff_radius": cutoff_radius,
                    "gaussian_tapering": gaussian_tapering
                }
            
            else:  # Band-stop
                inner_radius = st.slider(
                    "Inner radius:", 
                    1, min_dim - 1, min_dim // 8,
                    help="Inner boundary of the band to be removed"
                )
                outer_radius = st.slider(
                    "Outer radius:", 
                    inner_radius + 1, min_dim, min_dim // 3,
                    help="Outer boundary of the band to be removed"
                )
                gaussian_tapering = st.checkbox("Apply Gaussian tapering", 
                                               value=True,
                                               help="Smooths the filter transition to reduce ringing artifacts")
                filter_params = {
                    "type": filter_type,
                    "inner_radius": inner_radius,
                    "outer_radius": outer_radius,
                    "gaussian_tapering": gaussian_tapering
                }
            
            # Create filter mask
            if st.session_state.fft_shifted is not None:
                filter_mask = filters.create_filter_mask(
                    st.session_state.fft_shifted.shape,
                    filter_params
                )
                
                # Apply filter and perform inverse FFT
                filtered_img = filters.apply_filter(
                    st.session_state.fft_shifted,
                    filter_mask
                )
                
                # Store the filtered image and filter parameters
                st.session_state.filtered_image = filtered_img
                st.session_state.last_filter_params = filter_params
            
            # Advanced Options Expander
            with st.expander("Advanced Options"):
                if st.session_state.is_geotiff and len(st.session_state.bands) >= 4:
                    if st.button("Compute NDVI"):
                        red_band = image_processor.extract_band(st.session_state.original_image, 2)  # Typically band 3
                        nir_band = image_processor.extract_band(st.session_state.original_image, 3)  # Typically band 4
                        st.session_state.filtered_image = ndvi.compute_ndvi(red_band, nir_band)
                        st.info("NDVI computation complete!")
                
                if st.button("Apply Texture Classification"):
                    if st.session_state.preprocessed_image is not None:
                        st.session_state.filtered_image = classification.texture_classification(
                            st.session_state.preprocessed_image
                        )
                        st.info("Texture classification complete!")
                
                # Geo-referenced overlay is only applicable for GeoTIFF
                if st.session_state.is_geotiff:
                    st.write("Map overlay functionality available for GeoTIFF")
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

# Main content area
if st.session_state.preprocessed_image is not None:
    # Create three columns for side-by-side comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Original Image")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(st.session_state.preprocessed_image, cmap='gray')
        ax.axis('off')
        st.pyplot(fig)
        
        if st.session_state.is_geotiff and st.session_state.selected_band > 0:
            st.caption(f"Band {st.session_state.selected_band}")
    
    with col2:
        st.subheader("FFT Spectrum")
        if st.session_state.fft_magnitude is not None:
            fig, ax = plt.subplots(figsize=(5, 5))
            im = ax.imshow(st.session_state.fft_magnitude, cmap='viridis')
            ax.axis('off')
            fig.colorbar(im, ax=ax, shrink=0.8)
            st.pyplot(fig)
            
            # Add explanation
            st.caption("Brighter areas indicate stronger frequency components")
    
    with col3:
        st.subheader("Filtered Result")
        if st.session_state.filtered_image is not None:
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.imshow(st.session_state.filtered_image, cmap='gray')
            ax.axis('off')
            st.pyplot(fig)
            
            # Add filter info
            if 'type' in st.session_state.last_filter_params:
                filter_info = f"Filter: {st.session_state.last_filter_params['type']}"
                st.caption(filter_info)
            
            # Download button
            if st.button("Download Filtered Image"):
                # Convert filtered image to bytes
                filtered_pil = Image.fromarray(
                    (st.session_state.filtered_image * 255).astype(np.uint8)
                )
                buf = io.BytesIO()
                filtered_pil.save(buf, format='PNG')
                btn = st.download_button(
                    label="Download PNG",
                    data=buf.getvalue(),
                    file_name="filtered_image.png",
                    mime="image/png"
                )
else:
    # Display instructions when no image is uploaded
    st.info("👈 Please upload an image using the sidebar to begin analysis.")
    
    # Add explanations about the app
    st.markdown("""
    ## About this tool
    
    This Remote Sensing Data Analyzer allows you to:
    
    1. **Upload** satellite imagery in various formats (JPG, PNG, GeoTIFF)
    2. **Visualize** the frequency-domain representation using Fourier Transforms
    3. **Apply** customizable filters to highlight or suppress spatial features
    4. **Compare** original and processed images side-by-side
    5. **Download** filtered images for further analysis
    
    ### How Frequency-Domain Filtering Works
    
    Frequency-domain analysis transforms an image from its spatial representation (pixel values) 
    into its frequency components using the Fast Fourier Transform (FFT). This allows for:
    
    - **Low-pass filtering**: Preserves smooth areas by keeping low frequencies (reduces noise)
    - **High-pass filtering**: Emphasizes edges and fine details by keeping high frequencies
    - **Band-stop filtering**: Removes specific frequency bands (useful for removing periodic noise)
    
    ### Tips for Effective Analysis
    
    - Start with a clear, high-contrast image for best results
    - Try different filter types to see which best highlights your features of interest
    - For GeoTIFF files, experiment with different spectral bands
    """)

# Footer
st.markdown("---")
st.markdown("Remote Sensing Data Analyzer with Frequency-Domain Filtering | A tool for environmental scientists and GIS analysts")
