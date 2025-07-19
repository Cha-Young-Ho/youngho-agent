# 🚀 Youngho Agent - MCP 서버 & 벡터 DB 프로젝트 가이드

## 📋 프로젝트 개요

이 프로젝트는 **Model Context Protocol (MCP) 서버**와 **OpenSearch 벡터 데이터베이스**를 연동하여 회사 지식 베이스를 구축하고 관리하는 시스템입니다.

### 🎯 주요 기능
- **PDF 파일 텍스트 추출** 및 마크다운 변환
- **Google Drive 파일 처리** 및 벡터 DB 저장
- **회사 지식 베이스 검색** (사원 정보, 코드, 기획서)
- **자동화된 벡터 DB 구축** (코드와 기획서 자동 매핑)
- **유사도 기반 검색** 및 카테고리 자동 분류

---

## 🏗️ 시스템 아키텍처

### 기술 스택
- **MCP 서버**: Python FastMCP
- **벡터 DB**: OpenSearch 2.11.0
- **임베딩 모델**: sentence-transformers/all-MiniLM-L6-v2
- **컨테이너**: Docker & Docker Compose
- **외부 연동**: Google Drive API, PDF 처리

### 파일 구조
```
youngho-agent/
├── mcp-server/                 # MCP 서버 핵심 코드
│   ├── main.py                # MCP 서버 메인 로직
│   ├── auto_vector_db.py      # 자동화된 벡터 DB 관리
│   ├── config.py              # 설정 관리
│   ├── settings.py            # 환경 변수
│   ├── employee_data.py       # 사원 데이터 관리
│   ├── vector_db.py           # 벡터 DB 연동
│   ├── pdf_processor.py       # PDF 처리
│   ├── google_drive.py        # Google Drive 연동
│   └── pyproject.toml         # 프로젝트 의존성
├── docker-compose.yml         # OpenSearch 컨테이너 설정
├── opensearch-setup.sh        # 초기 설정 스크립트
└── PROJECT-GUIDE.md           # 이 파일
```

---

## 🚀 빠른 시작

### 1. OpenSearch 설정
```bash
# OpenSearch 컨테이너 실행
docker-compose up -d

# 초기 설정 (인덱스 생성, 매핑 설정)
./opensearch-setup.sh
```

### 2. MCP 서버 실행
```bash
cd mcp-server
python main.py
```

### 3. Cursor AI에서 연결
- MCP 서버 주소: `localhost:8000`
- 도구 목록이 자동으로 등록됩니다

---

## 🔧 MCP 도구 목록

### 📄 문서 처리 도구
- `getPdfToText`: PDF 파일에서 텍스트 추출
- `getPdfToMarkDown`: PDF 파일을 마크다운으로 변환
- `processDriveFile`: Google Drive 파일 처리

### 🔍 검색 도구
- `searchCompanyKnowledge`: 회사 지식 베이스 검색
- `searchSpecifications`: 기획서 검색
- `getSpecificationById`: 특정 기획서 조회
- `getEmployeeList`: 사원 목록 조회

### 💾 벡터 DB 관리 도구
- `addDocumentToVectorDB`: 문서를 벡터 DB에 추가
- `addEmployeeToVectorDB`: 사원 정보 추가
- `addCodeToVectorDB`: 코드 파일 추가
- `addSpecFromDrive`: Google Drive 기획서 추가
- `batchAddCodeDirectory`: 디렉토리 일괄 추가
- `searchSimilarDocuments`: 유사한 문서 검색
- `getCodeForSpec`: 기획서에 맞는 코드 검색

### 📋 기타 도구
- `getCompanyRules`: 회사 규칙 조회

---

## 📊 데이터 구조

### 문서 타입 (doc_type)
- **employee**: 사원 정보
- **code**: 코드 파일
- **spec**: 기획서/스펙 문서

### 카테고리 분류
- **user**: 사용자, 회원, 계정 관련
- **event**: 이벤트, 일정, 예약 관련
- **payment**: 결제, 청구, 구독 관련
- **notification**: 알림, 메시지 관련
- **file**: 파일, 업로드, 다운로드 관련
- **api**: API, 엔드포인트, 서비스 관련
- **database**: 데이터베이스, 모델, 스키마 관련
- **ui**: UI, 컴포넌트, 페이지 관련
- **config**: 설정, 환경, 옵션 관련
- **test**: 테스트, 스펙, 모킹 관련

### 벡터 임베딩
- **모델**: all-MiniLM-L6-v2
- **차원**: 384차원
- **유사도 측정**: 코사인 유사도

---

## 💡 사용 예시

### 1. 기획서 검색
```
프롬프트: "opensearch에 저장하는 내용이 담긴 기획서를 찾아줘"
MCP 호출: searchSpecifications("opensearch에 저장하는 내용이 담긴 기획서를 찾아줘")
```

### 2. Google Drive 기획서 처리
```
프롬프트: "Google Drive ID 123123을 우리 회사 코드 기반으로 작성해줘"
MCP 호출: 
1. processDriveFile("123123", "text")
2. getCodeForSpec("123123")
```

### 3. 사원 정보 검색
```
프롬프트: "Python 개발자 찾아줘"
MCP 호출: searchCompanyKnowledge("Python 개발자", "employee")
```

---

## 🔍 검색 기능

### 텍스트 검색
- **필드**: title, content
- **타입**: best_fields
- **퍼지 매칭**: AUTO
- **점수 계산**: TF-IDF 기반

### 벡터 검색 (향후 개선 예정)
- **임베딩**: 384차원 벡터
- **유사도**: 코사인 유사도
- **인덱스**: HNSW (Hierarchical Navigable Small World)

### 하이브리드 검색
- 텍스트 검색과 벡터 검색을 결합
- 더 정확한 검색 결과 제공

---

## 🛠️ 개발 가이드

### 새로운 MCP 도구 추가
1. `mcp-server/main.py`에 도구 함수 정의
2. `@mcp.tool` 데코레이터 사용
3. 함수 시그니처와 문서화 추가

### 벡터 DB 확장
1. `mcp-server/auto_vector_db.py`에서 새로운 문서 타입 처리
2. 카테고리 분류 규칙 추가
3. 특징 추출 로직 구현

### 설정 변경
- `mcp-server/settings.py`: 환경 변수 및 상수
- `mcp-server/config.py`: 외부 서비스 설정
- `docker-compose.yml`: OpenSearch 설정

---

## 📈 성능 최적화

### 검색 성능
- **인덱스 최적화**: 적절한 매핑 설정
- **쿼리 최적화**: 효율적인 쿼리 구조
- **캐싱**: 자주 사용되는 쿼리 결과 캐싱

### 벡터 검색 최적화
- **HNSW 파라미터**: m=16, ef_construction=128
- **인덱스 크기**: 적절한 샤드 수 설정
- **메모리 사용량**: 벡터 필드 메모리 할당

---

## 🔒 보안 고려사항

### 인증 및 권한
- OpenSearch 보안 플러그인 활성화
- 사용자별 접근 권한 설정
- API 키 관리

### 데이터 보호
- 민감한 정보 암호화
- 로그 데이터 보호
- 백업 및 복구 전략

---

## 🐛 문제 해결

### 일반적인 문제들

#### 1. MCP 서버 연결 실패
```bash
# 서버 상태 확인
ps aux | grep "python.*main.py"

# 포트 확인
netstat -an | grep 8000

# 서버 재시작
pkill -f "python.*main.py"
cd mcp-server && python main.py
```

#### 2. OpenSearch 연결 실패
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs opensearch

# 컨테이너 재시작
docker-compose restart
```

#### 3. 벡터 검색 결과 없음
- 인덱스 매핑 확인
- 벡터 데이터 존재 여부 확인
- k-NN 플러그인 활성화 확인

### 로그 확인
```bash
# OpenSearch 로그
docker-compose logs -f opensearch

# MCP 서버 로그
# 터미널에서 직접 확인
```

---

## 📚 추가 리소스

### 공식 문서
- [OpenSearch 공식 문서](https://opensearch.org/docs/)
- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Sentence Transformers](https://www.sbert.net/)

### 관련 프로젝트
- [FastMCP](https://github.com/jlowin/fastmcp)
- [OpenSearch Python Client](https://opensearch.org/docs/latest/clients/python/)

---

## 🤝 기여 가이드

### 개발 환경 설정
1. Python 3.11+ 설치
2. 가상환경 생성 및 활성화
3. 의존성 설치: `pip install -r requirements.txt`
4. OpenSearch 실행: `docker-compose up -d`

### 코드 스타일
- PEP 8 준수
- 타입 힌트 사용
- 문서화 주석 작성
- 테스트 코드 작성

### 이슈 리포트
- 명확한 문제 설명
- 재현 단계 포함
- 환경 정보 제공
- 로그 파일 첨부

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

**마지막 업데이트**: 2024년 12월 