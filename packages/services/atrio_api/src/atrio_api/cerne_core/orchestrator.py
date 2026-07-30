from __future__ import annotations

import re
from datetime import date
from uuid import uuid4

from atrio_api.cerne_core import __version__
from atrio_api.cerne_core.domain import (
    ACTIVE_OBJECT_TYPES,
    AuditLogRecord,
    AuditReport,
    AuditRequest,
    AuditResponse,
    AxisCode,
    ClientOutput,
    ConfrontationResult,
    GateDecision,
    GateState,
    InternalOutput,
    LensResult,
    StageTrace,
    TriageResult,
    utc_now,
)
from atrio_api.cerne_core.knowledge import KnowledgeBase
from atrio_api.cerne_core.provider import (
    ModelProvider,
    ProviderError,
    ProviderRateLimitError,
    StageCallResult,
)
from atrio_api.cerne_core.repository import AuditRepository
from atrio_api.cerne_core.sanitization import contains_internal_terms, sanitize_client_output


class DomainError(ValueError):
    pass


ALL_AXES = tuple(AxisCode)

CONFRONTATION_ROUTES: dict[str, tuple[AxisCode, AxisCode]] = {
    "CF-006": (AxisCode.EX011, AxisCode.EX004),
    "CF-007": (AxisCode.EX007, AxisCode.EX006),
    "CF-008": (AxisCode.EX007, AxisCode.EX003),
    "CF-010": (AxisCode.EX006, AxisCode.EX003),
    "CF-012": (AxisCode.EX006, AxisCode.EX008),
    "CF-013": (AxisCode.EX001, AxisCode.EX002),
    "CF-014": (AxisCode.EX001, AxisCode.EX003),
    "CF-016": (AxisCode.EX002, AxisCode.EX003),
    "CF-017": (AxisCode.EX002, AxisCode.EX004),
    "CF-019": (AxisCode.EX003, AxisCode.EX004),
    "CF-024": (AxisCode.EX005, AxisCode.EX009),
}

AXIS_LABELS: dict[AxisCode, tuple[str, str]] = {
    AxisCode.EX001: ("Arquitetura argumentativa", "Stephen Toulmin"),
    AxisCode.EX002: ("Dialética", "Sócrates"),
    AxisCode.EX003: ("Inferência abdutiva", "Charles Sanders Peirce"),
    AxisCode.EX004: ("Integridade cognitiva", "Wilfred R. Bion"),
    AxisCode.EX005: ("Hermenêutica", "Hans-Georg Gadamer"),
    AxisCode.EX006: ("Simetrização", "Ignacio Matte-Blanco"),
    AxisCode.EX007: ("Análise analógico-precedental", "Edward H. Levi"),
    AxisCode.EX008: ("Justificação de segunda ordem", "Neil MacCormick"),
    AxisCode.EX009: ("Textura aberta", "H. L. A. Hart"),
    AxisCode.EX010: ("Validade normativa", "Hans Kelsen"),
    AxisCode.EX011: ("Autoridade prática", "Joseph Raz"),
}


class CerneOrchestrator:
    def __init__(
        self,
        *,
        provider: ModelProvider,
        knowledge: KnowledgeBase,
        repository: AuditRepository,
    ):
        self.provider = provider
        self.knowledge = knowledge
        self.repository = repository

    async def audit(self, request: AuditRequest) -> AuditResponse:
        self._assert_scope(request)
        audit_id = str(uuid4())
        case_id = request.caso_id or audit_id
        created_at = utc_now()
        traces: list[StageTrace] = []
        operational_warnings: list[str] = []

        triage_call = await self.provider.run(
            stage="triagem",
            instructions=self.knowledge.triage_prompt(),
            payload=self._base_payload(request),
            response_model=TriageResult,
        )
        triage = triage_call.parsed
        traces.append(self._trace("triagem", triage_call))

        lenses: list[LensResult] = []
        for axis in ALL_AXES:
            lens_call = await self._run_lens(request, triage, axis)
            self._assert_lens_identity(axis, lens_call)
            lenses.append(lens_call.parsed)
            traces.append(self._trace(f"lente:{axis.value}", lens_call))

        confrontations: list[ConfrontationResult] = []
        lenses_by_axis = {lens.eixo: lens for lens in lenses}
        for code, axes in CONFRONTATION_ROUTES.items():
            pair = tuple(lenses_by_axis[axis] for axis in axes)
            if not all(lens.achados for lens in pair):
                continue
            confrontation_call = await self._run_confrontation(
                request=request,
                triage=triage,
                code=code,
                pair=pair,
            )
            confrontation = confrontation_call.parsed
            if confrontation.codigo != code:
                raise DomainError("O provedor retornou confronto diferente do roteado.")
            confrontations.append(confrontation)
            traces.append(self._trace(f"confronto:{code}", confrontation_call))

        gate_call = await self.provider.run(
            stage="gate",
            instructions=self.knowledge.gate_prompt(),
            payload={
                "objeto": {
                    "tipo_objeto": request.tipo_objeto.value,
                    "natureza_fonte": request.natureza_fonte.value,
                    "origem": request.origem,
                },
                "triagem": triage.model_dump(mode="json"),
                "lentes": [lens.model_dump(mode="json") for lens in lenses],
                "confrontos": [
                    confrontation.model_dump(mode="json")
                    for confrontation in confrontations
                ],
                "restricao": (
                    "Considere somente os achados fornecidos. "
                    "É proibido criar achado novo no gate."
                ),
            },
            response_model=GateDecision,
        )
        gate = gate_call.parsed
        traces.append(self._trace("gate", gate_call))

        internal = self._build_internal_output(
            triage=triage,
            lenses=lenses,
            confrontations=confrontations,
            gate=gate,
        )

        try:
            client_call = await self.provider.run(
                stage="saida_cliente",
                instructions=self.knowledge.client_output_prompt(),
                payload={
                    "gate": gate.model_dump(mode="json"),
                    "sintese_interna": internal.model_dump(mode="json"),
                    "restricao": (
                        "Traduza para o usuário sem códigos, nomes de eixos, escolas, "
                        "lentes, confrontos, marcadores ou referência ao gate técnico."
                    ),
                },
                response_model=ClientOutput,
            )
            client = sanitize_client_output(client_call.parsed)
            client = client.model_copy(
                update={"estado_documento": gate.estado.client_label}
            )
            if contains_internal_terms(client):
                raise DomainError("A sanitização da saída de tela não foi suficiente.")
            traces.append(self._trace("saida_cliente", client_call))
        except ProviderError as exc:
            client = self._build_client_fallback(gate)
            if isinstance(exc, ProviderRateLimitError):
                operational_warnings.append(
                    "A auditoria completa foi concluída. A cota gratuita do Gemini "
                    "oscilou na tradução final; por isso, o CERNE exibiu uma versão "
                    "simplificada de contingência."
                )
            else:
                operational_warnings.append(
                    "A auditoria completa foi concluída. O Gemini não entregou a tradução "
                    "final; por isso, o CERNE exibiu uma versão simplificada de contingência."
                )

        report = self._build_report(
            audit_id=audit_id,
            case_id=case_id,
            request=request,
            triage=triage,
            lenses=lenses,
            confrontations=confrontations,
            gate=gate,
            internal=internal,
            client=client,
            traces=traces,
        )
        log = self._build_log(
            case_id=case_id,
            request=request,
            triage=triage,
            lenses=lenses,
            confrontations=confrontations,
            gate=gate,
            internal=internal,
        )
        response = AuditResponse(
            auditoria_id=audit_id,
            criada_em=created_at,
            triagem=triage,
            lentes=lenses,
            confrontos=confrontations,
            gate=gate,
            saida_interna=internal,
            saida_cliente=client,
            relatorio=report,
            log=log,
            bloco_log=self._render_log_block(log),
            rastro_modelo=traces,
            avisos_operacionais=operational_warnings,
        )
        await self.repository.save_summary(response)
        return response

    async def _run_lens(
        self,
        request: AuditRequest,
        triage: TriageResult,
        axis: AxisCode,
    ) -> StageCallResult[LensResult]:
        return await self.provider.run(
            stage=f"lente:{axis.value}",
            instructions=self.knowledge.lens_prompt(axis),
            payload={
                "objeto": self._base_payload(request),
                "triagem": triage.model_dump(mode="json"),
                "eixo_unico": axis.value,
                "restricao": (
                    "Aplique somente o eixo indicado. Não confronte, não antecipe outra "
                    "lente e aceite resultado negativo."
                ),
            },
            response_model=LensResult,
        )

    async def _run_confrontation(
        self,
        *,
        request: AuditRequest,
        triage: TriageResult,
        code: str,
        pair: tuple[LensResult, LensResult],
    ) -> StageCallResult[ConfrontationResult]:
        return await self.provider.run(
            stage=f"confronto:{code}",
            instructions=self.knowledge.confrontation_prompt(code),
            payload={
                "objeto": self._base_payload(request),
                "triagem": triage.model_dump(mode="json"),
                "codigo_confronto": code,
                "achados_isolados": [
                    lens.model_dump(mode="json") for lens in pair
                ],
            },
            response_model=ConfrontationResult,
        )

    @staticmethod
    def _base_payload(request: AuditRequest) -> dict:
        return {
            "tipo_objeto_declarado": request.tipo_objeto.value,
            "natureza_fonte": request.natureza_fonte.value,
            "origem": request.origem,
            "modo_execucao": "auditoria_completa",
            "documento_auditado": request.texto,
        }

    @staticmethod
    def _assert_scope(request: AuditRequest) -> None:
        if request.tipo_objeto not in ACTIVE_OBJECT_TYPES:
            raise DomainError("O CERNE aceita apenas atos judiciais do escopo ativo.")

    @staticmethod
    def _assert_lens_identity(
        expected: AxisCode,
        call: StageCallResult[LensResult],
    ) -> None:
        if call.parsed.eixo is not expected:
            raise DomainError(
                f"Eixo retornado fora da rota: esperado {expected}, "
                f"recebido {call.parsed.eixo}."
            )

    @staticmethod
    def _trace(stage: str, call: StageCallResult) -> StageTrace:
        return StageTrace(
            etapa=stage,
            response_id=call.response_id,
            modelo=call.model,
        )

    @staticmethod
    def _build_internal_output(
        *,
        triage: TriageResult,
        lenses: list[LensResult],
        confrontations: list[ConfrontationResult],
        gate: GateDecision,
    ) -> InternalOutput:
        findings = [finding for lens in lenses for finding in lens.achados]
        emergent = [
            confrontation.achado_emergente
            for confrontation in confrontations
            if confrontation.achado_emergente is not None
        ]
        clean = not findings and not emergent and gate.estado is GateState.AVANCA
        summary = (
            "RESULTADO LIMPO. Os onze eixos analíticos foram executados e nenhum "
            "risco relevante de raciocínio cruzou o limiar de achado."
            if clean
            else gate.fundamento_sintetico
        )
        double_marking = (
            " | ".join(
                confrontation.risco_dupla_marcacao
                for confrontation in confrontations
            )
            or "Nenhum confronto ativado; preservar a separação dos achados isolados."
        )
        return InternalOutput(
            tipo_objeto=triage.tipo_objeto_detectado,
            tese_principal=triage.tese_principal,
            sintese_executiva=summary,
            trechos_criticos=triage.trechos_de_risco,
            lentes_acionadas=[lens.eixo for lens in lenses],
            confrontos_acionados=[
                confrontation.codigo for confrontation in confrontations
            ],
            achados_isolados=findings,
            achados_emergentes=emergent,
            risco_dupla_marcacao=double_marking,
            gate=gate,
            encaminhamento_final=gate.encaminhamento,
            observacao_operador=gate.observacao_final,
            resultado_limpo=clean,
        )

    @staticmethod
    def _build_client_fallback(gate: GateDecision) -> ClientOutput:
        candidate = sanitize_client_output(
            ClientOutput(
                estado_documento=gate.estado.client_label,
                sintese_objetiva=gate.fundamento_sintetico,
                ponto_principal_atencao=gate.ponto_de_bloqueio_ou_ajuste,
                impacto_pratico=gate.observacao_final,
                ajustes_necessarios=gate.condicoes_de_avanco,
                pode_ser_preservado=gate.pode_ser_preservado,
                recomendacao_final=gate.encaminhamento,
            )
        )
        if not contains_internal_terms(candidate):
            return candidate
        return ClientOutput(
            estado_documento=gate.estado.client_label,
            sintese_objetiva=(
                "A auditoria foi concluída. A versão simplificada abaixo foi montada "
                "automaticamente a partir do resultado."
            ),
            ponto_principal_atencao=(
                "Consulte o ponto principal indicado no relatório completo."
            ),
            impacto_pratico=(
                "A conclusão da auditoria permanece válida e disponível nesta tela."
            ),
            ajustes_necessarios=(
                ["Consulte as condições de avanço no relatório completo."]
                if gate.condicoes_de_avanco
                else []
            ),
            pode_ser_preservado=[
                "Consulte a seção correspondente no relatório completo."
            ],
            recomendacao_final=(
                "Siga o encaminhamento final indicado no relatório completo."
            ),
        )

    def _build_report(
        self,
        *,
        audit_id: str,
        case_id: str,
        request: AuditRequest,
        triage: TriageResult,
        lenses: list[LensResult],
        confrontations: list[ConfrontationResult],
        gate: GateDecision,
        internal: InternalOutput,
        client: ClientOutput,
        traces: list[StageTrace],
    ) -> AuditReport:
        lines = [
            "# RELATÓRIO TÉCNICO DE AUDITORIA — CERNE",
            "",
            f"- **Versão da API:** {__version__}",
            f"- **Auditoria:** {audit_id}",
            f"- **Caso:** {case_id}",
            f"- **Ato judicial:** {request.tipo_objeto.value}",
            f"- **Natureza da fonte:** {request.natureza_fonte.value}",
            f"- **Origem informada:** {request.origem or 'não informada'}",
            "- **Modo de execução:** auditoria completa",
            "- **Persistência textual no repositório CERNE:** não",
            "",
            "## 1. Conclusão executiva",
            "",
            internal.sintese_executiva,
            "",
            f"**Estado final:** {gate.estado.internal_label}",
            "",
            f"**Encaminhamento:** {gate.encaminhamento}",
            "",
            "## 2. Identificação e triagem",
            "",
            f"- **Tipo detectado:** {triage.tipo_objeto_detectado}",
            f"- **Tese principal:** {triage.tese_principal}",
            f"- **Modo decisório detectado:** {triage.modo_decisorio.value}",
            f"- **Prioridade técnica:** {triage.prioridade.value}",
            (
                "- **Validação de fonte:** "
                + (
                    "necessária"
                    if triage.checagem_validade.necessaria
                    else "não sinalizada"
                )
            ),
            f"- **Fundamento da triagem:** {triage.justificativa_operacional}",
            "",
            "## 3. Eixos analíticos e escolas de pensamento",
            "",
            (
                "Os onze eixos foram executados isoladamente. Resultado negativo "
                "significa que o eixo foi aplicado e não confirmou achado."
            ),
            "",
        ]
        for lens in lenses:
            method, thinker = AXIS_LABELS[lens.eixo]
            lines.extend(
                [
                    f"### {lens.eixo.value} — {method}",
                    "",
                    f"**Matriz de pensamento:** {thinker}",
                    "",
                    f"**Síntese:** {lens.sintese}",
                    "",
                ]
            )
            if lens.achados:
                lines.append(f"**Resultado:** {len(lens.achados)} achado(s) confirmado(s).")
                lines.append("")
                for index, finding in enumerate(lens.achados, start=1):
                    lines.extend(
                        [
                            f"**Achado {index}: {finding.marcador}**",
                            "",
                            f"- Severidade: {finding.severidade.value}",
                            f"- Localização: {finding.localizacao}",
                            f"- Natureza: {finding.natureza}",
                            f"- Impacto: {finding.impacto}",
                            f"- Roteamento: {finding.roteamento}",
                            "",
                        ]
                    )
            else:
                lines.extend(
                    [
                        f"**Resultado negativo:** {lens.resultado_negativo}",
                        "",
                    ]
                )

        lines.extend(["## 4. Confrontos aplicáveis", ""])
        if not confrontations:
            lines.extend(
                [
                    "Nenhum confronto reuniu simultaneamente os critérios de ativação.",
                    "",
                ]
            )
        for confrontation in confrontations:
            lines.extend(
                [
                    f"### {confrontation.codigo}",
                    "",
                    f"- Relação: {confrontation.tipo_relacao}",
                    (
                        "- Acoplamento confirmado: "
                        + ("sim" if confrontation.acoplamento_confirmado else "não")
                    ),
                    f"- Justificativa: {confrontation.justificativa_acoplamento}",
                    f"- Risco de dupla marcação: {confrontation.risco_dupla_marcacao}",
                    f"- Roteamento: {confrontation.roteamento_corretivo}",
                    "",
                ]
            )
            if confrontation.achado_emergente:
                finding = confrontation.achado_emergente
                lines.extend(
                    [
                        f"**Achado emergente: {finding.marcador}**",
                        "",
                        f"- Severidade: {finding.severidade.value}",
                        f"- Localização: {finding.localizacao}",
                        f"- Natureza: {finding.natureza}",
                        f"- Irredutibilidade: {finding.irredutibilidade}",
                        (
                            "- Consequência operacional: "
                            f"{finding.consequencia_operacional}"
                        ),
                        "",
                    ]
                )

        lines.extend(
            [
                "## 5. Consolidação da auditoria",
                "",
                f"**Fundamento:** {gate.fundamento_sintetico}",
                "",
                (
                    "**Ponto de bloqueio ou ajuste:** "
                    f"{gate.ponto_de_bloqueio_ou_ajuste}"
                ),
                "",
                "**Condições de avanço:**",
                "",
            ]
        )
        lines.extend(
            [f"- {condition}" for condition in gate.condicoes_de_avanco]
            or ["- Nenhuma condição adicional."]
        )
        lines.extend(["", "**Pode ser preservado:**", ""])
        lines.extend(
            [f"- {item}" for item in gate.pode_ser_preservado]
            or ["- Nenhum trecho indicado."]
        )
        lines.extend(
            [
                "",
                "## 6. Tradução entregue na tela",
                "",
                f"**Estado:** {client.estado_documento}",
                "",
                client.sintese_objetiva,
                "",
                f"**Recomendação:** {client.recomendacao_final}",
                "",
                "## 7. Rastro operacional",
                "",
            ]
        )
        lines.extend(
            f"- {trace.etapa} — {trace.modelo} — {trace.response_id}"
            for trace in traces
        )
        lines.extend(
            [
                "",
                "---",
                "",
                (
                    "Relatório gerado sem exposição de chain-of-thought. O conteúdo "
                    "registra justificativas operacionais auditáveis. O texto jurídico "
                    "não entram na telemetria CERNE; a integração ATRIO governa o artefato cifrado."
                ),
            ]
        )
        safe_case_id = re.sub(r"[^A-Za-z0-9._-]+", "-", case_id).strip("-")
        return AuditReport(
            nome_arquivo=f"cerne-{safe_case_id or audit_id}.md",
            conteudo="\n".join(lines),
        )

    def _build_log(
        self,
        *,
        case_id: str,
        request: AuditRequest,
        triage: TriageResult,
        lenses: list[LensResult],
        confrontations: list[ConfrontationResult],
        gate: GateDecision,
        internal: InternalOutput,
    ) -> AuditLogRecord:
        findings = [finding for lens in lenses for finding in lens.achados]
        discarded = sum(len(lens.achados_descartados) for lens in lenses)
        return AuditLogRecord(
            caso_id=case_id,
            data=date.today(),
            plataforma=self.provider.name,
            modelo=self.provider.model,
            tipo_objeto=request.tipo_objeto.value,
            modo_execucao="auditoria_completa",
            checagem_validade_entrada=triage.checagem_validade.necessaria,
            fontes_a_validar=triage.checagem_validade.fontes_a_validar,
            lentes_acionadas=[lens.eixo for lens in lenses],
            lentes_sem_achado=[lens.eixo for lens in lenses if not lens.achados],
            achados_confirmados=len(findings),
            achados_descartados=discarded,
            achados_rebaixados=0,
            confrontos_acionados=[
                confrontation.codigo for confrontation in confrontations
            ],
            emergentes_confirmados=sum(
                confrontation.achado_emergente is not None
                for confrontation in confrontations
            ),
            gate_final=gate.estado,
            resultado_limpo=internal.resultado_limpo,
            saida_interna_gerada=True,
            saida_cliente_gerada=True,
            relatorio_gerado=True,
            revisao_humana=gate.estado is GateState.REVISAO_HUMANA,
            decisao_humana_final="pendente",
            encaminhamento=gate.encaminhamento,
            observacao=("CERNE não persiste texto em telemetria; integração ATRIO "
                "governa o artefato cifrado."),
        )

    @staticmethod
    def _render_log_block(log: AuditLogRecord) -> str:
        def joined(values: list) -> str:
            return ";".join(
                str(value.value if hasattr(value, "value") else value)
                for value in values
            )

        return "\n".join(
            [
                "# BLOCO DE LOG",
                f"caso_id: {log.caso_id}",
                f"data: {log.data.isoformat()}",
                f"plataforma: {log.plataforma}",
                f"modelo: {log.modelo}",
                f"tipo_objeto: {log.tipo_objeto}",
                f"modo_execucao: {log.modo_execucao}",
                (
                    "checagem_validade_entrada: "
                    + ("sim" if log.checagem_validade_entrada else "não")
                ),
                f"fontes_a_validar: {joined(log.fontes_a_validar)}",
                f"lentes_acionadas: {joined(log.lentes_acionadas)}",
                f"lentes_sem_achado: {joined(log.lentes_sem_achado)}",
                f"achados_confirmados: {log.achados_confirmados}",
                f"achados_descartados: {log.achados_descartados}",
                f"achados_rebaixados: {log.achados_rebaixados}",
                f"confrontos_acionados: {joined(log.confrontos_acionados)}",
                f"emergentes_confirmados: {log.emergentes_confirmados}",
                f"gate_final: {log.gate_final.value}",
                f"resultado_limpo: {'sim' if log.resultado_limpo else 'não'}",
                f"saida_interna_gerada: {'sim' if log.saida_interna_gerada else 'não'}",
                f"saida_cliente_gerada: {'sim' if log.saida_cliente_gerada else 'não'}",
                f"relatorio_gerado: {'sim' if log.relatorio_gerado else 'não'}",
                f"revisao_humana: {'sim' if log.revisao_humana else 'não'}",
                f"decisao_humana_final: {log.decisao_humana_final}",
                f"encaminhamento: {log.encaminhamento}",
                f"observacao: {log.observacao}",
            ]
        )
