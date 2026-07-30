\set ON_ERROR_STOP on

-- ATRIO DB schema 1.2.0
-- Inventario seguro, revisao humana e handoff cifrado do CORPUS.

SELECT pg_catalog.set_config('search_path', 'pg_catalog', false);

SELECT EXISTS (
    SELECT 1
      FROM atrio.schema_migrations
     WHERE version = '1.2.0'
) AS migration_applied
\gset

\if :migration_applied
    SELECT checksum = :'migration_checksum' AS checksum_matches
      FROM atrio.schema_migrations
     WHERE version = '1.2.0'
    \gset

    \if :checksum_matches
        \echo 'ATRIO DB schema 1.2.0 ja aplicado; checksum confirmado.'
    \else
        \echo 'ERRO: schema 1.2.0 registrado com checksum diferente.'
        DO $migration_error$
        BEGIN
            RAISE EXCEPTION
                'Schema 1.2.0 registrado com checksum diferente';
        END
        $migration_error$;
    \endif
\else

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

ALTER TABLE atrio.corpus_intakes
    ADD CONSTRAINT corpus_intakes_document_execution_unique
    UNIQUE (document_id, execution_id);

CREATE TABLE atrio.corpus_processing_results (
    processing_id uuid PRIMARY KEY,
    document_id uuid NOT NULL,
    execution_id uuid NOT NULL,
    input_sha256 character(64) NOT NULL
        CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
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
    extraction_method text NOT NULL
        CHECK (
            extraction_method IN (
                'text_utf8',
                'docx_xml',
                'pdf_text',
                'ocr_pdf',
                'ocr_image'
            )
        ),
    page_count integer NOT NULL CHECK (page_count >= 0),
    extracted_char_count bigint NOT NULL CHECK (extracted_char_count >= 0),
    ocr_mean_confidence numeric(5, 2)
        CHECK (
            ocr_mean_confidence IS NULL
            OR (
                ocr_mean_confidence >= 0
                AND ocr_mean_confidence <= 100
            )
        ),
    cnj text
        CHECK (
            cnj IS NULL
            OR cnj ~ '^[0-9]{7}-[0-9]{2}[.][0-9]{4}[.][0-9][.][0-9]{2}[.][0-9]{4}$'
        ),
    procedural_class text NOT NULL
        CHECK (
            procedural_class IN (
                'MS',
                'ED',
                'RI',
                'AGRAVO',
                'SENTENCA',
                'OUTRO'
            )
        ),
    secrecy_level text NOT NULL
        CHECK (secrecy_level IN ('none', 'forte', 'fraco')),
    pii_counts jsonb NOT NULL
        CHECK (pg_catalog.jsonb_typeof(pii_counts) = 'object'),
    pseudonym_count integer NOT NULL CHECK (pseudonym_count >= 0),
    pseudonymized_sha256 character(64) NOT NULL
        CHECK (pseudonymized_sha256 ~ '^[0-9a-f]{64}$'),
    processing_status text NOT NULL
        CHECK (processing_status IN ('READY', 'REVIEW_REQUIRED')),
    review_type text
        CHECK (review_type IN ('ocr', 'secrecy', 'quality')),
    processed_storage_key text NOT NULL UNIQUE
        CHECK (
            processed_storage_key ~
            '^processed/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[.]atrio$'
        ),
    corpus_pipeline_version text NOT NULL
        CHECK (length(btrim(corpus_pipeline_version)) > 0),
    atrio_pii_version text NOT NULL
        CHECK (length(btrim(atrio_pii_version)) > 0),
    processed_by text NOT NULL
        CHECK (length(btrim(processed_by)) > 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (document_id),
    FOREIGN KEY (document_id, execution_id)
        REFERENCES atrio.corpus_intakes (document_id, execution_id)
        ON DELETE RESTRICT,
    CHECK (
        (
            processing_status = 'READY'
            AND review_type IS NULL
        )
        OR (
            processing_status = 'REVIEW_REQUIRED'
            AND review_type IS NOT NULL
        )
    )
);

CREATE INDEX corpus_processing_execution_created_idx
    ON atrio.corpus_processing_results (execution_id, created_at);

CREATE TABLE atrio.corpus_review_decisions (
    review_id uuid PRIMARY KEY,
    processing_id uuid NOT NULL UNIQUE
        REFERENCES atrio.corpus_processing_results (processing_id)
        ON DELETE RESTRICT,
    decision_code text NOT NULL
        CHECK (decision_code IN ('APPROVE', 'EXCLUDE')),
    actor_id text NOT NULL CHECK (length(btrim(actor_id)) > 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE atrio.corpus_outputs (
    artifact_id text PRIMARY KEY
        REFERENCES atrio.artifacts (artifact_id) ON DELETE RESTRICT,
    execution_id uuid NOT NULL UNIQUE
        REFERENCES atrio.executions (execution_id) ON DELETE RESTRICT,
    storage_key text NOT NULL UNIQUE
        CHECK (
            storage_key ~
            '^artifacts/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[.]atrio$'
        ),
    document_count integer NOT NULL CHECK (document_count > 0),
    bundle_sha256 character(64) NOT NULL
        CHECK (bundle_sha256 ~ '^[0-9a-f]{64}$'),
    corpus_pipeline_version text NOT NULL
        CHECK (length(btrim(corpus_pipeline_version)) > 0),
    created_by text NOT NULL CHECK (length(btrim(created_by)) > 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TRIGGER corpus_processing_results_are_immutable
BEFORE UPDATE OR DELETE ON atrio.corpus_processing_results
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER corpus_review_decisions_are_immutable
BEFORE UPDATE OR DELETE ON atrio.corpus_review_decisions
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER corpus_outputs_are_immutable
BEFORE UPDATE OR DELETE ON atrio.corpus_outputs
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

INSERT INTO atrio.schema_migrations (version, checksum)
VALUES ('1.2.0', :'migration_checksum');

COMMIT;

\echo 'ATRIO DB schema 1.2.0 aplicado com sucesso.'

\endif

SELECT version, checksum, applied_at, applied_by
  FROM atrio.schema_migrations
 ORDER BY applied_at;
