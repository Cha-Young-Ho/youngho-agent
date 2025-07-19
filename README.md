# 🚀 Youngho Agent - MCP 서버 & 벡터 DB

Model Context Protocol (MCP) 서버와 OpenSearch 벡터 데이터베이스를 연동한 회사 지식 베이스 시스템입니다.

## 🎯 주요 기능

- **PDF 파일 텍스트 추출** 및 마크다운 변환
- **Google Drive 파일 처리** 및 벡터 DB 저장
- **회사 지식 베이스 검색** (사원 정보, 코드, 기획서)
- **자동화된 벡터 DB 구축** (코드와 기획서 자동 매핑)
- **유사도 기반 검색** 및 카테고리 자동 분류

## 🚀 빠른 시작

### 1. 프로젝트 설정
```bash
# 저장소 클론
git clone <repository-url>
cd youngho-agent

# 환경 설정 가이드 참조
# SETUP-GUIDE.md 파일을 확인하세요
```

### 2. OpenSearch 설정
```bash
# OpenSearch 컨테이너 실행
docker-compose up -d

# 초기 설정 (인덱스 생성, 매핑 설정)
./opensearch-setup.sh
```

### 3. MCP 서버 실행
```bash
cd mcp-server
python main.py
```

### 4. Cursor AI에서 연결
- MCP 서버 주소: `localhost:8000`
- 도구 목록이 자동으로 등록됩니다

## 📚 상세 가이드

### 📋 설정 및 설치
- **[SETUP-GUIDE.md](SETUP-GUIDE.md)**: Mac 환경 설정, Python 설치, Docker 설정, OpenSearch 설정

### 🔍 OpenSearch 기능 설명
- **[OPENSEARCH-EXPLANATION.md](OPENSEARCH-EXPLANATION.md)**: OpenSearch 선택 이유, 사용 기능, 인덱스 설계, 검색 전략

### 🛠️ 프로젝트 전체 가이드
- **[PROJECT-GUIDE.md](PROJECT-GUIDE.md)**: 시스템 아키텍처, MCP 도구 목록, 사용 예시, 개발 가이드

## 🏗️ 프로젝트 구조

```
youngho-agent/
├── README.md                    # 프로젝트 메인 README
├── SETUP-GUIDE.md              # 설정 및 설치 가이드
├── OPENSEARCH-EXPLANATION.md   # OpenSearch 기능 설명
├── PROJECT-GUIDE.md            # 종합 프로젝트 가이드
├── .gitignore                  # Git 무시 파일 목록
├── docker-compose.yml          # OpenSearch 컨테이너 설정
├── opensearch-setup.sh         # 초기 설정 스크립트
├── Dockerfile                  # Docker 이미지 설정
└── mcp-server/                 # MCP 서버 핵심 코드
    ├── main.py                 # MCP 서버 (리팩토링됨)
    ├── core/                   # 핵심 모듈
    │   ├── config.py           # 설정 관리
    │   ├── exceptions.py       # 커스텀 예외
    │   └── logger.py           # 로깅 설정
    ├── services/               # 서비스 레이어
    │   ├── vector_service.py   # 벡터 DB 서비스
    │   ├── search_service.py   # 검색 서비스
    │   ├── document_service.py # 문서 처리 서비스
    │   └── employee_service.py # 사원 관리 서비스
    ├── auto_vector_db.py       # 기존 벡터 DB 관리
    ├── config.py               # 기존 설정
    ├── settings.py             # 환경 변수
    ├── employee_data.py        # 사원 데이터
    ├── vector_db.py            # 기존 벡터 DB
    ├── pdf_processor.py        # PDF 처리
    ├── google_drive.py         # Google Drive 연동
    ├── pyproject.toml          # 프로젝트 의존성
    └── requirements.txt        # Python 패키지 목록
```

## 🛠️ 기술 스택

- **MCP 서버**: Python FastMCP
- **벡터 DB**: OpenSearch 2.11.0
- **임베딩 모델**: sentence-transformers/all-MiniLM-L6-v2
- **컨테이너**: Docker & Docker Compose
- **외부 연동**: Google Drive API, PDF 처리

## 🔧 MCP 도구 목록

### 📄 문서 처리
- `getPdfToText`: PDF 파일에서 텍스트 추출
- `getPdfToMarkDown`: PDF 파일을 마크다운으로 변환
- `processDriveFile`: Google Drive 파일 처리

### 🔍 검색
- `searchCompanyKnowledge`: 회사 지식 베이스 검색
- `searchSpecifications`: 기획서 검색
- `getSpecificationById`: 특정 기획서 조회
- `getEmployeeList`: 사원 목록 조회

### 💾 벡터 DB 관리
- `addDocumentToVectorDB`: 문서를 벡터 DB에 추가
- `addEmployeeToVectorDB`: 사원 정보 추가

### 📋 기타
- `getCompanyRules`: 회사 규칙 조회

## 💡 사용 예시

### 기획서 검색
```
프롬프트: "opensearch에 저장하는 내용이 담긴 기획서를 찾아줘"
MCP 호출: searchSpecifications("opensearch에 저장하는 내용이 담긴 기획서를 찾아줘")
```

### 사원 정보 검색
```
프롬프트: "Python 개발자 찾아줘"
MCP 호출: searchCompanyKnowledge("Python 개발자", "employee")
```

## 🔄 리팩토링 내용

### 개선된 구조
- **모듈화**: 기능별로 서비스 레이어 분리
- **의존성 주입**: 서비스 간 느슨한 결합
- **에러 처리**: 커스텀 예외 클래스로 체계적 에러 관리
- **로깅**: 구조화된 로깅 시스템
- **설정 관리**: 환경별 설정 분리

### 새로운 파일 구조
- `core/`: 핵심 모듈 (설정, 예외, 로깅)
- `services/`: 비즈니스 로직 서비스
- `main.py`: 리팩토링된 메인 서버

## 📄 라이선스

MIT License

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

---

**마지막 업데이트**: 2024년 12월