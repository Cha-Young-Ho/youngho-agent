#!/bin/bash

# OpenSearch Docker 설정 스크립트

echo "🚀 OpenSearch Docker 설정을 시작합니다..."

# 1. Docker Compose로 OpenSearch 시작
echo "📦 OpenSearch 컨테이너를 시작합니다..."
docker-compose up -d

# 2. OpenSearch가 완전히 시작될 때까지 대기
echo "⏳ OpenSearch가 시작될 때까지 대기 중..."
sleep 30

# 3. OpenSearch 상태 확인
echo "🔍 OpenSearch 상태를 확인합니다..."
curl -X GET "localhost:9200/_cluster/health?pretty"

# 4. 벡터 검색을 위한 인덱스 생성
echo "📊 벡터 검색용 인덱스를 생성합니다..."
curl -X PUT "localhost:9200/company-knowledge" -H "Content-Type: application/json" -d'
{
  "mappings": {
    "properties": {
      "content": {
        "type": "text"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib",
          "parameters": {
            "ef_construction": 128,
            "m": 16
          }
        }
      },
      "doc_type": {
        "type": "keyword"
      },
      "employee_id": {
        "type": "keyword"
      },
      "name": {
        "type": "keyword"
      },
      "department": {
        "type": "keyword"
      },
      "position": {
        "type": "keyword"
      },
      "id": {
        "type": "keyword"
      },
      "metadata": {
        "type": "object"
      }
    }
  },
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 100
    }
  }
}'

echo ""
echo "✅ OpenSearch 설정이 완료되었습니다!"
echo ""
echo "📋 접속 정보:"
echo "   - OpenSearch: http://localhost:9200"
echo "   - OpenSearch Dashboards: http://localhost:5601"
echo ""
echo "🔧 유용한 명령어:"
echo "   - 컨테이너 상태 확인: docker-compose ps"
echo "   - 로그 확인: docker-compose logs -f"
echo "   - 컨테이너 중지: docker-compose down"
echo "   - 컨테이너 재시작: docker-compose restart" 