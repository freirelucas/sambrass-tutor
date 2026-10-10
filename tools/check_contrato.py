#!/usr/bin/env python3
"""Valida o CONTRATO entre o pipeline de dados e a PWA.

O problema que isto resolve: todo fetch do app tem `.catch()`, então um JSON que o
build deixou de escrever (ou que foi renomeado) não quebra nada visivelmente — some
em silêncio e a tela aparece vazia. Este validador lê os dois lados e compara:

  lado do app   — os nomes de .json pedidos em app/*.js e app/*.html
  lado do build — o que app/build_site.py de fato escreveu em _site/

Checa três coisas:
  1. todo arquivo pedido existe na jornada em que é pedido — a não ser que esteja
     DECLARADO em OPCIONAIS aqui embaixo, com motivo. Um 404 vira decisão escrita.
  2. nenhuma declaração de OPCIONAIS está obsoleta (o arquivo passou a existir).
  3. as chaves de topo de que o app depende existem no JSON construído.
Também relata (sem falhar) os órfãos: o build escreve, ninguém lê.

Pré-requisito: `python3 app/build_site.py` (precisa de _site/).
Uso:  python3 tools/check_contrato.py
"""
import json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SITE = RAIZ / "_site"
APP = RAIZ / "app"
JORNADAS = {"sambrass": "", "cumbias": "cumbias/"}   # espelha JORNADAS em app/app.js

# Arquivos que legitimamente NÃO existem numa jornada. Cada um precisa de motivo:
# se não dá pra escrever o motivo, provavelmente é bug, não escolha.
OPCIONAIS = {
    ("cumbias", "curriculum.json"): "as cumbias não têm currículo de 6 semanas (isso é do Sambrass)",
    ("cumbias", "rotina.json"): "rotina diária vem do currículo, que as cumbias não têm",
    ("cumbias", "trilha.json"): "a trilha das cumbias é derivada de percurso.json, não de um arquivo próprio",
    ("sambrass", "bars_warn.json"): "validação de compassos só roda no pipeline das cumbias",
    ("sambrass", "pitch_warn.json"): "validação de alturas só roda no pipeline das cumbias",
    ("sambrass", "abc_full.json"): "peça inteira só existe nas cumbias (o app já guarda esse caso)",
}

# Chaves de topo que o app acessa no objeto carregado (vistas em app/*.js).
# (arquivo, chave, "onde o app usa")
CHAVES = [
    ("pieces.json", "pieces", "DB.pieces?.pieces"),
    ("escada.json", "pieces", "DB.escada?.pieces"),
    ("cells.json", "celulas_ritmicas", "DB.cells?.celulas_ritmicas"),
    ("cells.json", "arpejos", "c.arpejos no Vocabulário"),
    ("blocos.json", "pecas", "BLK.pecas / _blocosPecas"),
]

FONTES = sorted(APP.glob("*.js")) + sorted(APP.glob("*.html"))


def pedidos_por_jornada():
    """Nomes pedidos através da BASE da jornada (helpers get/j/fetchJSON e concatenação)."""
    nomes = set()
    for f in FONTES:
        if "vendor" in f.parts:
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        # './data/' + BASE + 'x.json'  →  pedido relativo à jornada
        nomes |= set(re.findall(r"'\./data/'\s*\+\s*\w[\w().]*\s*\+\s*'([\w.-]+\.json)'", txt))
        # helpers que já embutem a base: get('x.json'), j('x.json'), fetchJSON('x.json')
        nomes |= set(re.findall(r"\b(?:get|j|fetchJSON)\('([\w.-]+\.json)'\)", txt))
        # a lista de nomes passada em bloco p/ .map(get) em app.js
        for bloco in re.findall(r"\[((?:\s*'[\w.-]+\.json'\s*,?)+)\]\.map\(get\)", txt):
            nomes |= set(re.findall(r"'([\w.-]+\.json)'", bloco))
    return nomes


def pedidos_caminho_fixo():
    """Pedidos com caminho escrito por extenso: './data/x.json', './data/cumbias/x.json', './audio/x.json'."""
    alvos = set()
    for f in FONTES:
        if "vendor" in f.parts:
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        alvos |= set(re.findall(r"'\./((?:data|audio)/(?:cumbias/)?[\w.-]+\.json)'", txt))
    return alvos


def main():
    if not SITE.exists():
        print("✗ _site/ não existe — rode antes: python3 app/build_site.py", file=sys.stderr)
        return 2

    escritos = {j: {p.name for p in (SITE / "data" / b).glob("*.json")} for j, b in JORNADAS.items()}
    pedidos = pedidos_por_jornada()
    erros, avisos = [], []

    # 1 e 2 — arquivos por jornada, contra a declaração de opcionais
    for jornada in JORNADAS:
        for nome in sorted(pedidos):
            declarado = (jornada, nome) in OPCIONAIS
            existe = nome in escritos[jornada]
            if not existe and not declarado:
                erros.append(f"{jornada}: o app pede data/{JORNADAS[jornada]}{nome} e o build não escreve "
                             f"(404 silencioso — ou corrija o build, ou declare em OPCIONAIS com motivo)")
            if existe and declarado:
                erros.append(f"{jornada}: {nome} está declarado OPCIONAL mas passou a existir — "
                             f"tire a linha de OPCIONAIS (a declaração virou mentira)")

    # caminhos fixos
    for alvo in sorted(pedidos_caminho_fixo()):
        if not (SITE / alvo).exists():
            erros.append(f"caminho fixo: o app pede ./{alvo} e o build não escreve")

    # 3 — chaves de topo
    for nome, chave, onde in CHAVES:
        for jornada, base in JORNADAS.items():
            p = SITE / "data" / base / nome
            if not p.exists():
                continue
            try:
                dados = json.load(open(p, encoding="utf-8"))
            except Exception as e:
                erros.append(f"{jornada}: {nome} não é JSON válido ({e})")
                continue
            if not isinstance(dados, dict) or chave not in dados:
                erros.append(f"{jornada}: {nome} não tem a chave de topo '{chave}' — o app lê isso em {onde}")

    # órfãos: escritos e nunca pedidos (só aviso; pode ser material de outra tela)
    fixos = {pathlib.PurePosixPath(a).name for a in pedidos_caminho_fixo()}
    for jornada in JORNADAS:
        for nome in sorted(escritos[jornada] - pedidos - fixos):
            avisos.append(f"{jornada}: data/{JORNADAS[jornada]}{nome} é escrito mas ninguém lê")

    for a in avisos:
        print(f"  ⚠ {a}")
    if erros:
        print(f"\n✗ contrato pipeline↔app quebrado ({len(erros)}):", file=sys.stderr)
        for e in erros:
            print(f"  - {e}", file=sys.stderr)
        return 1
    n = len(pedidos) * len(JORNADAS) + len(pedidos_caminho_fixo()) + len(CHAVES)
    print(f"✓ contrato pipeline↔app ok — {len(pedidos)} arquivos × {len(JORNADAS)} jornadas, "
          f"{len(OPCIONAIS)} ausências declaradas, {len(CHAVES)} chaves de topo conferidas ({n} checagens)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
