\set ON_ERROR_STOP on

-- ATRIO DB schema 1.1.0
-- Entrada documental criptografada e idempotente do CORPUS.

SELECT pg_catalog.set_config('search_path', 'pg_catalog', false);

SELECT EXISTS (
    SELECT 1
      FROM atrio.schema_migrations
     WHERE version = '1.1.0'
) AS migration_applied
\gset

\if :migration_applied
    SELECT checksum = :'migration_checksum' AS checksum_matches
      FROM atrio.schema_migrations
     WHERE version = '1.1.0'
    \gset

    \if :checksum_matches
        \echo 'ATRIO DB schema 1.1.0 ja aplicado; checksum confirmado.'
    \else
        \echo 'ERRO: schema 1.1.0 registrado com checksum diferente.'
        DO $migration_error$
        BEGIN
            RAISE EXCEPTION
                'Schema 1.1.0 registrado com checksum diferente';
        END
        $migration_error$;
    \endif
\else

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

ALTER TABLE atrio.command_log
    DROP CONSTRAINT command_log_command_kind_check;

ALTER TABLE atrio.command_log
    ADD CONSTRAINT command_log_command_kind_check
    CHECK (
        command_kind IN (
            'START_INGESTION',
            'REGISTER_CORPUS_DOCUMENT',
            'REQUEST_CORPUS_REVIEW',
            'RESUME_CORPUS',
            'COMPLETE_CORPUS',
            'START_RATIO',
            'REQUEST_OPERATOR_DECISION',
            'RECORD_OPERATOR_DECISION',
            'COMPLETE_RATIO',
            'START_CERNE',
            'APPLY_CERNE_GATE',
            'RETURN_TO_RATIO',
            'REOPEN_TOTAL_BLOCK',
            'COMPLETE_RATIO_REWORK',
            'START_LUX',
            'COMPLETE_LUX',
            'PASS_FINAL_INTEGRITY',
            'FAIL_FINAL_INTEGRITY',
            'RETRY_LUX',
            'RELEASE',
            'FAIL_TECHNICAL',
            'RETRY_TECHNICAL',
            'CANCEL'
        )
    );

CREATE TABLE atrio.corpus_intakes (
    document_id uuid PRIMARY KEY,
    execution_id uuid NOT NULL
        REFERENCES atrio.executions (execution_id) ON DELETE RESTRICT,
    idempotency_key text NOT NULL
        CHECK (
            length(btrim(idempotency_key)) > 0
            AND length(idempotency_key) <= 200
        ),
    created_by text NOT NULL
        CHECK (length(btrim(created_by)) > 0),
    sha256 character(64) NOT NULL
        CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    byte_length bigint NOT NULL
        CHECK (byte_length > 0 AND byte_length <= 52428800),
    media_type text NOT NULL
        CHECK (
            media_type IN (
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'image/tiff',
                'text/plain'
            )
        ),
    storage_key text NOT NULL UNIQUE
        CHECK (
            storage_key ~
            '^corpus/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[.]atrio$'
        ),
    encryption_algorithm text NOT NULL
        CHECK (encryption_algorithm = 'AES-256-GCM'),
    envelope_version text NOT NULL
        CHECK (envelope_version = 'ATRIO-V1'),
    intake_version text NOT NULL
        CHECK (intake_version = '1.0.0'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (execution_id, idempotency_key),
    UNIQUE (execution_id, sha256)
);

CREATE INDEX corpus_intakes_execution_created_idx
    ON atrio.corpus_intakes (execution_id, created_at);

CREATE TRIGGER corpus_intakes_are_immutable
BEFORE UPDATE OR DELETE ON atrio.corpus_intakes
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

INSERT INTO atrio.schema_migrations (version, checksum)
VALUES ('1.1.0', :'migration_checksum');

COMMIT;

\echo 'ATRIO DB schema 1.1.0 aplicado com sucesso.'

\endif

SELECT version, checksum, applied_at, applied_by
  FROM atrio.schema_migrations
 ORDER BY applied_at;
