#!/usr/bin/env python3
"""Valida a integridade do conteúdo versionado em content/.

Checa: referências de células/arpejos das peças existem no catálogo; ids de peça
citados por caderno e currículo existem; tons em concerto são válidos; instrumentos
têm os campos mínimos. Sai com código !=0 se algo quebrar (serve de teste de dados).

Uso:  python3 content/validate.py
"""
import json, pathlib, sys, glob

CONTENT = pathlib.Path(__file__).resolve().parent
PITCHES = {"C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb",
           "G", "G#", "Ab", "A", "A#", "Bb", "B"}


def load(p):
    return json.load(open(p, encoding="utf-8"))


def main():
    erros = []
    pieces = load(CONTENT / "pieces.json")["pieces"]
    cells = load(CONTENT / "cells.json")
    cel_ids = {c["id"] for c in cells["celulas_ritmicas"]}
    arp_ids = {a["id"] for a in cells["arpejos"]}
    piece_ids = {p["id"] for p in pieces}

    # peças
    nums = set()
    for p in pieces:
        ctx = p.get("id", "?")
        if p["num"] in nums:
            erros.append(f"{ctx}: num duplicado {p['num']}")
        nums.add(p["num"])
        if p["id"] != f"sb-{p['num']:03d}":
            erros.append(f"{ctx}: id não bate com num {p['num']}")
        if p["key_concert"] not in PITCHES:
            erros.append(f"{ctx}: key_concert inválido {p['key_concert']!r}")
        if p["modulates_to_concert"] not in (None, *PITCHES):
            erros.append(f"{ctx}: modulates_to_concert inválido {p['modulates_to_concert']!r}")
        for c in p["celulas"]:
            if c not in cel_ids:
                erros.append(f"{ctx}: célula desconhecida {c}")
        for a in p["arpejos"]:
            if a not in arp_ids:
                erros.append(f"{ctx}: arpejo desconhecido {a}")
        d = p["dificuldade"]
        if d is not None and not (1 <= d <= 10):
            erros.append(f"{ctx}: dificuldade fora de 1–10 ({d})")

    # instrumentos
    for ip in glob.glob(str(CONTENT / "instruments" / "*.json")):
        inst = load(ip)
        for campo in ("id", "transpose_semitones", "clave", "fingering"):
            if campo not in inst:
                erros.append(f"{pathlib.Path(ip).name}: falta campo {campo}")

    # cadernos
    for cp in glob.glob(str(CONTENT / "cadernos" / "*.json")):
        cad = load(cp)
        for pid in cad.get("ordem", []):
            if pid not in piece_ids:
                erros.append(f"{pathlib.Path(cp).name}: ordem cita peça inexistente {pid}")

    # currículos
    for qp in glob.glob(str(CONTENT / "curriculum" / "*.json")):
        cur = load(qp)
        nm = pathlib.Path(qp).name
        for s in cur.get("semanas", []):
            for pid in s.get("pieces_foco", []) + s.get("leitura_1avista", []):
                if pid not in piece_ids:
                    erros.append(f"{nm} sem {s.get('n')}: cita peça inexistente {pid}")
            if s.get("celula_alvo"):
                for c in str(s["celula_alvo"]).replace("+", " ").split():
                    if c not in cel_ids:
                        erros.append(f"{nm} sem {s.get('n')}: celula_alvo desconhecida {c}")

    if erros:
        print(f"FALHOU — {len(erros)} problema(s):")
        for e in erros:
            print("  -", e)
        sys.exit(1)
    ver = sum(1 for p in pieces if p.get("verificada"))
    print(f"OK — {len(pieces)} peças ({ver} verificadas), referências íntegras.")


if __name__ == "__main__":
    main()
