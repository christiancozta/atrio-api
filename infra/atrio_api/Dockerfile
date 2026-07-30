FROM python:3.13.5-slim-bookworm AS runtime

ARG ATRIO_API_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    ATRIO_API_HOST=0.0.0.0 \
    ATRIO_API_PORT=8080

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        bash \
        poppler-utils \
        postgresql-client \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY packages/services/atrio_api/pyproject.toml \
     packages/services/atrio_api/README.md \
     /build/atrio_api/
COPY packages/services/atrio_api/src/ /build/atrio_api/src/

RUN python -m pip install --no-compile /build/atrio_api \
    && python -c "import atrio_api; assert atrio_api.__version__ == '${ATRIO_API_VERSION}'" \
    && rm -rf /build

COPY packages/services/atrio_api/migrations/ /app/migrations/
COPY packages/atrio_pii/atrio_pii.py /app/packages/atrio_pii/atrio_pii.py
COPY packages/ratio/ /app/packages/ratio/
COPY packages/cerne/00_sistema_cerne/ /app/packages/cerne/00_sistema_cerne/
COPY packages/lux/00_KERNEL_CURTO_UNIVERSAL_GPT_SAFE.txt \
     packages/lux/01_UPLOAD_CONHECIMENTO_PERFIS_DE_ESTILO.txt \
     packages/lux/02_UPLOAD_CONHECIMENTO_GUIA_E_TEMPLATES.txt \
     /app/packages/lux/
COPY ATRIO-Core-Orchestrator.html /app/ATRIO-Core-Orchestrator.html
COPY MANIFEST.yaml VERSIONS.yaml /app/
COPY infra/atrio_api/RUNTIME_NORMATIVE_MANIFEST.json /app/
COPY tools/build_runtime_normative_manifest.py /app/tools/
COPY infra/atrio_api/docker-entrypoint.sh /usr/local/bin/atrio-entrypoint

RUN python /app/tools/build_runtime_normative_manifest.py --check \
    && python -c "import json; from pathlib import Path; from atrio_api.release_catalog import NORMATIVE_BUNDLE_SHA256; manifest=json.loads(Path('/app/RUNTIME_NORMATIVE_MANIFEST.json').read_text(encoding='utf-8')); assert manifest['content_digest'] == NORMATIVE_BUNDLE_SHA256" \
    && rm -rf /app/tools

RUN groupadd --gid 10001 atrio \
    && useradd --uid 10001 --gid atrio --no-create-home atrio \
    && mkdir -p /data/vault \
    && chown -R atrio:atrio /data/vault \
    && chmod 0555 /usr/local/bin/atrio-entrypoint

USER atrio

VOLUME ["/data/vault"]
EXPOSE 8080

ENTRYPOINT ["atrio-entrypoint"]
CMD ["uvicorn", "atrio_api.container_runtime:create_container_app", "--factory", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info", "--no-access-log", "--no-server-header", "--no-date-header"]
