#!/usr/bin/env python3
"""Transcrição-fusão: junta os 3 canais p/ tirar a melodia de cada página das 110.

  1. DEDOS (read_fingerings)  -> classe de altura EXATA por nota (canal limpo, validado).
  2. OMR (Audiveris)          -> oitava/registro + ritmo (o que o OMR acerta bem).
  3. CATÁLOGO                 -> tom (armadura) p/ grafia.

Estado (provado na 011):
  - Classe de altura pelos dedos: 100% no Sistema A (bate com a ditadura do Lucas).
  - Oitava por alinhamento (Needleman-Wunsch) dedos×OMR: boa no miolo, falha onde o OMR
    perde notas (ex. cadência) → marcada baixa-confiança p/ revisão pontual.
  - Ritmo: do OMR onde a contagem dedos==OMR no compasso; senão a revisar.
A altura (a parte que o OMR/visão erram) fica resolvida pelos dedos; resta oitava+ritmo.
"""
import sys, pathlib, json
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from read_fingerings import read_page

# dedo -> séries harmônicas (MIDI escrito) e classes (pitch-class)
HARM = {'0':[60,67,72,76,79], '2':[59,66,71,75,78], '1':[58,65,70,74,77],
        '12':[57,64,69,73,76], '23':[56,63,68,72,75], '13':[55,62,67,71,74], '123':[54,61,66,70,73]}
CLASSES = {f: {p % 12 for p in ps} for f, ps in HARM.items()}

def align_octaves(fings, omr_midi):
    """Needleman-Wunsch: casa classe do dedo com classe do OMR; transfere a oitava do OMR."""
    n, m = len(fings), len(omr_midi)
    S = np.zeros((n+1, m+1)); bt = np.zeros((n+1, m+1), int)
    for i in range(1, n+1): S[i][0] = -i
    for j in range(1, m+1): S[0][j] = -j
    for i in range(1, n+1):
        for j in range(1, m+1):
            hit = (omr_midi[j-1] % 12) in CLASSES.get(fings[i-1], set())
            diag = S[i-1][j-1] + (1 if hit else -2)
            up, left = S[i-1][j]-1, S[i][j-1]-1
            S[i][j] = max(diag, up, left)
            bt[i][j] = 0 if S[i][j]==diag else (1 if S[i][j]==up else 2)
    i, j, pair = n, m, {}
    while i > 0 and j > 0:
        if bt[i][j] == 0: pair[i-1] = j-1; i -= 1; j -= 1
        elif bt[i][j] == 1: i -= 1
        else: j -= 1
    seq, conf = [None]*n, [False]*n
    for k in range(n):
        if k in pair:
            seq[k] = min(HARM[fings[k]], key=lambda p: abs(p-omr_midi[pair[k]])); conf[k] = True
    for k in range(n):                       # não-alinhadas: oitava por contorno (baixa conf.)
        if seq[k] is None:
            ref = next((seq[t] for t in range(k-1,-1,-1) if seq[t] is not None), 67)
            seq[k] = min(HARM[fings[k]], key=lambda p: abs(p-ref))
    return seq, conf

def transcribe(num):
    img = f"content/scores/sb-{num:03d}.jpg"
    runtime = f"content/notes_runtime/sb-{num:03d}.json"
    systems = read_page(img)
    fings = [f for sysf in systems for _, f in sysf]
    omr = []
    if pathlib.Path(runtime).exists():
        d = json.load(open(runtime))
        omr = [e['written_midi'] for e in d['events'] if not e.get('rest')]
    seq, conf = align_octaves(fings, omr) if omr else ([HARM[f][1] for f in fings], [False]*len(fings))
    return {"num": num, "fingerings": fings, "written_midi": seq,
            "octave_confident": conf, "n_notes": len(fings),
            "n_low_conf": sum(1 for c in conf if not c)}

if __name__ == "__main__":
    for a in sys.argv[1:]:
        r = transcribe(int(a))
        print(f"sb-{r['num']:03d}: {r['n_notes']} notas, {r['n_low_conf']} oitavas a revisar")
        print("  dedos:", " ".join(r["fingerings"]))
