\set ON_ERROR_STOP on

-- ATRIO DB schema 1.0.0
-- O checksum deste arquivo e calculado pelo runner e nunca contem segredo.

SELECT pg_catalog.set_config('search_path', 'pg_catalog', false);

CREATE SCHEMA IF NOT EXISTS atrio AUTHORIZATION CURRENT_USER;
REVOKE ALL ON SCHEMA atrio FROM PUBLIC;
GRANT USAGE ON SCHEMA atrio TO CURRENT_USER;

CREATE TABLE IF NOT EXISTS atrio.schema_migrations (
    version text PRIMARY KEY,
    checksum character(64) NOT NULL
        CHECK (checksum ~ '^[0-9a-f]{64}$'),
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    applied_by text NOT NULL DEFAULT session_user
);

SELECT EXISTS (
    SELECT 1
      FROM atrio.schema_migrations
     WHERE version = '1.0.0'
) AS migration_applied
\gset

\if :migration_applied
    SELECT checksum = :'migration_checksum' AS checksum_matches
      FROM atrio.schema_migrations
     WHERE version = '1.0.0'
    \gset

    \if :checksum_matches
        \echo 'ATRIO DB schema 1.0.0 ja aplicado; checksum confirmado.'
    \else
        \echo 'ERRO: schema 1.0.0 registrado com checksum diferente.'
        DO $migration_error$
        BEGIN
            RAISE EXCEPTION
                'Schema 1.0.0 registrado com checksum diferente';
        END
        $migration_error$;
    \endif
\else

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

CREATE TABLE atrio.releases (
    release_id text PRIMARY KEY
        CHECK (length(btrim(release_id)) > 0),
    atrio_api_version text NOT NULL
        CHECK (length(btrim(atrio_api_version)) > 0),
    corpus_version text NOT NULL
        CHECK (length(btrim(corpus_version)) > 0),
    ratio_version text NOT NULL
        CHECK (length(btrim(ratio_version)) > 0),
    cerne_module_version text NOT NULL
        CHECK (length(btrim(cerne_module_version)) > 0),
    cerne_service_build text NOT NULL
        CHECK (length(btrim(cerne_service_build)) > 0),
    lux_version text NOT NULL
        CHECK (length(btrim(lux_version)) > 0),
    atrio_pii_version text NOT NULL
        CHECK (length(btrim(atrio_pii_version)) > 0),
    prompt_bundle_hash text NOT NULL
        CHECK (length(btrim(prompt_bundle_hash)) > 0),
    artifact_schema_version text NOT NULL
        CHECK (length(btrim(artifact_schema_version)) > 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE atrio.artifacts (
    artifact_id text PRIMARY KEY
        CHECK (length(btrim(artifact_id)) > 0),
    owner_execution_id uuid NOT NULL,
    release_id text NOT NULL
        REFERENCES atrio.releases (release_id) ON DELETE RESTRICT,
    sha256 character(64) NOT NULL
        CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    media_type text NOT NULL
        CHECK (length(btrim(media_type)) > 0),
    classification text NOT NULL
        CHECK (length(btrim(classification)) > 0),
    producer text NOT NULL
        CHECK (
            producer IN (
                'atrio_api',
                'corpus',
                'ratio',
                'cerne',
                'lux',
                'atrio_pii'
            )
        ),
    producer_version text NOT NULL
        CHECK (length(btrim(producer_version)) > 0),
    artifact_schema_version text NOT NULL
        CHECK (length(btrim(artifact_schema_version)) > 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE atrio.executions (
    execution_id uuid PRIMARY KEY,
    tenant_id text NOT NULL
        CHECK (length(btrim(tenant_id)) > 0),
    created_by text NOT NULL
        CHECK (length(btrim(created_by)) > 0),
    ratio_module text NOT NULL
        CHECK (ratio_module IN ('RI', 'ED', 'MS')),
    destination text NOT NULL
        CHECK (destination IN ('interno', 'externo', 'publico')),
    release_id text NOT NULL
        REFERENCES atrio.releases (release_id) ON DELETE RESTRICT,
    stage text NOT NULL
        CHECK (
            stage IN (
                'CREATED',
                'CORPUS_INGESTING',
                'CORPUS_REVIEW_REQUIRED',
                'CORPUS_READY',
                'RATIO_RUNNING',
                'RATIO_WAITING_OPERATOR',
                'RATIO_READY',
                'RATIO_REWORK',
                'CERNE_AUDITING',
                'CERNE_APPROVED',
                'CERNE_HUMAN_REVIEW',
                'CERNE_PARTIAL_BLOCK',
                'CERNE_TOTAL_BLOCK',
                'LUX_REFINING',
                'FINAL_INTEGRITY_CHECK',
                'FINAL_INTEGRITY_BLOCK',
                'READY_FOR_RELEASE',
                'RELEASED',
                'TECHNICAL_FAILURE',
                'CANCELLED'
            )
        ),
    status text NOT NULL
        CHECK (
            status IN (
                'ACTIVE',
                'WAITING_HUMAN',
                'BLOCKED',
                'COMPLETED',
                'FAILED',
                'CANCELLED'
            )
        ),
    state_version bigint NOT NULL DEFAULT 0
        CHECK (state_version >= 0),
    corpus_artifact_id text
        REFERENCES atrio.artifacts (artifact_id) ON DELETE RESTRICT,
    ratio_artifact_id text
        REFERENCES atrio.artifacts (artifact_id) ON DELETE RESTRICT,
    cerne_artifact_id text
        REFERENCES atrio.artifacts (artifact_id) ON DELETE RESTRICT,
    lux_artifact_id text
        REFERENCES atrio.artifacts (artifact_id) ON DELETE RESTRICT,
    released_artifact_id text
        REFERENCES atrio.artifacts (artifact_id) ON DELETE RESTRICT,
    current_ratio_phase text,
    waiting_reason text,
    last_operator_actor text,
    last_operator_decision text,
    cerne_gate text
        CHECK (
            cerne_gate IS NULL
            OR cerne_gate IN (
                'AVANCA',
                'AVANCA_COM_AJUSTE',
                'REVISAO_HUMANA',
                'BLOQUEIO_PARCIAL',
                'BLOQUEIO_TOTAL'
            )
        ),
    last_error_code text,
    retry_stage text,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    released_at timestamptz,
    CHECK (
        (stage = 'RELEASED' AND released_at IS NOT NULL)
        OR (stage <> 'RELEASED' AND released_at IS NULL)
    ),
    CHECK (
        (
            stage IN (
                'CORPUS_REVIEW_REQUIRED',
                'RATIO_WAITING_OPERATOR',
                'CERNE_HUMAN_REVIEW'
            )
            AND status = 'WAITING_HUMAN'
        )
        OR (
            stage IN (
                'CERNE_PARTIAL_BLOCK',
                'CERNE_TOTAL_BLOCK',
                'FINAL_INTEGRITY_BLOCK'
            )
            AND status = 'BLOCKED'
        )
        OR (stage = 'RELEASED' AND status = 'COMPLETED')
        OR (stage = 'TECHNICAL_FAILURE' AND status = 'FAILED')
        OR (stage = 'CANCELLED' AND status = 'CANCELLED')
        OR (
            stage NOT IN (
                'CORPUS_REVIEW_REQUIRED',
                'RATIO_WAITING_OPERATOR',
                'CERNE_HUMAN_REVIEW',
                'CERNE_PARTIAL_BLOCK',
                'CERNE_TOTAL_BLOCK',
                'FINAL_INTEGRITY_BLOCK',
                'RELEASED',
                'TECHNICAL_FAILURE',
                'CANCELLED'
            )
            AND status = 'ACTIVE'
        )
    )
);

ALTER TABLE atrio.artifacts
    ADD CONSTRAINT artifacts_owner_execution_fk
    FOREIGN KEY (owner_execution_id)
    REFERENCES atrio.executions (execution_id)
    ON DELETE RESTRICT;

CREATE TABLE atrio.idempotency_keys (
    tenant_id text NOT NULL
        CHECK (length(btrim(tenant_id)) > 0),
    idempotency_key text NOT NULL
        CHECK (
            length(btrim(idempotency_key)) > 0
            AND length(idempotency_key) <= 200
        ),
    request_fingerprint character(64) NOT NULL
        CHECK (request_fingerprint ~ '^[0-9a-f]{64}$'),
    execution_id uuid NOT NULL UNIQUE
        REFERENCES atrio.executions (execution_id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, idempotency_key)
);

CREATE TABLE atrio.command_log (
    execution_id uuid NOT NULL
        REFERENCES atrio.executions (execution_id) ON DELETE RESTRICT,
    sequence bigint NOT NULL CHECK (sequence > 0),
    command_kind text NOT NULL
        CHECK (
            command_kind IN (
                'START_INGESTION',
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
        ),
    expected_version bigint NOT NULL CHECK (expected_version >= 0),
    resulting_version bigint NOT NULL CHECK (resulting_version > 0),
    actor_id text NOT NULL
        CHECK (length(btrim(actor_id)) > 0),
    payload_fingerprint character(64) NOT NULL
        CHECK (payload_fingerprint ~ '^[0-9a-f]{64}$'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (execution_id, sequence),
    UNIQUE (execution_id, expected_version),
    CHECK (resulting_version = expected_version + 1),
    CHECK (sequence = resulting_version)
);

CREATE TABLE atrio.execution_events (
    execution_id uuid NOT NULL,
    sequence bigint NOT NULL,
    command_kind text NOT NULL,
    from_stage text NOT NULL,
    to_stage text NOT NULL,
    component text NOT NULL
        CHECK (
            component IN (
                'atrio_api',
                'corpus',
                'ratio',
                'cerne',
                'lux',
                'atrio_pii'
            )
        ),
    component_version text NOT NULL
        CHECK (length(btrim(component_version)) > 0),
    release_id text NOT NULL
        REFERENCES atrio.releases (release_id) ON DELETE RESTRICT,
    actor_id text NOT NULL
        CHECK (length(btrim(actor_id)) > 0),
    occurred_at timestamptz NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (execution_id, sequence),
    FOREIGN KEY (execution_id, sequence)
        REFERENCES atrio.command_log (execution_id, sequence)
        ON DELETE RESTRICT,
    CHECK (jsonb_typeof(metadata) = 'object'),
    CHECK (
        metadata - ARRAY[
            'artifact_id',
            'artifact_producer',
            'artifact_release_id',
            'artifact_schema_version',
            'artifact_version',
            'decision_code',
            'error_code',
            'gate',
            'phase',
            'reason_code',
            'review_type'
        ] = '{}'::jsonb
    )
);

CREATE INDEX executions_tenant_created_idx
    ON atrio.executions (tenant_id, created_at DESC);

CREATE INDEX executions_active_idx
    ON atrio.executions (status, updated_at)
    WHERE status IN ('ACTIVE', 'WAITING_HUMAN', 'FAILED');

CREATE INDEX artifacts_owner_idx
    ON atrio.artifacts (owner_execution_id, created_at);

CREATE INDEX execution_events_occurred_idx
    ON atrio.execution_events (occurred_at);

CREATE FUNCTION atrio.expected_component_version(
    p_release_id text,
    p_component text
) RETURNS text
LANGUAGE sql
STABLE
SET search_path = pg_catalog, atrio
AS $$
    SELECT CASE p_component
        WHEN 'atrio_api' THEN r.atrio_api_version
        WHEN 'corpus' THEN r.corpus_version
        WHEN 'ratio' THEN r.ratio_version
        WHEN 'cerne' THEN r.cerne_module_version
        WHEN 'lux' THEN r.lux_version
        WHEN 'atrio_pii' THEN r.atrio_pii_version
    END
      FROM atrio.releases AS r
     WHERE r.release_id = p_release_id
$$;

CREATE FUNCTION atrio.validate_artifact_version()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
DECLARE
    expected_version text;
    expected_schema text;
BEGIN
    SELECT atrio.expected_component_version(NEW.release_id, NEW.producer),
           r.artifact_schema_version
      INTO expected_version, expected_schema
      FROM atrio.releases AS r
     WHERE r.release_id = NEW.release_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Release desconhecida para artefato: %', NEW.release_id;
    END IF;

    IF NEW.producer_version <> expected_version THEN
        RAISE EXCEPTION
            'Versao do artefato divergente: esperado %, recebido %',
            expected_version,
            NEW.producer_version;
    END IF;

    IF NEW.artifact_schema_version <> expected_schema THEN
        RAISE EXCEPTION
            'Schema do artefato divergente: esperado %, recebido %',
            expected_schema,
            NEW.artifact_schema_version;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER artifacts_validate_version
BEFORE INSERT ON atrio.artifacts
FOR EACH ROW
EXECUTE FUNCTION atrio.validate_artifact_version();

CREATE FUNCTION atrio.validate_execution_artifacts()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
DECLARE
    artifact_record record;
    artifact_slot text;
    expected_producer text;
    selected_artifact_id text;
BEGIN
    FOREACH artifact_slot IN ARRAY ARRAY[
        'corpus',
        'ratio',
        'cerne',
        'lux',
        'released'
    ]
    LOOP
        selected_artifact_id := CASE artifact_slot
            WHEN 'corpus' THEN NEW.corpus_artifact_id
            WHEN 'ratio' THEN NEW.ratio_artifact_id
            WHEN 'cerne' THEN NEW.cerne_artifact_id
            WHEN 'lux' THEN NEW.lux_artifact_id
            WHEN 'released' THEN NEW.released_artifact_id
        END;

        IF selected_artifact_id IS NULL THEN
            CONTINUE;
        END IF;

        expected_producer := CASE artifact_slot
            WHEN 'released' THEN 'lux'
            ELSE artifact_slot
        END;

        SELECT a.release_id, a.owner_execution_id, a.producer
          INTO artifact_record
          FROM atrio.artifacts AS a
         WHERE a.artifact_id = selected_artifact_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Artefato desconhecido: %', selected_artifact_id;
        END IF;

        IF artifact_record.release_id <> NEW.release_id
           OR artifact_record.owner_execution_id <> NEW.execution_id
           OR artifact_record.producer <> expected_producer THEN
            RAISE EXCEPTION
                'Handoff invalido para slot % e artefato %',
                artifact_slot,
                selected_artifact_id;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER executions_validate_artifacts
BEFORE INSERT OR UPDATE ON atrio.executions
FOR EACH ROW
EXECUTE FUNCTION atrio.validate_execution_artifacts();

CREATE FUNCTION atrio.validate_event_version()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
DECLARE
    execution_release_id text;
    execution_stage text;
    execution_state_version bigint;
    expected_version text;
    expected_from_stage text;
    logged_command_kind text;
    logged_actor_id text;
BEGIN
    SELECT e.release_id, e.stage, e.state_version
      INTO execution_release_id, execution_stage, execution_state_version
      FROM atrio.executions AS e
     WHERE e.execution_id = NEW.execution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Execucao desconhecida para evento: %', NEW.execution_id;
    END IF;

    IF execution_release_id <> NEW.release_id THEN
        RAISE EXCEPTION
            'Release do evento nao corresponde a execucao: %',
            NEW.execution_id;
    END IF;

    IF execution_stage <> NEW.to_stage
       OR execution_state_version <> NEW.sequence THEN
        RAISE EXCEPTION
            'Evento nao corresponde ao estado persistido da execucao: %',
            NEW.execution_id;
    END IF;

    SELECT c.command_kind, c.actor_id
      INTO logged_command_kind, logged_actor_id
      FROM atrio.command_log AS c
     WHERE c.execution_id = NEW.execution_id
       AND c.sequence = NEW.sequence;

    IF NOT FOUND
       OR logged_command_kind <> NEW.command_kind
       OR logged_actor_id <> NEW.actor_id THEN
        RAISE EXCEPTION
            'Evento nao corresponde ao comando persistido da execucao: %',
            NEW.execution_id;
    END IF;

    IF NEW.sequence = 1 THEN
        expected_from_stage := 'CREATED';
    ELSE
        SELECT previous_event.to_stage
          INTO expected_from_stage
          FROM atrio.execution_events AS previous_event
         WHERE previous_event.execution_id = NEW.execution_id
           AND previous_event.sequence = NEW.sequence - 1;
    END IF;

    IF expected_from_stage IS NULL
       OR expected_from_stage <> NEW.from_stage THEN
        RAISE EXCEPTION
            'Evento rompe a cadeia de etapas da execucao: %',
            NEW.execution_id;
    END IF;

    expected_version := atrio.expected_component_version(
        NEW.release_id,
        NEW.component
    );

    IF NEW.component_version <> expected_version THEN
        RAISE EXCEPTION
            'Versao do evento divergente: esperado %, recebido %',
            expected_version,
            NEW.component_version;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER execution_events_validate_version
BEFORE INSERT ON atrio.execution_events
FOR EACH ROW
EXECUTE FUNCTION atrio.validate_event_version();

CREATE FUNCTION atrio.protect_immutable_row()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
BEGIN
    RAISE EXCEPTION
        'Registro imutavel em %.%: operacao % recusada',
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_OP;
END;
$$;

CREATE TRIGGER releases_are_immutable
BEFORE UPDATE OR DELETE ON atrio.releases
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER schema_migrations_are_immutable
BEFORE UPDATE OR DELETE ON atrio.schema_migrations
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER artifacts_are_immutable
BEFORE UPDATE OR DELETE ON atrio.artifacts
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER idempotency_keys_are_immutable
BEFORE UPDATE OR DELETE ON atrio.idempotency_keys
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER command_log_is_append_only
BEFORE UPDATE OR DELETE ON atrio.command_log
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER execution_events_are_append_only
BEFORE UPDATE OR DELETE ON atrio.execution_events
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE FUNCTION atrio.protect_released_execution()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Execucoes nao podem ser excluidas.';
    END IF;

    IF OLD.stage = 'RELEASED' THEN
        RAISE EXCEPTION 'Execucao liberada e imutavel: %', OLD.execution_id;
    END IF;

    IF ROW(
        NEW.execution_id,
        NEW.tenant_id,
        NEW.created_by,
        NEW.ratio_module,
        NEW.destination,
        NEW.release_id,
        NEW.created_at
    ) IS DISTINCT FROM ROW(
        OLD.execution_id,
        OLD.tenant_id,
        OLD.created_by,
        OLD.ratio_module,
        OLD.destination,
        OLD.release_id,
        OLD.created_at
    ) THEN
        RAISE EXCEPTION
            'Identidade e release da execucao sao imutaveis: %',
            OLD.execution_id;
    END IF;

    IF NEW.state_version <> OLD.state_version + 1 THEN
        RAISE EXCEPTION
            'Versao de estado deve avancar exatamente uma unidade: %',
            OLD.execution_id;
    END IF;

    NEW.updated_at := clock_timestamp();
    IF NEW.stage = 'RELEASED' THEN
        NEW.released_at := COALESCE(NEW.released_at, clock_timestamp());
    ELSE
        NEW.released_at := NULL;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER executions_protect_release
BEFORE UPDATE OR DELETE ON atrio.executions
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_released_execution();

CREATE FUNCTION atrio.validate_execution_transition_audit()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
          FROM atrio.command_log AS c
          JOIN atrio.execution_events AS ev
            ON ev.execution_id = c.execution_id
           AND ev.sequence = c.sequence
         WHERE c.execution_id = NEW.execution_id
           AND c.expected_version = OLD.state_version
           AND c.resulting_version = NEW.state_version
           AND ev.from_stage = OLD.stage
           AND ev.to_stage = NEW.stage
    ) THEN
        RAISE EXCEPTION
            'Transicao sem comando e evento correspondentes: execucao %, versao %',
            NEW.execution_id,
            NEW.state_version;
    END IF;

    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER executions_require_audit
AFTER UPDATE ON atrio.executions
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION atrio.validate_execution_transition_audit();

INSERT INTO atrio.schema_migrations (version, checksum)
VALUES ('1.0.0', :'migration_checksum');

COMMIT;

\echo 'ATRIO DB schema 1.0.0 aplicado com sucesso.'

\endif

SELECT version, checksum, applied_at, applied_by
  FROM atrio.schema_migrations
 ORDER BY applied_at;
