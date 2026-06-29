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


def extract_riffs(events, k=3, min_len=3, max_len=8):
    """Os k trechos DISTINTOS que mais se repetem (>=2x, sem sobreposição) — os 'blocos' da peça.
    Distintos = não cobrem majoritariamente as mesmas notas (descarta variações/sub-frases)."""
    notes = _notes(events)
    if len(notes) < min_len * 2:
        return []
    cands = []
    for L in range(max_len, min_len - 1, -1):
        seen = defaultdict(list)
        for i in range(len(notes) - L + 1):
            seen[tuple(notes[i:i + L])].append(i)
        for gram, pos in seen.items():
            nonov, last = [], -10 ** 9
            for p in pos:
                if p - last >= L:
                    nonov.append(p); last = p
            if len(nonov) >= 2:
                cands.append(dict(notes=list(gram), count=len(nonov), positions=nonov, len=L, score=len(nonov) * L))
    cands.sort(key=lambda c: -c["score"])
    chosen, used = [], set()
    for c in cands:
        cov = set()
        for p in c["positions"]:
            cov.update(range(p, p + c["len"]))
        if cov and len(cov & used) > 0.5 * len(cov):     # sobrepõe muito com um já escolhido → é variação
            continue
        chosen.append(c); used |= cov
        if len(chosen) >= k:
            break
    return chosen


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


def _event_measures(events):
    """Compasso de cada NOTA (na ordem de _notes/positions). Mapeia índice de nota → compasso."""
    return [e["measure"] for e in events if "written_midi" in e]


def theme_measure_span(events, riff=None, min_bars=8, max_bars=16):
    """[primeiro, último] compasso (inclusive) do TEMA de abertura — compassos INTEIROS.
    Ancora nas ~2 primeiras ocorrências do riff dominante; clampa em [min,max]; abre no compasso 1.
    Retorna None se não houver notas. Para peças curtas (DSL ≤8 comp.) devolve a peça inteira."""
    if riff is None:
        riff = extract_riff(events)
    meas = _event_measures(events)
    if not meas:
        return None
    first, last_measure = min(meas), max(meas)
    end = min(first + min_bars - 1, last_measure)            # default: primeiros min_bars
    if riff and riff.get("positions"):
        pos = riff["positions"]
        second_start = pos[1] if len(pos) >= 2 else pos[0]
        idx_end = min(second_start + riff["len"] - 1, len(meas) - 1)
        end = meas[idx_end]                                  # fecha após ~2 voltas do riff
    end = max(end, first + min_bars - 1)                     # pelo menos min_bars
    end = min(end, first + max_bars - 1, last_measure)       # no máximo max_bars, nunca além da peça
    return (first, end)


def slice_events_by_measure(events, lo, hi):
    """Sub-lista de eventos com compasso em [lo,hi], RENUMERADOS p/ começar em 1 (ABC self-contained)."""
    out = []
    for e in events:
        m = e.get("measure")
        if m is not None and lo <= m <= hi:
            e2 = dict(e)
            e2["measure"] = m - lo + 1
            out.append(e2)
    return out


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
