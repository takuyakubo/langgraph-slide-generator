"""
Data models for the LangGraph Slide Generator.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ProcessingStatus(str, Enum):
    """Processing status enum."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BoundingBox(BaseModel):
    """Bounding box for text or elements in an image."""
    x: int
    y: int
    width: int
    height: int

class TextBox(BaseModel):
    """Detected text box in an image."""
    text: str
    bbox: BoundingBox
    confidence: float
    text_type: str = "regular"  # regular, heading, list, etc.

class MathExpression(BaseModel):
    """Detected math expression in an image."""
    expression: str
    latex: Optional[str] = None
    bbox: BoundingBox
    confidence: float

class ImageMetadata(BaseModel):
    """Metadata for a processed image."""
    image_id: str
    original_width: int
    original_height: int
    processed_width: Optional[int] = None
    processed_height: Optional[int] = None
    file_name: Optional[str] = None
    format: Optional[str] = None
    dpi: Optional[int] = None

class ExtractedText(BaseModel):
    """Text extracted from an image."""
    text_boxes: List[TextBox] = Field(default_factory=list)
    math_expressions: List[MathExpression] = Field(default_factory=list)
    raw_text: str = ""
    language: str = "ja"
    confidence: float = 0.0

class ContentElement(BaseModel):
    """Base class for content elements."""
    element_type: str
    content: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ContentSection(BaseModel):
    """Section in the content structure."""
    level: int
    title: Optional[str] = None
    elements: List[ContentElement] = Field(default_factory=list)
    subsections: List["ContentSection"] = Field(default_factory=list)

class ContentStructure(BaseModel):
    """Overall content structure."""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    sections: List[ContentSection] = Field(default_factory=list)

class SlideElement(BaseModel):
    """Element in a slide."""
    element_type: str
    content: str
    style: Dict[str, str] = Field(default_factory=dict)
    attributes: Dict[str, Any] = Field(default_factory=dict)

class SlideDefinition(BaseModel):
    """Definition of a single slide."""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    type: str = "content"  # cover, toc, content, divider
    elements: List[SlideElement] = Field(default_factory=list)
    style: Dict[str, str] = Field(default_factory=dict)

class ProcessingState(BaseModel):
    """State for the processing workflow."""
    job_id: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    images: List[bytes] = Field(default_factory=list)
    image_metadata: List[ImageMetadata] = Field(default_factory=list)
    extracted_text: List[ExtractedText] = Field(default_factory=list)
    content_structure: Optional[ContentStructure] = None
    slide_definitions: List[SlideDefinition] = Field(default_factory=list)
    html_output: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    progress: int = 0
    options: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

# Import cycle handling
ContentSection.update_forward_refs()
