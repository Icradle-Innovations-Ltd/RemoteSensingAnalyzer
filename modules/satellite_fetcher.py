"""
Satellite Fetcher module for the Remote Sensing Data Analyzer
Contains functions to fetch satellite imagery from various sources
"""

import os
import re
import datetime
import tempfile
from pathlib import Path
import numpy as np
import rasterio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for Earth Engine API credentials
have_earthengine = False
try:
    import ee
    ee_user = os.environ.get('EARTHENGINE_USER')
    ee_password = os.environ.get('EARTHENGINE_PASSWORD')
    if ee_user and ee_password and ee_user != "your_earthengine_user_here":
        have_earthengine = True
except ImportError:
    pass

# Check for SentinelSat API credentials
have_sentinelsat = False
try:
    from sentinelsat import SentinelAPI
    sentinel_user = os.environ.get('SENTINEL_USER')
    sentinel_password = os.environ.get('SENTINEL_PASSWORD')
    if sentinel_user and sentinel_password and sentinel_user != "your_sentinel_user_here":
        have_sentinelsat = True
except ImportError:
    pass

def get_available_sources():
    """
    Get list of available satellite imagery sources based on configured credentials
    """
    sources = []
    if have_earthengine:
        sources.append("Google Earth Engine")
    if have_sentinelsat:
        sources.append("Sentinel Hub")
    return sources

def initialize_apis():
    """
    Initialize APIs for satellite imagery retrieval
    """
    apis = {}
    
    # Initialize Earth Engine API if credentials are available
    if have_earthengine:
        try:
            ee.Initialize()
            apis['earth_engine'] = "initialized"
        except Exception as e:
            apis['earth_engine'] = f"error: {str(e)}"
    
    # Initialize SentinelSat API if credentials are available
    if have_sentinelsat:
        try:
            api = SentinelAPI(sentinel_user, sentinel_password, 'https://apihub.copernicus.eu/apihub')
            apis['sentinel'] = api
        except Exception as e:
            apis['sentinel'] = f"error: {str(e)}"
    
    return apis

def search_sentinel_images(location, date_range, cloud_cover_limit=20):
    """
    Search for Sentinel-2 satellite images based on location and date range
    
    Parameters:
    ----------
    location : dict
        Dictionary with 'lat', 'lon' keys for the center coordinates
    date_range : dict
        Dictionary with 'start' and 'end' dates (YYYY-MM-DD format)
    cloud_cover_limit : int
        Maximum cloud cover percentage (0-100)
    
    Returns:
    -------
    results : list
        List of dictionaries with image metadata
    """
    if not have_sentinelsat:
        return {'error': 'Sentinel API credentials not configured'}
    
    try:
        # Initialize the Sentinel API
        api = SentinelAPI(sentinel_user, sentinel_password, 'https://apihub.copernicus.eu/apihub')
        
        # Parse date range
        start_date = datetime.datetime.strptime(date_range['start'], '%Y-%m-%d')
        end_date = datetime.datetime.strptime(date_range['end'], '%Y-%m-%d')
        
        # Create a point for the location
        from shapely.geometry import Point
        point = Point(location['lon'], location['lat'])
        
        # Search for Sentinel-2 products
        products = api.query(
            area=point.buffer(0.1),  # Buffer the point for a small area search
            date=(start_date, end_date),
            platformname='Sentinel-2',
            cloudcoverpercentage=(0, cloud_cover_limit)
        )
        
        # Convert to list of dictionaries
        results = []
        for product_id, product_info in products.items():
            results.append({
                'id': product_id,
                'title': product_info['title'],
                'date': product_info['beginposition'].strftime('%Y-%m-%d'),
                'cloud_cover': product_info['cloudcoverpercentage'],
                'download_size_mb': product_info['size'] / (1024 * 1024),
                'preview_url': api.get_product_odata(product_id)['url']
            })
        
        return results
    
    except Exception as e:
        return {'error': f'Error searching Sentinel images: {str(e)}'}

def download_sentinel_image(product_id):
    """
    Download a Sentinel-2 image by product ID
    
    Parameters:
    ----------
    product_id : str
        Sentinel product ID
    
    Returns:
    -------
    image_path : str
        Path to downloaded image
    """
    if not have_sentinelsat:
        return {'error': 'Sentinel API credentials not configured'}
    
    try:
        # Initialize the Sentinel API
        api = SentinelAPI(sentinel_user, sentinel_password, 'https://apihub.copernicus.eu/apihub')
        
        # Create a temporary directory for the download
        temp_dir = tempfile.mkdtemp()
        
        # Download the product
        download_path = api.download(product_id, directory_path=temp_dir)
        
        return {'path': download_path}
    
    except Exception as e:
        return {'error': f'Error downloading Sentinel image: {str(e)}'}

def get_earth_engine_image(location, date_range, dataset='LANDSAT/LC08/C02/T1_TOA'):
    """
    Get a satellite image from Google Earth Engine
    
    Parameters:
    ----------
    location : dict
        Dictionary with 'lat', 'lon' keys for the center coordinates
    date_range : dict
        Dictionary with 'start' and 'end' dates (YYYY-MM-DD format)
    dataset : str
        Earth Engine dataset ID
    
    Returns:
    -------
    image_data : dict
        Dictionary with image data and metadata
    """
    if not have_earthengine:
        return {'error': 'Earth Engine API credentials not configured'}
    
    try:
        # Initialize Earth Engine
        ee.Initialize()
        
        # Parse date range
        start_date = date_range['start']
        end_date = date_range['end']
        
        # Create a point for the location
        point = ee.Geometry.Point([location['lon'], location['lat']])
        
        # Buffer the point to create a region (1km buffer)
        region = point.buffer(1000)
        
        # Get the image collection
        collection = ee.ImageCollection(dataset) \
            .filterDate(start_date, end_date) \
            .filterBounds(region)
        
        # Sort by cloud cover and get the least cloudy image
        if dataset.startswith('LANDSAT'):
            collection = collection.sort('CLOUD_COVER')
        elif dataset.startswith('COPERNICUS/S2'):
            collection = collection.sort('CLOUDY_PIXEL_PERCENTAGE')
        
        # Get the first (least cloudy) image
        image = collection.first()
        
        if image is None:
            return {'error': 'No images found for the specified criteria'}
        
        # Get image properties
        image_id = image.get('system:id').getInfo()
        date = image.date().format('YYYY-MM-dd').getInfo()
        
        # Select visible bands (for Landsat 8, these are 4,3,2 for RGB)
        if dataset == 'LANDSAT/LC08/C02/T1_TOA':
            visible_image = image.select(['B4', 'B3', 'B2'])
            band_names = ['B4 (Red)', 'B3 (Green)', 'B2 (Blue)']
        elif dataset.startswith('COPERNICUS/S2'):
            visible_image = image.select(['B4', 'B3', 'B2'])
            band_names = ['B4 (Red)', 'B3 (Green)', 'B2 (Blue)']
        else:
            # Use default band selection
            visible_image = image.select(0, 1, 2)
            band_names = ['Band 1', 'Band 2', 'Band 3']
        
        # Export the image to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
        temp_file.close()
        
        # Create export parameters
        export_params = {
            'image': visible_image,
            'description': 'export_image',
            'fileNamePrefix': Path(temp_file.name).stem,
            'region': region,
            'scale': 30,  # 30m resolution for Landsat, 10m for Sentinel-2
            'crs': 'EPSG:4326',
            'fileFormat': 'GeoTIFF'
        }
        
        # Start the export task
        task = ee.batch.Export.image.toDrive(**export_params)
        task.start()
        
        # Wait for the export to complete
        while task.status()['state'] in ['READY', 'RUNNING']:
            import time
            time.sleep(5)
        
        # Check if export completed successfully
        if task.status()['state'] != 'COMPLETED':
            return {'error': f'Export failed: {task.status()}'}
        
        # Return image metadata
        return {
            'id': image_id,
            'date': date,
            'path': temp_file.name,
            'bands': band_names,
            'dataset': dataset,
            'region': region.getInfo()
        }
    
    except Exception as e:
        return {'error': f'Error accessing Earth Engine: {str(e)}'}

def load_satellite_image(image_info):
    """
    Load a satellite image from a file path or URL
    
    Parameters:
    ----------
    image_info : dict
        Dictionary with image information including path
    
    Returns:
    -------
    image_data : ndarray
        Image data as a numpy array
    metadata : dict
        Image metadata
    """
    try:
        # Check if image path exists
        if 'path' not in image_info or not os.path.exists(image_info['path']):
            return None, {'error': 'Image file not found'}
        
        # Open the image with rasterio
        with rasterio.open(image_info['path']) as src:
            # Read all bands
            data = src.read()
            
            # Get metadata
            metadata = {
                'driver': src.driver,
                'width': src.width,
                'height': src.height,
                'count': src.count,
                'crs': src.crs.to_string() if src.crs else None,
                'bounds': src.bounds,
                'transform': src.transform
            }
            
            # Normalize and convert to numpy array
            image_data = np.transpose(data, (1, 2, 0))  # Reshape to height x width x bands
            
            return image_data, metadata
    
    except Exception as e:
        return None, {'error': f'Error loading satellite image: {str(e)}'}