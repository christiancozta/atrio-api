from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ObjectType(StrEnum):
    DECISAO_LIMINAR = "decisao_liminar"
    VOTO = "voto"
    SENTENCA = "sentenca"
    ACORDAO = "acordao"


ACTIVE_OBJECT_TYPES = frozenset(ObjectType)


class SourceType(StrEnum):
    CASO_FICTICIO = "caso_ficticio"
    DECISAO_PUBLICA = "decisao_publica"
    ATRIO_INTERNO = "atrio_interno"


class DecisionMode(StrEnum):
    PRECEDENTE = "precedente"
    CONSTRUCAO_PROPRIA = "construcao_propria"
    INDETERMINADO = "indeterminado"


class Priority(StrEnum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class Severity(StrEnum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class GateState(StrEnum):
    AVANCA = "AVANCA"
    AVANCA_COM_AJUSTE = "AVANCA_COM_AJUSTE"
    REVISAO_HUMANA = "REVISAO_HUMANA"
    BLOQUEIO_PARCIAL = "BLOQUEIO_PARCIAL"
    BLOQUEIO_TOTAL = "BLOQUEIO_TOTAL"

    @property
    def internal_label(self) -> str:
        return {
            self.AVANCA: "AVANÇA",
            self.AVANCA_COM_AJUSTE: "AVANÇA COM AJUSTE",
            self.REVISAO_HUMANA: "REVISÃO HUMANA",
            self.BLOQUEIO_PARCIAL: "BLOQUEIO PARCIAL",
            self.BLOQUEIO_TOTAL: "BLOQUEIO TOTAL",
        }[self]

    @property
    def client_label(self) -> str:
        return {
            self.AVANCA: "Pode avançar.",
            self.AVANCA_COM_AJUSTE: "Pode avançar após ajuste pontual.",
            self.REVISAO_HUMANA: "Exige revisão técnica antes de uso.",
            self.BLOQUEIO_PARCIAL: (
                "Trecho ou conclusão específica não deve ser usada sem correção."
            ),
            self.BLOQUEIO_TOTAL: "O documento não deve ser usado na forma atual.",
        }[self]


class AxisCode(StrEnum):
    EX001 = "EX001"
    EX002 = "EX002"
    EX003 = "EX003"
    EX004 = "EX004"
    EX005 = "EX005"
    EX006 = "EX006"
    EX007 = "EX007"
    EX008 = "EX008"
    EX009 = "EX009"
    EX010 = "EX010"
    EX011 = "EX011"


class AuditRequest(StrictModel):
    caso_id: str | None = Field(default=None, min_length=1, max_length=120)
    tipo_objeto: ObjectType
    natureza_fonte: SourceType
    texto: str = Field(min_length=40, max_length=250_000)
    origem: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def public_source_requires_origin(self) -> Self:
        if self.natureza_fonte is SourceType.DECISAO_PUBLICA and not self.origem:
            raise ValueError("Decisão pública exige identificação da fonte.")
        return self


class ValidityCheck(StrictModel):
    necessaria: bool
    suspender_auditoria: bool
    fontes_a_validar: list[str]
    fundamento: str

    @model_validator(mode="after")
    def suspension_requires_validation(self) -> Self:
        if self.suspender_auditoria and not self.necessaria:
            raise ValueError("A suspensão exige checagem de validade.")
        return self


class RiskSignal(StrictModel):
    localizacao: str
    trecho: str
    risco: str


class TriageResult(StrictModel):
    tipo_objeto_detectado: str
    tese_principal: str
    checagem_validade: ValidityCheck
    modo_decisorio: DecisionMode
    prioridade: Priority
    trechos_de_risco: list[RiskSignal]
    resultado_limpo_preliminar: bool
    justificativa_operacional: str

    @model_validator(mode="after")
    def clean_result_has_no_risk(self) -> Self:
        if self.resultado_limpo_preliminar and self.trechos_de_risco:
            raise ValueError("Resultado limpo preliminar não pode conter trechos de risco.")
        return self


class Finding(StrictModel):
    marcador: str
    severidade: Severity
    localizacao: str
    natureza: str
    impacto: str
    aciona_gate: bool
    roteamento: str


class LensResult(StrictModel):
    eixo: AxisCode
    sintese: str
    achados: list[Finding]
    achados_descartados: list[str]
    sinalizacoes: list[AxisCode]
    gate_preliminar: GateState
    produto_exportavel: str | None
    resultado_negativo: str | None
    observacao_de_contencao: str

    @model_validator(mode="after")
    def negative_result_matches_findings(self) -> Self:
        if self.achados and self.resultado_negativo:
            raise ValueError("Uma lente com achados não pode declarar resultado negativo.")
        if not self.achados and not self.resultado_negativo:
            raise ValueError("Uma lente sem achados deve explicar o resultado negativo.")
        return self


class EmergentFinding(StrictModel):
    marcador: str
    severidade: Severity
    localizacao: str
    natureza: str
    irredutibilidade: str
    consequencia_operacional: str
    produto_exportavel: str


class ConfrontationResult(StrictModel):
    codigo: str
    tipo_relacao: str
    acoplamento_confirmado: bool
    justificativa_acoplamento: str
    achado_emergente: EmergentFinding | None
    risco_dupla_marcacao: str
    gate_preliminar: GateState
    roteamento_corretivo: str
    observacao_operacional: str

    @model_validator(mode="after")
    def coupling_matches_emergent(self) -> Self:
        if self.acoplamento_confirmado != (self.achado_emergente is not None):
            raise ValueError("Acoplamento e achado emergente devem ser coerentes.")
        return self


class HumanReviewRequest(StrictModel):
    motivo: str
    pergunta_ao_operador: str
    decisao_esperada: str


class GateDecision(StrictModel):
    estado: GateState
    fundamento_sintetico: str
    achados_considerados: list[str]
    ponto_de_bloqueio_ou_ajuste: str
    pode_ser_preservado: list[str]
    condicoes_de_avanco: list[str]
    encaminhamento: str
    revisao_humana: HumanReviewRequest | None
    observacao_final: str

    @model_validator(mode="after")
    def human_review_is_typed(self) -> Self:
        if self.estado is GateState.REVISAO_HUMANA and self.revisao_humana is None:
            raise ValueError("REVISÃO HUMANA exige motivo, pergunta e decisão esperada.")
        return self


class InternalOutput(StrictModel):
    tipo_objeto: str
    tese_principal: str
    sintese_executiva: str
    trechos_criticos: list[RiskSignal]
    lentes_acionadas: list[AxisCode]
    confrontos_acionados: list[str]
    achados_isolados: list[Finding]
    achados_emergentes: list[EmergentFinding]
    risco_dupla_marcacao: str
    gate: GateDecision
    encaminhamento_final: str
    observacao_operador: str
    resultado_limpo: bool


class ClientOutput(StrictModel):
    estado_documento: str
    sintese_objetiva: str
    ponto_principal_atencao: str
    impacto_pratico: str
    ajustes_necessarios: list[str]
    pode_ser_preservado: list[str]
    recomendacao_final: str


class AuditReport(StrictModel):
    nome_arquivo: str
    formato: str = "text/markdown"
    conteudo: str


class StageTrace(StrictModel):
    etapa: str
    response_id: str
    modelo: str


class AuditLogRecord(StrictModel):
    caso_id: str
    data: date
    plataforma: str
    modelo: str
    tipo_objeto: str
    modo_execucao: str
    checagem_validade_entrada: bool
    fontes_a_validar: list[str]
    lentes_acionadas: list[AxisCode]
    lentes_sem_achado: list[AxisCode]
    achados_confirmados: int
    achados_descartados: int
    achados_rebaixados: int
    confrontos_acionados: list[str]
    emergentes_confirmados: int
    gate_final: GateState
    resultado_limpo: bool
    saida_interna_gerada: bool
    saida_cliente_gerada: bool
    relatorio_gerado: bool
    revisao_humana: bool
    decisao_humana_final: str
    encaminhamento: str
    observacao: str


class AuditResponse(StrictModel):
    auditoria_id: str
    criada_em: datetime
    triagem: TriageResult
    lentes: list[LensResult]
    confrontos: list[ConfrontationResult]
    gate: GateDecision
    saida_interna: InternalOutput
    saida_cliente: ClientOutput
    relatorio: AuditReport
    log: AuditLogRecord
    bloco_log: str
    rastro_modelo: list[StageTrace]
    avisos_operacionais: list[str] = Field(default_factory=list)


def utc_now() -> datetime:
    return datetime.now(UTC)
