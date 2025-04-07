"""
OCR module for extracting text from images.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import pytesseract
import logging

from ..models import TextBox, BoundingBox, ExtractedText
from ..exceptions import OCRError
from ..utils.error_handling import error_handling, retry

logger = logging.getLogger(__name__)

@retry(max_attempts=2, exceptions=(OCRError,))
def extract_text(
    image: np.ndarray,
    image_id: str,
    options: Optional[Dict[str, Any]] = None
) -> ExtractedText:
    """
    Extract text from an image using OCR.
    
    Args:
        image: Preprocessed image as numpy array
        image_id: Unique identifier for the image
        options: OCR options
        
    Returns:
        ExtractedText object with detected text
        
    Raises:
        OCRError: If OCR processing fails
    """
    options = options or {}
    
    with error_handling(OCRError, f"OCR failed for image {image_id}"):
        # Convert numpy array to PIL image for tesseract
        pil_image = Image.fromarray(image)
        
        # Set language based on options, default to Japanese
        lang = options.get('language', 'jpn+eng')
        
        # Configure OCR options
        config = build_tesseract_config(options)
        
        # Perform OCR to get data
        ocr_data = pytesseract.image_to_data(
            pil_image, 
            lang=lang,
            config=config,
            output_type=pytesseract.Output.DICT
        )
        
        # Get text boxes from OCR data
        text_boxes = extract_text_boxes(ocr_data)
        
        # Get raw text from OCR data
        raw_text = " ".join([box.text for box in text_boxes if box.text.strip()])
        
        # Calculate average confidence
        confidences = [box.confidence for box in text_boxes if box.confidence > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Create and return ExtractedText object
        return ExtractedText(
            text_boxes=text_boxes,
            raw_text=raw_text,
            language=lang.split('+')[0],  # Use primary language
            confidence=avg_confidence
        )

def build_tesseract_config(options: Dict[str, Any]) -> str:
    """
    Build tesseract configuration string from options.
    
    Args:
        options: OCR options
        
    Returns:
        Tesseract configuration string
    """
    config_parts = []
    
    # OCR engine mode
    # 0 = Original Tesseract only
    # 1 = Neural nets LSTM only
    # 2 = Tesseract + LSTM
    # 3 = Default, based on what is available
    ocr_engine_mode = options.get('ocr_engine_mode', 1)  # Default to LSTM only for better Japanese support
    config_parts.append(f'--oem {ocr_engine_mode}')
    
    # Page segmentation mode
    # 0 = Orientation and script detection (OSD) only
    # 1 = Automatic page segmentation with OSD
    # 3 = Fully automatic page segmentation, but no OSD (Default)
    # 4 = Assume a single column of text of variable sizes
    # 6 = Assume a single uniform block of text
    # 11 = Sparse text. Find as much text as possible in no particular order
    psm = options.get('page_segmentation_mode', 3)
    config_parts.append(f'--psm {psm}')
    
    # Additional options
    if options.get('enable_japanese_vertical', False):
        config_parts.append('-c "textord_direction_flag=1"')
    
    if options.get('preserve_interword_spaces', True):
        config_parts.append('-c "preserve_interword_spaces=1"')
    
    # Join all config parts
    return ' '.join(config_parts)

def extract_text_boxes(ocr_data: Dict[str, Any]) -> List[TextBox]:
    """
    Extract text boxes from OCR data.
    
    Args:
        ocr_data: OCR data dictionary from pytesseract
        
    Returns:
        List of TextBox objects
    """
    text_boxes = []
    
    n_boxes = len(ocr_data['text'])
    for i in range(n_boxes):
        # Skip empty text
        if int(ocr_data['conf'][i]) < 0 or not ocr_data['text'][i].strip():
            continue
            
        # Create bounding box
        bbox = BoundingBox(
            x=ocr_data['left'][i],
            y=ocr_data['top'][i],
            width=ocr_data['width'][i],
            height=ocr_data['height'][i]
        )
        
        # Determine text type based on level
        text_type = "regular"
        if ocr_data['level'][i] == 2:  # Paragraph
            text_type = "paragraph"
        elif ocr_data['level'][i] == 3:  # Line
            text_type = "line"
        elif ocr_data['level'][i] == 4:  # Word
            text_type = "word"
        
        # Create text box
        text_box = TextBox(
            text=ocr_data['text'][i],
            bbox=bbox,
            confidence=float(ocr_data['conf'][i]),
            text_type=text_type
        )
        
        text_boxes.append(text_box)
    
    return text_boxes

def use_alternative_ocr(
    image: np.ndarray,
    image_id: str,
    options: Optional[Dict[str, Any]] = None
) -> ExtractedText:
    """
    Use an alternative OCR engine (EasyOCR) as a fallback.
    
    Args:
        image: Preprocessed image as numpy array
        image_id: Unique identifier for the image
        options: OCR options
        
    Returns:
        ExtractedText object with detected text
    """
    try:
        import easyocr
        
        # Initialize EasyOCR reader
        lang_list = ['ja', 'en']
        reader = easyocr.Reader(lang_list)
        
        # Perform OCR
        results = reader.readtext(image)
        
        # Convert to our data format
        text_boxes = []
        for (bbox, text, confidence) in results:
            # EasyOCR returns bbox as [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
            x1, y1 = bbox[0]
            x2, y2 = bbox[2]
            
            text_box = TextBox(
                text=text,
                bbox=BoundingBox(
                    x=int(x1),
                    y=int(y1),
                    width=int(x2 - x1),
                    height=int(y2 - y1)
                ),
                confidence=float(confidence),
                text_type="line"
            )
            text_boxes.append(text_box)
        
        # Create ExtractedText object
        raw_text = " ".join([box.text for box in text_boxes if box.text.strip()])
        avg_confidence = sum([box.confidence for box in text_boxes]) / len(text_boxes) if text_boxes else 0.0
        
        return ExtractedText(
            text_boxes=text_boxes,
            raw_text=raw_text,
            language='ja',  # Default to Japanese
            confidence=avg_confidence
        )
    except ImportError:
        logger.error("EasyOCR not installed, can't use alternative OCR")
        raise OCRError(f"Alternative OCR failed for image {image_id}: EasyOCR not installed")
    except Exception as e:
        logger.error(f"Alternative OCR failed: {str(e)}")
        raise OCRError(f"Alternative OCR failed for image {image_id}: {str(e)}")
