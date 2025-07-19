#!/usr/bin/env python3
"""
자동화된 벡터 DB 구축 시스템
- 코드와 기획서 자동 매핑
- 카테고리 자동 분류
- 유사도 검색 최적화
- 자동 저장 시스템
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
import numpy as np

from config import get_vector_db_config
from settings import OPENSEARCH_INDEX
from google_drive import process_drive_file

@dataclass
class CodeDocument:
    """코드 문서 정보"""
    file_path: str
    content: str
    language: str
    framework: str
    category: str
    functions: List[str]
    classes: List[str]
    dependencies: List[str]
    metadata: Dict[str, Any]

@dataclass
class SpecDocument:
    """기획서 문서 정보"""
    file_id: str
    content: str
    title: str
    category: str
    features: List[str]
    requirements: List[str]
    metadata: Dict[str, Any]

class AutoVectorDB:
    """자동화된 벡터 DB 관리 시스템"""
    
    def __init__(self):
        self.config = get_vector_db_config()
        self.client = self.config['client']
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.index = OPENSEARCH_INDEX
        
        # 카테고리 매핑 규칙
        self.category_keywords = {
            'user': ['user', 'member', 'account', 'profile', 'auth', 'login', 'register'],
            'event': ['event', 'schedule', 'booking', 'reservation', 'calendar'],
            'payment': ['payment', 'billing', 'invoice', 'subscription', 'purchase'],
            'notification': ['notification', 'alert', 'message', 'email', 'sms'],
            'file': ['file', 'upload', 'download', 'document', 'attachment'],
            'api': ['api', 'endpoint', 'rest', 'graphql', 'service'],
            'database': ['database', 'model', 'schema', 'migration', 'query'],
            'ui': ['ui', 'component', 'page', 'view', 'template', 'layout'],
            'config': ['config', 'setting', 'environment', 'option'],
            'test': ['test', 'spec', 'mock', 'fixture', 'coverage']
        }
    
    def auto_categorize(self, content: str, doc_type: str = "code") -> str:
        """내용을 기반으로 자동 카테고리 분류"""
        content_lower = content.lower()
        
        # 코드 문서의 경우 파일 확장자와 내용 기반 분류
        if doc_type == "code":
            # 파일 확장자 기반 분류
            if any(ext in content_lower for ext in ['.py', 'python', 'django', 'flask']):
                return 'backend'
            elif any(ext in content_lower for ext in ['.js', '.ts', '.jsx', '.tsx', 'react', 'vue']):
                return 'frontend'
            elif any(ext in content_lower for ext in ['.sql', 'database', 'model']):
                return 'database'
            elif any(ext in content_lower for ext in ['.yml', '.yaml', '.json', 'config']):
                return 'config'
            elif any(ext in content_lower for ext in ['.test', '.spec', 'test_']):
                return 'test'
        
        # 키워드 기반 분류
        for category, keywords in self.category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def extract_code_features(self, content: str, file_path: str) -> Dict[str, Any]:
        """코드에서 특징 추출"""
        features = {
            'functions': [],
            'classes': [],
            'dependencies': [],
            'language': self._detect_language(file_path),
            'framework': self._detect_framework(content, file_path)
        }
        
        # 함수 추출
        if features['language'] == 'python':
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            features['functions'] = functions
        elif features['language'] in ['javascript', 'typescript']:
            functions = re.findall(r'(?:function\s+)?(\w+)\s*\([^)]*\)\s*{', content)
            features['functions'] = functions
        
        # 클래스 추출
        classes = re.findall(r'class\s+(\w+)', content)
        features['classes'] = classes
        
        # 의존성 추출
        if 'import' in content:
            imports = re.findall(r'import\s+([^\s]+)', content)
            features['dependencies'] = imports
        
        return features
    
    def _detect_language(self, file_path: str) -> str:
        """파일 확장자로 언어 감지"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss'
        }
        return language_map.get(ext, 'unknown')
    
    def _detect_framework(self, content: str, file_path: str) -> str:
        """프레임워크 감지"""
        content_lower = content.lower()
        
        if 'django' in content_lower or 'from django' in content_lower:
            return 'django'
        elif 'flask' in content_lower or 'from flask' in content_lower:
            return 'flask'
        elif 'react' in content_lower or 'import react' in content_lower:
            return 'react'
        elif 'vue' in content_lower or 'import vue' in content_lower:
            return 'vue'
        elif 'angular' in content_lower:
            return 'angular'
        elif 'spring' in content_lower:
            return 'spring'
        elif 'express' in content_lower:
            return 'express'
        
        return 'vanilla'
    
    def extract_spec_features(self, content: str) -> Dict[str, Any]:
        """기획서에서 특징 추출"""
        features = {
            'features': [],
            'requirements': [],
            'entities': []
        }
        
        # 기능 요구사항 추출
        feature_patterns = [
            r'기능[:\s]*([^\n]+)',
            r'feature[:\s]*([^\n]+)',
            r'요구사항[:\s]*([^\n]+)',
            r'requirement[:\s]*([^\n]+)'
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            features['features'].extend(matches)
        
        # 엔티티 추출 (사용자, 이벤트, 결제 등)
        entity_keywords = ['사용자', '회원', '이벤트', '결제', '알림', '파일', 'API']
        for keyword in entity_keywords:
            if keyword in content:
                features['entities'].append(keyword)
        
        return features
    
    def create_code_document(self, file_path: str, content: str) -> CodeDocument:
        """코드 문서 생성"""
        features = self.extract_code_features(content, file_path)
        category = self.auto_categorize(content, "code")
        
        return CodeDocument(
            file_path=file_path,
            content=content,
            language=features['language'],
            framework=features['framework'],
            category=category,
            functions=features['functions'],
            classes=features['classes'],
            dependencies=features['dependencies'],
            metadata={
                'file_size': len(content),
                'lines': len(content.split('\n')),
                'created_at': datetime.now().isoformat()
            }
        )
    
    def create_spec_document(self, file_id: str, content: str, title: str = "") -> SpecDocument:
        """기획서 문서 생성"""
        features = self.extract_spec_features(content)
        category = self.auto_categorize(content, "spec")
        
        return SpecDocument(
            file_id=file_id,
            content=content,
            title=title or f"기획서_{file_id}",
            category=category,
            features=features['features'],
            requirements=features['requirements'],
            metadata={
                'file_id': file_id,
                'content_length': len(content),
                'created_at': datetime.now().isoformat()
            }
        )
    
    def add_code_to_vector_db(self, file_path: str) -> bool:
        """코드 파일을 벡터 DB에 추가"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc = self.create_code_document(file_path, content)
            embedding = self.embedder.encode(content).tolist()
            
            doc_body = {
                "content": content,
                "doc_type": "code",
                "embedding": embedding,
                "file_path": doc.file_path,
                "language": doc.language,
                "framework": doc.framework,
                "category": doc.category,
                "functions": doc.functions,
                "classes": doc.classes,
                "dependencies": doc.dependencies,
                "metadata": doc.metadata
            }
            
            self.client.index(
                index=self.index,
                body=doc_body,
                id=f"code_{doc.file_path.replace('/', '_')}"
            )
            
            print(f"✅ 코드 추가 완료: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 코드 추가 실패: {file_path} - {e}")
            return False
    
    def add_spec_from_drive(self, file_id: str, mode: str = "text") -> bool:
        """Google Drive 기획서를 벡터 DB에 추가"""
        try:
            content = process_drive_file(file_id, mode)
            if not content:
                return False
            
            doc = self.create_spec_document(file_id, content)
            embedding = self.embedder.encode(content).tolist()
            
            doc_body = {
                "content": content,
                "doc_type": "spec",
                "embedding": embedding,
                "file_id": doc.file_id,
                "title": doc.title,
                "category": doc.category,
                "features": doc.features,
                "requirements": doc.requirements,
                "metadata": doc.metadata
            }
            
            self.client.index(
                index=self.index,
                body=doc_body,
                id=f"spec_{doc.file_id}"
            )
            
            print(f"✅ 기획서 추가 완료: {doc.title}")
            return True
            
        except Exception as e:
            print(f"❌ 기획서 추가 실패: {file_id} - {e}")
            return False
    
    def add_spec_from_content(self, spec_id: str, content: str, title: str = "") -> bool:
        """직접 내용으로 기획서를 벡터 DB에 추가"""
        try:
            doc = self.create_spec_document(spec_id, content)
            embedding = self.embedder.encode(content).tolist()
            
            doc_body = {
                "content": content,
                "doc_type": "spec",
                "embedding": embedding,
                "file_id": doc.file_id,
                "title": title or doc.title,
                "category": doc.category,
                "features": doc.features,
                "requirements": doc.requirements,
                "metadata": doc.metadata
            }
            
            self.client.index(
                index=self.index,
                body=doc_body,
                id=f"spec_{doc.file_id}"
            )
            
            print(f"✅ 기획서 추가 완료: {title or doc.title}")
            return True
            
        except Exception as e:
            print(f"❌ 기획서 추가 실패: {spec_id} - {e}")
            return False
    
    def search_similar_documents(self, query: str, doc_type: str = "all", 
                               category: str = None, max_results: int = 10) -> List[Dict]:
        """유사한 문서 검색 (텍스트 검색 기반)"""
        try:
            # 쿼리 구성
            must_conditions = []
            
            if doc_type != "all":
                must_conditions.append({"term": {"doc_type": doc_type}})
            
            if category:
                must_conditions.append({"term": {"category": category}})
            
            # 텍스트 검색 조건 추가
            must_conditions.append({
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
            
            query_body = {
                "size": max_results,
                "query": {
                    "bool": {
                        "must": must_conditions
                    }
                }
            }
            
            response = self.client.search(
                body=query_body,
                index=self.index
            )
            
            return response['hits']['hits']
            
        except Exception as e:
            print(f"검색 오류: {e}")
            return []
    
    def get_code_for_spec(self, spec_file_id: str, max_results: int = 5) -> Dict[str, Any]:
        """기획서에 맞는 코드 검색"""
        try:
            # 기획서 내용 가져오기
            spec_response = self.client.search(
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"doc_type": "spec"}},
                                {"term": {"file_id": spec_file_id}}
                            ]
                        }
                    }
                },
                index=self.index
            )
            
            if not spec_response['hits']['hits']:
                return {"error": "기획서를 찾을 수 없습니다."}
            
            spec_content = spec_response['hits']['hits'][0]['_source']['content']
            
            # 기획서 내용으로 유사한 코드 검색
            similar_codes = self.search_similar_documents(
                spec_content, 
                doc_type="code", 
                max_results=max_results
            )
            
            return {
                "spec": {
                    "file_id": spec_file_id,
                    "content": spec_content,
                    "title": spec_response['hits']['hits'][0]['_source'].get('title', '')
                },
                "similar_codes": [
                    {
                        "file_path": hit['_source']['file_path'],
                        "content": hit['_source']['content'][:500] + "...",
                        "language": hit['_source']['language'],
                        "framework": hit['_source']['framework'],
                        "category": hit['_source']['category'],
                        "similarity_score": hit['_score']
                    }
                    for hit in similar_codes
                ]
            }
            
        except Exception as e:
            return {"error": f"검색 중 오류 발생: {e}"}
    
    def batch_add_code_directory(self, directory_path: str, extensions: List[str] = None) -> Dict[str, int]:
        """디렉토리의 모든 코드 파일을 일괄 추가"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.go', '.php', '.rb']
        
        success_count = 0
        fail_count = 0
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    if self.add_code_to_vector_db(file_path):
                        success_count += 1
                    else:
                        fail_count += 1
        
        return {
            "success": success_count,
            "failed": fail_count,
            "total": success_count + fail_count
        }

# 사용 예시
if __name__ == "__main__":
    auto_db = AutoVectorDB()
    
    # 코드 디렉토리 일괄 추가
    # result = auto_db.batch_add_code_directory("./src")
    # print(f"코드 추가 결과: {result}")
    
    # 기획서 추가
    # auto_db.add_spec_from_drive("your_google_drive_file_id")
    
    # 유사한 문서 검색
    # results = auto_db.search_similar_documents("사용자 인증 기능", doc_type="code", category="user")
    # print(f"검색 결과: {len(results)}개") 