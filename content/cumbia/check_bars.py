#!/usr/bin/env python3
"""Valida se cada compasso do ABC preenche a fórmula de compasso (M:).

Compasso que não soma a métrica = erro de transcrição (silêncio/duração errada). As cumbias
são MONOFÔNICAS e sem tercina/acorde (verificado), então a soma direta das durações vale.
O app usa isto para AVISAR honestamente ("ritmo/silêncio em revisão") em vez de fingir
"conferida" num compasso quebrado.

Uso: `check_all(abc_dict) -> {id: [nºs de compasso ruins]}`; ou rode p/ um relatório.
"""
import re
import json
import pathlib

# nota (com acidentes ^_= e oitava ,') OU pausa (z/x/Z), capturando o comprimento
_TOKEN = re.compile(r"(?:[\^_=]*[a-gA-G][,']*|[zxZ])(\d*/?\d*)")


def _plen(s):
    if not s:
        return 1.0
    if s == "/":
        return 0.5
    if s.startswith("/"):
        return 1.0 / float(s[1:])
    if "/" in s:
        n, d = s.split("/")
        return float(n or 1) / float(d or 2)
    return float(s)


def bad_bars(abc):
    """Lista (1-indexada) dos compassos do ABC que não somam a métrica."""
    m = re.search(r"M:\s*(\d+)\s*/\s*(\d+)", abc)
    L = re.search(r"L:\s*1\s*/\s*(\d+)", abc)
    if not m or not L or "K:" not in abc:
        return []
    beats, bd, unit_den = int(m.group(1)), int(m.group(2)), int(L.group(1))
    target = beats * (unit_den / bd)                     # unidades-L por compasso (4/4, L:1/16 -> 16)
    after_k = abc.split("K:", 1)[1]
    body = after_k.split("\n", 1)[1] if "\n" in after_k else ""
    body = body.replace("|]", "|").replace("|:", "|").replace(":|", "|")
    bad = []
    for i, bar in enumerate(b for b in re.split(r"\|", body) if b.strip()):
        s = sum(_plen(mt.group(1)) for mt in _TOKEN.finditer(bar))
        if s > 0 and abs(s - target) > 0.01:
            bad.append(i + 1)
    return bad


def check_all(abc_dict):
    out = {}
    for k, v in abc_dict.items():
        if k.startswith("_") or k.startswith("cell-") or not isinstance(v, str):
            continue                                     # células são fragmentos, não compassos inteiros
        b = bad_bars(v)
        if b:
            out[k] = b
    return out


if __name__ == "__main__":
    p = pathlib.Path(__file__).resolve().parent / "build" / "abc.json"
    warn = check_all(json.load(open(p, encoding="utf-8")))
    for k in sorted(warn):
        print(f"  {k}: compassos {warn[k]}")
    print(f"--- {sum(len(v) for v in warn.values())} compassos malformados em {len(warn)} peças ---")
