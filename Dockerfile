# OpenSearch 설정을 위한 Dockerfile
# 이 파일은 OpenSearch 컨테이너의 추가 설정이 필요할 때 사용합니다.

FROM opensearchproject/opensearch:2.11.0

# 필요한 플러그인 설치 (필요시)
# RUN /usr/share/opensearch/bin/opensearch-plugin install analysis-kuromoji

# 커스텀 설정 파일 복사 (필요시)
# COPY opensearch.yml /usr/share/opensearch/config/opensearch.yml

# 권한 설정
USER root
RUN chown -R opensearch:opensearch /usr/share/opensearch

USER opensearch

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9200/_cluster/health || exit 1 