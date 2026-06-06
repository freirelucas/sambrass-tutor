#!/usr/bin/env python3
"""Recalibra a dificuldade por uma fórmula transparente de features (não sobrescreve a manual).

Eixos (pesos em lib.raw_difficulty): tom (acidentes) → densidade → cromatismo → forma,
+ semicolcheia/tercina/contratempo/modulação. O raw é normalizado para 1–10 (usa a escala
cheia, corrigindo o aglomerado em 6–7 da estimativa manual).

Saída: content/curadoria/dificuldade.json. Uso: python3 content/curadoria/recalibrar.py
"""
import json, collections
from lib import load_pieces, features, difficulty_table, ROOT

OUT = ROOT / "curadoria" / "dificuldade.json"


def main():
    pieces = load_pieces()
    calc, raw = difficulty_table(pieces)
    rows = []
    for p in sorted(pieces, key=lambda x: x["num"]):
        rows.append({
            "num": p["num"], "titulo": p["titulo"],
            "dificuldade_manual": p["dificuldade"],
            "dificuldade_calc": calc[p["num"]],
            "raw": round(raw[p["num"]], 2),
            "features": features(p),
        })
    json.dump({
        "_meta": {
            "metodo": "raw = 1 + 0.6*acidentes + densidade + cromatismo + 0.5*(seções-2) "
                      "+ 1.5*extensa + 1.5*semicolcheia + 0.7*tercina + 0.3*contratempo + modulação; "
                      "depois normalizado min-max para 1–10.",
            "uso": "comparar com a manual; adotar/mesclar a gosto. Não sobrescreve pieces.json.",
        },
        "pieces": rows,
    }, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    dm = collections.Counter(r["dificuldade_manual"] for r in rows)
    dc = collections.Counter(r["dificuldade_calc"] for r in rows)
    print(f"OK — {len(rows)} peças → {OUT}")
    print("manual :", dict(sorted(dm.items())))
    print("calc   :", dict(sorted(dc.items())))
    print("sanidade: 013 calc", calc[13], "| 009 calc", calc[9], "| 039 calc", calc[39])
    div = sorted(rows, key=lambda r: abs(r["dificuldade_calc"] - r["dificuldade_manual"]), reverse=True)
    print("maiores divergências (manual→calc):")
    for r in div[:6]:
        print(f"  {r['num']:03d} {r['titulo'][:28]:28} {r['dificuldade_manual']}→{r['dificuldade_calc']}")


if __name__ == "__main__":
    main()
