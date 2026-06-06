#!/usr/bin/env python3
"""Funções compartilhadas da curadoria/analytics: features, dificuldade, habilidades.

Tudo deriva de content/pieces.json (catálogo) + cells.json. Transparente e reprodutível.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
      "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
# nº de acidentes da tonalidade maior, por classe de altura da tônica (menor entre #/b)
ACC_BY_PC = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 5: 1, 10: 2, 3: 3, 8: 4, 1: 5}
DENS = {"baixa": 0.0, "baixa-média": 0.5, "média": 1.0, "média-alta": 2.0, "alta": 3.0}


def load_pieces():
    return json.load(open(ROOT / "pieces.json", encoding="utf-8"))["pieces"]


def written_acc(key_concert):
    """nº de acidentes da armadura ESCRITA (trompete) = concerto transposto +2 semitons."""
    if key_concert not in PC:
        return 0
    return ACC_BY_PC[(PC[key_concert] + 2) % 12]


def features(p):
    reqs = " ".join(p.get("requisitos", []))
    acc = written_acc(p["key_concert"])
    if p.get("modulates_to_concert"):
        acc = max(acc, written_acc(p["modulates_to_concert"]))
    cel = set(p.get("celulas", []))
    forma = p.get("forma", [])
    chrom = 2 if "cromatismo-denso" in reqs else (1 if "cromatismo" in reqs else 0)
    return {
        "acidentes": acc,
        "densidade": DENS.get(p.get("densidade"), 1.0),
        "cromatismo": chrom,
        "n_secoes": len(forma),
        "extensa": 1 if ("extensa" in reqs or "ABCD" in reqs or len(forma) >= 4) else 0,
        "semicolcheia": 1 if "C4" in cel else 0,
        "tercina": 1 if "C5" in cel else 0,
        "contratempo": 1 if ("C6" in cel or "síncope" in reqs or "contratempo" in reqs) else 0,
        "modulacao": 1 if p.get("modulates_to_concert") else 0,
        "quatro_quartos": 1 if p.get("compasso") == "4/4" else 0,
    }


def raw_difficulty(f):
    """Soma ponderada e transparente das features (eixos: tom → densidade → cromatismo → forma)."""
    return (1.0
            + 0.6 * f["acidentes"]
            + 1.0 * f["densidade"]
            + 1.0 * f["cromatismo"]
            + 0.5 * max(0, f["n_secoes"] - 2)
            + 1.5 * f["extensa"]
            + 1.5 * f["semicolcheia"]
            + 0.7 * f["tercina"]
            + 0.3 * f["contratempo"]
            + 1.0 * f["modulacao"])


def difficulty_table(pieces):
    """Devolve {num: dificuldade_calc 1–10} normalizando o raw para a faixa cheia."""
    raw = {p["num"]: raw_difficulty(features(p)) for p in pieces}
    lo, hi = min(raw.values()), max(raw.values())
    calc = {n: round(1 + 9 * (r - lo) / (hi - lo)) for n, r in raw.items()}
    return calc, raw


# --- Habilidades (taxonomia normalizada) ---
SKILLS = {
    "tom-0": "tonalidade sem acidentes (Dó/Sib escritos)",
    "tom-1": "tonalidade 1 acidente (Fá/Sol)",
    "tom-2": "tonalidade 2 acidentes (Ré/Sib)",
    "tom-3": "tonalidade 3 acidentes (Lá/Mib)",
    "tom-6": "tonalidade extrema (Fá#, 6 sustenidos)",
    "sincope": "síncope (C2)",
    "tercina": "tercina (C5)",
    "colcheia-pontuada": "colcheia pontuada + semicolcheia (C3)",
    "semicolcheia": "semicolcheias / staccato duplo (C4)",
    "contratempo": "contratempo / ataque no 'e' (C6)",
    "anacruse": "anacruse (C7)",
    "casas": "casas 1ª/2ª",
    "ds-dc": "D.S. / D.C. (saltos)",
    "modulacao": "modulação de armadura",
    "forma-longa": "forma longa (A/B/C/D)",
    "forma-extensa": "forma extensa / resistência",
    "cromatismo": "cromatismo de passagem",
    "compasso-4-4": "leitura em 4/4",
}


def piece_skills(p):
    """Conjunto de habilidades exigidas pela peça (derivado de tom/células/requisitos/forma)."""
    s = set()
    a = written_acc(p["key_concert"])
    s.add("tom-6" if a >= 6 else f"tom-{min(a, 3)}")
    cel = set(p.get("celulas", []))
    reqs = " ".join(p.get("requisitos", []))
    if "C2" in cel or "síncope" in reqs:
        s.add("sincope")
    if "C5" in cel or "tercina" in reqs:
        s.add("tercina")
    if "C3" in cel:
        s.add("colcheia-pontuada")
    if "C4" in cel or "semicolcheia" in reqs:
        s.add("semicolcheia")
    if "C6" in cel or "contratempo" in reqs:
        s.add("contratempo")
    if "C7" in cel or "anacruse" in reqs:
        s.add("anacruse")
    if "casas" in reqs:
        s.add("casas")
    if "DS" in reqs or "DC" in reqs:
        s.add("ds-dc")
    if p.get("modulates_to_concert"):
        s.add("modulacao")
    if "cromatismo" in reqs:
        s.add("cromatismo")
    if p.get("compasso") == "4/4":
        s.add("compasso-4-4")
    if "extensa" in reqs or len(p.get("forma", [])) >= 4:
        s.add("forma-extensa")
    elif len(p.get("forma", [])) >= 3:
        s.add("forma-longa")
    return s
