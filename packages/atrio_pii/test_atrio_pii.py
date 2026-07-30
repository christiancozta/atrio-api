# -*- coding: utf-8 -*-
"""
Autoteste do motor compartilhado. Sem framework: roda com

    py test_atrio_pii.py

Cobre as duas correções que mudaram comportamento — a triagem de segredo em
dois níveis e a proteção condicional do número CNJ — e o vocabulário de
marcação do robô de saída.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lux" / "bin"))

import atrio_pii as pii
import lux_pentefino as lux

CNJ = "0001234-56.2020.8.16.0001"


def test_menor_valor_nao_sai_mais_da_base():
    # o falso positivo caro: "menor valor" mandava causa de consumo para a
    # pasta de segredo e a tirava da base sem alarme. Quem resolve este caso é
    # o segundo nível, não a fronteira de palavra: "menor" continua casando,
    # mas agora como gatilho fraco, que fica na base e só pede leitura humana.
    for texto in ("ação de cobrança de menor valor",
                  "dano de menor monta",
                  "questão de menor complexidade"):
        nivel, _ = pii.eh_segredo(texto)
        assert nivel != "forte", f"{texto!r} ainda sairia da base"
        assert nivel == "fraco"


def test_fronteira_de_palavra():
    # o que a fronteira resolve: gatilho casando dentro de outra palavra.
    # No teste por substring que existia antes, todos estes davam positivo.
    for texto in ("discussão sobre menoridade penal",
                  "comprou um guardanapo",
                  "serviço de guardamóveis"):
        nivel, termo = pii.eh_segredo(texto)
        assert nivel is None, f"{texto!r} casou por {termo!r}"


def test_fronteira_nao_pega_plural():
    # consequência conhecida e registrada da fronteira de palavra: forma
    # flexionada deixa de casar. Documentado no relatório como estreitamento
    # de detecção, pendente de decisão do autor.
    assert pii.eh_segredo("guarda dos menores")[0] == "fraco"   # casa por "guarda"
    assert pii.eh_segredo("os menores do casal")[0] is None     # "menores" não casa
    assert pii.eh_segredo("duas curatelas")[0] is None          # "curatelas" não casa


def test_segredo_forte_segrega():
    for texto, esperado in (
        ("Processo em segredo de justiça", "segredo de justiça"),
        ("aplicação da Lei Maria da Penha", "lei maria da penha"),
        ("pedido de curatela", "curatela"),
        ("nos termos do ECA", "eca"),
    ):
        nivel, termo = pii.eh_segredo(texto)
        assert nivel == "forte", f"{texto!r} -> {nivel}"
        assert termo == esperado, f"{texto!r} -> {termo!r}"


def test_segredo_fraco_vai_para_revisao():
    for texto, esperado in (
        ("guarda compartilhada do menor", "menor"),
        ("ação de alimentos", "alimentos"),
        ("reconhecimento de união estável", "união estável"),
    ):
        nivel, termo = pii.eh_segredo(texto)
        assert nivel == "fraco", f"{texto!r} -> {nivel}"
        assert termo == esperado, f"{texto!r} -> {termo!r}"


def test_forte_tem_precedencia_sobre_fraco():
    nivel, termo = pii.eh_segredo("guarda do menor em segredo de justiça")
    assert (nivel, termo) == ("forte", "segredo de justiça")


def test_cnj_protegido_na_entrada():
    texto = f"Autos {CNJ}, requerente João da Silva, CPF 123.456.789-00."
    achados = pii.detectar(texto)          # padrão: proteger_cnj=True
    tipos = {t for _, _, t, _ in achados}
    assert "CNJ" not in tipos, "CNJ não pode ser achado quando está protegido"
    assert "CPF" in tipos
    for ini, fim, _, _ in achados:
        assert CNJ not in texto[ini:fim], "achado encostou no número CNJ"


def test_cnj_cortado_na_saida_publica():
    texto = f"Autos {CNJ}, requerente João da Silva."
    achados = pii.detectar(texto, proteger_cnj=False)
    assert CNJ in [v for _, _, t, v in achados if t == "CNJ"]
    limpo, _ = lux.cortar(texto, achados)
    assert CNJ not in limpo, "número de processo vazou para a saída pública"
    assert "[processo]" in limpo


def test_marcadores_sao_de_tipo_e_minusculos():
    # papel — [parte autora], [parte ré] — é exclusivo do kernel: o detector
    # acha um nome, não sabe de quem é o papel
    for marca in lux.MARCA.values():
        assert marca == marca.lower(), marca
        assert marca.startswith("[") and marca.endswith("]"), marca
    assert set(lux.MARCA) >= {"PESSOA", "CPF", "CNPJ", "OAB", "RG", "EMAIL",
                              "CEP", "TELEFONE", "CNJ"}
    assert lux.MARCA["CNJ"] == "[processo]"
    assert lux.MARCA["CEP"] == "[endereço]"
    assert lux.MARCA["PESSOA"] == "[pessoa]"


def test_todo_tipo_detectavel_tem_marcador():
    # se um tipo novo entrar em PADROES sem marcador, o corte estoura em vez
    # de emitir marca genérica silenciosa; este teste avisa antes
    tipos = {t for t, _ in pii.PADROES} | {"PESSOA", "CNJ"}
    faltando = tipos - set(lux.MARCA)
    assert not faltando, f"tipo sem marcador em tokens.yaml: {faltando}"


def test_versao_declarada():
    assert pii.VERSAO == "1.0.0"


if __name__ == "__main__":
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in testes:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(testes)} testes passaram (atrio_pii {pii.VERSAO})")
