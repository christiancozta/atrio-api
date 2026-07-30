\set ON_ERROR_STOP on

-- ATRIO DB schema 1.3.0
-- Runtime interno do RATIO: head, snapshots, transicoes, decisoes,
-- referencias de artefato e idempotencia.

SELECT pg_catalog.set_config('search_path', 'pg_catalog', false);

SELECT EXISTS (
    SELECT 1
      FROM atrio.schema_migrations
     WHERE version = '1.3.0'
) AS migration_applied
\gset

\if :migration_applied
    SELECT checksum = :'migration_checksum' AS checksum_matches
      FROM atrio.schema_migrations
     WHERE version = '1.3.0'
    \gset

    \if :checksum_matches
        \echo 'ATRIO DB schema 1.3.0 ja aplicado; checksum confirmado.'
    \else
        \echo 'ERRO: schema 1.3.0 registrado com checksum diferente.'
        DO $migration_error$
        BEGIN
            RAISE EXCEPTION
                'Schema 1.3.0 registrado com checksum diferente';
        END
        $migration_error$;
    \endif
\else

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

CREATE TABLE atrio.ratio_runs (
    execution_id uuid PRIMARY KEY
        REFERENCES atrio.executions (execution_id) ON DELETE RESTRICT,
    module text NOT NULL
        CHECK (module IN ('RI', 'ED', 'MS')),
    head_revision bigint NOT NULL DEFAULT 0
        CHECK (head_revision >= 0),
    started_command_sequence bigint NOT NULL
        CHECK (started_command_sequence > 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (execution_id, module),
    FOREIGN KEY (execution_id, started_command_sequence)
        REFERENCES atrio.command_log (execution_id, sequence)
        ON DELETE RESTRICT
);

CREATE FUNCTION atrio.validate_ratio_run_start()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
DECLARE
    execution_module text;
    command_kind_value text;
BEGIN
    SELECT e.ratio_module
      INTO execution_module
      FROM atrio.executions AS e
     WHERE e.execution_id = NEW.execution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Execucao desconhecida para runtime RATIO: %',
            NEW.execution_id;
    END IF;

    IF execution_module <> NEW.module THEN
        RAISE EXCEPTION
            'Modulo RATIO diverge da execucao: %',
            NEW.execution_id;
    END IF;

    SELECT c.command_kind
      INTO command_kind_value
      FROM atrio.command_log AS c
     WHERE c.execution_id = NEW.execution_id
       AND c.sequence = NEW.started_command_sequence;

    IF NOT FOUND OR command_kind_value <> 'START_RATIO' THEN
        RAISE EXCEPTION
            'Runtime RATIO exige comando START_RATIO persistido: %',
            NEW.execution_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER ratio_runs_validate_start
BEFORE INSERT ON atrio.ratio_runs
FOR EACH ROW
EXECUTE FUNCTION atrio.validate_ratio_run_start();

CREATE FUNCTION atrio.protect_ratio_run_head()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION
            'Runtime RATIO nao pode ser excluido: %',
            OLD.execution_id;
    END IF;

    IF ROW(
        NEW.execution_id,
        NEW.module,
        NEW.started_command_sequence,
        NEW.created_at
    ) IS DISTINCT FROM ROW(
        OLD.execution_id,
        OLD.module,
        OLD.started_command_sequence,
        OLD.created_at
    ) THEN
        RAISE EXCEPTION
            'Identidade do runtime RATIO e imutavel: %',
            OLD.execution_id;
    END IF;

    IF NEW.head_revision <> OLD.head_revision + 1 THEN
        RAISE EXCEPTION
            'Revisao RATIO deve avancar exatamente uma unidade: %',
            OLD.execution_id;
    END IF;

    IF NEW.updated_at < OLD.updated_at THEN
        RAISE EXCEPTION
            'updated_at do runtime RATIO nao pode retroceder: %',
            OLD.execution_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER ratio_runs_protect_head
BEFORE UPDATE OR DELETE ON atrio.ratio_runs
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_ratio_run_head();

CREATE TABLE atrio.ratio_snapshots (
    execution_id uuid NOT NULL,
    revision bigint NOT NULL CHECK (revision >= 0),
    module text NOT NULL CHECK (module IN ('RI', 'ED', 'MS')),
    current_phase text NOT NULL
        CHECK (
            current_phase IN (
                'RI_01', 'RI_02', 'RI_03', 'RI_04', 'RI_05', 'RI_06',
                'ED_01', 'ED_02', 'ED_03', 'ED_04', 'ED_05',
                'MS_01', 'MS_02', 'MS_03', 'MS_04', 'MS_05', 'MS_06', 'MS_07'
            )
        ),
    last_operator_action text
        CHECK (
            last_operator_action IS NULL
            OR length(btrim(last_operator_action)) > 0
        ),
    troia_mode text NOT NULL
        CHECK (
            troia_mode IN (
                'AUTONOMOUS_REQUIRED',
                'EMBEDDED_CONDITIONAL',
                'NOT_DEFINED'
            )
        ),
    troia_phase text
        CHECK (
            troia_phase IS NULL
            OR troia_phase IN (
                'RI_01', 'RI_02', 'RI_03', 'RI_04', 'RI_05', 'RI_06',
                'ED_01', 'ED_02', 'ED_03', 'ED_04', 'ED_05',
                'MS_01', 'MS_02', 'MS_03', 'MS_04', 'MS_05', 'MS_06', 'MS_07'
            )
        ),
    troia_status text NOT NULL
        CHECK (
            troia_status IN (
                'NOT_STARTED',
                'RUNNING',
                'BLOCKED',
                'PENDING_REMEDIATION',
                'VALIDATED',
                'DISPENSED',
                'INVALIDATED',
                'NOT_DEFINED'
            )
        ),
    troia_triggers text[] NOT NULL DEFAULT ARRAY[]::text[]
        CHECK (
            troia_triggers <@ ARRAY[
                'INFRINGING_EFFECT_REQUEST',
                'MATERIAL_RESULT_CHANGE',
                'RELEVANT_ADVERSARIAL_ROUTE',
                'MERITS_REDISCUSSION_RISK',
                'REASONING_DISPOSITION_CONTRADICTION',
                'BREAKING_POINT_IDENTIFIED',
                'FUTURE_VOTE_OMISSION_RISK'
            ]::text[]
        ),
    troia_blocking_code text
        CHECK (
            troia_blocking_code IS NULL
            OR length(btrim(troia_blocking_code)) > 0
        ),
    state_sha256 character(64) NOT NULL
        CHECK (state_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (execution_id, revision),
    UNIQUE (execution_id, revision, module),
    FOREIGN KEY (execution_id, module)
        REFERENCES atrio.ratio_runs (execution_id, module)
        ON DELETE RESTRICT,
    CHECK (
        (
            module = 'RI'
            AND current_phase IN (
                'RI_01', 'RI_02', 'RI_03', 'RI_04', 'RI_05', 'RI_06'
            )
        )
        OR (
            module = 'ED'
            AND current_phase IN (
                'ED_01', 'ED_02', 'ED_03', 'ED_04', 'ED_05'
            )
        )
        OR (
            module = 'MS'
            AND current_phase IN (
                'MS_01', 'MS_02', 'MS_03', 'MS_04', 'MS_05', 'MS_06', 'MS_07'
            )
        )
    ),
    CHECK (
        (
            module = 'RI'
            AND troia_mode = 'AUTONOMOUS_REQUIRED'
            AND troia_phase = 'RI_03'
            AND troia_status <> 'NOT_DEFINED'
            AND cardinality(troia_triggers) = 0
        )
        OR (
            module = 'ED'
            AND troia_mode = 'EMBEDDED_CONDITIONAL'
            AND troia_phase = 'ED_03'
            AND troia_status <> 'NOT_DEFINED'
        )
        OR (
            module = 'MS'
            AND troia_mode = 'NOT_DEFINED'
            AND troia_phase IS NULL
            AND troia_status = 'NOT_DEFINED'
            AND cardinality(troia_triggers) = 0
            AND troia_blocking_code IS NULL
        )
    ),
    CHECK (
        (
            troia_status = 'BLOCKED'
            AND troia_blocking_code IS NOT NULL
        )
        OR (
            troia_status <> 'BLOCKED'
            AND troia_blocking_code IS NULL
        )
    )
);

CREATE INDEX ratio_snapshots_created_idx
    ON atrio.ratio_snapshots (execution_id, created_at DESC);

CREATE TABLE atrio.ratio_snapshot_phases (
    execution_id uuid NOT NULL,
    revision bigint NOT NULL CHECK (revision >= 0),
    module text NOT NULL CHECK (module IN ('RI', 'ED', 'MS')),
    phase text NOT NULL
        CHECK (
            phase IN (
                'RI_01', 'RI_02', 'RI_03', 'RI_04', 'RI_05', 'RI_06',
                'ED_01', 'ED_02', 'ED_03', 'ED_04', 'ED_05',
                'MS_01', 'MS_02', 'MS_03', 'MS_04', 'MS_05', 'MS_06', 'MS_07'
            )
        ),
    status text NOT NULL
        CHECK (
            status IN (
                'NOT_STARTED',
                'ANALYZING',
                'BLOCKED',
                'PENDING_REMEDIATION',
                'VALIDATED',
                'VALIDATED_WITH_NONBLOCKING_CAVEAT',
                'DISPENSED_BY_EXCEPTION',
                'INVALIDATED_BY_SUBSTANTIAL_CHANGE',
                'ENDED_FOR_NOW_AFTER_INJUNCTION'
            )
        ),
    PRIMARY KEY (execution_id, revision, phase),
    FOREIGN KEY (execution_id, revision, module)
        REFERENCES atrio.ratio_snapshots (execution_id, revision, module)
        ON DELETE RESTRICT,
    CHECK (
        (module = 'RI' AND phase LIKE 'RI\_%' ESCAPE '\')
        OR (module = 'ED' AND phase LIKE 'ED\_%' ESCAPE '\')
        OR (module = 'MS' AND phase LIKE 'MS\_%' ESCAPE '\')
    )
);

CREATE TABLE atrio.ratio_transitions (
    execution_id uuid NOT NULL,
    expected_revision bigint NOT NULL CHECK (expected_revision >= 0),
    resulting_revision bigint NOT NULL CHECK (resulting_revision > 0),
    action text NOT NULL CHECK (length(btrim(action)) > 0),
    actor_id text NOT NULL CHECK (length(btrim(actor_id)) > 0),
    payload_fingerprint character(64) NOT NULL
        CHECK (payload_fingerprint ~ '^[0-9a-f]{64}$'),
    external_command_sequence bigint
        CHECK (
            external_command_sequence IS NULL
            OR external_command_sequence > 0
        ),
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (execution_id, resulting_revision),
    FOREIGN KEY (execution_id, expected_revision)
        REFERENCES atrio.ratio_snapshots (execution_id, revision)
        ON DELETE RESTRICT,
    FOREIGN KEY (execution_id, resulting_revision)
        REFERENCES atrio.ratio_snapshots (execution_id, revision)
        ON DELETE RESTRICT,
    FOREIGN KEY (execution_id, external_command_sequence)
        REFERENCES atrio.command_log (execution_id, sequence)
        ON DELETE RESTRICT,
    CHECK (resulting_revision = expected_revision + 1)
);

CREATE UNIQUE INDEX ratio_transitions_external_command_unique
    ON atrio.ratio_transitions (execution_id, external_command_sequence)
    WHERE external_command_sequence IS NOT NULL;

CREATE TABLE atrio.ratio_operator_decisions (
    decision_id uuid PRIMARY KEY,
    execution_id uuid NOT NULL,
    ratio_revision bigint NOT NULL CHECK (ratio_revision > 0),
    phase text NOT NULL
        CHECK (
            phase IN (
                'RI_01', 'RI_02', 'RI_03', 'RI_04', 'RI_05', 'RI_06',
                'ED_01', 'ED_02', 'ED_03', 'ED_04', 'ED_05',
                'MS_01', 'MS_02', 'MS_03', 'MS_04', 'MS_05', 'MS_06', 'MS_07'
            )
        ),
    decision_code text NOT NULL
        CHECK (length(btrim(decision_code)) > 0),
    actor_id text NOT NULL
        CHECK (length(btrim(actor_id)) > 0),
    payload_fingerprint character(64) NOT NULL
        CHECK (payload_fingerprint ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (execution_id, ratio_revision),
    FOREIGN KEY (execution_id, ratio_revision)
        REFERENCES atrio.ratio_snapshots (execution_id, revision)
        ON DELETE RESTRICT
);

CREATE TABLE atrio.ratio_artifact_refs (
    execution_id uuid NOT NULL,
    ratio_revision bigint NOT NULL CHECK (ratio_revision >= 0),
    artifact_role text NOT NULL
        CHECK (length(btrim(artifact_role)) > 0),
    artifact_id text NOT NULL
        REFERENCES atrio.artifacts (artifact_id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (
        execution_id,
        ratio_revision,
        artifact_role,
        artifact_id
    ),
    FOREIGN KEY (execution_id, ratio_revision)
        REFERENCES atrio.ratio_snapshots (execution_id, revision)
        ON DELETE RESTRICT
);

CREATE FUNCTION atrio.validate_ratio_artifact_ref()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, atrio
AS $$
DECLARE
    artifact_execution_id uuid;
    artifact_release_id text;
    execution_release_id text;
BEGIN
    SELECT a.owner_execution_id, a.release_id
      INTO artifact_execution_id, artifact_release_id
      FROM atrio.artifacts AS a
     WHERE a.artifact_id = NEW.artifact_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Artefato desconhecido para RATIO: %',
            NEW.artifact_id;
    END IF;

    SELECT e.release_id
      INTO execution_release_id
      FROM atrio.executions AS e
     WHERE e.execution_id = NEW.execution_id;

    IF artifact_execution_id <> NEW.execution_id
       OR artifact_release_id <> execution_release_id THEN
        RAISE EXCEPTION
            'Referencia de artefato RATIO cruza execucao ou release: %',
            NEW.artifact_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER ratio_artifact_refs_validate
BEFORE INSERT ON atrio.ratio_artifact_refs
FOR EACH ROW
EXECUTE FUNCTION atrio.validate_ratio_artifact_ref();

CREATE TABLE atrio.ratio_idempotency_keys (
    execution_id uuid NOT NULL,
    idempotency_key text NOT NULL
        CHECK (
            length(btrim(idempotency_key)) > 0
            AND length(idempotency_key) <= 200
        ),
    request_fingerprint character(64) NOT NULL
        CHECK (request_fingerprint ~ '^[0-9a-f]{64}$'),
    resulting_revision bigint NOT NULL CHECK (resulting_revision >= 0),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (execution_id, idempotency_key),
    FOREIGN KEY (execution_id, resulting_revision)
        REFERENCES atrio.ratio_snapshots (execution_id, revision)
        ON DELETE RESTRICT
);

CREATE TRIGGER ratio_snapshots_are_immutable
BEFORE UPDATE OR DELETE ON atrio.ratio_snapshots
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER ratio_snapshot_phases_are_immutable
BEFORE UPDATE OR DELETE ON atrio.ratio_snapshot_phases
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER ratio_transitions_are_immutable
BEFORE UPDATE OR DELETE ON atrio.ratio_transitions
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER ratio_operator_decisions_are_immutable
BEFORE UPDATE OR DELETE ON atrio.ratio_operator_decisions
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER ratio_artifact_refs_are_immutable
BEFORE UPDATE OR DELETE ON atrio.ratio_artifact_refs
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

CREATE TRIGGER ratio_idempotency_keys_are_immutable
BEFORE UPDATE OR DELETE ON atrio.ratio_idempotency_keys
FOR EACH ROW
EXECUTE FUNCTION atrio.protect_immutable_row();

INSERT INTO atrio.schema_migrations (version, checksum)
VALUES ('1.3.0', :'migration_checksum');

COMMIT;

\echo 'ATRIO DB schema 1.3.0 aplicado com sucesso.'

\endif

SELECT version, checksum, applied_at, applied_by
  FROM atrio.schema_migrations
 ORDER BY applied_at;
