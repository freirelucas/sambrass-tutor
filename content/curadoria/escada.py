#!/usr/bin/env python3
"""Curadoria 3e — Escada pedagógica: nível mínimo de método por peça (Essential Elements
Book 1 → Book 2 → Arban) + camada idiomática Sambrass, derivado do catálogo.

Materializa o mapeamento da HANDOFF de pedagogia (§8) para as 110 peças, validado contra as
30 hand-curadas do site_preview (oráculo, casado por TÍTULO — a numeração derivou; ver
docs/escada_pedagogica.md). A regra mora em curadoria/lib.py (transparente e reprodutível).

Saída: content/curadoria/escada.json. Uso: python3 content/curadoria/escada.py
"""
import json, collections, unicodedata, re
from lib import (load_pieces, difficulty_table, written_key, nivel_minimo,
                 prerequisitos, orfaos_book1, ARBAN_REQ, ROOT)

OUTDIR = ROOT / "curadoria"

# Oráculo da handoff §4 (funil estrito), por TÍTULO. A numeração do site_preview não bate
# com a atual (ex.: handoff "010 Preciso Me Encontrar" = sb-011 hoje), então casamos por nome.
ORACLE = {
    "book1": ["Até Amanhã", "Com Que Roupa", "Feitiço da Vila", "Trem das Onze",
              "Alguém Me Avisou", "Se Você Jurar", "Tristeza", "Não Deixe o Samba Morrer",
              "A Felicidade", "Pra Que Chorar"],
    "book2": ["Fita Amarela", "Acontece", "As Rosas Não Falam", "O Mundo é um Moinho",
              "A Voz do Morro", "Sonho Meu", "Casa de Bamba", "Andança", "Vou Festejar",
              "Quem Te Viu, Quem Te Vê", "O Morro Não Tem Vez", "Mas Que Nada", "Maracangalha"],
    "arban": ["Preciso Me Encontrar", "A Flor e o Espinho", "Vai Vadiar", "Dança da Solidão",
              "Foi um Rio Que Passou em Minha Vida", "Flor de Lis"],
}


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def main():
    P = load_pieces()
    calc, _ = difficulty_table(P)
    by_title = {_norm(p["titulo"]): p for p in P}

    model = []
    for p in sorted(P, key=lambda x: x["num"]):
        nm = nivel_minimo(p)
        model.append({
            "num": p["num"], "id": p["id"], "titulo": p["titulo"],
            "tom_escrito": written_key(p["key_concert"]),
            "nivel_minimo": nm,
            "tocavel_book1": nm == "book1",
            "requisito_orfao_book1": orfaos_book1(p),
            "prerequisitos": prerequisitos(p),
            "dificuldade_calc": calc[p["num"]],
        })

    funil = collections.Counter(m["nivel_minimo"] for m in model)
    acumulado = {"book1": funil["book1"],
                 "book2": funil["book1"] + funil["book2"],
                 "arban": sum(funil.values())}

    # validação contra o oráculo da handoff (por título)
    match, div, divergencias = 0, 0, []
    for lvl, titles in ORACLE.items():
        for t in titles:
            p = by_title.get(_norm(t))
            if not p:
                divergencias.append({"titulo": t, "status": "ausente"})
                continue
            got = nivel_minimo(p)
            if got == lvl:
                match += 1
            else:
                div += 1
                divergencias.append({"titulo": t, "num": p["num"], "handoff": lvl,
                                     "regra": got, "status": "diverge"})

    json.dump({
        "_meta": {
            "sobre": "Escada pedagógica: nível mínimo de método (Essential Elements Book 1/2, "
                     "Arban) + camada idiomática Sambrass, por peça. Derivado de pieces.json "
                     "pela regra em curadoria/lib.py. Materializa a HANDOFF §8 para as 110.",
            "regra": {
                "book1_tons_escritos": ["C", "F", "G", "Bb"],
                "book2_tons_escritos": ["D", "A", "Eb", "E"],
                "book2_celulas": ["C3", "C4", "C5"],
                "arban_marcadores": sorted(ARBAN_REQ),
            },
            "funil": dict(funil),
            "acumulado_tocavel": acumulado,
            "validacao_oraculo": {
                "match": match, "diverge": div, "de": match + div,
                "divergencias": divergencias,
                "nota": "Divergências justificadas em docs/escada_pedagogica.md: 'Fita Amarela' "
                        "segue a tabela-mestre §3 (Sib 2♭ = Book 1, não Book 2); 'Preciso Me "
                        "Encontrar' é drift de numeração/metadados (handoff Lá/dif7 vs sb-011 Sol/dif4).",
            },
        },
        "pieces": model,
    }, open(OUTDIR / "escada.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"OK — escada.json ({len(model)} peças) em {OUTDIR}")
    print("funil (nível mínimo):", dict(funil), "→ acumulado tocável:", acumulado)
    print(f"oráculo handoff: {match}/{match + div} batem; {div} divergem (justificadas)")
    for v in divergencias:
        if v.get("status") == "diverge":
            print(f"  · {v['titulo']} (#{v['num']:03d}): handoff={v['handoff']} regra={v['regra']}")


if __name__ == "__main__":
    main()
