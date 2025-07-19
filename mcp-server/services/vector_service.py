"""
Vector database service for managing embeddings and vector operations.
"""

import json
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer

from ..core import config, get_logger, OpenSearchError, ValidationError
from ..core.exceptions import SearchError

logger = get_logger(__name__)


class VectorService:
    """Service for managing vector operations with OpenSearch."""
    
    def __init__(self):
        self.client = config.opensearch_client
        self.embedder = config.embedding_model
        self.index = config.opensearch.index
        self.dimension = config.embedding.dimension
    
    def create_index(self) -> bool:
        """
        Create the OpenSearch index with proper mapping.
        
        Returns:
            True if index created successfully, False otherwise
        """
        try:
            # Check if index already exists
            if self.client.indices.exists(index=self.index):
                logger.info(f"Index {self.index} already exists")
                return True
            
            # Create index mapping
            mapping = {
                "mappings": {
                    "properties": {
                        "doc_type": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": self.dimension,
                            "method": {
                                "engine": "nmslib",
                                "space_type": "cosinesimil",
                                "name": "hnsw",
                                "parameters": {
                                    "ef_construction": 128,
                                    "m": 16
                                }
                            }
                        },
                        "category": {"type": "keyword"},
                        "metadata": {"type": "object", "enabled": True},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                }
            }
            
            # Create index
            response = self.client.indices.create(
                index=self.index,
                body=mapping
            )
            
            logger.info(f"Index {self.index} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise OpenSearchError(f"Index creation failed: {e}")
    
    def add_document(self, doc_type: str, title: str, content: str, 
                    category: str = "general", metadata: Optional[Dict] = None) -> str:
        """
        Add a document to the vector database.
        
        Args:
            doc_type: Type of document (employee, code, spec)
            title: Document title
            content: Document content
            category: Document category
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            # Generate embedding
            embedding = self.embedder.encode(content).tolist()
            
            # Prepare document
            doc = {
                "doc_type": doc_type,
                "title": title,
                "content": content,
                "embedding": embedding,
                "category": category,
                "metadata": metadata or {},
                "created_at": "now",
                "updated_at": "now"
            }
            
            # Index document
            response = self.client.index(
                index=self.index,
                body=doc
            )
            
            doc_id = response['_id']
            logger.info(f"Document added successfully with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise OpenSearchError(f"Document addition failed: {e}")
    
    def search_similar(self, query: str, doc_type: Optional[str] = None, 
                      k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            doc_type: Filter by document type
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Build search query
            search_body = {
                "size": k,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "knn": {
                                    "embedding": {
                                        "vector": query_embedding,
                                        "k": k
                                    }
                                }
                            }
                        ]
                    }
                },
                "_source": ["title", "content", "doc_type", "category", "metadata"]
            }
            
            # Add doc_type filter if specified
            if doc_type:
                search_body["query"]["bool"]["filter"] = [
                    {"term": {"doc_type": doc_type}}
                ]
            
            # Execute search
            response = self.client.search(
                index=self.index,
                body=search_body
            )
            
            # Process results
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'id': hit['_id'],
                    'score': hit['_score'],
                    **hit['_source']
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise SearchError(f"Vector search failed: {e}")
    
    def search_text(self, query: str, doc_type: Optional[str] = None, 
                   k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents using text-based search.
        
        Args:
            query: Search query
            doc_type: Filter by document type
            k: Number of results to return
            
        Returns:
            List of matching documents
        """
        try:
            # Build search query
            search_body = {
                "size": k,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^2", "content"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "_source": ["title", "content", "doc_type", "category", "metadata"]
            }
            
            # Add doc_type filter if specified
            if doc_type:
                search_body["query"]["bool"]["filter"] = [
                    {"term": {"doc_type": doc_type}}
                ]
            
            # Execute search
            response = self.client.search(
                index=self.index,
                body=search_body
            )
            
            # Process results
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'id': hit['_id'],
                    'score': hit['_score'],
                    **hit['_source']
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} matching documents")
            return results
            
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            raise SearchError(f"Text search failed: {e}")
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            response = self.client.get(
                index=self.index,
                id=doc_id
            )
            
            return {
                'id': response['_id'],
                **response['_source']
            }
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            response = self.client.delete(
                index=self.index,
                id=doc_id
            )
            
            logger.info(f"Document {doc_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Index statistics
        """
        try:
            # Get document count
            count_response = self.client.count(index=self.index)
            total_docs = count_response['count']
            
            # Get document type distribution
            agg_response = self.client.search(
                index=self.index,
                body={
                    "size": 0,
                    "aggs": {
                        "doc_types": {
                            "terms": {
                                "field": "doc_type",
                                "size": 10
                            }
                        },
                        "categories": {
                            "terms": {
                                "field": "category",
                                "size": 10
                            }
                        }
                    }
                }
            )
            
            stats = {
                'total_documents': total_docs,
                'doc_type_distribution': {
                    bucket['key']: bucket['doc_count'] 
                    for bucket in agg_response['aggregations']['doc_types']['buckets']
                },
                'category_distribution': {
                    bucket['key']: bucket['doc_count'] 
                    for bucket in agg_response['aggregations']['categories']['buckets']
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise OpenSearchError(f"Stats retrieval failed: {e}")


# Global vector service instance
vector_service = VectorService() 