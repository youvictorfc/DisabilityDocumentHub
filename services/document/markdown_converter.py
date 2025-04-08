"""
Enhanced document conversion service using Microsoft's MarkItDown tool.
This module converts various document formats (DOCX, PDF, etc.) to markdown
format for improved text extraction and structure preservation.
"""

import os
import io
import logging
from typing import Dict, Any, Optional
from markitdown import MarkItDown

logger = logging.getLogger(__name__)

class MarkdownConverter:
    """
    Wrapper for Microsoft's MarkItDown tool to convert documents to markdown.
    This class provides methods to convert various document formats to markdown
    for enhanced text extraction while preserving document structure.
    """
    
    def __init__(self):
        """Initialize the MarkItDown converter."""
        # Create MarkItDown instance without LLM capabilities
        # We already use OpenAI for further processing
        self.converter = MarkItDown(enable_plugins=False)
        logger.info("MarkdownConverter initialized")
    
    def convert_to_markdown(self, file_path: str) -> Dict[str, Any]:
        """
        Convert a document to markdown format.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            dict: Dictionary containing:
                - markdown: The markdown representation of the document
                - metadata: Any extracted metadata
                - success: Boolean indicating success
                - error: Error message if any
        """
        try:
            logger.info(f"Converting file to markdown: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return {"success": False, "error": f"File not found: {file_path}", "markdown": ""}
            
            # Convert the document to markdown
            result = self.converter.convert(file_path)
            
            # Extract the markdown content and metadata
            markdown = result.text_content
            metadata = result.metadata
            
            logger.info(f"Successfully converted {file_path} to markdown")
            logger.debug(f"Markdown content (excerpt): {markdown[:500]}...")
            logger.debug(f"Extracted metadata: {metadata}")
            
            return {
                "success": True,
                "markdown": markdown,
                "metadata": metadata,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error converting file to markdown: {str(e)}")
            return {
                "success": False,
                "markdown": "",
                "metadata": {},
                "error": f"Error converting file to markdown: {str(e)}"
            }
    
    def extract_text_from_file_markdown(self, file_path: str) -> str:
        """
        Extract text from a file using markdown conversion.
        This is a simpler interface that just returns the markdown text.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            str: Markdown text content
        """
        result = self.convert_to_markdown(file_path)
        if result["success"]:
            return result["markdown"]
        else:
            logger.warning(f"Failed to extract text using markdown. Error: {result['error']}")
            return ""