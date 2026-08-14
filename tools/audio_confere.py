#!/usr/bin/env python3
"""Confere a partitura transcrita CONTRA uma gravação real (validação cruzada).

As gravações em app/audio/ (modelo tocado no trompete pela banda) são a única
referência INDEPENDENTE do dado: o "ouvir o modelo" do app é sintetizado do
mesmo ABC que está sendo conferido — se o ABC está uma 8ª acima (caso cu-005),
o modelo sintetizado também está, e ninguém percebe olhando só o app.

O que faz, por peça com gravação:
  1. Extrai o contorno de alturas da gravação (YIN simplificado, monofônico).
  2. Compara com os eventos do notes_manual/cu-NNN.abc (concert = escrito − 2):
     a. DESVIO DE OITAVA — mediana da gravação vs mediana do ABC: |Δ| ≥ 7
        semitons denuncia oitava global errada (teria pego o cu-005 na hora).
     b. CASAMENTO MELÓDICO — n-grams de intervalos (invariante a transposição):
        score baixo = a gravação não é desta peça, ou a transcrição diverge.
  3. Imprime um relatório; código de saída 1 se houver desvio de oitava.

Ferramenta LOCAL (precisa de numpy + soundfile p/ decodificar .ogg) — não roda
no CI. Uso:
    pip install numpy soundfile
    python3 tools/audio_confere.py                      # todas as peças com gravação
    python3 tools/audio_confere.py cu-011               # uma peça
"""
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "content" / "cumbia"))
from abc_events import events_from_abc  # noqa: E402

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    sys.exit("precisa de: pip install numpy soundfile")

AUDIO = ROOT / "app" / "audio"
MANUAL = ROOT / "content" / "cumbia" / "notes_manual"
NAMES = ["Dó", "Dó#", "Ré", "Ré#", "Mi", "Fá", "Fá#", "Sol", "Sol#", "Lá", "Lá#", "Si"]


def nome(m):
    return f"{NAMES[m % 12]}{m // 12 - 1}"


def yin_track(x, sr, fmin=100, fmax=1200, frame=2048, hop=512, thresh=0.15):
    """f0 por frame (Hz; 0 = silêncio). YIN clássico com limiar absoluto."""
    tmin, tmax = int(sr / fmax), int(sr / fmin)
    out = []
    for i in range(0, len(x) - frame - tmax, hop):
        w = x[i:i + frame]
        if np.sqrt((w ** 2).mean()) < 0.01:
            out.append(0.0)
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
        out.append(sr / tau)
    return out


def audio_notes(path):
    """Sequência de notas MIDI (concert, como soa) segmentada da gravação."""
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    step = max(1, sr // 16000)                     # ~16 kHz basta p/ trompete
    x = x[::step]
    track = yin_track(np.asarray(x, dtype=float), sr // step)
    midis = [int(round(69 + 12 * np.log2(f / 440))) if f > 0 else 0 for f in track]
    notes, cur, count = [], None, 0
    for m in midis:
        if m == cur:
            count += 1
        else:
            if cur and count >= 3:                 # ≥ ~100 ms = nota de verdade
                notes.append(cur)
            cur, count = m, 1
    if cur and count >= 3:
        notes.append(cur)
    return [m for m in notes if m > 45]            # tira sub-graves de respiração/ruído


def intervals(seq):
    return [max(-12, min(12, b - a)) for a, b in zip(seq, seq[1:]) if b != a]


def ngrams(s, n):
    return set(tuple(s[i:i + n]) for i in range(len(s) - n + 1))


def match_score(a, b):
    """Fração de n-grams (3 e 4) de intervalos compartilhados — 0..3."""
    s = 0.0
    for n, w in ((3, 1.0), (4, 2.0)):
        ga, gb = ngrams(a, n), ngrams(b, n)
        if ga and gb:
            s += w * len(ga & gb) / min(len(ga), len(gb))
    return s


def abc_of(pid):
    """ABC do tema: notes_manual (conferido) ou, p/ as peças DSL, o abc do build."""
    p = MANUAL / f"{pid}.abc"
    if p.exists():
        return p.read_text(encoding="utf-8")
    build = ROOT / "content" / "cumbia" / "build" / "abc.json"
    if build.exists():
        return json.load(open(build, encoding="utf-8")).get(pid)
    return None


def confere(pid, files):
    abc = abc_of(pid)
    if not abc:
        print(f"  {pid}: sem ABC (rode build_cumbia.py) — pulei")
        return True
    ev = [e["concert_midi"] for e in events_from_abc(abc) if "concert_midi" in e]
    if not ev:
        return True
    med_abc = statistics.median(ev)
    ok = True
    for a in files:
        f, conf = a["f"], a.get("conf", False)
        seq = audio_notes(AUDIO / f)
        if len(seq) < 8:
            print(f"  {pid} × {f}: gravação curta/ruidosa demais ({len(seq)} notas) — pulei")
            continue
        med_au = statistics.median(seq)
        delta = med_au - med_abc
        score = match_score(intervals(seq), intervals(ev))
        flag = "✓" if abs(delta) < 7 else ("🔴 OITAVA?" if conf else "≠ (não gateia: 'a confirmar')")
        print(f"  {pid} × {f}: mediana gravação {nome(round(med_au))} vs ABC {nome(round(med_abc))} "
              f"(Δ {delta:+.0f} st) {flag} · casamento melódico {score:.2f}"
              + ("  ⚠ score baixo — gravação de outra peça/voz?" if score < 0.15 else ""))
        if conf and abs(delta) >= 7:
            ok = False                             # só gravação marcada "conf" reprova o build
    return ok


def main():
    ref = json.load(open(AUDIO / "referencia.json", encoding="utf-8"))
    só = sys.argv[1] if len(sys.argv) > 1 else None
    ok = True
    for pid, files in sorted(ref.get("pecas", {}).items()):
        if só and pid != só:
            continue
        ok = confere(pid, files) and ok
    print("--- ok: partitura e gravação na mesma oitava ---" if ok
          else "--- 🔴 há desvio de oitava entre partitura e gravação ---")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
