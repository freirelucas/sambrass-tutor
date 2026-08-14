#!/usr/bin/env python3
"""ABC (tom ESCRITO) → eventos compatíveis com build_notes/blocos.

Existe para re-derivar os "legos" (células, riff, cor) da melodia CONFERIDA à mão
(notes_manual/cu-*.abc), e não da transcrição OMR bruta. Eventos têm o mesmo schema
que compile_file: written_midi, concert_midi, dur_beats (em semínimas), measure, rest.

CONVENÇÃO DO PIPELINE: todo ABC (build_abc.to_abc e notes_manual/*.abc) está em tom
ESCRITO da parte de trompete Bb — é o que o músico lê (K:C p/ peça em Bb concert).
Logo o midi lido do .abc É o written_midi; concert = written − transpose (Bb = 2).
(Antes daqui assumia-se ABC concert e somava-se +2 — o que empurrava riff/perfil/
dificuldade um tom acima do real nas peças conferidas.)
"""
import re

_PCBASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_SHARPS = ["F", "C", "G", "D", "A", "E", "B"]
_FLATS = ["B", "E", "A", "D", "G", "C", "F"]
_FIFTHS_MAJ = {"C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6,
               "Gb": -6, "Db": -5, "Ab": -4, "Eb": -3, "Bb": -2, "F": -1}
_FIFTHS_MIN = {"A": 0, "E": 1, "B": 2, "F#": 3, "C#": 4, "G#": 5, "D#": 6,
               "Eb": -6, "Bb": -5, "F": -4, "C": -3, "G": -2, "D": -1}
_PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6,
       "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def _split_key(kfield):
    m = re.match(r"\s*([A-G][#b]?)\s*(m|min|maj|dor|mix|phr|lyd|loc|aeo|ion)?", kfield or "C")
    if not m:
        return "C", ""
    return m.group(1), (m.group(2) or "").lower()


def _keysig(kfield):
    tonic, mode = _split_key(kfield)
    minor = mode in ("m", "min", "aeo")
    fifths = (_FIFTHS_MIN if minor else _FIFTHS_MAJ).get(tonic, 0)
    acc = {}
    if fifths > 0:
        for L in _SHARPS[:fifths]:
            acc[L] = 1
    elif fifths < 0:
        for L in _FLATS[:-fifths]:
            acc[L] = -1
    return acc


def key_from_abc(abc, transpose=2):
    """pc CONCERT da tônica do campo K: (K: está em tom escrito → −transpose)."""
    for line in abc.splitlines():
        if line.strip().startswith("K:"):
            tonic, _ = _split_key(line.split(":", 1)[1])
            return (_PC.get(tonic, 0) - transpose) % 12
    return 0


def _parselen(s):
    s = s or ""
    if s == "":
        return 1.0
    if s == "/":
        return 0.5
    if s.startswith("/"):
        return 1.0 / int(s[1:])
    if "/" in s:
        a, b = s.split("/")
        return (int(a) if a else 1) / (int(b) if b else 2)
    return float(int(s))


_TOK = re.compile(r"""
    (?P<bar>\|\]|\|\||:\||\|:|\|)
  | (?P<trip>\(3)
  | (?P<rest>[zZx])(?P<rlen>\d*/?\d*)
  | (?P<acc>\^{1,2}|_{1,2}|=)?(?P<note>[A-Ga-g])(?P<oct>[,']*)(?P<len>\d*/?\d*)
  | (?P<other>.)
""", re.VERBOSE)


def events_from_abc(abc, transpose=2):
    head, body = {}, []
    for line in abc.splitlines():
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        m = re.match(r"^([A-Za-z]):(.*)$", line)
        if m and m.group(1) in "XTMLKQVWwsZIPNR":
            head[m.group(1)] = m.group(2).strip()
        else:
            body.append(line)
    try:
        ln, ld = head.get("L", "1/8").split("/")
        unit = (int(ln) / int(ld)) * 4                        # unidade em semínimas
    except Exception:
        unit = 0.5
    ksig = _keysig(head.get("K", "C"))
    events, measure = [], 1
    bar_acc = {}                                              # acidentes vigentes no compasso
    tie = False                                               # ligadura de valor pendente
    trip = 0                                                  # tercina "(3": próximas 3 notas valem 2/3
    for mt in _TOK.finditer(" ".join(body)):
        if mt.group("bar"):
            measure += 1
            bar_acc = {}
        elif mt.group("trip"):
            trip = 3
        elif mt.group("rest"):
            d = _parselen(mt.group("rlen")) * unit
            if trip:
                d *= 2 / 3
                trip -= 1
            events.append({"measure": measure, "dur_beats": round(d, 3), "rest": True})
        elif mt.group("note"):
            letter = mt.group("note")
            up = letter.upper()
            midi = 60 + _PCBASE[up] + (12 if letter.islower() else 0)
            for ch in mt.group("oct") or "":
                midi += 12 if ch == "'" else -12
            acc = mt.group("acc")
            if acc == "=":
                bar_acc[up] = 0
            elif acc:
                bar_acc[up] = acc.count("^") - acc.count("_")
            if up in bar_acc:
                midi += bar_acc[up]
            elif up in ksig:
                midi += ksig[up]
            dur = _parselen(mt.group("len")) * unit
            if trip:
                dur *= 2 / 3
                trip -= 1
            dur = round(dur, 3)
            if tie and events and events[-1].get("written_midi") == midi:   # ligadura: nota igual funde (1 ataque só)
                events[-1]["dur_beats"] = round(events[-1]["dur_beats"] + dur, 3)
            else:
                events.append({"measure": measure, "written_midi": midi, "concert_midi": midi - transpose, "dur_beats": dur})
            tie = False
        elif mt.group("other") == "-":                        # liga a próxima nota igual à anterior
            tie = True
    return events


if __name__ == "__main__":
    import sys, pathlib
    for p in sorted(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").glob("cu-*.abc")):
        ev = events_from_abc(p.read_text(encoding="utf-8"))
        notes = [e for e in ev if "concert_midi" in e]
        print(f"{p.stem}: {len(notes)} notas, K-pc={key_from_abc(p.read_text())}, "
              f"range concert {min(e['concert_midi'] for e in notes)}-{max(e['concert_midi'] for e in notes)}")
