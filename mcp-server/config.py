import os
import chromadb
from sentence_transformers import SentenceTransformer
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from settings import (
    ENVIRONMENT, 
    OPENSEARCH_ENDPOINT, 
    OPENSEARCH_INDEX,
    OPENSEARCH_USERNAME,
    OPENSEARCH_PASSWORD,
    GOOGLE_SERVICE_ACCOUNT_FILE,
    GOOGLE_SCOPES,
    VECTOR_DB_PATH,
    VECTOR_DB_COLLECTION,
    EMBEDDING_MODEL
)

# 벡터 DB 설정
def get_vector_db_config():
    # 로컬과 프로덕션 모두 OpenSearch 사용
    if ENVIRONMENT == 'local':
        # 로컬 OpenSearch 설정
        opensearch_client = OpenSearch(
            hosts=[{'host': 'localhost', 'port': 9200}],
            http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
            use_ssl=False,
            verify_certs=False,
            connection_class=RequestsHttpConnection
        )
    else:
        # AWS OpenSearch 설정
        session = boto3.Session()
        credentials = session.get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key, 
            credentials.secret_key, 
            session.region_name, 
            'es', 
            session_token=credentials.token
        )
        opensearch_client = OpenSearch(
            hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
    
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    return {
        'type': 'opensearch',
        'client': opensearch_client,
        'embedder': embedder
    }

# Google Drive 설정
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'path/to/your/service-account.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly'] 