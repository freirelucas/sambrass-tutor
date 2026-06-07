#!/usr/bin/env python3
"""Funde DEDOS (classe de altura) + OMR (oitava/ritmo) → melodias PROVISÓRIAS.

Conservador por desenho: parte da melodia do OMR (ritmo, oitava, conjunto de notas) e
só CORRIGE a classe de altura de cada nota onde o dedo alinhado discorda do OMR. Nunca
inventa nota a partir de dedo não-alinhado nem mexe no ritmo → não piora a altura, só
conserta os erros de classe do OMR usando o canal validado.

Escopo: páginas de confiança 'alta' que ainda não têm melodia conferida à mão.
Saída: content/notes_auto/sb-NNN.abc (marcadas provisórias; o build as põe abaixo das
conferidas e acima do OMR cru).
"""
import sys, json, pathlib, glob
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))      # content/
from build_abc import to_abc, get_meta
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))          # fingering/
import read_fingerings as R

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "content" / "notes_runtime"
READS = ROOT / "content" / "fingering" / "reads"
MUSICXML = ROOT / "content" / "notes" / "omr"
MANUAL = ROOT / "content" / "notes_manual"
OUT = ROOT / "content" / "notes_auto"
CAT = json.load(open(ROOT / "content" / "pieces.json", encoding="utf-8"))
TITLES = {p["num"]: p.get("titulo", f"sb-{p['num']:03d}") for p in CAT.get("pieces", [])}

HARM = {'0': [60, 67, 72, 76, 79], '2': [59, 66, 71, 75, 78], '1': [58, 65, 70, 74, 77],
        '3': [57, 64, 69, 73, 76], '12': [57, 64, 69, 73, 76], '23': [56, 63, 68, 72, 75],
        '13': [55, 62, 67, 71, 74], '123': [54, 61, 66, 70, 73]}   # 3 ≈ 1+2 (−3 semitons)
CLASSES = {f: {p % 12 for p in ps} for f, ps in HARM.items()}


def nw_align(omr_pc, fing):
    """Needleman-Wunsch: casa classe do OMR com classes do dedo. Devolve {i_omr: j_fing}."""
    n, m = len(omr_pc), len(fing)
    S = [[0.0] * (m + 1) for _ in range(n + 1)]
    bt = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): S[i][0] = -i
    for j in range(1, m + 1): S[0][j] = -j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            hit = omr_pc[i - 1] in CLASSES.get(fing[j - 1], set())
            diag = S[i - 1][j - 1] + (1 if hit else -1)
            up, left = S[i - 1][j] - 1, S[i][j - 1] - 1
            S[i][j] = max(diag, up, left)
            bt[i][j] = 0 if S[i][j] == diag else (1 if S[i][j] == up else 2)
    i, j, pair = n, m, {}
    while i > 0 and j > 0:
        if bt[i][j] == 0: pair[i - 1] = j - 1; i -= 1; j -= 1
        elif bt[i][j] == 1: i -= 1
        else: j -= 1
    return pair


def fuse(num):
    runtime = RUNTIME / f"sb-{num:03d}.json"
    read = READS / f"sb-{num:03d}.json"
    mxml = MUSICXML / f"sb-{num:03d}.musicxml"
    if not (runtime.exists() and read.exists() and mxml.exists()):
        return None
    events = json.load(open(runtime))["events"]
    fing = [d["f"] for sysf in json.load(open(read))["systems"] for d in sysf]
    note_idx = [k for k, e in enumerate(events) if "written_midi" in e]
    omr_pc = [events[k]["written_midi"] % 12 for k in note_idx]
    pair = nw_align(omr_pc, fing)
    changed = 0
    for ni, oi in enumerate(note_idx):           # ni = posição entre as notas; oi = índice no events
        if ni in pair:
            f = fing[pair[ni]]
            old = events[oi]["written_midi"]
            if old % 12 not in CLASSES[f]:        # OMR discorda do dedo → corrige a classe
                events[oi] = dict(events[oi],
                                  written_midi=min(HARM[f], key=lambda p: abs(p - old)))
                changed += 1
    fifths, meter = get_meta(mxml)
    abc = to_abc(events, fifths, meter, TITLES.get(num, f"sb-{num:03d}"))
    return abc, changed, len(note_idx)


def main():
    OUT.mkdir(exist_ok=True)
    summary = json.load(open(READS / "_summary.json"))
    alta = [r["num"] for r in summary if r["confidence"] == "alta"]
    manual = {int(p.stem.split("-")[1]) for p in MANUAL.glob("sb-*.abc")}
    done, tot_changed = 0, 0
    for num in alta:
        if num in manual:                         # conferida à mão vence — não sobrescreve
            continue
        res = fuse(num)
        if not res:
            continue
        abc, changed, nnotes = res
        (OUT / f"sb-{num:03d}.abc").write_text(abc, encoding="utf-8")
        done += 1; tot_changed += changed
    print(f"melodias provisórias geradas: {done} (páginas 'alta' sem versão conferida)")
    print(f"notas com classe corrigida pelo dedo: {tot_changed}")


if __name__ == "__main__":
    main()
