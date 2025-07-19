"""
Configuration management for MCP server.
"""

import os
from dataclasses import dataclass
from typing import Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from sentence_transformers import SentenceTransformer


@dataclass
class OpenSearchConfig:
    """OpenSearch connection configuration."""
    hosts: list
    username: str
    password: str
    use_ssl: bool = False
    verify_certs: bool = False
    index: str = "company-knowledge"


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384


@dataclass
class GoogleDriveConfig:
    """Google Drive configuration."""
    service_account_file: str
    scopes: list


class Config:
    """Main configuration class for MCP server."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "local")
        self.opensearch = self._load_opensearch_config()
        self.embedding = self._load_embedding_config()
        self.google_drive = self._load_google_drive_config()
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        
        # Initialize clients
        self.opensearch_client = self._create_opensearch_client()
        self.embedding_model = self._create_embedding_model()
    
    def _load_opensearch_config(self) -> OpenSearchConfig:
        """Load OpenSearch configuration from environment variables."""
        if self.environment == "local":
            return OpenSearchConfig(
                hosts=[{'host': 'localhost', 'port': 9200}],
                username=os.getenv("OPENSEARCH_USERNAME", "admin"),
                password=os.getenv("OPENSEARCH_PASSWORD", "admin"),
                use_ssl=False,
                verify_certs=False,
                index=os.getenv("OPENSEARCH_INDEX", "company-knowledge")
            )
        else:
            # Production configuration
            return OpenSearchConfig(
                hosts=[{'host': os.getenv("OPENSEARCH_ENDPOINT"), 'port': 443}],
                username=os.getenv("OPENSEARCH_USERNAME", ""),
                password=os.getenv("OPENSEARCH_PASSWORD", ""),
                use_ssl=True,
                verify_certs=True,
                index=os.getenv("OPENSEARCH_INDEX", "company-knowledge")
            )
    
    def _load_embedding_config(self) -> EmbeddingConfig:
        """Load embedding configuration from environment variables."""
        return EmbeddingConfig(
            model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            dimension=int(os.getenv("EMBEDDING_DIMENSION", "384"))
        )
    
    def _load_google_drive_config(self) -> GoogleDriveConfig:
        """Load Google Drive configuration from environment variables."""
        return GoogleDriveConfig(
            service_account_file=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", ""),
            scopes=[os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/drive.readonly")]
        )
    
    def _create_opensearch_client(self) -> OpenSearch:
        """Create OpenSearch client instance."""
        return OpenSearch(
            hosts=self.opensearch.hosts,
            http_auth=(self.opensearch.username, self.opensearch.password),
            use_ssl=self.opensearch.use_ssl,
            verify_certs=self.opensearch.verify_certs,
            connection_class=RequestsHttpConnection
        )
    
    def _create_embedding_model(self) -> SentenceTransformer:
        """Create embedding model instance."""
        return SentenceTransformer(self.embedding.model_name)
    
    def get_vector_db_config(self) -> dict:
        """Get vector database configuration for backward compatibility."""
        return {
            'type': 'opensearch',
            'client': self.opensearch_client,
            'embedder': self.embedding_model,
            'index': self.opensearch.index
        }


# Global configuration instance
config = Config() 