"""
Document processing service for handling various file types.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from ..core import get_logger
from ..core.exceptions import FileProcessingError, DocumentProcessingError
from .vector_service import VectorService

logger = get_logger(__name__)


class DocumentService:
    """Service for processing and managing documents."""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
    
    async def extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            # This would integrate with actual PDF processing library
            # For now, return a placeholder
            if not os.path.exists(pdf_path):
                raise FileProcessingError(f"PDF file not found: {pdf_path}")
            
            # Placeholder implementation
            return f"Extracted text from {pdf_path}"
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            raise FileProcessingError(f"PDF 텍스트 추출 실패: {e}")
    
    async def extract_pdf_markdown(self, pdf_path: str) -> str:
        """
        Extract markdown from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted markdown
        """
        try:
            # This would integrate with actual PDF processing library
            # For now, return a placeholder
            if not os.path.exists(pdf_path):
                raise FileProcessingError(f"PDF file not found: {pdf_path}")
            
            # Placeholder implementation
            return f"# Extracted Markdown from {pdf_path}\n\nThis is a placeholder for markdown extraction."
            
        except Exception as e:
            logger.error(f"PDF markdown extraction failed: {e}")
            raise FileProcessingError(f"PDF 마크다운 추출 실패: {e}")
    
    async def process_drive_file(self, file_id: str, mode: str = "text") -> str:
        """
        Process Google Drive file.
        
        Args:
            file_id: Google Drive file ID
            mode: Processing mode ('text' or 'markdown')
            
        Returns:
            Processed content
        """
        try:
            # This would integrate with Google Drive API
            # For now, return a placeholder
            if mode == "markdown":
                return f"# Google Drive File {file_id}\n\nMarkdown content placeholder."
            else:
                return f"Text content from Google Drive file {file_id}"
                
        except Exception as e:
            logger.error(f"Drive file processing failed: {e}")
            raise FileProcessingError(f"드라이브 파일 처리 실패: {e}")
    
    async def add_document_to_vector_db(self, file_path: str, doc_type: str = "code") -> Dict[str, Any]:
        """
        Add document to vector database.
        
        Args:
            file_path: Path to file
            doc_type: Document type
            
        Returns:
            Addition result
        """
        try:
            if not os.path.exists(file_path):
                raise FileProcessingError(f"File not found: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine title from file path
            title = os.path.basename(file_path)
            
            # Determine category based on file path and content
            category = self._determine_category(file_path, content)
            
            # Add to vector database
            doc_id = self.vector_service.add_document(
                doc_type=doc_type,
                title=title,
                content=content,
                category=category,
                metadata={
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path),
                    "file_type": Path(file_path).suffix
                }
            )
            
            return {
                "success": True,
                "message": f"문서가 성공적으로 추가되었습니다. ID: {doc_id}",
                "doc_id": doc_id,
                "file_path": file_path,
                "doc_type": doc_type,
                "category": category
            }
            
        except Exception as e:
            logger.error(f"Document addition failed: {e}")
            return {
                "success": False,
                "error": f"문서 추가 실패: {e}"
            }
    
    async def get_specification_by_id(self, spec_id: str) -> Dict[str, Any]:
        """
        Get specification by ID.
        
        Args:
            spec_id: Specification ID
            
        Returns:
            Specification data
        """
        try:
            spec = self.vector_service.get_document(spec_id)
            
            if not spec:
                return {
                    "success": False,
                    "message": "기획서를 찾을 수 없습니다.",
                    "spec_id": spec_id
                }
            
            return {
                "success": True,
                "specification": spec
            }
            
        except Exception as e:
            logger.error(f"Specification retrieval failed: {e}")
            return {
                "success": False,
                "error": f"기획서 조회 실패: {e}"
            }
    
    def _determine_category(self, file_path: str, content: str) -> str:
        """
        Determine document category based on file path and content.
        
        Args:
            file_path: File path
            content: File content
            
        Returns:
            Category string
        """
        # Simple category determination logic
        path_lower = file_path.lower()
        content_lower = content.lower()
        
        # User-related
        if any(keyword in path_lower or keyword in content_lower 
               for keyword in ['user', 'auth', 'login', 'register', 'profile']):
            return "user"
        
        # API-related
        if any(keyword in path_lower or keyword in content_lower 
               for keyword in ['api', 'endpoint', 'controller', 'service']):
            return "api"
        
        # Database-related
        if any(keyword in path_lower or keyword in content_lower 
               for keyword in ['model', 'schema', 'database', 'db', 'table']):
            return "database"
        
        # UI-related
        if any(keyword in path_lower or keyword in content_lower 
               for keyword in ['component', 'page', 'view', 'ui', 'frontend']):
            return "ui"
        
        # Config-related
        if any(keyword in path_lower or keyword in content_lower 
               for keyword in ['config', 'setting', 'env', 'conf']):
            return "config"
        
        # Test-related
        if any(keyword in path_lower or keyword in content_lower 
               for keyword in ['test', 'spec', 'mock', 'fixture']):
            return "test"
        
        # Default
        return "general"


# Global document service instance
document_service = DocumentService(VectorService()) 