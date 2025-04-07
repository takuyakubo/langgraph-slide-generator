"""
LangGraph Slide Generator exception hierarchy.
"""

class SlideGeneratorError(Exception):
    """Base exception class for the application."""
    
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}

class ImageProcessingError(SlideGeneratorError):
    """Error during image processing."""
    pass

class OCRError(ImageProcessingError):
    """Error during OCR processing."""
    
    def __init__(self, message, image_id=None, details=None):
        super().__init__(message, details)
        self.image_id = image_id

class ImagePreprocessingError(ImageProcessingError):
    """Error during image preprocessing."""
    pass

class StructureAnalysisError(ImageProcessingError):
    """Error during structure analysis."""
    pass

class LLMProcessingError(SlideGeneratorError):
    """Error during LLM processing."""
    pass

class LLMConnectionError(LLMProcessingError):
    """Error connecting to the LLM service."""
    pass

class LLMResponseError(LLMProcessingError):
    """Error with the LLM response."""
    pass

class ContentAnalysisError(LLMProcessingError):
    """Error during content analysis."""
    pass

class HTMLGenerationError(SlideGeneratorError):
    """Error during HTML generation."""
    pass

class TemplateRenderingError(HTMLGenerationError):
    """Error during template rendering."""
    pass

class StyleProcessingError(HTMLGenerationError):
    """Error during style processing."""
    pass

class MathRenderingError(HTMLGenerationError):
    """Error during math rendering."""
    pass

class APIError(SlideGeneratorError):
    """API-related error."""
    
    def __init__(self, message, status_code=500, details=None):
        super().__init__(message, details)
        self.status_code = status_code

class AuthenticationError(APIError):
    """Authentication error."""
    
    def __init__(self, message="Authentication failed", details=None):
        super().__init__(message, 401, details)

class ValidationError(APIError):
    """Validation error."""
    
    def __init__(self, message="Validation failed", details=None):
        super().__init__(message, 400, details)

class ResourceNotFoundError(APIError):
    """Resource not found error."""
    
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, 404, details)
