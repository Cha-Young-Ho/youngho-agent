"""
Employee management service.
"""

import json
from typing import List, Dict, Any, Optional
from ..core import get_logger
from ..core.exceptions import DocumentProcessingError
from .vector_service import VectorService

logger = get_logger(__name__)


class EmployeeService:
    """Service for managing employee data."""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.sample_employees = self._get_sample_employees()
    
    async def add_employee_to_vector_db(self, employee_id: str = "") -> Dict[str, Any]:
        """
        Add employee data to vector database.
        
        Args:
            employee_id: Specific employee ID (empty string for all employees)
            
        Returns:
            Addition result
        """
        try:
            if employee_id:
                # Add specific employee
                employee = self._get_employee_by_id(employee_id)
                if not employee:
                    return {
                        "success": False,
                        "error": f"사원 ID {employee_id}를 찾을 수 없습니다."
                    }
                
                doc_id = self.vector_service.add_document(
                    doc_type="employee",
                    title=f"{employee['name']} - {employee['position']}",
                    content=self._format_employee_content(employee),
                    category="employee",
                    metadata=employee
                )
                
                return {
                    "success": True,
                    "message": f"사원 {employee['name']}이(가) 성공적으로 추가되었습니다. ID: {doc_id}",
                    "employee_id": employee_id,
                    "doc_id": doc_id
                }
            else:
                # Add all employees
                added_count = 0
                for employee in self.sample_employees:
                    try:
                        doc_id = self.vector_service.add_document(
                            doc_type="employee",
                            title=f"{employee['name']} - {employee['position']}",
                            content=self._format_employee_content(employee),
                            category="employee",
                            metadata=employee
                        )
                        added_count += 1
                        logger.info(f"Added employee {employee['name']} with doc_id: {doc_id}")
                    except Exception as e:
                        logger.error(f"Failed to add employee {employee['name']}: {e}")
                
                return {
                    "success": True,
                    "message": f"{added_count}명의 사원이 성공적으로 추가되었습니다.",
                    "added_count": added_count,
                    "total_employees": len(self.sample_employees)
                }
                
        except Exception as e:
            logger.error(f"Employee addition failed: {e}")
            return {
                "success": False,
                "error": f"사원 정보 추가 실패: {e}"
            }
    
    async def get_employee_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all employees.
        
        Returns:
            List of employees
        """
        try:
            # Search for all employee documents
            results = self.vector_service.search_text("", "employee", 100)
            
            if not results:
                # If no employees in DB, return sample data
                return self.sample_employees
            
            # Extract employee data from search results
            employees = []
            for result in results:
                if 'metadata' in result:
                    employees.append(result['metadata'])
                else:
                    # Fallback to sample data if metadata not available
                    employees.extend(self.sample_employees)
                    break
            
            return employees[:10]  # Limit to 10 employees
            
        except Exception as e:
            logger.error(f"Employee list retrieval failed: {e}")
            # Return sample data as fallback
            return self.sample_employees
    
    def _get_sample_employees(self) -> List[Dict[str, Any]]:
        """Get sample employee data."""
        return [
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
            {
                "employee_id": "EMP002",
                "name": "이영희",
                "position": "프론트엔드 개발자",
                "department": "개발팀",
                "email": "lee@company.com",
                "phone": "010-2345-6789",
                "skills": ["JavaScript", "React", "Vue.js", "TypeScript"],
                "projects": ["사용자 인터페이스", "반응형 웹", "PWA"],
                "hire_date": "2022-03-20",
                "responsibilities": "프론트엔드 개발, UI/UX 구현"
            },
            {
                "employee_id": "EMP003",
                "name": "박민수",
                "position": "DevOps 엔지니어",
                "department": "인프라팀",
                "email": "park@company.com",
                "phone": "010-3456-7890",
                "skills": ["Docker", "Kubernetes", "AWS", "Terraform"],
                "projects": ["CI/CD 파이프라인", "클라우드 인프라", "모니터링"],
                "hire_date": "2021-11-10",
                "responsibilities": "인프라 관리, 배포 자동화, 보안"
            },
            {
                "employee_id": "EMP004",
                "name": "정수진",
                "position": "데이터 엔지니어",
                "department": "데이터팀",
                "email": "jung@company.com",
                "phone": "010-4567-8901",
                "skills": ["Python", "SQL", "Spark", "Hadoop"],
                "projects": ["데이터 파이프라인", "ETL 프로세스", "데이터 웨어하우스"],
                "hire_date": "2022-06-01",
                "responsibilities": "데이터 처리, 분석, 시각화"
            },
            {
                "employee_id": "EMP005",
                "name": "최동현",
                "position": "AI/ML 엔지니어",
                "department": "AI팀",
                "email": "choi@company.com",
                "phone": "010-5678-9012",
                "skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn"],
                "projects": ["머신러닝 모델", "자연어 처리", "컴퓨터 비전"],
                "hire_date": "2022-08-15",
                "responsibilities": "AI 모델 개발, 알고리즘 연구"
            }
        ]
    
    def _get_employee_by_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get employee by ID from sample data."""
        for employee in self.sample_employees:
            if employee["employee_id"] == employee_id:
                return employee
        return None
    
    def _format_employee_content(self, employee: Dict[str, Any]) -> str:
        """Format employee data as searchable content."""
        content_parts = [
            f"이름: {employee['name']}",
            f"직책: {employee['position']}",
            f"부서: {employee['department']}",
            f"이메일: {employee['email']}",
            f"전화번호: {employee['phone']}",
            f"기술 스택: {', '.join(employee['skills'])}",
            f"프로젝트: {', '.join(employee['projects'])}",
            f"입사일: {employee['hire_date']}",
            f"담당 업무: {employee['responsibilities']}"
        ]
        return "\n".join(content_parts)


# Global employee service instance
employee_service = EmployeeService(VectorService()) 