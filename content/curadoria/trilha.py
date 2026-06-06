#!/usr/bin/env python3
"""Curadoria 3b–3d: habilidades por peça, trilha mestra graded, trilhas por habilidade,
escada de leitura à 1ª vista. Tudo derivado do catálogo + dificuldade recalibrada.

Saídas em content/curadoria/: skills.json, piece_skills.json, trilha.json.
Uso: python3 content/curadoria/trilha.py
"""
import json, collections
from lib import load_pieces, piece_skills, difficulty_table, written_acc, SKILLS, DENS, ROOT

OUTDIR = ROOT / "curadoria"
# pré-requisitos pedagógicos (a habilidade só entra depois dos seus pré-requisitos)
PREREQ = {
    "tom-1": {"tom-0"}, "tom-2": {"tom-1"}, "tom-3": {"tom-2"}, "tom-6": {"tom-3"},
    "semicolcheia": {"tercina"}, "forma-extensa": {"forma-longa"},
}


def master_path(pieces, calc, req):
    """Greedy: a cada passo, a peça que introduz o MENOS de habilidade nova (com pré-reqs
    atendidos), desempate por dificuldade recalibrada. Registra skill_introduced."""
    learned, order, remaining = set(), [], list(pieces)
    while remaining:
        best, best_key = None, None
        for p in remaining:
            new = req[p["num"]] - learned
            # uma habilidade nova é "liberável" se seus pré-reqs já foram aprendidos
            blocked = any((PREREQ.get(s, set()) - learned) for s in new)
            key = (len(new), 1 if blocked else 0, calc[p["num"]], p["num"])
            if best_key is None or key < best_key:
                best, best_key = p, key
        new = sorted(req[best["num"]] - learned)
        learned |= req[best["num"]]
        order.append((best, new))
        remaining.remove(best)
    return order


def main():
    pieces = load_pieces()
    calc, _ = difficulty_table(pieces)
    req = {p["num"]: piece_skills(p) for p in pieces}

    # 3b — taxonomia + habilidades por peça
    json.dump({"skills": SKILLS}, open(OUTDIR / "skills.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump({"pieces": [{"num": p["num"], "titulo": p["titulo"],
                           "skills": sorted(req[p["num"]])} for p in
                          sorted(pieces, key=lambda x: x["num"])]},
              open(OUTDIR / "piece_skills.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 3c — trilha mestra
    order = master_path(pieces, calc, req)
    trilha = [{"passo": i + 1, "num": p["num"], "titulo": p["titulo"],
               "dificuldade_calc": calc[p["num"]],
               "habilidade_nova": intro} for i, (p, intro) in enumerate(order)]

    # 3d — trilhas por habilidade (fácil→difícil) + escada de leitura
    por_hab = {}
    for s in SKILLS:
        membros = [p for p in pieces if s in req[p["num"]]]
        membros.sort(key=lambda p: (calc[p["num"]], p["num"]))
        por_hab[s] = [{"num": p["num"], "titulo": p["titulo"], "dificuldade_calc": calc[p["num"]]}
                      for p in membros]
    leitura = sorted(pieces, key=lambda p: (calc[p["num"]], written_acc(p["key_concert"]),
                                            DENS.get(p["densidade"], 1), p["num"]))
    escada = [{"num": p["num"], "titulo": p["titulo"], "tom_concert": p["key_concert"],
               "dificuldade_calc": calc[p["num"]]} for p in leitura]

    json.dump({
        "_meta": {"sobre": "trilha mestra (1 habilidade nova/passo), trilhas por habilidade, "
                            "escada de leitura à 1ª vista. dificuldade_calc = recalibrada 1–10."},
        "trilha_mestra": trilha,
        "trilhas_por_habilidade": por_hab,
        "escada_leitura": escada,
    }, open(OUTDIR / "trilha.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    intro_dist = collections.Counter(len(intro) for _, intro in order)
    print(f"OK — skills.json, piece_skills.json, trilha.json → {OUTDIR}")
    print("habilidades novas por passo (qtde→passos):", dict(sorted(intro_dist.items())))
    print("início da trilha:", [f'{t["num"]:03d}' for t in trilha[:8]])
    print("fim da trilha   :", [f'{t["num"]:03d}' for t in trilha[-5:]])
    print("escada leitura (5 + fáceis):", [f'{e["num"]:03d}' for e in escada[:5]])


if __name__ == "__main__":
    main()
