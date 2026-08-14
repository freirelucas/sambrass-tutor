#!/usr/bin/env python3
"""Decompõe as gravações reais (app/audio/) em unidades PEDAGÓGICAS.

Para cada modelo solo: notas com timestamp (YIN), FRASES (separadas pelas
respirações — os silêncios são onde o trompetista respira, e é onde o aluno
deve respirar), andamento estimado, tessitura usada e as ocorrências dos
LEGOS da peça (os trechos que se repetem, de blocos.json) dentro da gravação
— com t0/t1 para o app tocar "o riff na gravação real".

Para os ensaios de banda (polifônicos): andamento + marcos de seção
(novidade espectral) para navegação.

Saída: app/audio/segmentos.json — consumido pela página de estudo (bloco 🎙).
Ferramenta LOCAL (numpy + soundfile), como tools/audio_confere.py. Uso:
    python3 tools/audio_segmenta.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIO = ROOT / "app" / "audio"

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    sys.exit("precisa de: pip install numpy soundfile")

NAMES = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]


def nome(m):
    return f"{NAMES[m % 12]}{m // 12 - 1}"


def load_mono(path, target_sr=16000):
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    step = max(1, sr // target_sr)
    return np.asarray(x[::step], dtype=float), sr // step


def yin_track(x, sr, fmin=100, fmax=1200, frame=2048, hop=512, thresh=0.15):
    """[(t, f0_hz|0, rms)] por frame."""
    tmin, tmax = int(sr / fmax), int(sr / fmin)
    out = []
    for i in range(0, len(x) - frame - tmax, hop):
        w = x[i:i + frame]
        rms = float(np.sqrt((w ** 2).mean()))
        if rms < 0.01:
            out.append((i / sr, 0.0, rms))
            continue
        seg = x[i:i + frame + tmax]
        d = np.zeros(tmax + 1)
        for tau in range(tmin, tmax + 1):
            diff = seg[:frame] - seg[tau:tau + frame]
            d[tau] = float((diff ** 2).sum())
        cum = np.cumsum(d[1:])
        dp = d[1:] * np.arange(1, tmax + 1) / np.maximum(cum, 1e-10)
        cand = np.where(dp[tmin:] < thresh)[0]
        tau = (cand[0] + tmin + 1) if len(cand) else (int(np.argmin(dp[tmin:])) + tmin + 1)
        out.append((i / sr, sr / tau, rms))
    return out


def notes_of(track, min_frames=3):
    """Segmenta o track em notas [(t0, dur, midi_soando)]."""
    midis = [(t, int(round(69 + 12 * np.log2(f / 440))) if f > 0 else 0) for t, f, _ in track]
    hop_dt = midis[1][0] - midis[0][0] if len(midis) > 1 else 0.032
    notes, cur, start, count = [], 0, 0.0, 0
    for t, m in midis:
        if m == cur:
            count += 1
        else:
            if cur > 45 and count >= min_frames:
                notes.append((round(start, 3), round(t - start, 3), cur))
            cur, start, count = m, t, 1
    if cur > 45 and count >= min_frames:
        notes.append((round(start, 3), round(midis[-1][0] + hop_dt - start, 3), cur))
    return notes


def phrases_of(notes, gap=0.5):
    """Frases separadas por silêncio ≥ gap (a respiração). [(t0, t1, [notas…])]."""
    if not notes:
        return []
    out, cur = [], [notes[0]]
    for prev, n in zip(notes, notes[1:]):
        if n[0] - (prev[0] + prev[1]) >= gap:
            out.append(cur)
            cur = []
        cur.append(n)
    out.append(cur)
    return [(ph[0][0], round(ph[-1][0] + ph[-1][1], 3), ph) for ph in out if len(ph) >= 2]


def tempo_of(x, sr, lo=60, hi=200):
    """BPM pelo pico da autocorrelação do fluxo espectral (e o candidato 2:1)."""
    frame, hop = 2048, 512
    win = np.hanning(frame)
    n = (len(x) - frame) // hop
    env = np.array([np.abs(np.fft.rfft(x[i * hop:i * hop + frame] * win)).sum() for i in range(n)])
    flux = np.diff(env)
    flux[flux < 0] = 0
    fps = sr / hop
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    lags = np.arange(len(ac)) / fps
    valid = (lags > 60 / hi / 1) & (lags < 60 / lo)
    if not valid.any():
        return 0
    beat = lags[valid][int(np.argmax(ac[valid]))]
    peak = float(ac[valid].max())
    # preferir o tempo METADE quando a autocorrelação no dobro do lag é comparável
    # (senão passagens de semicolcheia dobram o BPM: 94 vira 188)
    j = int(round(2 * beat * fps))
    if j < len(ac) and float(ac[j]) >= 0.55 * peak and 60 / (2 * beat) >= lo:
        beat *= 2
    return round(60 / beat)


def match_legos(notes, legos, transpose=2):
    """Ocorrências dos legos (midis ESCRITOS de blocos.json) no áudio (que SOA concert):
    escrito = soando + transpose. Ornamentos/transientes (<90 ms) saem antes do
    casamento; intervalos toleram ±1 st (afinação/vibrato) e erro de 8ª.
    [(idx_lego, t0, t1, acerto)]."""
    seq = [(t, d, m + transpose) for t, d, m in notes if d >= 0.09]   # sem ornamentos
    out = []
    for li, lego in enumerate(legos):
        lm = lego.get("midis") or []
        if len(lm) < 3:
            continue
        liv = [b - a for a, b in zip(lm, lm[1:])]
        L = len(liv)
        i = 0
        while i + L < len(seq):
            aiv = [seq[j + 1][2] - seq[j][2] for j in range(i, i + L)]
            hits = sum(1 for a, b in zip(aiv, liv)
                       if abs(a - b) <= 1 or abs(abs(a - b) - 12) <= 1)
            if hits / L >= 0.7:
                t0 = seq[i][0]
                t1 = seq[i + L][0] + seq[i + L][1]
                out.append((li, round(t0, 2), round(t1, 2), round(hits / L, 2)))
                i += L                                        # não sobrepõe
            else:
                i += 1
    # curadoria p/ a UI: por lego, fica com as melhores ocorrências SEM sobreposição (máx 4)
    kept = []
    for li in sorted({o[0] for o in out}):
        cand = sorted((o for o in out if o[0] == li), key=lambda o: (-o[3], o[1]))
        sel = []
        for o in cand:
            if all(o[2] <= k[1] or o[1] >= k[2] for k in sel):
                sel.append(o)
            if len(sel) == 4:
                break
        kept += sorted(sel, key=lambda o: o[1])
    return kept


def sections_of(x, sr, min_gap=15.0):
    """Marcos de mudança (novidade espectral em janelas de 1 s) p/ navegar o ensaio."""
    frame = sr  # 1 s
    n = len(x) // frame
    feats = []
    for i in range(n):
        s = np.abs(np.fft.rfft(x[i * frame:(i + 1) * frame]))
        s = s / (s.sum() + 1e-9)
        feats.append(s[:2000])
    feats = np.array(feats)
    nov = np.array([0.0] + [float(np.abs(feats[i] - feats[i - 1]).sum()) for i in range(1, n)])
    marks, last = [], -min_gap
    thr = float(np.percentile(nov, 92))
    for i in range(2, n - 2):
        if nov[i] >= thr and nov[i] == nov[max(0, i - 3):i + 4].max() and i - last >= min_gap:
            marks.append(float(i))
            last = i
    return marks


def main():
    ref = json.load(open(AUDIO / "referencia.json", encoding="utf-8"))
    blocos_p = ROOT / "content" / "curadoria" / "build" / "blocos.json"
    blocos = json.load(open(blocos_p, encoding="utf-8")) if blocos_p.exists() else {}
    pecas_blk = blocos.get("pecas", {})
    out = {"_doc": ("Decomposição pedagógica das gravações. Solo: notas=[t0,dur,midi SOANDO], "
                    "frases=[{t0,t1,notas,grave,agudo}] separadas pelas RESPIRAÇÕES (respire onde o "
                    "modelo respira), legos=[{lego,t0,t1,acerto}] = onde cada trecho-que-se-repete "
                    "(blocos.json) acontece na gravação. Banda: bpm + marcos de seção.")}

    for pid, files in sorted(ref.get("pecas", {}).items()):
        legos = (pecas_blk.get(pid) or {}).get("legos") or []
        for a in files:
            f = a["f"]
            x, sr = load_mono(AUDIO / f)
            track = yin_track(x, sr)
            notes = notes_of(track)
            phr = phrases_of(notes)
            occ = match_legos(notes, legos)
            bpm = tempo_of(x, sr)
            while bpm > 140:                                  # solo não é dobrado: 188→94
                bpm = round(bpm / 2)
            entry = {
                "peca": pid,
                "bpm": bpm,
                "notas": [[t, d, m] for t, d, m in notes],
                "frases": [{"t0": round(t0, 2), "t1": round(t1, 2), "notas": len(ph),
                            "grave": nome(min(m for _, _, m in ph)),
                            "agudo": nome(max(m for _, _, m in ph))}
                           for t0, t1, ph in phr],
                "legos": [{"lego": li, "t0": t0, "t1": t1, "acerto": h} for li, t0, t1, h in occ],
            }
            out[f] = entry
            print(f"{f}: {len(notes)} notas · {len(phr)} frases · {len(occ)} ocorrências de lego · ~{entry['bpm']} BPM")

    for a in ref.get("ensaio", []):
        f = a["f"]
        x, sr = load_mono(AUDIO / f)
        marks = sections_of(x, sr)
        out[f] = {"bpm": tempo_of(x, sr), "secoes": [{"t0": m} for m in marks]}
        print(f"{f}: ~{out[f]['bpm']} BPM · {len(marks)} marcos de seção")

    json.dump(out, open(AUDIO / "segmentos.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"→ {AUDIO / 'segmentos.json'}")


if __name__ == "__main__":
    main()
