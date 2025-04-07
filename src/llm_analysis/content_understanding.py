"""
Content understanding module using LLMs to analyze text.
"""

import logging
from typing import Dict, Any, List, Optional

from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

from ..models import ExtractedText, ContentStructure, ContentSection, ContentElement
from ..exceptions import ContentAnalysisError, LLMConnectionError, LLMResponseError
from ..utils.error_handling import error_handling, retry

logger = logging.getLogger(__name__)

def analyze_content(
    extracted_text: List[ExtractedText],
    options: Optional[Dict[str, Any]] = None
) -> ContentStructure:
    """
    Analyze extracted text content to understand its semantic structure.
    
    Args:
        extracted_text: List of extracted text from images
        options: Analysis options
        
    Returns:
        ContentStructure representing the document structure
        
    Raises:
        ContentAnalysisError: If content analysis fails
        LLMConnectionError: If connection to LLM fails
        LLMResponseError: If LLM response is invalid
    """
    options = options or {}
    
    with error_handling(ContentAnalysisError, "Failed to analyze content"):
        # Combine text from all images
        combined_text = combine_extracted_text(extracted_text)
        
        # Choose analysis method based on options
        if options.get('analysis_method', 'llm') == 'llm':
            # Use LLM for content analysis
            content_structure = analyze_with_llm(combined_text, options)
        else:
            # Use rule-based analysis as fallback
            content_structure = analyze_with_rules(combined_text, options)
        
        return content_structure

def combine_extracted_text(extracted_texts: List[ExtractedText]) -> str:
    """
    Combine text from multiple extracted text objects.
    
    Args:
        extracted_texts: List of extracted text objects
        
    Returns:
        Combined text string
    """
    combined = []
    
    for ext_text in extracted_texts:
        # Add raw text
        combined.append(ext_text.raw_text)
        
    return "\n\n".join(combined)

@retry(max_attempts=2, exceptions=(LLMConnectionError, LLMResponseError))
def analyze_with_llm(text: str, options: Dict[str, Any]) -> ContentStructure:
    """
    Analyze content using a large language model.
    
    Args:
        text: Combined text to analyze
        options: Analysis options including LLM settings
        
    Returns:
        ContentStructure with analysis results
        
    Raises:
        LLMConnectionError: If connection to LLM fails
        LLMResponseError: If LLM response is invalid
    """
    try:
        from langchain_openai import ChatOpenAI
        
        # Initialize language model
        model_name = options.get('llm_model', 'gpt-4')
        temperature = options.get('llm_temperature', 0.0)
        
        llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        
        # Set up prompt for content analysis
        prompt_template = """
        あなたは日本語のテキストの構造を分析する専門家です。
        以下のテキストを分析して、その論理構造を特定してください。
        
        # テキスト:
        {text}
        
        # 分析手順:
        1. テキスト全体のタイトルと副題（存在する場合）を特定してください。
        2. 主要なセクションとその見出しを特定してください。
        3. 各セクション内の段落、リスト項目、引用などの要素を特定してください。
        4. 各要素の種類（段落、箇条書き、引用、コードブロックなど）を明記してください。
        
        # 出力形式:
        {format_instructions}
        """
        
        # Set up output parser
        parser = PydanticOutputParser(pydantic_object=ContentStructure)
        
        # Create full prompt with format instructions
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Create chain
        chain = (
            {"text": RunnablePassthrough()} 
            | prompt 
            | llm 
            | StrOutputParser() 
            | parser
        )
        
        # Run chain
        result = chain.invoke(text)
        
        # Return parsed ContentStructure
        return result
        
    except Exception as e:
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            logger.error(f"LLM connection error: {str(e)}")
            raise LLMConnectionError(f"Failed to connect to LLM: {str(e)}")
        else:
            logger.error(f"LLM analysis error: {str(e)}")
            raise LLMResponseError(f"Invalid response from LLM: {str(e)}")

def analyze_with_rules(text: str, options: Dict[str, Any]) -> ContentStructure:
    """
    Analyze content using rule-based methods as a fallback.
    
    Args:
        text: Combined text to analyze
        options: Analysis options
        
    Returns:
        ContentStructure with analysis results
    """
    # Split text into lines
    lines = text.split('\n')
    
    # Initialize content structure
    content_structure = ContentStructure(
        title=None,
        subtitle=None,
        sections=[]
    )
    
    # Find title (usually first non-empty line)
    for line in lines:
        if line.strip():
            content_structure.title = line.strip()
            break
    
    # Simple heuristics to identify sections
    current_section = None
    current_level = 0
    
    # States
    in_list = False
    list_items = []
    
    for line in lines[1:]:  # Skip first line (title)
        line = line.strip()
        
        if not line:
            # Empty line - close list if in one
            if in_list and list_items:
                # Add list to current section
                if current_section:
                    current_section.elements.append(
                        ContentElement(
                            element_type="list",
                            content="\n".join(list_items)
                        )
                    )
                list_items = []
                in_list = False
            continue
        
        # Check if this is a heading
        if is_likely_heading(line, lines):
            # Determine heading level
            level = estimate_heading_level(line)
            
            # Create new section
            new_section = ContentSection(
                level=level,
                title=line,
                elements=[],
                subsections=[]
            )
            
            # Add to structure
            if level == 1:
                # Top-level section
                content_structure.sections.append(new_section)
                current_section = new_section
                current_level = level
            elif current_section and level > current_level:
                # Subsection
                current_section.subsections.append(new_section)
                current_section = new_section
                current_level = level
            else:
                # Sibling or cousin section
                # Find appropriate parent
                parent = find_parent_section(content_structure, level)
                if parent:
                    parent.subsections.append(new_section)
                else:
                    # Fallback to top level
                    content_structure.sections.append(new_section)
                current_section = new_section
                current_level = level
        
        # Check if this is a list item
        elif line.startswith(('- ', '• ', '* ', '1. ', '2. ')) or line[0].isdigit() and line[1:3] in ('. ', ') '):
            in_list = True
            list_items.append(line)
        
        # Regular paragraph
        else:
            # Close list if in one
            if in_list and list_items:
                # Add list to current section
                if current_section:
                    current_section.elements.append(
                        ContentElement(
                            element_type="list",
                            content="\n".join(list_items)
                        )
                    )
                list_items = []
                in_list = False
            
            # Add paragraph to current section
            if current_section:
                current_section.elements.append(
                    ContentElement(
                        element_type="paragraph",
                        content=line
                    )
                )
    
    # Close any open list
    if in_list and list_items and current_section:
        current_section.elements.append(
            ContentElement(
                element_type="list",
                content="\n".join(list_items)
            )
        )
    
    return content_structure

def is_likely_heading(line: str, all_lines: List[str]) -> bool:
    """
    Determine if a line is likely a heading based on heuristics.
    
    Args:
        line: Line to check
        all_lines: All lines in the text
        
    Returns:
        True if the line is likely a heading, False otherwise
    """
    # Check for common heading patterns
    if line.startswith('#') or line.endswith(':'):
        return True
    
    # Check for short lines (headings tend to be shorter)
    if len(line) < 50 and line[0].isupper():
        return True
    
    # Check if followed by empty line
    line_index = all_lines.index(line)
    if line_index < len(all_lines) - 1 and not all_lines[line_index + 1].strip():
        return True
    
    return False

def estimate_heading_level(heading: str) -> int:
    """
    Estimate the level of a heading based on heuristics.
    
    Args:
        heading: Heading text
        
    Returns:
        Estimated heading level (1-6)
    """
    # Count leading # characters
    if heading.startswith('#'):
        hashes = 0
        for char in heading:
            if char == '#':
                hashes += 1
            else:
                break
        return min(hashes, 6)
    
    # Check for other indicators of level
    if heading.isupper():
        return 1
    elif len(heading) < 30:
        return 2
    else:
        return 3

def find_parent_section(content_structure: ContentStructure, level: int) -> Optional[ContentSection]:
    """
    Find the appropriate parent section for a given heading level.
    
    Args:
        content_structure: Current content structure
        level: Heading level to find parent for
        
    Returns:
        Parent section or None if not found
    """
    # For level 1, there's no parent
    if level <= 1:
        return None
    
    # Start with top-level sections
    sections_to_check = content_structure.sections
    
    # Find section with level one less than target
    target_level = level - 1
    
    while sections_to_check:
        for section in sections_to_check:
            if section.level == target_level:
                return section
            
        # If not found, collect subsections to check in next iteration
        next_sections = []
        for section in sections_to_check:
            next_sections.extend(section.subsections)
        
        sections_to_check = next_sections
    
    # No appropriate parent found
    return None
