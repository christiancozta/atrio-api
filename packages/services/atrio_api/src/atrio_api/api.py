from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, Header, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from atrio_api import __version__
from atrio_api.api_models import (
    CommandBody,
    CerneAuditBody,
    CerneAuditResponse,
    CerneOperatorBody,
    LuxRefineBody,
    LuxRefineResponse,
    CorpusActionBody,
    CorpusBatchResponse,
    CorpusDocumentStatusResponse,
    CorpusFinalizeResponse,
    CorpusReviewBody,
    CorpusReviewResponse,
    CreateCorpusDocumentResponse,
    CreateExecutionBody,
    CreateExecutionResponse,
    EventResponse,
    ExecutionResponse,
    FinalActionBody,
    FinalIntegrityFailureBody,
    RatioActionBody,
    RatioMutationResponse,
    RatioExecuteBody,
    RatioExecutionResponse,
    RatioFinalizeBody,
    RatioFinalizeResponse,
    RatioStartBody,
    RatioStateResponse,
    LuxRetryBody,
    corpus_batch_response,
    cerne_audit_response,
    lux_refinement_response,
    corpus_document_response,
    corpus_document_status_response,
    corpus_finalize_response,
    corpus_review_response,
    event_response,
    execution_response,
    ratio_mutation_response,
    ratio_execution_response,
    ratio_finalize_response,
    ratio_state_response,
)
from atrio_api.corpus_processing import (
    CORPUS_PIPELINE_VERSION,
    CorpusExtractionFailed,
    CorpusIntegrityMismatch,
    CorpusToolUnavailable,
)
from atrio_api.corpus_service import (
    CorpusNoDocuments,
    CorpusProcessingIncomplete,
    CorpusReviewNotFound,
    CorpusWorkflowService,
)
from atrio_api.corpus_intake import (
    ENVELOPE_VERSION,
    INTAKE_VERSION,
    MAX_DOCUMENT_BYTES,
    CorpusIntakeConflict,
    CorpusIntakeService,
    DocumentTooLarge,
    InvalidDocumentSignature,
    UnsupportedDocumentType,
    VaultIntegrityError,
)
from atrio_api.cerne.execution import (
    CerneArtifactMissing,
    CerneExecutionUnavailable,
    CerneIntegrityError,
)
from atrio_api.cerne.service import CerneWorkflowService
from atrio_api.cerne_core.knowledge import KnowledgeError as CerneKnowledgeError
from atrio_api.cerne_core.orchestrator import DomainError as CerneDomainError
from atrio_api.cerne_core.provider import ProviderError as CerneProviderError
from atrio_api.database import DATABASE_SCHEMA_VERSION
from atrio_api.domain import (
    Command,
    CommandKind,
    CreateExecutionRequest,
    ReleaseEnvelope,
)
from atrio_api.lux.execution import (
    LuxArtifactMissing,
    LuxExecutionUnavailable,
    LuxGeneratedOutputInvalid,
    LuxIntegrityError,
    LuxPrivacyError,
    LuxProviderError,
    LuxRequestError,
)
from atrio_api.lux.service import LuxWorkflowService
from atrio_api.ratio.catalog import HardStopCatalogError
from atrio_api.ratio.engine import RatioTransitionError
from atrio_api.ratio.execution import (
    RatioArtifactMissing,
    RatioExecutionUnavailable,
    RatioExecutorIntegrityError,
    RatioGeneratedOutputInvalid,
)
from atrio_api.ratio.persistence import (
    RatioPersistenceIntegrityError,
    RatioRevisionConflict,
    RatioRuntimeAlreadyStarted,
    RatioRuntimeNotFound,
)
from atrio_api.ratio.service import (
    RatioActionPayloadError,
    RatioWorkflowService,
)
from atrio_api.repository import (
    ExecutionNotFound,
    IdempotencyConflict,
    RepositoryError,
)
from atrio_api.service import ExecutionService
from atrio_api.state_machine import (
    InvalidCommandPayload,
    InvalidTransition,
    VersionConflict,
)


ReadinessCheck = Callable[[], None]
IDEMPOTENCY_PATTERN = r"^[A-Za-z0-9_][A-Za-z0-9_.:@/-]*$"


class CorpusIntakeUnavailable(RuntimeError):
    pass


class CorpusWorkflowUnavailable(RuntimeError):
    pass


class RatioWorkflowUnavailable(RuntimeError):
    pass


class CerneWorkflowUnavailable(RuntimeError):
    pass


class LuxWorkflowUnavailable(RuntimeError):
    pass


def create_app(
    service: ExecutionService,
    *,
    release: ReleaseEnvelope,
    readiness_check: ReadinessCheck,
    corpus_intake: CorpusIntakeService | None = None,
    corpus_workflow: CorpusWorkflowService | None = None,
    ratio_workflow: RatioWorkflowService | None = None,
    cerne_workflow: CerneWorkflowService | None = None,
    lux_workflow: LuxWorkflowService | None = None,
    ui_path: Path | None = None,
) -> FastAPI:
    resolved_ui_path = ui_path.resolve() if ui_path is not None else None
    if resolved_ui_path is not None and not resolved_ui_path.is_file():
        raise FileNotFoundError(
            f"Interface ATRIO não encontrada: {resolved_ui_path}"
        )

    app = FastAPI(
        title="ATRIO Local API",
        version=__version__,
        description=(
            "Via única local para CORPUS → RATIO → CERNE → LUX. "
            "A API transporta apenas comandos, códigos e referências."
        ),
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    _install_exception_handlers(app)

    if resolved_ui_path is not None:

        @app.get("/", include_in_schema=False)
        def interface() -> FileResponse:
            return FileResponse(
                resolved_ui_path,
                media_type="text/html",
                headers={
                    "Cache-Control": "no-store",
                    "X-Content-Type-Options": "nosniff",
                    "Referrer-Policy": "no-referrer",
                    "Permissions-Policy": (
                        "camera=(), microphone=(), geolocation=()"
                    ),
                },
            )

    @app.get("/v1/health/live")
    def live() -> dict[str, str]:
        return {
            "status": "live",
            "atrio_api_version": __version__,
        }

    @app.get("/v1/health/ready")
    def ready() -> dict[str, str]:
        readiness_check()
        return {
            "status": "ready",
            "atrio_api_version": __version__,
            "database_schema_version": DATABASE_SCHEMA_VERSION,
            "release_id": release.release_id,
            "corpus_intake_version": INTAKE_VERSION,
            "corpus_pipeline_version": CORPUS_PIPELINE_VERSION,
            "vault_envelope_version": ENVELOPE_VERSION,
        }

    @app.post(
        "/v1/executions",
        response_model=CreateExecutionResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_execution(
        body: CreateExecutionBody,
        response: Response,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
    ) -> CreateExecutionResponse:
        result = service.create(
            CreateExecutionRequest(
                tenant_id=body.tenant_id,
                actor_id=body.actor_id,
                idempotency_key=idempotency_key,
                ratio_module=body.ratio_module,
                destination=body.destination,
            ),
            release,
        )
        if not result.created:
            response.status_code = status.HTTP_200_OK
        return CreateExecutionResponse(
            created=result.created,
            execution=execution_response(result.state),
        )

    @app.get(
        "/v1/executions/{execution_id}",
        response_model=ExecutionResponse,
    )
    def get_execution(execution_id: UUID) -> ExecutionResponse:
        return execution_response(service.get(str(execution_id)))

    @app.post(
        "/v1/executions/{execution_id}/commands",
        response_model=ExecutionResponse,
    )
    def apply_command(
        execution_id: UUID,
        body: CommandBody,
    ) -> ExecutionResponse:
        if body.kind in {
            CommandKind.REGISTER_CORPUS_DOCUMENT,
            CommandKind.REQUEST_CORPUS_REVIEW,
            CommandKind.RESUME_CORPUS,
            CommandKind.COMPLETE_CORPUS,
        }:
            raise InvalidCommandPayload(
                "O comando só pode ocorrer pela rota governada do CORPUS."
            )
        if body.kind in {
            CommandKind.START_RATIO,
            CommandKind.REQUEST_OPERATOR_DECISION,
            CommandKind.RECORD_OPERATOR_DECISION,
            CommandKind.COMPLETE_RATIO,
            CommandKind.COMPLETE_RATIO_REWORK,
        }:
            raise InvalidCommandPayload(
                "O comando só pode ocorrer pela rota governada do RATIO."
            )
        if body.kind in {
            CommandKind.START_CERNE,
            CommandKind.APPLY_CERNE_GATE,
            CommandKind.RETURN_TO_RATIO,
            CommandKind.REOPEN_TOTAL_BLOCK,
        }:
            raise InvalidCommandPayload(
                "O comando só pode ocorrer pela rota governada do CERNE."
            )
        if body.kind in {
            CommandKind.START_LUX,
            CommandKind.COMPLETE_LUX,
        }:
            raise InvalidCommandPayload(
                "O comando só pode ocorrer pela rota governada do LUX."
            )
        if body.kind in {
            CommandKind.PASS_FINAL_INTEGRITY,
            CommandKind.FAIL_FINAL_INTEGRITY,
            CommandKind.RETRY_LUX,
            CommandKind.RELEASE,
        }:
            raise InvalidCommandPayload(
                "O comando exige o runtime governado de integridade/release."
            )
        result = service.command(str(execution_id), body.to_domain())
        return execution_response(result.state)

    @app.post(
        "/v1/executions/{execution_id}/corpus/documents",
        response_model=CreateCorpusDocumentResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_corpus_document(
        execution_id: UUID,
        request: Request,
        response: Response,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
        expected_version: Annotated[
            int,
            Header(alias="X-ATRIO-Expected-Version", ge=0),
        ],
        actor_id: Annotated[
            str,
            Header(
                alias="X-ATRIO-Actor",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
        content_type: Annotated[str, Header(alias="Content-Type")],
        content_length: Annotated[
            int | None,
            Header(alias="Content-Length", ge=0),
        ] = None,
    ) -> CreateCorpusDocumentResponse:
        if corpus_intake is None:
            raise CorpusIntakeUnavailable
        if content_length is not None and content_length > MAX_DOCUMENT_BYTES:
            raise DocumentTooLarge(
                "Documento excede o limite de 50 MiB."
            )
        media_type = _normalize_media_type(content_type)
        result = await corpus_intake.ingest(
            request.stream(),
            execution_id=str(execution_id),
            idempotency_key=idempotency_key,
            actor_id=actor_id,
            expected_version=expected_version,
            media_type=media_type,
        )
        if not result.created:
            response.status_code = status.HTTP_200_OK
        return CreateCorpusDocumentResponse(
            created=result.created,
            document=corpus_document_response(result.intake),
            execution=execution_response(result.state),
        )

    @app.get(
        "/v1/executions/{execution_id}/corpus/documents",
        response_model=list[CorpusDocumentStatusResponse],
    )
    def list_corpus_documents(
        execution_id: UUID,
    ) -> list[CorpusDocumentStatusResponse]:
        if corpus_workflow is None:
            raise CorpusWorkflowUnavailable
        return [
            corpus_document_status_response(document)
            for document in corpus_workflow.list_documents(str(execution_id))
        ]

    @app.post(
        "/v1/executions/{execution_id}/corpus/process",
        response_model=CorpusBatchResponse,
    )
    def process_corpus_documents(
        execution_id: UUID,
        body: CorpusActionBody,
    ) -> CorpusBatchResponse:
        if corpus_workflow is None:
            raise CorpusWorkflowUnavailable
        return corpus_batch_response(
            corpus_workflow.process_pending(
                execution_id=str(execution_id),
                actor_id=body.actor_id,
                expected_version=body.expected_version,
            )
        )

    @app.post(
        (
            "/v1/executions/{execution_id}/corpus/documents/"
            "{document_id}/review"
        ),
        response_model=CorpusReviewResponse,
    )
    def review_corpus_document(
        execution_id: UUID,
        document_id: UUID,
        body: CorpusReviewBody,
    ) -> CorpusReviewResponse:
        if corpus_workflow is None:
            raise CorpusWorkflowUnavailable
        return corpus_review_response(
            corpus_workflow.review(
                execution_id=str(execution_id),
                document_id=str(document_id),
                decision=body.decision,
                actor_id=body.actor_id,
                expected_version=body.expected_version,
            )
        )

    @app.post(
        "/v1/executions/{execution_id}/corpus/finalize",
        response_model=CorpusFinalizeResponse,
    )
    def finalize_corpus(
        execution_id: UUID,
        body: CorpusActionBody,
    ) -> CorpusFinalizeResponse:
        if corpus_workflow is None:
            raise CorpusWorkflowUnavailable
        return corpus_finalize_response(
            corpus_workflow.finalize(
                execution_id=str(execution_id),
                actor_id=body.actor_id,
                expected_version=body.expected_version,
            )
        )

    @app.post(
        "/v1/executions/{execution_id}/ratio/start",
        response_model=RatioMutationResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def start_ratio(
        execution_id: UUID,
        body: RatioStartBody,
        response: Response,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
    ) -> RatioMutationResponse:
        if ratio_workflow is None:
            raise RatioWorkflowUnavailable
        result = ratio_workflow.start(
            str(execution_id),
            actor_id=body.actor_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
        if not result.created:
            response.status_code = status.HTTP_200_OK
        return ratio_mutation_response(
            execution=result.execution_state,
            ratio=result.ratio_state,
            created=result.created,
        )

    @app.get(
        "/v1/executions/{execution_id}/ratio",
        response_model=RatioStateResponse,
    )
    def get_ratio(execution_id: UUID) -> RatioStateResponse:
        if ratio_workflow is None:
            raise RatioWorkflowUnavailable
        return ratio_state_response(ratio_workflow.get(str(execution_id)))

    @app.post(
        "/v1/executions/{execution_id}/ratio/actions",
        response_model=RatioMutationResponse,
    )
    def apply_ratio_action(
        execution_id: UUID,
        body: RatioActionBody,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
    ) -> RatioMutationResponse:
        if ratio_workflow is None:
            raise RatioWorkflowUnavailable
        result = ratio_workflow.act(
            str(execution_id),
            action=body.action,
            expected_revision=body.expected_revision,
            actor_id=body.actor_id,
            idempotency_key=idempotency_key,
            troia_triggers=frozenset(body.troia_triggers),
            blocking_code=body.blocking_code,
            target_phase=body.target_phase,
        )
        return ratio_mutation_response(
            execution=result.execution_state,
            ratio=result.ratio_state,
            created=result.created,
        )

    @app.post(
        "/v1/executions/{execution_id}/ratio/execute",
        response_model=RatioExecutionResponse,
    )
    def execute_ratio_phase(
        execution_id: UUID,
        body: RatioExecuteBody,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
    ) -> RatioExecutionResponse:
        if ratio_workflow is None:
            raise RatioWorkflowUnavailable
        return ratio_execution_response(
            ratio_workflow.execute_phase(
                str(execution_id),
                expected_revision=body.expected_revision,
                actor_id=body.actor_id,
                idempotency_key=idempotency_key,
            )
        )

    @app.post(
        "/v1/executions/{execution_id}/ratio/finalize",
        response_model=RatioFinalizeResponse,
    )
    def finalize_ratio(
        execution_id: UUID,
        body: RatioFinalizeBody,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
    ) -> RatioFinalizeResponse:
        if ratio_workflow is None:
            raise RatioWorkflowUnavailable
        return ratio_finalize_response(
            ratio_workflow.finalize(
                str(execution_id),
                expected_revision=body.expected_revision,
                expected_version=body.expected_version,
                actor_id=body.actor_id,
                idempotency_key=idempotency_key,
            )
        )

    @app.post(
        "/v1/executions/{execution_id}/cerne/audit",
        response_model=CerneAuditResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def audit_cerne(
        execution_id: UUID,
        body: CerneAuditBody,
        response: Response,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
    ) -> CerneAuditResponse:
        if cerne_workflow is None:
            raise CerneWorkflowUnavailable
        result = await cerne_workflow.audit(
            str(execution_id),
            expected_version=body.expected_version,
            actor_id=body.actor_id,
            idempotency_key=idempotency_key,
        )
        if not result.created:
            response.status_code = status.HTTP_200_OK
        return cerne_audit_response(result)

    @app.post(
        "/v1/executions/{execution_id}/cerne/return-to-ratio",
        response_model=ExecutionResponse,
    )
    def return_cerne_to_ratio(
        execution_id: UUID,
        body: CerneOperatorBody,
    ) -> ExecutionResponse:
        if cerne_workflow is None:
            raise CerneWorkflowUnavailable
        return execution_response(
            cerne_workflow.return_to_ratio(
                str(execution_id),
                expected_version=body.expected_version,
                actor_id=body.actor_id,
                decision_code=body.decision_code,
            )
        )

    @app.post(
        "/v1/executions/{execution_id}/cerne/reopen-total-block",
        response_model=ExecutionResponse,
    )
    def reopen_cerne_total_block(
        execution_id: UUID,
        body: CerneOperatorBody,
    ) -> ExecutionResponse:
        if cerne_workflow is None:
            raise CerneWorkflowUnavailable
        return execution_response(
            cerne_workflow.reopen_total_block(
                str(execution_id),
                expected_version=body.expected_version,
                actor_id=body.actor_id,
                decision_code=body.decision_code,
            )
        )

    @app.post(
        "/v1/executions/{execution_id}/lux/refine",
        response_model=LuxRefineResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def refine_lux(
        execution_id: UUID,
        body: LuxRefineBody,
        response: Response,
        idempotency_key: Annotated[
            str,
            Header(
                alias="Idempotency-Key",
                min_length=1,
                max_length=200,
                pattern=IDEMPOTENCY_PATTERN,
            ),
        ],
    ) -> LuxRefineResponse:
        if lux_workflow is None:
            raise LuxWorkflowUnavailable
        result = lux_workflow.refine(
            str(execution_id),
            expected_version=body.expected_version,
            actor_id=body.actor_id,
            idempotency_key=idempotency_key,
            mode=body.mode.value,
            profile=body.profile,
            data_mode=(
                body.data_mode.value
                if body.data_mode is not None
                else None
            ),
        )
        if not result.created:
            response.status_code = status.HTTP_200_OK
        return lux_refinement_response(result)

    @app.post(
        "/v1/executions/{execution_id}/final-integrity/pass",
        response_model=ExecutionResponse,
    )
    def pass_final_integrity(
        execution_id: UUID,
        body: FinalActionBody,
    ) -> ExecutionResponse:
        result = service.command(
            str(execution_id),
            Command(
                kind=CommandKind.PASS_FINAL_INTEGRITY,
                expected_version=body.expected_version,
                actor_id=body.actor_id,
            ),
        )
        return execution_response(result.state)

    @app.post(
        "/v1/executions/{execution_id}/final-integrity/fail",
        response_model=ExecutionResponse,
    )
    def fail_final_integrity(
        execution_id: UUID,
        body: FinalIntegrityFailureBody,
    ) -> ExecutionResponse:
        result = service.command(
            str(execution_id),
            Command(
                kind=CommandKind.FAIL_FINAL_INTEGRITY,
                expected_version=body.expected_version,
                actor_id=body.actor_id,
                payload={"reason_code": body.reason_code},
            ),
        )
        return execution_response(result.state)

    @app.post(
        "/v1/executions/{execution_id}/final-integrity/retry-lux",
        response_model=ExecutionResponse,
    )
    def retry_lux_after_integrity_block(
        execution_id: UUID,
        body: LuxRetryBody,
    ) -> ExecutionResponse:
        result = service.command(
            str(execution_id),
            Command(
                kind=CommandKind.RETRY_LUX,
                expected_version=body.expected_version,
                actor_id=body.actor_id,
                payload={"decision_code": body.decision_code},
            ),
        )
        return execution_response(result.state)

    @app.post(
        "/v1/executions/{execution_id}/release",
        response_model=ExecutionResponse,
    )
    def release_execution(
        execution_id: UUID,
        body: FinalActionBody,
    ) -> ExecutionResponse:
        result = service.command(
            str(execution_id),
            Command(
                kind=CommandKind.RELEASE,
                expected_version=body.expected_version,
                actor_id=body.actor_id,
            ),
        )
        return execution_response(result.state)

    @app.get(
        "/v1/executions/{execution_id}/events",
        response_model=list[EventResponse],
    )
    def get_events(execution_id: UUID) -> list[EventResponse]:
        return [
            event_response(item)
            for item in service.events(str(execution_id))
        ]

    return app


def _install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        safe_errors = [
            {
                "location": list(error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "REQUEST_VALIDATION_FAILED",
            errors=safe_errors,
        )

    @app.exception_handler(ExecutionNotFound)
    async def execution_not_found(
        _request: Request,
        _exc: ExecutionNotFound,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_404_NOT_FOUND,
            "EXECUTION_NOT_FOUND",
        )

    @app.exception_handler(IdempotencyConflict)
    async def idempotency_conflict(
        _request: Request,
        _exc: IdempotencyConflict,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "IDEMPOTENCY_CONFLICT",
        )

    @app.exception_handler(VersionConflict)
    async def version_conflict(
        _request: Request,
        exc: VersionConflict,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "STATE_VERSION_CONFLICT",
            expected=exc.expected,
            actual=exc.actual,
        )

    @app.exception_handler(InvalidTransition)
    async def invalid_transition(
        _request: Request,
        exc: InvalidTransition,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "INVALID_TRANSITION",
            stage=exc.stage.value,
            command=exc.command.value,
        )

    @app.exception_handler(InvalidCommandPayload)
    async def invalid_command_payload(
        _request: Request,
        _exc: InvalidCommandPayload,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "INVALID_COMMAND_PAYLOAD",
        )

    @app.exception_handler(UnsupportedDocumentType)
    async def unsupported_document_type(
        _request: Request,
        _exc: UnsupportedDocumentType,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "UNSUPPORTED_DOCUMENT_TYPE",
        )

    @app.exception_handler(DocumentTooLarge)
    async def document_too_large(
        _request: Request,
        _exc: DocumentTooLarge,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_413_CONTENT_TOO_LARGE,
            "DOCUMENT_TOO_LARGE",
            max_bytes=MAX_DOCUMENT_BYTES,
        )

    @app.exception_handler(InvalidDocumentSignature)
    async def invalid_document_signature(
        _request: Request,
        _exc: InvalidDocumentSignature,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "INVALID_DOCUMENT_SIGNATURE",
        )

    @app.exception_handler(CorpusIntakeConflict)
    async def corpus_intake_conflict(
        _request: Request,
        _exc: CorpusIntakeConflict,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "CORPUS_INTAKE_CONFLICT",
        )

    @app.exception_handler(VaultIntegrityError)
    async def vault_integrity_error(
        _request: Request,
        _exc: VaultIntegrityError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "VAULT_INTEGRITY_ERROR",
        )

    @app.exception_handler(CorpusIntakeUnavailable)
    async def corpus_intake_unavailable(
        _request: Request,
        _exc: CorpusIntakeUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "CORPUS_INTAKE_UNAVAILABLE",
        )

    @app.exception_handler(CorpusWorkflowUnavailable)
    async def corpus_workflow_unavailable(
        _request: Request,
        _exc: CorpusWorkflowUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "CORPUS_WORKFLOW_UNAVAILABLE",
        )

    @app.exception_handler(CorpusToolUnavailable)
    async def corpus_tool_unavailable(
        _request: Request,
        _exc: CorpusToolUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "CORPUS_TOOL_UNAVAILABLE",
        )

    @app.exception_handler(CorpusExtractionFailed)
    async def corpus_extraction_failed(
        _request: Request,
        _exc: CorpusExtractionFailed,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "CORPUS_EXTRACTION_FAILED",
        )

    @app.exception_handler(CorpusIntegrityMismatch)
    async def corpus_integrity_mismatch(
        _request: Request,
        _exc: CorpusIntegrityMismatch,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "CORPUS_INTEGRITY_MISMATCH",
        )

    @app.exception_handler(CorpusNoDocuments)
    async def corpus_no_documents(
        _request: Request,
        _exc: CorpusNoDocuments,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "CORPUS_NO_DOCUMENTS",
        )

    @app.exception_handler(CorpusProcessingIncomplete)
    async def corpus_processing_incomplete(
        _request: Request,
        _exc: CorpusProcessingIncomplete,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "CORPUS_PROCESSING_INCOMPLETE",
        )

    @app.exception_handler(CorpusReviewNotFound)
    async def corpus_review_not_found(
        _request: Request,
        _exc: CorpusReviewNotFound,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_404_NOT_FOUND,
            "CORPUS_REVIEW_NOT_FOUND",
        )

    @app.exception_handler(LuxArtifactMissing)
    async def lux_artifact_missing(
        _request: Request,
        _exc: LuxArtifactMissing,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "LUX_ARTIFACT_REQUIRED",
        )

    @app.exception_handler(LuxExecutionUnavailable)
    async def lux_execution_unavailable(
        _request: Request,
        _exc: LuxExecutionUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "LUX_EXECUTION_UNAVAILABLE",
        )

    @app.exception_handler(LuxRequestError)
    async def lux_request_error(
        _request: Request,
        _exc: LuxRequestError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "LUX_REQUEST_REJECTED",
        )

    @app.exception_handler(LuxPrivacyError)
    async def lux_privacy_error(
        _request: Request,
        _exc: LuxPrivacyError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "LUX_PRIVACY_REJECTED",
        )

    @app.exception_handler(LuxGeneratedOutputInvalid)
    async def lux_generated_output_invalid(
        _request: Request,
        _exc: LuxGeneratedOutputInvalid,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_502_BAD_GATEWAY,
            "LUX_OUTPUT_REJECTED",
        )

    @app.exception_handler(LuxProviderError)
    async def lux_provider_error(
        _request: Request,
        _exc: LuxProviderError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_502_BAD_GATEWAY,
            "LUX_PROVIDER_ERROR",
        )

    @app.exception_handler(LuxIntegrityError)
    async def lux_integrity_error(
        _request: Request,
        _exc: LuxIntegrityError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "LUX_INTEGRITY_ERROR",
        )

    @app.exception_handler(LuxWorkflowUnavailable)
    async def lux_workflow_unavailable(
        _request: Request,
        _exc: LuxWorkflowUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "LUX_WORKFLOW_UNAVAILABLE",
        )

    @app.exception_handler(CerneArtifactMissing)
    async def cerne_artifact_missing(
        _request: Request,
        _exc: CerneArtifactMissing,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "CERNE_ARTIFACT_REQUIRED",
        )

    @app.exception_handler(CerneExecutionUnavailable)
    async def cerne_execution_unavailable(
        _request: Request,
        _exc: CerneExecutionUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "CERNE_EXECUTION_UNAVAILABLE",
        )

    @app.exception_handler(CerneIntegrityError)
    async def cerne_integrity_error(
        _request: Request,
        _exc: CerneIntegrityError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "CERNE_INTEGRITY_ERROR",
        )

    @app.exception_handler(CerneProviderError)
    async def cerne_provider_error(
        _request: Request,
        _exc: CerneProviderError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_502_BAD_GATEWAY,
            "CERNE_PROVIDER_ERROR",
        )

    @app.exception_handler(CerneKnowledgeError)
    async def cerne_knowledge_error(
        _request: Request,
        _exc: CerneKnowledgeError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "CERNE_KNOWLEDGE_ERROR",
        )

    @app.exception_handler(CerneDomainError)
    async def cerne_domain_error(
        _request: Request,
        _exc: CerneDomainError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "CERNE_DOMAIN_REJECTED",
        )

    @app.exception_handler(CerneWorkflowUnavailable)
    async def cerne_workflow_unavailable(
        _request: Request,
        _exc: CerneWorkflowUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "CERNE_WORKFLOW_UNAVAILABLE",
        )

    @app.exception_handler(RatioRuntimeNotFound)
    async def ratio_runtime_not_found(
        _request: Request,
        _exc: RatioRuntimeNotFound,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_404_NOT_FOUND,
            "RATIO_RUNTIME_NOT_FOUND",
        )

    @app.exception_handler(RatioRuntimeAlreadyStarted)
    async def ratio_runtime_already_started(
        _request: Request,
        _exc: RatioRuntimeAlreadyStarted,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "RATIO_RUNTIME_ALREADY_STARTED",
        )

    @app.exception_handler(RatioRevisionConflict)
    async def ratio_revision_conflict(
        _request: Request,
        exc: RatioRevisionConflict,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "RATIO_REVISION_CONFLICT",
            expected=exc.expected,
            actual=exc.actual,
        )

    @app.exception_handler(RatioTransitionError)
    async def ratio_transition_error(
        _request: Request,
        _exc: RatioTransitionError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "RATIO_TRANSITION_REJECTED",
        )

    @app.exception_handler(HardStopCatalogError)
    async def ratio_hard_stop_error(
        _request: Request,
        _exc: HardStopCatalogError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "RATIO_HARD_STOP_INVALID",
        )

    @app.exception_handler(RatioActionPayloadError)
    async def ratio_action_payload_error(
        _request: Request,
        _exc: RatioActionPayloadError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "RATIO_ACTION_PAYLOAD_INVALID",
        )

    @app.exception_handler(RatioPersistenceIntegrityError)
    async def ratio_persistence_integrity_error(
        _request: Request,
        _exc: RatioPersistenceIntegrityError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "RATIO_PERSISTENCE_INTEGRITY_ERROR",
        )

    @app.exception_handler(RatioWorkflowUnavailable)
    async def ratio_workflow_unavailable(
        _request: Request,
        _exc: RatioWorkflowUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "RATIO_WORKFLOW_UNAVAILABLE",
        )

    @app.exception_handler(RatioExecutionUnavailable)
    async def ratio_execution_unavailable(
        _request: Request,
        _exc: RatioExecutionUnavailable,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "RATIO_EXECUTION_UNAVAILABLE",
        )

    @app.exception_handler(RatioArtifactMissing)
    async def ratio_artifact_missing(
        _request: Request,
        _exc: RatioArtifactMissing,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_409_CONFLICT,
            "RATIO_ARTIFACT_REQUIRED",
        )

    @app.exception_handler(RatioGeneratedOutputInvalid)
    async def ratio_generated_output_invalid(
        _request: Request,
        _exc: RatioGeneratedOutputInvalid,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_502_BAD_GATEWAY,
            "RATIO_GENERATED_OUTPUT_INVALID",
        )

    @app.exception_handler(RatioExecutorIntegrityError)
    async def ratio_executor_integrity_error(
        _request: Request,
        _exc: RatioExecutorIntegrityError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "RATIO_EXECUTOR_INTEGRITY_ERROR",
        )

    @app.exception_handler(RepositoryError)
    async def repository_error(
        _request: Request,
        _exc: RepositoryError,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "PERSISTENCE_UNAVAILABLE",
        )

    @app.exception_handler(Exception)
    async def unexpected_error(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
        )


def _error_response(
    status_code: int,
    code: str,
    **details: object,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                **details,
            }
        },
    )


def _normalize_media_type(content_type: str) -> str:
    parts = [part.strip() for part in content_type.split(";")]
    media_type = parts[0].lower()
    if media_type == "text/plain":
        parameters = {
            key.strip().lower(): value.strip().strip('"').lower()
            for part in parts[1:]
            if "=" in part
            for key, value in [part.split("=", 1)]
        }
        charset = parameters.get("charset")
        if charset not in {None, "utf-8", "utf8"}:
            raise UnsupportedDocumentType(
                "Somente text/plain em UTF-8 é permitido."
            )
    return media_type
