\set ON_ERROR_STOP on

-- ATRIO DB schema 1.1.1
-- Permite apenas os identificadores seguros da entrada CORPUS no evento.

SELECT pg_catalog.set_config('search_path', 'pg_catalog', false);

SELECT EXISTS (
    SELECT 1
      FROM atrio.schema_migrations
     WHERE version = '1.1.1'
) AS migration_applied
\gset

\if :migration_applied
    SELECT checksum = :'migration_checksum' AS checksum_matches
      FROM atrio.schema_migrations
     WHERE version = '1.1.1'
    \gset

    \if :checksum_matches
        \echo 'ATRIO DB schema 1.1.1 ja aplicado; checksum confirmado.'
    \else
        \echo 'ERRO: schema 1.1.1 registrado com checksum diferente.'
        DO $migration_error$
        BEGIN
            RAISE EXCEPTION
                'Schema 1.1.1 registrado com checksum diferente';
        END
        $migration_error$;
    \endif
\else

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

DO $drop_legacy_constraint$
DECLARE
    legacy_constraint name;
BEGIN
    SELECT constraint_definition.conname
      INTO legacy_constraint
      FROM pg_catalog.pg_constraint AS constraint_definition
      JOIN pg_catalog.pg_class AS relation_definition
        ON relation_definition.oid = constraint_definition.conrelid
      JOIN pg_catalog.pg_namespace AS namespace_definition
        ON namespace_definition.oid = relation_definition.relnamespace
     WHERE namespace_definition.nspname = 'atrio'
       AND relation_definition.relname = 'execution_events'
       AND constraint_definition.contype = 'c'
       AND pg_catalog.pg_get_constraintdef(
               constraint_definition.oid
           ) LIKE '%artifact_id%'
       AND pg_catalog.pg_get_constraintdef(
               constraint_definition.oid
           ) LIKE '%review_type%';

    IF legacy_constraint IS NULL THEN
        RAISE EXCEPTION
            'Constraint de metadados seguros de execution_events nao encontrada';
    END IF;

    EXECUTE pg_catalog.format(
        'ALTER TABLE atrio.execution_events DROP CONSTRAINT %I',
        legacy_constraint
    );
END
$drop_legacy_constraint$;

ALTER TABLE atrio.execution_events
    ADD CONSTRAINT execution_events_safe_metadata_check
    CHECK (
        metadata - ARRAY[
            'artifact_id',
            'artifact_producer',
            'artifact_release_id',
            'artifact_schema_version',
            'artifact_version',
            'decision_code',
            'document_id',
            'document_sha256',
            'error_code',
            'gate',
            'phase',
            'reason_code',
            'review_type'
        ] = '{}'::jsonb
    );

INSERT INTO atrio.schema_migrations (version, checksum)
VALUES ('1.1.1', :'migration_checksum');

COMMIT;

\echo 'ATRIO DB schema 1.1.1 aplicado com sucesso.'

\endif

SELECT version, checksum, applied_at, applied_by
  FROM atrio.schema_migrations
 ORDER BY applied_at;
