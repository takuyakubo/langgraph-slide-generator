"""
Layout analysis module for detecting document structure.
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging

from ..models import TextBox, BoundingBox, ExtractedText
from ..exceptions import StructureAnalysisError
from ..utils.error_handling import error_handling

logger = logging.getLogger(__name__)

def analyze_layout(
    image: np.ndarray,
    extracted_text: ExtractedText,
    options: Optional[Dict[str, Any]] = None
) -> ExtractedText:
    """
    Analyze the layout of the document to identify structural elements.
    
    Args:
        image: Preprocessed image as numpy array
        extracted_text: Previously extracted text data
        options: Layout analysis options
        
    Returns:
        Updated ExtractedText with structural information
        
    Raises:
        StructureAnalysisError: If layout analysis fails
    """
    options = options or {}
    
    with error_handling(StructureAnalysisError, "Layout analysis failed"):
        # Identify headings and structural elements
        extracted_text = identify_headings(extracted_text, options)
        
        # Identify paragraphs and text blocks
        extracted_text = identify_paragraphs(extracted_text, options)
        
        # Identify list items
        extracted_text = identify_list_items(extracted_text, options)
        
        # Return updated extracted text
        return extracted_text

def identify_headings(
    extracted_text: ExtractedText, 
    options: Dict[str, Any]
) -> ExtractedText:
    """
    Identify headings in the extracted text based on size and position.
    
    Args:
        extracted_text: Extracted text data
        options: Heading identification options
        
    Returns:
        Updated ExtractedText with heading information
    """
    # Copy text boxes to avoid modifying the original list while iterating
    text_boxes = extracted_text.text_boxes.copy()
    
    # Sort text boxes by y-coordinate (top to bottom)
    sorted_boxes = sorted(text_boxes, key=lambda box: box.bbox.y)
    
    if not sorted_boxes:
        return extracted_text
    
    # Get average height and font size to compare
    heights = [box.bbox.height for box in sorted_boxes]
    avg_height = sum(heights) / len(heights)
    
    # Threshold for heading detection (configurable)
    heading_size_threshold = options.get('heading_size_threshold', 1.3)
    
    # Update text boxes with heading information
    updated_boxes = []
    for box in sorted_boxes:
        if box.bbox.height > avg_height * heading_size_threshold:
            # This is likely a heading
            if is_title_or_heading(box, sorted_boxes, avg_height):
                box.text_type = "heading"
        
        updated_boxes.append(box)
    
    # Update extracted text with new text box information
    extracted_text.text_boxes = updated_boxes
    return extracted_text

def identify_paragraphs(
    extracted_text: ExtractedText, 
    options: Dict[str, Any]
) -> ExtractedText:
    """
    Identify paragraphs and text blocks in the extracted text.
    
    Args:
        extracted_text: Extracted text data
        options: Paragraph identification options
        
    Returns:
        Updated ExtractedText with paragraph information
    """
    # Sort text boxes by y-coordinate (top to bottom)
    sorted_boxes = sorted(extracted_text.text_boxes, key=lambda box: box.bbox.y)
    
    if not sorted_boxes:
        return extracted_text
    
    # Group text boxes into paragraphs based on y-coordinate proximity
    paragraph_threshold = options.get('paragraph_threshold', 1.5)  # Configurable
    
    current_paragraph = []
    paragraphs = []
    
    # Average line height calculation
    line_heights = [box.bbox.height for box in sorted_boxes]
    avg_line_height = sum(line_heights) / len(line_heights) if line_heights else 0
    
    for i, box in enumerate(sorted_boxes):
        if not current_paragraph:
            current_paragraph.append(box)
        else:
            prev_box = current_paragraph[-1]
            
            # Check if this box is within the paragraph threshold
            y_distance = box.bbox.y - (prev_box.bbox.y + prev_box.bbox.height)
            
            if y_distance <= avg_line_height * paragraph_threshold:
                # This box belongs to the current paragraph
                current_paragraph.append(box)
            else:
                # This box starts a new paragraph
                paragraphs.append(current_paragraph)
                current_paragraph = [box]
    
    # Add the last paragraph
    if current_paragraph:
        paragraphs.append(current_paragraph)
    
    # Update text types for boxes in paragraphs
    updated_boxes = []
    for paragraph in paragraphs:
        # First box in paragraph
        if paragraph[0].text_type != "heading":
            paragraph[0].text_type = "paragraph_start"
            
        # Middle boxes in paragraph
        for box in paragraph[1:]:
            if box.text_type != "heading":
                box.text_type = "paragraph_content"
        
        updated_boxes.extend(paragraph)
    
    # Update extracted text with new text box information
    extracted_text.text_boxes = updated_boxes
    return extracted_text

def identify_list_items(
    extracted_text: ExtractedText, 
    options: Dict[str, Any]
) -> ExtractedText:
    """
    Identify list items in the extracted text.
    
    Args:
        extracted_text: Extracted text data
        options: List item identification options
        
    Returns:
        Updated ExtractedText with list item information
    """
    text_boxes = extracted_text.text_boxes.copy()
    updated_boxes = []
    
    # List marker patterns
    list_markers = [
        r'^\s*[\•\-\*]\s+',  # Bullet points
        r'^\s*\d+[\.\)]\s+',  # Numbered list
        r'^\s*[a-zA-Z][\.\)]\s+',  # Alphabetic list
        r'^\s*[(（][a-zA-Z0-9一二三四五六七八九十１２３４５６７８９０]+[)）]\s+',  # Parenthesized markers
    ]
    
    import re
    for box in text_boxes:
        # Check if this box starts with a list marker
        for marker_pattern in list_markers:
            if re.match(marker_pattern, box.text):
                box.text_type = "list_item"
                break
        
        updated_boxes.append(box)
    
    # Update extracted text with new text box information
    extracted_text.text_boxes = updated_boxes
    return extracted_text

def is_title_or_heading(
    box: TextBox, 
    all_boxes: List[TextBox], 
    avg_height: float
) -> bool:
    """
    Determine if a text box is a title or heading based on position and size.
    
    Args:
        box: Text box to check
        all_boxes: All text boxes in the document
        avg_height: Average text box height
        
    Returns:
        True if the box is likely a title or heading, False otherwise
    """
    # Check if this is at the top of the page (likely title)
    is_at_top = box.bbox.y < avg_height * 3
    
    # Check if this is significantly larger than average
    is_large = box.bbox.height > avg_height * 1.5
    
    # Check if this is followed by normal text (context indicates heading)
    is_followed_by_normal_text = False
    box_bottom = box.bbox.y + box.bbox.height
    
    for other_box in all_boxes:
        if other_box is box:
            continue
            
        if (other_box.bbox.y > box_bottom and 
            other_box.bbox.height <= avg_height * 1.2):
            is_followed_by_normal_text = True
            break
    
    # Check if this has few words (headings tend to be short)
    is_short = len(box.text.split()) <= 10
    
    # Combine these heuristics
    return (is_at_top or is_large) and (is_followed_by_normal_text or is_short)
