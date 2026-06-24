#!/usr/bin/env python3
"""Detector de FRASES REPETITIVAS (o riff/ostinato que define a cumbia).

A cumbia/chicha vive de uma frase curta que volta o tempo todo. Aqui achamos a frase
(sequência de (altura escrita, duração)) mais REPETIDA da peça — o "riff dominante" —
para a escada pedagógica ("escada = músicas") destacar o riff em cada Story.

Entrada: eventos do build_notes (written_midi, dur_beats). Saída: o melhor riff
(notas, nº de repetições, posições) + a densidade de repetição (sinal de dificuldade:
mais repetido = mais fácil de decorar = entra antes na escada).
"""
from collections import defaultdict


def _notes(events):
    return [(e["written_midi"], round(e.get("dur_beats", 0), 3)) for e in events if "written_midi" in e]


def extract_riff(events, min_len=3, max_len=8):
    """Acha a frase mais longa que REPETE (>=2x, sem sobreposição), ponderada por cobertura."""
    notes = _notes(events)
    if len(notes) < min_len * 2:
        return None
    best = None
    for L in range(max_len, min_len - 1, -1):
        seen = defaultdict(list)
        for i in range(len(notes) - L + 1):
            seen[tuple(notes[i:i + L])].append(i)
        for gram, pos in seen.items():
            # conta só ocorrências NÃO sobrepostas
            nonov, last = [], -10 ** 9
            for p in pos:
                if p - last >= L:
                    nonov.append(p); last = p
            if len(nonov) >= 2:
                score = len(nonov) * L            # cobre mais notas = riff mais forte
                if not best or score > best["score"]:
                    best = dict(notes=list(gram), count=len(nonov), positions=nonov, len=L, score=score)
        if best:                                   # prefere o riff mais LONGO que repete
            break
    return best


def repeticao_ratio(events):
    """Fração das notas da peça cobertas pelo riff dominante (0–1). Sinal de 'decorabilidade'."""
    notes = _notes(events)
    riff = extract_riff(events)
    if not riff or not notes:
        return 0.0
    return min(1.0, riff["count"] * riff["len"] / len(notes))


def riff_events(riff, fifths_meta_measure=1):
    """Converte o riff em eventos (p/ to_abc/render) — todos no 'compasso 1'."""
    if not riff:
        return []
    return [{"measure": fifths_meta_measure, "written_midi": m, "dur_beats": d} for m, d in riff["notes"]]


if __name__ == "__main__":
    import sys, pathlib, glob
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from build_notes import compile_file, load_fingering
    fing, tr = load_fingering()
    for f in sorted(glob.glob(str(pathlib.Path(__file__).resolve().parents[1] / "notes" / "cumbia" / "cu-*.musicxml"))):
        data = compile_file(pathlib.Path(f), fing, tr)
        riff = extract_riff(data["events"])
        stem = pathlib.Path(f).stem
        if riff:
            from build_notes import name, SHARP
            seq = " ".join(name(m, SHARP) for m, _ in riff["notes"])
            print(f"{stem}: riff de {riff['len']} notas, {riff['count']}× · {seq} · cobertura {repeticao_ratio(data['events']):.0%}")
        else:
            print(f"{stem}: (sem riff repetido claro)")
