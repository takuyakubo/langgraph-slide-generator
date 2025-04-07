"""
Image preprocessing module for slide generator.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any

from ..models import ImageMetadata
from ..exceptions import ImagePreprocessingError
from ..utils.error_handling import error_handling

def preprocess_image(
    image_data: bytes, 
    options: Optional[Dict[str, Any]] = None
) -> Tuple[np.ndarray, ImageMetadata]:
    """
    Preprocess the image for optimal OCR and layout analysis.
    
    Args:
        image_data: Raw image data bytes
        options: Preprocessing options
        
    Returns:
        Tuple of preprocessed image and image metadata
        
    Raises:
        ImagePreprocessingError: If image preprocessing fails
    """
    options = options or {}
    
    with error_handling(ImagePreprocessingError, "Failed to preprocess image"):
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ImagePreprocessingError("Failed to decode image data")
        
        # Create image metadata
        original_height, original_width = image.shape[:2]
        image_id = generate_image_id()
        metadata = ImageMetadata(
            image_id=image_id,
            original_width=original_width,
            original_height=original_height
        )
        
        # Apply preprocessing steps
        processed_image = apply_preprocessing(image, options)
        
        # Update metadata with processed dimensions
        processed_height, processed_width = processed_image.shape[:2]
        metadata.processed_width = processed_width
        metadata.processed_height = processed_height
        
        return processed_image, metadata

def apply_preprocessing(image: np.ndarray, options: Dict[str, Any]) -> np.ndarray:
    """
    Apply various preprocessing techniques to improve OCR quality.
    
    Args:
        image: Input image as numpy array
        options: Preprocessing options
        
    Returns:
        Preprocessed image
    """
    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Noise removal with Gaussian blur if specified
    if options.get('denoise', True):
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Binarization with adaptive thresholding
    if options.get('binarize', True):
        binary = cv2.adaptiveThreshold(
            gray, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 
            2
        )
    else:
        binary = gray
    
    # Deskew if specified
    if options.get('deskew', True):
        binary = deskew_image(binary)
    
    # Remove borders if specified
    if options.get('remove_borders', False):
        binary = remove_borders(binary)
    
    # Resize if specified
    if 'resize_factor' in options:
        factor = float(options['resize_factor'])
        if factor != 1.0:
            new_width = int(binary.shape[1] * factor)
            new_height = int(binary.shape[0] * factor)
            binary = cv2.resize(binary, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    return binary

def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Deskew (straighten) an image.
    
    Args:
        image: Input image
        
    Returns:
        Deskewed image
    """
    # Find all non-zero points
    coords = np.column_stack(np.where(image > 0))
    
    # Get rotated rectangle
    if len(coords) <= 10:  # Not enough points to compute angle
        return image
        
    angle = cv2.minAreaRect(coords)[-1]
    
    # Adjust the angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    # Rotate the image to deskew it
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )
    
    return rotated

def remove_borders(image: np.ndarray) -> np.ndarray:
    """
    Remove borders/edges from the image.
    
    Args:
        image: Input image
        
    Returns:
        Image with borders removed
    """
    # Get contours
    contours, hierarchy = cv2.findContours(
        ~image,  # Invert for finding outer contours
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    # Calculate bounding boxes and find largest area
    if not contours:
        return image
        
    # Get bounding rectangle for all contours
    rects = [cv2.boundingRect(c) for c in contours]
    
    # Find the largest rectangle by area
    largest_rect = max(rects, key=lambda r: r[2] * r[3])
    x, y, w, h = largest_rect
    
    # Crop the image
    return image[y:y+h, x:x+w]

def generate_image_id() -> str:
    """
    Generate a unique ID for the image.
    
    Returns:
        Unique image ID
    """
    import uuid
    import time
    
    # Create a time-based UUID (version 1)
    return f"img_{uuid.uuid1().hex}"
