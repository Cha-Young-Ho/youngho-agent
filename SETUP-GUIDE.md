# 🛠️ 프로젝트 셋팅 가이드

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [Mac 환경 설정](#mac-환경-설정)
3. [Python 환경 설정](#python-환경-설정)
4. [Docker 설정](#docker-설정)
5. [OpenSearch 설정](#opensearch-설정)
6. [MCP 서버 설정](#mcp-서버-설정)
7. [데이터 설정](#데이터-설정)
8. [테스트 및 검증](#테스트-및-검증)

---

## 🖥️ 시스템 요구사항

### 최소 요구사항
- **OS**: macOS 12.0+ (Monterey)
- **RAM**: 8GB 이상 (OpenSearch 권장 4GB)
- **Storage**: 10GB 이상 여유 공간
- **CPU**: 2코어 이상

### 권장 사항
- **RAM**: 16GB 이상
- **Storage**: 20GB 이상 여유 공간
- **CPU**: 4코어 이상

---

## 🍎 Mac 환경 설정

### 1. Homebrew 설치
```bash
# Homebrew 설치 (이미 설치되어 있다면 생략)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Homebrew 업데이트
brew update
```

### 2. 필수 도구 설치
```bash
# Git 설치
brew install git

# wget 설치 (파일 다운로드용)
brew install wget

# jq 설치 (JSON 처리용)
brew install jq

# curl 업데이트 (이미 설치되어 있음)
brew install curl
```

### 3. 개발 도구 설치
```bash
# Visual Studio Code 설치 (선택사항)
brew install --cask visual-studio-code

# iTerm2 설치 (선택사항)
brew install --cask iterm2
```

---

## 🐍 Python 환경 설정

### 1. Python 설치
```bash
# Python 3.11 설치 (권장 버전)
brew install python@3.11

# Python 경로 확인
python3.11 --version
which python3.11
```

### 2. pyenv 설치 (Python 버전 관리)
```bash
# pyenv 설치
brew install pyenv

# shell 설정 추가
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# shell 재시작 또는 설정 적용
source ~/.zshrc

# Python 3.11.7 설치 및 설정
pyenv install 3.11.7
pyenv global 3.11.7
pyenv local 3.11.7
```

### 3. 가상환경 설정
```bash
# 프로젝트 디렉토리로 이동
cd /path/to/youngho-agent

# 가상환경 생성
python3.11 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

---

## 🐳 Docker 설정

### 1. Docker Desktop 설치
```bash
# Docker Desktop 설치
brew install --cask docker

# Docker Desktop 실행
open /Applications/Docker.app
```

### 2. Docker 설정 확인
```bash
# Docker 버전 확인
docker --version
docker-compose --version

# Docker 데몬 상태 확인
docker info

# Docker 권한 확인
docker run hello-world
```

### 3. Docker 리소스 설정
Docker Desktop > Settings > Resources에서:
- **Memory**: 4GB 이상 할당
- **CPU**: 2코어 이상 할당
- **Disk**: 20GB 이상 할당

---

## 🔍 OpenSearch 설정

### 1. OpenSearch 컨테이너 실행
```bash
# 프로젝트 루트 디렉토리에서
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs opensearch
```

### 2. OpenSearch 초기 설정
```bash
# 초기 설정 스크립트 실행
chmod +x opensearch-setup.sh
./opensearch-setup.sh
```

### 3. OpenSearch 상태 확인
```bash
# 클러스터 상태 확인
curl -X GET "localhost:9200/_cluster/health?pretty" -u admin:admin

# 인덱스 목록 확인
curl -X GET "localhost:9200/_cat/indices?v" -u admin:admin

# 플러그인 목록 확인
curl -X GET "localhost:9200/_cat/plugins?v" -u admin:admin
```

---

## 🚀 MCP 서버 설정

### 1. 의존성 설치
```bash
# mcp-server 디렉토리로 이동
cd mcp-server

# 가상환경 활성화 (아직 활성화되지 않은 경우)
source ../.venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 또는 pyproject.toml 사용
pip install -e .
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
cat > .env << EOF
ENVIRONMENT=local
OPENSEARCH_ENDPOINT=localhost:9200
OPENSEARCH_INDEX=company-knowledge
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=admin
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/your/service-account.json
GOOGLE_SCOPES=https://www.googleapis.com/auth/drive.readonly
VECTOR_DB_PATH=./vector_db
VECTOR_DB_COLLECTION=company_docs
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
EOF
```

### 3. MCP 서버 실행
```bash
# 서버 실행
python main.py

# 백그라운드 실행 (선택사항)
nohup python main.py > mcp-server.log 2>&1 &
```

---

## 📊 데이터 설정

### 1. 샘플 데이터 구조

#### 사원 데이터 (employee)
```json
{
  "employee_id": "EMP001",
  "name": "김철수",
  "position": "시니어 개발자",
  "department": "개발팀",
  "email": "kim@company.com",
  "phone": "010-1234-5678",
  "skills": ["Python", "JavaScript", "React"],
  "projects": ["웹 애플리케이션", "API 개발"],
  "hire_date": "2022-01-15",
  "responsibilities": "백엔드 개발, API 설계"
}
```

#### 코드 데이터 (code)
```json
{
  "file_path": "src/api/user_controller.py",
  "content": "코드 내용...",
  "language": "python",
  "framework": "django",
  "category": "user",
  "functions": ["get_user", "create_user", "update_user"],
  "classes": ["UserController"],
  "dependencies": ["django", "rest_framework"],
  "metadata": {
    "author": "김철수",
    "lines": 150,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 기획서 데이터 (spec)
```json
{
  "file_id": "spec_user_auth",
  "title": "사용자 인증 시스템 기획서",
  "content": "기획서 내용...",
  "category": "user",
  "features": ["로그인", "회원가입", "비밀번호 재설정"],
  "requirements": ["JWT 토큰", "OAuth2", "2FA"],
  "metadata": {
    "author": "이영희",
    "version": "1.0",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. 데이터 추가 명령어

#### 사원 데이터 추가
```bash
# 개별 사원 추가
curl -X POST "localhost:9200/company-knowledge/_doc" \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "employee_id": "EMP001",
    "name": "김철수",
    "position": "시니어 개발자",
    "department": "개발팀",
    "doc_type": "employee",
    "skills": ["Python", "JavaScript", "React"]
  }'
```

#### 코드 데이터 추가
```bash
# 코드 파일 추가
curl -X POST "localhost:9200/company-knowledge/_doc" \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "file_path": "src/api/user_controller.py",
    "content": "코드 내용...",
    "language": "python",
    "framework": "django",
    "category": "user",
    "doc_type": "code"
  }'
```

#### 기획서 데이터 추가
```bash
# 기획서 추가
curl -X POST "localhost:9200/company-knowledge/_doc" \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "file_id": "spec_user_auth",
    "title": "사용자 인증 시스템 기획서",
    "content": "기획서 내용...",
    "category": "user",
    "doc_type": "spec"
  }'
```

### 3. 데이터 조회 명령어

#### 전체 데이터 조회
```bash
# 모든 문서 조회
curl -X GET "localhost:9200/company-knowledge/_search?pretty" \
  -u admin:admin \
  -d '{"size": 10}'
```

#### 타입별 데이터 조회
```bash
# 사원 데이터만 조회
curl -X GET "localhost:9200/company-knowledge/_search?pretty" \
  -u admin:admin \
  -d '{
    "query": {"term": {"doc_type": "employee"}},
    "size": 10
  }'

# 코드 데이터만 조회
curl -X GET "localhost:9200/company-knowledge/_search?pretty" \
  -u admin:admin \
  -d '{
    "query": {"term": {"doc_type": "code"}},
    "size": 10
  }'

# 기획서 데이터만 조회
curl -X GET "localhost:9200/company-knowledge/_search?pretty" \
  -u admin:admin \
  -d '{
    "query": {"term": {"doc_type": "spec"}},
    "size": 10
  }'
```

#### 검색 쿼리
```bash
# 텍스트 검색
curl -X GET "localhost:9200/company-knowledge/_search?pretty" \
  -u admin:admin \
  -d '{
    "query": {
      "multi_match": {
        "query": "Python",
        "fields": ["title", "content", "skills"]
      }
    },
    "size": 10
  }'

# 카테고리별 검색
curl -X GET "localhost:9200/company-knowledge/_search?pretty" \
  -u admin:admin \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"doc_type": "employee"}},
          {"term": {"category": "user"}}
        ]
      }
    },
    "size": 10
  }'
```

---

## 🧪 테스트 및 검증

### 1. OpenSearch 연결 테스트
```bash
# 클러스터 상태 확인
curl -X GET "localhost:9200/_cluster/health?pretty" -u admin:admin

# 인덱스 상태 확인
curl -X GET "localhost:9200/company-knowledge/_stats?pretty" -u admin:admin
```

### 2. MCP 서버 연결 테스트
```bash
# 서버 상태 확인
curl -X GET "http://localhost:8000/health"

# 도구 목록 확인
curl -X GET "http://localhost:8000/tools"
```

### 3. 데이터 검증
```bash
# 문서 수 확인
curl -X GET "localhost:9200/company-knowledge/_count?pretty" \
  -u admin:admin \
  -d '{"query": {"match_all": {}}}'

# 타입별 문서 수 확인
curl -X GET "localhost:9200/company-knowledge/_count?pretty" \
  -u admin:admin \
  -d '{"query": {"term": {"doc_type": "employee"}}}'
```

---

## 🔧 문제 해결

### 1. Docker 문제
```bash
# Docker 재시작
docker-compose down
docker-compose up -d

# Docker 로그 확인
docker-compose logs -f opensearch
```

### 2. Python 문제
```bash
# 가상환경 재생성
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. OpenSearch 문제
```bash
# 인덱스 재생성
curl -X DELETE "localhost:9200/company-knowledge" -u admin:admin
./opensearch-setup.sh
```

---

## 📚 추가 리소스

- [OpenSearch 공식 문서](https://opensearch.org/docs/)
- [Docker 공식 문서](https://docs.docker.com/)
- [Python 공식 문서](https://docs.python.org/)
- [MCP 공식 문서](https://modelcontextprotocol.io/) 