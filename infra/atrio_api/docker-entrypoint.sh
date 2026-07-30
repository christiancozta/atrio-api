#!/usr/bin/env bash
set -euo pipefail

: "${ATRIO_DB_HOST:?ATRIO_DB_HOST ausente}"
: "${ATRIO_DB_PORT:?ATRIO_DB_PORT ausente}"
: "${ATRIO_DB_NAME:?ATRIO_DB_NAME ausente}"
: "${ATRIO_DB_USER:?ATRIO_DB_USER ausente}"
: "${ATRIO_DB_PASSWORD_FILE:?ATRIO_DB_PASSWORD_FILE ausente}"

if [[ ! -r "${ATRIO_DB_PASSWORD_FILE}" ]]; then
    echo "ERRO: segredo PostgreSQL indisponível." >&2
    exit 1
fi

echo "ATRIO API: aguardando PostgreSQL..."
until pg_isready \
    --host="${ATRIO_DB_HOST}" \
    --port="${ATRIO_DB_PORT}" \
    --username="${ATRIO_DB_USER}" \
    --dbname="${ATRIO_DB_NAME}" \
    >/dev/null 2>&1
do
    sleep 2
done

export PGCLIENTENCODING=UTF8
export PGPASSWORD
PGPASSWORD="$(<"${ATRIO_DB_PASSWORD_FILE}")"

while IFS= read -r -d '' migration; do
    checksum="$(sha256sum "${migration}" | cut -d' ' -f1)"
    echo "ATRIO API: verificando migração $(basename "${migration}")"
    psql \
        --host="${ATRIO_DB_HOST}" \
        --port="${ATRIO_DB_PORT}" \
        --username="${ATRIO_DB_USER}" \
        --dbname="${ATRIO_DB_NAME}" \
        --set=ON_ERROR_STOP=1 \
        --set="migration_checksum=${checksum}" \
        --file="${migration}"
done < <(find /app/migrations -maxdepth 1 -type f -name '*.sql' -print0 | sort -z)

unset PGPASSWORD

exec "$@"
