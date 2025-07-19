"""
Search service for company knowledge base.
"""

import json
from typing import List, Dict, Any, Optional
from ..core import get_logger
from ..core.exceptions import SearchError
from .vector_service import VectorService

logger = get_logger(__name__)


class SearchService:
    """Service for searching company knowledge base."""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
    
    async def search_company_knowledge(self, query: str, context_type: str = "all", 
                                     max_results: int = 5) -> Dict[str, Any]:
        """
        Search company knowledge base.
        
        Args:
            query: Search query
            context_type: Document type filter
            max_results: Maximum number of results
            
        Returns:
            Search results
        """
        try:
            # Map context_type to doc_type
            doc_type_map = {
                "all": None,
                "code": "code",
                "spec": "spec",
                "doc": "doc",
                "employee": "employee"
            }
            
            doc_type = doc_type_map.get(context_type, None)
            
            # Try vector search first
            try:
                results = self.vector_service.search_similar(query, doc_type, max_results)
                if results:
                    return {
                        "success": True,
                        "method": "vector_search",
                        "results": results,
                        "total": len(results)
                    }
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to text search: {e}")
            
            # Fallback to text search
            results = self.vector_service.search_text(query, doc_type, max_results)
            
            return {
                "success": True,
                "method": "text_search",
                "results": results,
                "total": len(results)
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(f"검색 실패: {e}")
    
    async def search_specifications(self, query: str) -> Dict[str, Any]:
        """
        Search specifications.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        try:
            results = self.vector_service.search_text(query, "spec", 10)
            
            if not results:
                return {
                    "success": False,
                    "message": "관련 기획서를 찾을 수 없습니다.",
                    "results": []
                }
            
            return {
                "success": True,
                "results": results,
                "total": len(results)
            }
            
        except Exception as e:
            logger.error(f"Specification search failed: {e}")
            return {
                "success": False,
                "message": f"기획서 검색 실패: {e}",
                "results": []
            }
    
    async def get_company_rules(self) -> Dict[str, Any]:
        """
        Get company rules.
        
        Returns:
            Company rules
        """
        try:
            # Search for company rules in the knowledge base
            results = self.vector_service.search_text("회사 규칙 개발자 가이드라인", "doc", 5)
            
            rules = {
                "company_name": "Youngho Company",
                "rules": [
                    "코드 품질 관리: 모든 코드는 리뷰를 거쳐야 합니다.",
                    "문서화: API와 주요 기능은 반드시 문서화해야 합니다.",
                    "테스트: 새로운 기능은 테스트 코드와 함께 작성해야 합니다.",
                    "보안: 사용자 데이터는 항상 암호화하여 처리해야 합니다.",
                    "성능: 데이터베이스 쿼리는 최적화되어야 합니다."
                ],
                "best_practices": [
                    "코드 컨벤션 준수",
                    "변수명과 함수명은 명확하게 작성",
                    "주석은 필요한 경우에만 작성",
                    "에러 처리는 적절히 구현",
                    "로깅은 구조화된 형태로 작성"
                ]
            }
            
            return rules
            
        except Exception as e:
            logger.error(f"Company rules retrieval failed: {e}")
            return {
                "error": f"회사 규칙 조회 실패: {e}"
            }


# Global search service instance
search_service = SearchService(VectorService()) 