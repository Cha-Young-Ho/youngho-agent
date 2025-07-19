# 🔍 OpenSearch 기능 및 설계 설명

## 📋 목차
1. [OpenSearch 선택 이유](#opensearch-선택-이유)
2. [사용한 주요 기능들](#사용한-주요-기능들)
3. [인덱스 설계](#인덱스-설계)
4. [검색 전략](#검색-전략)
5. [성능 최적화](#성능-최적화)
6. [확장성 고려사항](#확장성-고려사항)

---

## 🎯 OpenSearch 선택 이유

### 1. 벡터 검색 지원
- **k-NN 플러그인**: 고성능 벡터 유사도 검색
- **다양한 알고리즘**: HNSW, IVF, LSH 등 지원
- **실시간 검색**: 빠른 응답 시간

### 2. 텍스트 검색 강점
- **Elasticsearch 기반**: 강력한 텍스트 검색 엔진
- **다양한 쿼리 타입**: match, term, bool, range 등
- **스코어링 시스템**: TF-IDF, BM25 등

### 3. 하이브리드 검색
- **텍스트 + 벡터**: 두 검색 방식을 결합
- **가중치 조정**: 검색 정확도 향상
- **유연한 쿼리**: 복잡한 검색 조건 지원

### 4. 오픈소스
- **무료 사용**: 라이선스 비용 없음
- **커뮤니티**: 활발한 개발 및 지원
- **커스터마이징**: 자유로운 수정 및 확장

---

## 🛠️ 사용한 주요 기능들

### 1. k-NN 벡터 검색

#### HNSW (Hierarchical Navigable Small World)
```json
{
  "embedding": {
    "type": "knn_vector",
    "dimension": 384,
    "method": {
      "engine": "nmslib",
      "space_type": "cosinesimil",
      "name": "hnsw",
      "parameters": {
        "ef_construction": 128,
        "m": 16
      }
    }
  }
}
```

**선택 이유:**
- **빠른 검색**: O(log n) 시간 복잡도
- **높은 정확도**: 근사 최근접 이웃 검색
- **메모리 효율**: 계층적 구조로 메모리 사용량 최적화

**파라미터 설명:**
- `ef_construction`: 인덱스 구축 시 검색 품질 (높을수록 정확하지만 느림)
- `m`: 각 노드의 최대 연결 수 (높을수록 정확하지만 메모리 사용량 증가)

#### 코사인 유사도
```json
"space_type": "cosinesimil"
```

**선택 이유:**
- **방향성 고려**: 벡터의 방향이 중요할 때 적합
- **정규화 효과**: 벡터 크기에 영향받지 않음
- **텍스트 임베딩에 적합**: 의미적 유사도 측정에 효과적

### 2. 텍스트 검색

#### Multi-Match 쿼리
```json
{
  "multi_match": {
    "query": "Python 개발자",
    "fields": ["title", "content", "skills"],
    "type": "best_fields",
    "fuzziness": "AUTO"
  }
}
```

**선택 이유:**
- **다중 필드 검색**: 여러 필드에서 동시 검색
- **퍼지 매칭**: 오타나 유사한 단어 허용
- **스코어링**: 가장 관련성 높은 필드 기준으로 점수 계산

#### Bool 쿼리
```json
{
  "bool": {
    "must": [
      {"term": {"doc_type": "employee"}},
      {"term": {"category": "user"}}
    ],
    "should": [
      {"match": {"skills": "Python"}}
    ],
    "filter": [
      {"range": {"hire_date": {"gte": "2022-01-01"}}}
    ]
  }
}
```

**선택 이유:**
- **복합 조건**: AND, OR, NOT 논리 연산
- **필터링**: 스코어에 영향 없는 조건
- **성능 최적화**: 필터는 캐싱되어 빠른 실행

### 3. 집계 (Aggregation)

#### 카테고리별 통계
```json
{
  "aggs": {
    "categories": {
      "terms": {
        "field": "category",
        "size": 10
      }
    }
  }
}
```

**사용 목적:**
- **데이터 분석**: 카테고리별 문서 수 확인
- **시각화**: 차트 및 대시보드 구성
- **모니터링**: 데이터 분포 파악

---

## 🏗️ 인덱스 설계

### 1. 인덱스 매핑

#### 문서 타입별 필드 설계
```json
{
  "mappings": {
    "properties": {
      "doc_type": {
        "type": "keyword",
        "index": true
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 384
      },
      "category": {
        "type": "keyword",
        "index": true
      },
      "metadata": {
        "type": "object",
        "enabled": true
      }
    }
  }
}
```

**설계 원칙:**
- **단일 인덱스**: 모든 문서 타입을 하나의 인덱스에 저장
- **공통 필드**: doc_type으로 문서 구분
- **유연한 스키마**: metadata 필드로 확장 가능

### 2. 샤딩 전략

#### 단일 샤드 설정
```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}
```

**선택 이유:**
- **개발 환경**: 단순한 설정으로 빠른 개발
- **리소스 효율**: 적은 메모리 사용량
- **확장 가능**: 필요시 샤드 수 증가 가능

### 3. 분석기 설정

#### Standard Analyzer
```json
{
  "content": {
    "type": "text",
    "analyzer": "standard"
  }
}
```

**선택 이유:**
- **언어 무관**: 모든 언어 지원
- **토큰화**: 공백 기준 단어 분리
- **정규화**: 소문자 변환, 불용어 제거

---

## 🔍 검색 전략

### 1. 하이브리드 검색

#### 텍스트 + 벡터 결합
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"doc_type": "spec"}}
      ],
      "should": [
        {
          "multi_match": {
            "query": "사용자 인증",
            "fields": ["title", "content"],
            "boost": 2.0
          }
        }
      ],
      "filter": [
        {
          "knn": {
            "embedding": {
              "vector": [0.1, 0.2, ...],
              "k": 10
            }
          }
        }
      ]
    }
  }
}
```

**전략 설명:**
- **텍스트 검색**: 정확한 키워드 매칭
- **벡터 검색**: 의미적 유사도
- **가중치 조정**: 텍스트 검색에 더 높은 가중치

### 2. 페이징 및 정렬

#### 스크롤 검색
```json
{
  "size": 100,
  "sort": [
    {"_score": {"order": "desc"}},
    {"created_at": {"order": "desc"}}
  ]
}
```

**사용 이유:**
- **대용량 데이터**: 효율적인 페이징
- **정렬**: 관련성 + 시간순 정렬
- **성능**: 인덱스 활용한 빠른 정렬

### 3. 필터링 최적화

#### Term 필터
```json
{
  "filter": [
    {"term": {"doc_type": "employee"}},
    {"term": {"category": "user"}}
  ]
}
```

**최적화 이유:**
- **캐싱**: 필터 결과 캐싱
- **스코어 무관**: 검색 점수에 영향 없음
- **빠른 실행**: 인덱스 기반 빠른 필터링

---

## ⚡ 성능 최적화

### 1. 인덱스 최적화

#### 매핑 최적화
```json
{
  "settings": {
    "index": {
      "max_result_window": 10000,
      "refresh_interval": "1s"
    }
  }
}
```

**최적화 내용:**
- **결과 창 제한**: 메모리 사용량 제한
- **새로고침 간격**: 실시간성과 성능의 균형

#### 쿼리 최적화
```json
{
  "query": {
    "bool": {
      "filter": [
        {"term": {"doc_type": "employee"}}
      ],
      "must": [
        {"match": {"skills": "Python"}}
      ]
    }
  }
}
```

**최적화 원칙:**
- **필터 우선**: 스코어 계산 전 필터링
- **인덱스 활용**: term 쿼리로 정확한 매칭
- **불필요한 계산 제거**: 필요한 필드만 검색

### 2. 메모리 최적화

#### 벡터 필드 최적화
```json
{
  "embedding": {
    "type": "knn_vector",
    "dimension": 384,
    "method": {
      "parameters": {
        "m": 16,
        "ef_construction": 128
      }
    }
  }
}
```

**최적화 내용:**
- **차원 최적화**: 384차원으로 성능과 정확도 균형
- **HNSW 파라미터**: 메모리 사용량과 정확도 조절
- **압축**: 벡터 데이터 압축으로 메모리 절약

### 3. 캐싱 전략

#### 필터 캐싱
- **자동 캐싱**: term 필터 결과 자동 캐싱
- **캐시 크기**: JVM 힙의 10% 할당
- **캐시 무효화**: 인덱스 업데이트 시 자동 무효화

---

## 📈 확장성 고려사항

### 1. 수평 확장

#### 샤딩 전략
```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}
```

**확장 계획:**
- **샤드 분할**: 데이터 증가 시 샤드 수 증가
- **복제본**: 가용성과 읽기 성능 향상
- **노드 분산**: 여러 노드에 샤드 분산

### 2. 수직 확장

#### 리소스 증가
- **메모리**: JVM 힙 크기 증가
- **CPU**: 더 많은 코어 할당
- **디스크**: SSD 사용으로 I/O 성능 향상

### 3. 클러스터 구성

#### 다중 노드 설정
```yaml
# docker-compose.yml 확장 예시
services:
  opensearch-node1:
    image: opensearch:2.11.0
    environment:
      - cluster.name=opensearch-cluster
      - node.name=node1
      - discovery.seed_hosts=node1,node2,node3
  opensearch-node2:
    image: opensearch:2.11.0
    environment:
      - cluster.name=opensearch-cluster
      - node.name=node2
      - discovery.seed_hosts=node1,node2,node3
```

**클러스터 장점:**
- **고가용성**: 노드 장애 시 자동 복구
- **부하 분산**: 검색 요청 분산 처리
- **백업**: 자동 복제본 관리

---

## 🔧 모니터링 및 관리

### 1. 클러스터 모니터링

#### 상태 확인
```bash
# 클러스터 상태
curl -X GET "localhost:9200/_cluster/health?pretty"

# 노드 상태
curl -X GET "localhost:9200/_cat/nodes?v"

# 인덱스 상태
curl -X GET "localhost:9200/_cat/indices?v"
```

### 2. 성능 모니터링

#### 쿼리 성능
```bash
# 쿼리 실행 시간 측정
curl -X GET "localhost:9200/company-knowledge/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"match_all": {}},
    "size": 1
  }'
```

### 3. 로그 관리

#### 로그 설정
```json
{
  "settings": {
    "index": {
      "search": {
        "slowlog": {
          "threshold": {
            "query": "2s",
            "fetch": "1s"
          }
        }
      }
    }
  }
}
```

---

## 📚 추가 리소스

- [OpenSearch k-NN 가이드](https://opensearch.org/docs/latest/search-plugins/knn/)
- [OpenSearch 쿼리 DSL](https://opensearch.org/docs/latest/opensearch/query-dsl/)
- [OpenSearch 성능 튜닝](https://opensearch.org/docs/latest/opensearch/performance/)
- [HNSW 알고리즘 설명](https://arxiv.org/abs/1603.09320) 