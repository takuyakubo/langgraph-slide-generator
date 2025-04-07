"""
Structure detection module for identifying hierarchical relationships in content.
"""

import logging
from typing import Dict, Any, List, Optional

from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from ..models import ContentStructure
from ..exceptions import ContentAnalysisError
from ..utils.error_handling import error_handling

logger = logging.getLogger(__name__)

def detect_structure(
    content_structure: ContentStructure,
    options: Optional[Dict[str, Any]] = None
) -> ContentStructure:
    """
    Detect hierarchical structure in content.
    
    This function enhances the existing ContentStructure by refining the
    hierarchical relationships between sections.
    
    Args:
        content_structure: Initial content structure
        options: Structure detection options
        
    Returns:
        Enhanced ContentStructure with refined hierarchical relationships
        
    Raises:
        ContentAnalysisError: If structure detection fails
    """
    options = options or {}
    
    with error_handling(ContentAnalysisError, "Failed to detect structure"):
        # Apply structure detection methods
        content_structure = refine_section_hierarchy(content_structure, options)
        
        # Validate and fix inconsistencies
        content_structure = validate_structure(content_structure)
        
        return content_structure

def refine_section_hierarchy(
    content_structure: ContentStructure,
    options: Dict[str, Any]
) -> ContentStructure:
    """
    Refine the hierarchical relationships between sections.
    
    Args:
        content_structure: Content structure to refine
        options: Refinement options
        
    Returns:
        Refined content structure
    """
    # Create a copy to avoid modifying the input during processing
    refined = ContentStructure(
        title=content_structure.title,
        subtitle=content_structure.subtitle,
        sections=content_structure.sections.copy()
    )
    
    # Ensure section levels are consistent
    normalize_section_levels(refined)
    
    # Re-organize subsections based on level
    reorganize_sections(refined)
    
    # Use LLM to refine relationships if specified
    if options.get('use_llm_for_hierarchy', True):
        refined = refine_with_llm(refined)
    
    return refined

def normalize_section_levels(content_structure: ContentStructure) -> None:
    """
    Ensure section levels are consistent and normalized.
    
    Args:
        content_structure: Content structure to normalize
    """
    # Start with top-level sections
    if not content_structure.sections:
        return
    
    # Find min section level
    min_level = min(section.level for section in content_structure.sections)
    
    # If min level is not 1, adjust all levels
    if min_level != 1:
        adjust_level = 1 - min_level
        for section in content_structure.sections:
            adjust_section_level(section, adjust_level)

def adjust_section_level(section, adjust_by: int) -> None:
    """
    Recursively adjust section level.
    
    Args:
        section: Section to adjust
        adjust_by: Amount to adjust level by
    """
    section.level += adjust_by
    
    # Recursively adjust subsections
    for subsection in section.subsections:
        adjust_section_level(subsection, adjust_by)

def reorganize_sections(content_structure: ContentStructure) -> None:
    """
    Reorganize sections to ensure proper nesting based on level.
    
    Args:
        content_structure: Content structure to reorganize
    """
    # Skip if no sections
    if not content_structure.sections:
        return
    
    # Start with original top-level sections
    all_sections = flatten_sections(content_structure)
    
    # Sort by level and original order
    sorted_sections = sorted(all_sections, key=lambda s: (s.level, all_sections.index(s)))
    
    # Clear existing structure
    content_structure.sections = []
    
    # Rebuilding hierarchy
    for section in sorted_sections:
        # Reset subsections
        section.subsections = []
    
    # First pass - add level 1 sections to content structure
    for section in sorted_sections:
        if section.level == 1:
            content_structure.sections.append(section)
    
    # Second pass - add subsections to appropriate parent
    for section in sorted_sections:
        if section.level > 1:
            parent = find_parent_for_section(content_structure, section)
            if parent:
                parent.subsections.append(section)
            else:
                # Promote to top level if no parent found
                section.level = 1
                content_structure.sections.append(section)

def flatten_sections(content_structure: ContentStructure) -> List:
    """
    Flatten hierarchical sections into a single list.
    
    Args:
        content_structure: Content structure to flatten
        
    Returns:
        List of all sections in the content structure
    """
    flat_list = []
    
    def _flatten(sections):
        for section in sections:
            flat_list.append(section)
            _flatten(section.subsections)
    
    _flatten(content_structure.sections)
    return flat_list

def find_parent_for_section(content_structure, section):
    """
    Find appropriate parent for a section based on level.
    
    Args:
        content_structure: Content structure to search
        section: Section to find parent for
        
    Returns:
        Appropriate parent section or None if not found
    """
    # For level 1, there's no parent
    if section.level <= 1:
        return None
    
    # Get all sections flattened
    all_sections = flatten_sections(content_structure)
    
    # Find index of current section in flattened list
    current_index = all_sections.index(section)
    
    # Search backwards for the closest section with level = current level - 1
    target_level = section.level - 1
    
    for i in range(current_index - 1, -1, -1):
        if all_sections[i].level == target_level:
            return all_sections[i]
    
    # No appropriate parent found
    return None

def refine_with_llm(content_structure: ContentStructure) -> ContentStructure:
    """
    Use LLM to refine the content structure hierarchy.
    
    Args:
        content_structure: Content structure to refine
        
    Returns:
        Refined content structure
    """
    try:
        from langchain_openai import ChatOpenAI
        import json
        
        # Convert to JSON for LLM processing
        structure_json = content_structure.model_dump_json(indent=2)
        
        # Initialize language model
        llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.0
        )
        
        # Prompt for refinement
        prompt_template = """
        あなたは日本語のテキスト構造解析の専門家です。
        次の文書構造を分析し、セクション間の階層関係を最適化してください。

        # 現在の構造:
        ```json
        {structure_json}
        ```

        # 指示:
        1. セクションの階層関係を分析し、意味的に適切な親子関係になるよう調整してください
        2. レベルが適切でないセクションの階層レベルを修正してください
        3. タイトルと内容から判断して、必要に応じてセクションの階層を変更してください
        4. 結果はJSONで返してください（元の構造と互換性を保ちながら最適化）

        # 出力:
        修正されたJSONを出力してください。元のJSONと同じ構造を保ちつつ、階層関係のみを最適化してください。
        ```json
        """
        
        # Create prompt and chain
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["structure_json"]
        )
        
        chain = (
            {"structure_json": RunnablePassthrough()} 
            | prompt 
            | llm 
            | StrOutputParser()
        )
        
        # Run chain
        result = chain.invoke(structure_json)
        
        # Parse the result
        # First find the JSON part
        json_start = result.find('```json')
        json_end = result.rfind('```')
        
        if json_start != -1 and json_end != -1:
            json_content = result[json_start + 7:json_end].strip()
            # Parse JSON
            refined_structure = ContentStructure.model_validate_json(json_content)
            return refined_structure
        
        # Fall back to original if parsing fails
        return content_structure
        
    except Exception as e:
        logger.warning(f"LLM refinement failed, using original structure: {str(e)}")
        return content_structure

def validate_structure(content_structure: ContentStructure) -> ContentStructure:
    """
    Validate the content structure and fix any inconsistencies.
    
    Args:
        content_structure: Content structure to validate
        
    Returns:
        Validated content structure
    """
    # Check title
    if not content_structure.title and content_structure.sections:
        # Use first section as title if no title exists
        content_structure.title = content_structure.sections[0].title
        content_structure.sections = content_structure.sections[1:]
    
    # Validate section levels
    validate_section_levels(content_structure.sections)
    
    return content_structure

def validate_section_levels(sections, current_level: int = 1) -> None:
    """
    Recursively validate section levels.
    
    Args:
        sections: Sections to validate
        current_level: Expected level for these sections
    """
    for section in sections:
        # Ensure section has the correct level
        if section.level != current_level:
            section.level = current_level
        
        # Validate subsections
        validate_section_levels(section.subsections, current_level + 1)
