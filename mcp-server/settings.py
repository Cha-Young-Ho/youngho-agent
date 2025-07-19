# 환경 설정
ENVIRONMENT = "local"  # "local" 또는 "production"

# OpenSearch 설정 (로컬 및 프로덕션 공통)
OPENSEARCH_ENDPOINT = "localhost:9200"  # 로컬: localhost:9200, 프로덕션: your-domain.region.es.amazonaws.com
OPENSEARCH_INDEX = "company-knowledge"
OPENSEARCH_USERNAME = "admin"  # 로컬 OpenSearch 기본 사용자
OPENSEARCH_PASSWORD = "admin"  # 로컬 OpenSearch 기본 비밀번호

# Google Drive 설정
GOOGLE_SERVICE_ACCOUNT_FILE = "path/to/your/service-account.json"
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# 벡터 DB 설정 (ChromaDB는 백업용으로 유지)
VECTOR_DB_PATH = "./vector_db"
VECTOR_DB_COLLECTION = "company_docs"

# 임베딩 모델 설정
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# 텍스트 청크 설정
CHUNK_SIZE = 1000 