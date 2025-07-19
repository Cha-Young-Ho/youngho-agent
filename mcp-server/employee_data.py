import json
from datetime import datetime
from vector_db import add_content_to_vector_db, search_vector_db
from settings import ENVIRONMENT

# 샘플 사원 정보
SAMPLE_EMPLOYEES = [
    {
        "employee_id": "EMP001",
        "name": "김철수",
        "department": "개발팀",
        "position": "시니어 개발자",
        "email": "kim.chulsoo@company.com",
        "phone": "010-1234-5678",
        "hire_date": "2020-03-15",
        "skills": ["Python", "JavaScript", "React", "Django", "AWS"],
        "projects": ["웹사이트 리뉴얼", "모바일 앱 개발", "API 설계"],
        "responsibilities": "백엔드 개발 및 API 설계 담당"
    },
    {
        "employee_id": "EMP002",
        "name": "이영희",
        "department": "디자인팀",
        "position": "UI/UX 디자이너",
        "email": "lee.younghee@company.com",
        "phone": "010-2345-6789",
        "hire_date": "2019-07-20",
        "skills": ["Figma", "Adobe XD", "Photoshop", "Illustrator", "프로토타이핑"],
        "projects": ["브랜드 아이덴티티 디자인", "사용자 인터페이스 설계", "사용자 경험 개선"],
        "responsibilities": "사용자 인터페이스 및 경험 디자인 담당"
    },
    {
        "employee_id": "EMP003",
        "name": "박민수",
        "department": "기획팀",
        "position": "프로덕트 매니저",
        "email": "park.minsu@company.com",
        "phone": "010-3456-7890",
        "hire_date": "2021-01-10",
        "skills": ["프로젝트 관리", "요구사항 분석", "스크럼", "Jira", "Confluence"],
        "projects": ["신규 서비스 기획", "사용자 리서치", "로드맵 수립"],
        "responsibilities": "제품 기획 및 프로젝트 관리 담당"
    },
    {
        "employee_id": "EMP004",
        "name": "정수진",
        "department": "개발팀",
        "position": "주니어 개발자",
        "email": "jung.sujin@company.com",
        "phone": "010-4567-8901",
        "hire_date": "2022-09-01",
        "skills": ["Java", "Spring Boot", "MySQL", "Git", "Docker"],
        "projects": ["관리자 시스템 개발", "데이터베이스 설계", "테스트 자동화"],
        "responsibilities": "백엔드 개발 및 데이터베이스 관리"
    },
    {
        "employee_id": "EMP005",
        "name": "최동현",
        "department": "개발팀",
        "position": "프론트엔드 개발자",
        "email": "choi.donghyun@company.com",
        "phone": "010-5678-9012",
        "hire_date": "2021-06-15",
        "skills": ["Vue.js", "TypeScript", "SCSS", "Webpack", "Jest"],
        "projects": ["관리자 대시보드", "사용자 포털", "모바일 웹 개발"],
        "responsibilities": "프론트엔드 개발 및 사용자 인터페이스 구현"
    }
]

def format_employee_info(employee):
    """사원 정보를 텍스트 형태로 포맷팅"""
    info = f"""
사원 정보:
- 사원번호: {employee['employee_id']}
- 이름: {employee['name']}
- 부서: {employee['department']}
- 직급: {employee['position']}
- 이메일: {employee['email']}
- 연락처: {employee['phone']}
- 입사일: {employee['hire_date']}
- 기술 스택: {', '.join(employee['skills'])}
- 참여 프로젝트: {', '.join(employee['projects'])}
- 담당 업무: {employee['responsibilities']}
"""
    return info.strip()

def add_employee_to_vector_db(employee_id: str = "") -> str:
    """
    사원 정보를 벡터 DB에 추가합니다.
    :param employee_id: 특정 사원 ID (빈 문자열이면 모든 사원 추가)
    """
    try:
        if employee_id:
            # 특정 사원만 추가
            employee = next((emp for emp in SAMPLE_EMPLOYEES if emp['employee_id'] == employee_id), None)
            if not employee:
                return f"사원 ID {employee_id}를 찾을 수 없습니다."
            
            employees_to_add = [employee]
        else:
            # 모든 사원 추가
            employees_to_add = SAMPLE_EMPLOYEES
        
        added_count = 0
        for employee in employees_to_add:
            # 사원 정보를 텍스트로 포맷팅
            employee_text = format_employee_info(employee)
            
            # 메타데이터 생성
            metadata = {
                "employee_id": employee['employee_id'],
                "name": employee['name'],
                "department": employee['department'],
                "position": employee['position'],
                "id": employee['employee_id']
            }
            
            # OpenSearch에 추가
            success = add_content_to_vector_db(
                content=employee_text,
                doc_type="employee",
                metadata=metadata
            )
            
            if success:
                added_count += 1
        
        if employee_id:
            return f"사원 {employee_id}가 벡터 DB에 성공적으로 추가되었습니다."
        else:
            return f"총 {added_count}명의 사원 정보가 벡터 DB에 성공적으로 추가되었습니다."
            
    except Exception as e:
        return f"사원 정보 추가 중 오류 발생: {e}"

def get_employee_list() -> str:
    """벡터 DB에서 등록된 사원 목록을 검색하여 반환합니다."""
    try:
        # OpenSearch에서 직접 텍스트 검색
        from config import get_vector_db_config
        from settings import OPENSEARCH_INDEX
        
        config = get_vector_db_config()
        client = config['client']
        
        # 사원 정보만 검색
        response = client.search(
            body={
                "query": {
                    "term": {"doc_type": "employee"}
                },
                "size": 50,
                "_source": ["employee_id", "name", "department", "position"]
            },
            index=OPENSEARCH_INDEX
        )
        
        hits = response['hits']['hits']
        
        if not hits:
            return "벡터 DB에 등록된 사원 정보가 없습니다. 먼저 사원 정보를 추가해주세요." + "\n" + ENVIRONMENT
        
        # 사원 목록 포맷팅
        employee_list = "등록된 사원 목록:\n"
        for hit in hits:
            source = hit['_source']
            employee_list += f"- {source.get('employee_id', 'Unknown')}: {source.get('name', 'Unknown')} ({source.get('department', 'Unknown')} - {source.get('position', 'Unknown')})\n"
        
        return employee_list.strip()
        
    except Exception as e:
        return f"사원 목록 조회 중 오류 발생: {e}" 