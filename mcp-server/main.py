"""
MCP server main module with refactored structure and improved maintainability.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Import refactored modules
from core import config, get_logger, setup_logging
from core.exceptions import MCPError, ValidationError
from services.vector_service import VectorService
from services.search_service import SearchService
from services.document_service import DocumentService
from services.employee_service import EmployeeService

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize services
vector_service = VectorService()
search_service = SearchService(vector_service)
document_service = DocumentService(vector_service)
employee_service = EmployeeService(vector_service)

# Initialize MCP server
mcp = FastMCP("youngho-agent-mcp-server")


@mcp.tool(name="getPdfToText")
def get_pdf_to_text_tool(pdf_path: str) -> str:
    """
    PDF 파일에서 일반 텍스트를 추출합니다.
    
    이 도구는 PDF 파일을 읽어서 모든 텍스트 내용을 추출합니다.
    이미지나 표의 텍스트는 추출되지 않을 수 있으며, 텍스트 레이어만 처리됩니다.
    
    Args:
        pdf_path (str): PDF 파일의 절대 경로 또는 상대 경로
                       예: "/path/to/document.pdf" 또는 "documents/report.pdf"
    
    Returns:
        str: 추출된 텍스트 내용. 실패 시 에러 메시지
    
    Raises:
        MCPError: PDF 파일을 찾을 수 없거나 읽을 수 없는 경우
    
    Example:
        >>> getPdfToText("/Users/user/Documents/report.pdf")
        "이것은 PDF에서 추출된 텍스트입니다..."
    """
    try:
        return asyncio.run(document_service.extract_pdf_text(pdf_path))
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        raise MCPError(f"PDF 텍스트 추출 실패: {e}")


@mcp.tool(name="getPdfToMarkDown")
def get_pdf_to_markdown_tool(pdf_path: str) -> str:
    """
    PDF 파일에서 마크다운 포맷으로 텍스트를 추출합니다.
    
    이 도구는 PDF 파일을 읽어서 마크다운 형식으로 변환합니다.
    제목, 목록, 강조 등의 구조를 마크다운 문법으로 변환하여
    문서의 구조를 보존합니다.
    
    Args:
        pdf_path (str): PDF 파일의 절대 경로 또는 상대 경로
                       예: "/path/to/document.pdf" 또는 "documents/report.pdf"
    
    Returns:
        str: 마크다운 형식으로 변환된 텍스트. 실패 시 에러 메시지
    
    Raises:
        MCPError: PDF 파일을 찾을 수 없거나 읽을 수 없는 경우
    
    Example:
        >>> getPdfToMarkDown("/Users/user/Documents/report.pdf")
        "# 제목\n\n이것은 **굵은 텍스트**입니다.\n\n- 목록 항목 1\n- 목록 항목 2"
    """
    try:
        return asyncio.run(document_service.extract_pdf_markdown(pdf_path))
    except Exception as e:
        logger.error(f"PDF markdown extraction failed: {e}")
        raise MCPError(f"PDF 마크다운 추출 실패: {e}")


@mcp.tool(name="processDriveFile")
def process_drive_file_tool(file_id: str, mode: str = "text") -> str:
    """
    Google Drive에서 파일을 받아 확장자별로 처리합니다.
    
    이 도구는 Google Drive에 저장된 파일을 다운로드하고 내용을 추출합니다.
    지원하는 파일 형식: PDF, DOCX, TXT, MD 등
    파일의 내용을 텍스트 또는 마크다운 형식으로 변환합니다.
    
    Args:
        file_id (str): Google Drive 파일의 고유 ID
                      예: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        mode (str): 처리 모드
                   - "text": 일반 텍스트로 추출
                   - "markdown": 마크다운 형식으로 변환
    
    Returns:
        str: 추출된 파일 내용. 실패 시 에러 메시지
    
    Raises:
        MCPError: 파일을 찾을 수 없거나 접근 권한이 없는 경우
    
    Example:
        >>> processDriveFile("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", "text")
        "Google Drive 파일의 텍스트 내용..."
    """
    try:
        return asyncio.run(document_service.process_drive_file(file_id, mode))
    except Exception as e:
        logger.error(f"Drive file processing failed: {e}")
        raise MCPError(f"드라이브 파일 처리 실패: {e}")


@mcp.tool(name="searchCompanyKnowledge")
def search_company_knowledge_tool(query: str, context_type: str = "all", max_results: int = 5) -> str:
    """
    회사 지식 베이스에서 관련 정보를 검색합니다.
    
    이 도구는 OpenSearch 벡터 데이터베이스에서 회사 관련 문서들을 검색합니다.
    벡터 유사도 검색과 텍스트 검색을 모두 사용하여 가장 관련성 높은 결과를 반환합니다.
    
    Args:
        query (str): 검색할 키워드나 문장
                    예: "Python 개발자", "사용자 인증 시스템", "API 설계"
        context_type (str): 검색할 문서 타입 필터
                           - "all": 모든 문서 타입 (기본값)
                           - "code": 코드 파일만
                           - "spec": 기획서만
                           - "doc": 일반 문서만
                           - "employee": 사원 정보만
        max_results (int): 반환할 최대 결과 수 (기본값: 5, 최대: 50)
    
    Returns:
        str: JSON 형식의 검색 결과
             - success: 검색 성공 여부
             - method: 사용된 검색 방법 (vector_search 또는 text_search)
             - results: 검색 결과 목록
             - total: 총 결과 수
    
    Example:
        >>> searchCompanyKnowledge("Python 개발자", "employee", 3)
        {
          "success": true,
          "method": "vector_search",
          "results": [...],
          "total": 2
        }
    """
    try:
        results = asyncio.run(search_service.search_company_knowledge(query, context_type, max_results))
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Company knowledge search failed: {e}")
        return json.dumps({"error": f"검색 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="addDocumentToVectorDB")
def add_document_to_vector_db_tool(file_path: str, doc_type: str = "code") -> str:
    """
    파일을 벡터 DB에 추가합니다.
    
    이 도구는 로컬 파일을 읽어서 OpenSearch 벡터 데이터베이스에 추가합니다.
    파일의 내용을 분석하여 카테고리를 자동으로 분류하고,
    텍스트를 벡터 임베딩으로 변환하여 저장합니다.
    
    Args:
        file_path (str): 추가할 파일의 절대 경로 또는 상대 경로
                        예: "/path/to/file.py" 또는 "src/api/user.py"
        doc_type (str): 문서 타입 분류
                       - "code": 코드 파일 (기본값)
                       - "spec": 기획서/스펙 문서
                       - "doc": 일반 문서
    
    Returns:
        str: JSON 형식의 추가 결과
             - success: 추가 성공 여부
             - message: 결과 메시지
             - doc_id: 생성된 문서 ID
             - file_path: 파일 경로
             - doc_type: 문서 타입
             - category: 자동 분류된 카테고리
    
    Example:
        >>> addDocumentToVectorDB("/path/to/user_controller.py", "code")
        {
          "success": true,
          "message": "문서가 성공적으로 추가되었습니다. ID: abc123",
          "doc_id": "abc123",
          "file_path": "/path/to/user_controller.py",
          "doc_type": "code",
          "category": "user"
        }
    """
    try:
        result = asyncio.run(document_service.add_document_to_vector_db(file_path, doc_type))
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Document addition to vector DB failed: {e}")
        return json.dumps({"error": f"문서 추가 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="addEmployeeToVectorDB")
def add_employee_to_vector_db_tool(employee_id: str = "") -> str:
    """
    사원 정보를 벡터 DB에 추가합니다.
    
    이 도구는 사원 정보를 OpenSearch 벡터 데이터베이스에 추가합니다.
    특정 사원 ID를 지정하면 해당 사원만 추가하고,
    빈 문자열을 전달하면 모든 샘플 사원 데이터를 추가합니다.
    
    Args:
        employee_id (str): 추가할 사원의 ID
                          - 빈 문자열 "": 모든 사원 추가 (기본값)
                          - "EMP001": 특정 사원만 추가
                          예: "EMP001", "EMP002", ""
    
    Returns:
        str: JSON 형식의 추가 결과
             - success: 추가 성공 여부
             - message: 결과 메시지
             - employee_id: 사원 ID (특정 사원 추가 시)
             - doc_id: 생성된 문서 ID (특정 사원 추가 시)
             - added_count: 추가된 사원 수 (전체 추가 시)
             - total_employees: 전체 사원 수 (전체 추가 시)
    
    Example:
        >>> addEmployeeToVectorDB("EMP001")
        {
          "success": true,
          "message": "사원 김철수가 성공적으로 추가되었습니다. ID: def456",
          "employee_id": "EMP001",
          "doc_id": "def456"
        }
        
        >>> addEmployeeToVectorDB("")
        {
          "success": true,
          "message": "5명의 사원이 성공적으로 추가되었습니다.",
          "added_count": 5,
          "total_employees": 5
        }
    """
    try:
        result = asyncio.run(employee_service.add_employee_to_vector_db(employee_id))
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Employee addition to vector DB failed: {e}")
        return json.dumps({"error": f"사원 정보 추가 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="getEmployeeList")
def get_employee_list_tool() -> str:
    """
    등록된 사원 목록을 반환합니다.
    
    이 도구는 벡터 데이터베이스에 저장된 사원 정보를 조회합니다.
    데이터베이스에 사원 정보가 없으면 샘플 사원 데이터를 반환합니다.
    
    Returns:
        str: JSON 형식의 사원 목록
             각 사원 정보는 다음을 포함:
             - employee_id: 사원 ID
             - name: 이름
             - position: 직책
             - department: 부서
             - email: 이메일
             - phone: 전화번호
             - skills: 기술 스택 목록
             - projects: 프로젝트 목록
             - hire_date: 입사일
             - responsibilities: 담당 업무
    
    Example:
        >>> getEmployeeList()
        [
          {
            "employee_id": "EMP001",
            "name": "김철수",
            "position": "시니어 개발자",
            "department": "개발팀",
            "email": "kim@company.com",
            "phone": "010-1234-5678",
            "skills": ["Python", "JavaScript", "React", "Django"],
            "projects": ["웹 애플리케이션", "API 개발", "마이크로서비스"],
            "hire_date": "2022-01-15",
            "responsibilities": "백엔드 개발, API 설계, 코드 리뷰"
          },
          ...
        ]
    """
    try:
        employees = asyncio.run(employee_service.get_employee_list())
        return json.dumps(employees, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Employee list retrieval failed: {e}")
        return json.dumps({"error": f"사원 목록 조회 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="getCompanyRules")
def get_company_rules_tool() -> str:
    """
    우리 회사 전사 개발자들이 적용할 수 있는 rules를 리턴합니다.
    
    이 도구는 회사 개발자들이 따라야 할 코딩 규칙과 모범 사례를 반환합니다.
    코드 품질, 보안, 성능, 문서화 등에 대한 가이드라인을 제공합니다.
    
    Returns:
        str: JSON 형식의 회사 규칙
             - company_name: 회사명
             - rules: 주요 개발 규칙 목록
             - best_practices: 모범 사례 목록
    
    Example:
        >>> getCompanyRules()
        {
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
    """
    try:
        rules = asyncio.run(search_service.get_company_rules())
        return json.dumps(rules, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Company rules retrieval failed: {e}")
        return json.dumps({"error": f"회사 규칙 조회 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="searchSpecifications")
def search_specifications_tool(query: str) -> str:
    """
    기획서를 검색합니다.
    
    이 도구는 벡터 데이터베이스에서 기획서 문서들을 검색합니다.
    텍스트 기반 검색을 사용하여 관련성 높은 기획서를 찾습니다.
    
    Args:
        query (str): 검색할 키워드나 문장
                    예: "사용자 인증", "API 설계", "데이터베이스 설계"
    
    Returns:
        str: JSON 형식의 검색 결과
             - success: 검색 성공 여부
             - message: 결과 메시지 (실패 시)
             - results: 검색 결과 목록
             - total: 총 결과 수
    
    Example:
        >>> searchSpecifications("사용자 인증 시스템")
        {
          "success": true,
          "results": [
            {
              "id": "spec_001",
              "score": 0.85,
              "title": "사용자 인증 시스템 기획서",
              "content": "JWT 토큰 기반 인증 시스템...",
              "doc_type": "spec",
              "category": "user"
            }
          ],
          "total": 1
        }
    """
    try:
        results = asyncio.run(search_service.search_specifications(query))
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Specification search failed: {e}")
        return json.dumps({"error": f"기획서 검색 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="getSpecificationById")
def get_specification_by_id_tool(spec_id: str) -> str:
    """
    특정 기획서를 ID로 조회합니다.
    
    이 도구는 벡터 데이터베이스에서 특정 ID의 기획서를 조회합니다.
    기획서의 전체 내용과 메타데이터를 반환합니다.
    
    Args:
        spec_id (str): 조회할 기획서의 고유 ID
                      예: "spec_001", "user_auth_spec", "api_design_spec"
    
    Returns:
        str: JSON 형식의 기획서 정보
             - success: 조회 성공 여부
             - message: 결과 메시지 (실패 시)
             - specification: 기획서 상세 정보 (성공 시)
    
    Example:
        >>> getSpecificationById("spec_001")
        {
          "success": true,
          "specification": {
            "id": "spec_001",
            "title": "사용자 인증 시스템 기획서",
            "content": "JWT 토큰 기반 인증 시스템 설계...",
            "doc_type": "spec",
            "category": "user",
            "metadata": {
              "author": "김철수",
              "version": "1.0",
              "created_at": "2024-01-01T00:00:00Z"
            }
          }
        }
    """
    try:
        spec = asyncio.run(document_service.get_specification_by_id(spec_id))
        return json.dumps(spec, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Specification retrieval failed: {e}")
        return json.dumps({"error": f"기획서 조회 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="addCodeToVectorDB")
def add_code_to_vector_db_tool(file_path: str) -> str:
    """
    코드 파일을 벡터 DB에 추가합니다.
    
    이 도구는 코드 파일을 읽어서 OpenSearch 벡터 데이터베이스에 추가합니다.
    코드의 내용을 분석하여 언어, 프레임워크, 카테고리를 자동으로 분류하고,
    벡터 임베딩으로 변환하여 저장합니다.
    
    Args:
        file_path (str): 추가할 코드 파일의 절대 경로 또는 상대 경로
                        예: "/path/to/user_controller.py" 또는 "src/api/auth.py"
                        지원 형식: .py, .js, .ts, .java, .cpp, .c, .go, .rs 등
    
    Returns:
        str: JSON 형식의 추가 결과
             - success: 추가 성공 여부
             - message: 결과 메시지
             - doc_id: 생성된 문서 ID
             - file_path: 파일 경로
             - doc_type: 문서 타입 (항상 "code")
             - category: 자동 분류된 카테고리
    
    Example:
        >>> addCodeToVectorDB("/path/to/user_controller.py")
        {
          "success": true,
          "message": "문서가 성공적으로 추가되었습니다. ID: ghi789",
          "doc_id": "ghi789",
          "file_path": "/path/to/user_controller.py",
          "doc_type": "code",
          "category": "user"
        }
    """
    try:
        result = asyncio.run(document_service.add_document_to_vector_db(file_path, "code"))
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Code file addition failed: {e}")
        return json.dumps({"error": f"코드 파일 추가 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="addSpecFromDrive")
def add_spec_from_drive_tool(file_id: str, mode: str = "text") -> str:
    """
    Google Drive의 기획서를 벡터 DB에 추가합니다.
    
    이 도구는 Google Drive에 저장된 기획서 파일을 다운로드하고
    OpenSearch 벡터 데이터베이스에 추가합니다.
    파일의 내용을 텍스트 또는 마크다운 형식으로 변환하여 저장합니다.
    
    Args:
        file_id (str): Google Drive 파일의 고유 ID
                      예: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        mode (str): 처리 모드
                   - "text": 일반 텍스트로 추출 (기본값)
                   - "markdown": 마크다운 형식으로 변환
    
    Returns:
        str: JSON 형식의 추가 결과
             - success: 추가 성공 여부
             - message: 결과 메시지
             - doc_id: 생성된 문서 ID
    
    Example:
        >>> addSpecFromDrive("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", "text")
        {
          "success": true,
          "message": "기획서가 벡터 DB에 성공적으로 추가되었습니다: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
          "doc_id": "jkl012"
        }
    """
    try:
        # Process drive file first
        content = asyncio.run(document_service.process_drive_file(file_id, mode))
        
        # Add to vector DB
        doc_id = vector_service.add_document(
            doc_type="spec",
            title=f"Google Drive Spec - {file_id}",
            content=content,
            category="spec",
            metadata={"file_id": file_id, "source": "google_drive"}
        )
        
        return json.dumps({
            "success": True,
            "message": f"기획서가 벡터 DB에 성공적으로 추가되었습니다: {file_id}",
            "doc_id": doc_id
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Spec from drive addition failed: {e}")
        return json.dumps({"error": f"기획서 추가 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="batchAddCodeDirectory")
def batch_add_code_directory_tool(directory_path: str, extensions: str = None) -> str:
    """
    디렉토리의 모든 코드 파일을 일괄 추가합니다.
    
    이 도구는 지정된 디렉토리와 하위 디렉토리에서 모든 코드 파일을 찾아
    OpenSearch 벡터 데이터베이스에 일괄 추가합니다.
    파일 확장자를 지정하여 특정 언어의 파일만 처리할 수 있습니다.
    
    Args:
        directory_path (str): 코드 파일이 있는 디렉토리 경로
                            예: "/path/to/project/src" 또는 "src/api"
        extensions (str): 처리할 파일 확장자 (쉼표로 구분)
                         - None: 기본 확장자 (.py, .js, .ts, .java, .cpp, .c, .go, .rs)
                         - ".py,.js": Python과 JavaScript 파일만
                         - ".java,.cpp": Java와 C++ 파일만
    
    Returns:
        str: JSON 형식의 일괄 추가 결과
             - success: 추가 성공 여부
             - message: 결과 메시지
             - success_count: 성공한 파일 수
             - failed_count: 실패한 파일 수
             - total_count: 총 처리한 파일 수
    
    Example:
        >>> batchAddCodeDirectory("/path/to/project/src", ".py,.js")
        {
          "success": true,
          "message": "일괄 추가 완료: 성공 15개, 실패 2개, 총 17개",
          "success_count": 15,
          "failed_count": 2,
          "total_count": 17
        }
    """
    try:
        import os
        from pathlib import Path
        
        if not os.path.exists(directory_path):
            return json.dumps({"error": f"디렉토리를 찾을 수 없습니다: {directory_path}"}, ensure_ascii=False)
        
        # Parse extensions
        if extensions:
            ext_list = [ext.strip() for ext in extensions.split(',')]
        else:
            ext_list = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']
        
        # Find all files with specified extensions
        files_to_process = []
        for ext in ext_list:
            files_to_process.extend(Path(directory_path).rglob(f"*{ext}"))
        
        success_count = 0
        failed_count = 0
        
        for file_path in files_to_process:
            try:
                result = asyncio.run(document_service.add_document_to_vector_db(str(file_path), "code"))
                if result.get("success"):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to add file {file_path}: {e}")
                failed_count += 1
        
        return json.dumps({
            "success": True,
            "message": f"일괄 추가 완료: 성공 {success_count}개, 실패 {failed_count}개, 총 {len(files_to_process)}개",
            "success_count": success_count,
            "failed_count": failed_count,
            "total_count": len(files_to_process)
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Batch addition failed: {e}")
        return json.dumps({"error": f"일괄 추가 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="searchSimilarDocuments")
def search_similar_documents_tool(query: str, doc_type: str = "all", category: str = None, max_results: int = 10) -> str:
    """
    유사한 문서를 검색합니다.
    
    이 도구는 OpenSearch 벡터 데이터베이스에서 유사한 문서를 검색합니다.
    벡터 유사도 검색을 우선 시도하고, 실패 시 텍스트 검색을 사용합니다.
    문서 타입과 카테고리로 필터링할 수 있습니다.
    
    Args:
        query (str): 검색할 키워드나 문장
                    예: "사용자 인증", "API 엔드포인트", "데이터베이스 연결"
        doc_type (str): 검색할 문서 타입
                       - "all": 모든 문서 타입 (기본값)
                       - "code": 코드 파일만
                       - "spec": 기획서만
        category (str): 검색할 카테고리 (선택사항)
                       - "user": 사용자 관련
                       - "event": 이벤트 관련
                       - "payment": 결제 관련
                       - "notification": 알림 관련
                       - "file": 파일 관련
                       - "api": API 관련
                       - "database": 데이터베이스 관련
                       - "ui": UI 관련
                       - "config": 설정 관련
                       - "test": 테스트 관련
        max_results (int): 반환할 최대 결과 수 (기본값: 10, 최대: 50)
    
    Returns:
        str: JSON 형식의 검색 결과
             - success: 검색 성공 여부
             - message: 결과 메시지 (실패 시)
             - results: 검색 결과 목록
             - total: 총 결과 수
    
    Example:
        >>> searchSimilarDocuments("사용자 인증", "code", "user", 5)
        {
          "success": true,
          "results": [
            {
              "id": "doc_001",
              "score": 0.92,
              "title": "user_authentication.py",
              "content": "JWT 토큰 기반 사용자 인증...",
              "doc_type": "code",
              "category": "user"
            }
          ],
          "total": 1
        }
    """
    try:
        # Map doc_type
        doc_type_map = {"all": None, "code": "code", "spec": "spec"}
        mapped_doc_type = doc_type_map.get(doc_type, None)
        
        # Try vector search first, then text search
        try:
            results = vector_service.search_similar(query, mapped_doc_type, max_results)
        except Exception:
            results = vector_service.search_text(query, mapped_doc_type, max_results)
        
        if not results:
            return json.dumps({"message": "유사한 문서를 찾을 수 없습니다.", "results": []}, ensure_ascii=False)
        
        # Filter by category if specified
        if category:
            results = [r for r in results if r.get('category') == category]
        
        return json.dumps({
            "success": True,
            "results": results,
            "total": len(results)
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Similar documents search failed: {e}")
        return json.dumps({"error": f"검색 실패: {e}"}, ensure_ascii=False)


@mcp.tool(name="getCodeForSpec")
def get_code_for_spec_tool(spec_file_id: str, max_results: int = 5) -> str:
    """
    기획서에 맞는 코드를 검색합니다.
    
    이 도구는 Google Drive의 기획서 파일을 읽어서
    해당 기획서와 유사한 코드를 벡터 데이터베이스에서 검색합니다.
    기획서의 내용을 분석하여 관련성 높은 코드 파일들을 찾습니다.
    
    Args:
        spec_file_id (str): Google Drive 기획서 파일의 고유 ID
                           예: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        max_results (int): 반환할 최대 코드 파일 수 (기본값: 5, 최대: 20)
    
    Returns:
        str: JSON 형식의 검색 결과
             - success: 검색 성공 여부
             - spec: 기획서 정보
             - similar_codes: 유사한 코드 파일 목록
    
    Example:
        >>> getCodeForSpec("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", 3)
        {
          "success": true,
          "spec": {
            "file_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            "content": "사용자 인증 시스템 기획서... JWT 토큰 기반 인증..."
          },
          "similar_codes": [
            {
              "id": "code_001",
              "score": 0.89,
              "title": "auth_controller.py",
              "content": "JWT 토큰 기반 사용자 인증...",
              "doc_type": "code",
              "category": "user"
            }
          ]
        }
    """
    try:
        # Get spec content from drive
        spec_content = asyncio.run(document_service.process_drive_file(spec_file_id, "text"))
        
        # Search for similar code
        results = vector_service.search_similar(spec_content, "code", max_results)
        
        return json.dumps({
            "success": True,
            "spec": {
                "file_id": spec_file_id,
                "content": spec_content[:500] + "..." if len(spec_content) > 500 else spec_content
            },
            "similar_codes": results
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Code for spec search failed: {e}")
        return json.dumps({"error": f"코드 검색 실패: {e}"}, ensure_ascii=False)


if __name__ == "__main__":
    try:
        # Initialize vector database
        logger.info("Initializing vector database...")
        vector_service.create_index()
        
        # Start MCP server
        logger.info("Starting MCP server...")
        mcp.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise
