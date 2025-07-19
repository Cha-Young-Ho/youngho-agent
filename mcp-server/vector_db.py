import os
from config import get_vector_db_config
from settings import OPENSEARCH_INDEX, CHUNK_SIZE

def search_vector_db(query: str, n_results: int = 5):
    try:
        config = get_vector_db_config()
        embedder = config['embedder']
        client = config['client']
        
        query_embedding = embedder.encode(query).tolist()
        query_body = {
            "size": n_results,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": n_results
                    }
                }
            }
        }
        response = client.search(
            body=query_body, 
            index=OPENSEARCH_INDEX
        )
        return response['hits']['hits']
    except Exception as e:
        print(f"OpenSearch 검색 오류: {e}")
        return None

def add_document_to_vector_db(file_path: str, doc_type: str = "code"):
    """OpenSearch에 파일 문서 추가"""
    try:
        config = get_vector_db_config()
        embedder = config['embedder']
        client = config['client']
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = split_text_into_chunks(content, chunk_size=CHUNK_SIZE)
        
        for i, chunk in enumerate(chunks):
            embedding = embedder.encode(chunk).tolist()
            doc_body = {
                "content": chunk,
                "file_path": file_path,
                "doc_type": doc_type,
                "chunk_id": i,
                "embedding": embedding
            }
            client.index(
                index=OPENSEARCH_INDEX,
                body=doc_body,
                id=f"{file_path}_{i}"
            )
        return True
    except Exception as e:
        print(f"OpenSearch 문서 추가 오류: {e}")
        return False

def add_content_to_vector_db(content: str, doc_type: str = "text", metadata: dict = None):
    """OpenSearch에 직접 내용 추가"""
    try:
        config = get_vector_db_config()
        embedder = config['embedder']
        client = config['client']
        
        if metadata is None:
            metadata = {}
        
        embedding = embedder.encode(content).tolist()
        doc_body = {
            "content": content,
            "doc_type": doc_type,
            **metadata,
            "embedding": embedding
        }
        client.index(
            index=OPENSEARCH_INDEX,
            body=doc_body,
            id=f"{doc_type}_{metadata.get('id', 'unknown')}"
        )
        return True
    except Exception as e:
        print(f"OpenSearch 내용 추가 오류: {e}")
        return False

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    """텍스트를 청크로 분할"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        if current_size + len(word) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks 