from __future__ import annotations

import asyncio
import json
import sqlite3
import threading
from pathlib import Path
from typing import Protocol

from atrio_api.cerne_core.domain import AuditResponse


class AuditRepository(Protocol):
    async def initialize(self) -> None: ...

    async def save_summary(self, response: AuditResponse) -> None: ...


class SQLiteAuditRepository:
    """Persiste somente telemetria; nunca o documento ou os achados textuais."""

    def __init__(self, path: Path):
        self._path = path
        self._lock = threading.Lock()

    async def initialize(self) -> None:
        await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_runs (
                    audit_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    gate TEXT NOT NULL,
                    decision_mode TEXT NOT NULL,
                    model TEXT NOT NULL,
                    axes TEXT NOT NULL,
                    confrontations TEXT NOT NULL,
                    finding_count INTEGER NOT NULL,
                    clean_result INTEGER NOT NULL,
                    log_json TEXT NOT NULL
                )
                """
            )

    async def save_summary(self, response: AuditResponse) -> None:
        await asyncio.to_thread(self._save_summary_sync, response)

    def _save_summary_sync(self, response: AuditResponse) -> None:
        log_json = response.log.model_dump_json()
        axes = json.dumps([axis.value for axis in response.log.lentes_acionadas])
        confrontations = json.dumps(response.log.confrontos_acionados)
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_runs (
                    audit_id, case_id, created_at, status, gate, decision_mode,
                    model, axes, confrontations, finding_count, clean_result, log_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response.auditoria_id,
                    response.log.caso_id,
                    response.criada_em.isoformat(),
                    "concluida",
                    response.gate.estado.value,
                    response.triagem.modo_decisorio.value,
                    response.log.modelo,
                    axes,
                    confrontations,
                    response.log.achados_confirmados,
                    int(response.log.resultado_limpo),
                    log_json,
                ),
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path)


class InMemoryAuditRepository:
    def __init__(self):
        self.records: list[AuditResponse] = []

    async def initialize(self) -> None:
        return None

    async def save_summary(self, response: AuditResponse) -> None:
        self.records.append(response)
