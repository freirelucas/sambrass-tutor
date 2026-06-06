#!/usr/bin/env python3
"""Converte as notas (MusicXML em content/notes/**) para ABC, para o player do app
(abcjs: renderiza partitura + toca MIDI + cursor). Saída: content/notes_abc.json
{ id: "<abc>" } — peças (sb-NNN) e células (cell-CX).

ABC em tom ESCRITO (parte do trompete) — é o que o músico lê e toca junto.
Uso: python3 content/build_abc.py
"""
import json, sys, pathlib, glob
import xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_notes import compile_file, load_fingering, CONTENT
sys.path.insert(0, str(CONTENT / "curadoria"))
from lib import load_pieces

SHARP_NAMES = ["C", "C", "D", "D", "E", "F", "F", "G", "G", "A", "A", "B"]
SHARP_ACC   = ["=", "^", "=", "^", "=", "=", "^", "=", "^", "=", "^", "="]
FLAT_NAMES  = ["C", "D", "D", "E", "E", "F", "G", "G", "A", "A", "B", "B"]
FLAT_ACC    = ["=", "_", "=", "_", "=", "=", "_", "=", "_", "=", "_", "="]
SHARP_ORDER = ["F", "C", "G", "D", "A", "E", "B"]
FLAT_ORDER  = ["B", "E", "A", "D", "G", "C", "F"]


def keysig_acc(fifths):
    """letra -> acidente da armadura ('^','_' ou '=')."""
    d = {L: "=" for L in "ABCDEFG"}
    if fifths > 0:
        for L in SHARP_ORDER[:fifths]: d[L] = "^"
    elif fifths < 0:
        for L in FLAT_ORDER[:-fifths]: d[L] = "_"
    return d


def abc_pitch(midi, fifths):
    pc = midi % 12
    if fifths >= 0:
        L, acc = SHARP_NAMES[pc], SHARP_ACC[pc]
    else:
        L, acc = FLAT_NAMES[pc], FLAT_ACC[pc]
    octave = midi // 12 - 1
    if octave >= 5:
        ch = L.lower() + "'" * (octave - 5)
    else:
        ch = L + "," * (4 - octave)
    return L, acc, ch


def dur_token(beats, L=16):
    """beats (semínima=1) -> comprimento ABC com unidade 1/L (1/16)."""
    units = round(beats * (L / 4))
    return str(units) if units != 1 else ""


def to_abc(events, fifths, meter, title, idx=1):
    head = f"X:{idx}\nT:{title}\nM:{meter}\nL:1/16\nQ:1/4=96\nK:{fifths_to_key(fifths)}\n"
    body, measure, eff = [], None, keysig_acc(fifths)
    i, evs = 0, events
    while i < len(evs):
        e = evs[i]
        if e.get("measure") != measure:
            if measure is not None: body.append(" |")
            measure = e.get("measure"); eff = keysig_acc(fifths)
        # tercina: 3 notas seguidas ~0.333 tempo
        trip = [evs[j] for j in range(i, min(i + 3, len(evs)))]
        if len(trip) == 3 and all(abs(t.get("dur_beats", 0) - 1 / 3) < 0.04 for t in trip) \
                and all(t.get("measure") == measure for t in trip):
            body.append(" (3")
            for t in trip: body.append(note_token(t, fifths, eff, force_units=2))
            i += 3; continue
        body.append(note_token(e, fifths, eff))
        i += 1
    return head + "".join(body) + " |]\n"


def note_token(e, fifths, eff, force_units=None):
    beats = e.get("dur_beats", 1)
    length = str(force_units) if force_units else dur_token(beats)
    if e.get("rest"):
        return " z" + length
    L, acc, ch = abc_pitch(e["written_midi"], fifths)
    tok = ""
    if acc != eff.get(L, "="):
        tok = acc; eff[L] = acc
    tie = "-" if e.get("tie") == "start" else ""
    return " " + tok + ch + length + tie


def fifths_to_key(f):
    return {0: "C", 1: "G", 2: "D", 3: "A", 4: "E", 5: "B", 6: "F#",
            -1: "F", -2: "Bb", -3: "Eb", -4: "Ab", -5: "Db"}.get(f, "C")


def get_meta(path):
    root = ET.parse(path).getroot()
    fifths = root.findtext(".//attributes/key/fifths")
    beats = root.findtext(".//attributes/time/beats")
    bt = root.findtext(".//attributes/time/beat-type")
    return int(fifths) if fifths not in (None, "") else 0, f"{beats}/{bt}" if beats else "2/4"


def main():
    fingering, tr = load_fingering()
    cat = {p["num"]: p for p in load_pieces()}
    out = {}
    for p in sorted(glob.glob(str(CONTENT / "notes" / "**" / "*.musicxml"), recursive=True)):
        stem = pathlib.Path(p).stem
        if stem.startswith("_"): continue
        data = compile_file(pathlib.Path(p), fingering, tr)
        fifths, meter = get_meta(p)
        if stem.startswith("sb-"):
            num = int(stem.split("-")[1]); title = cat.get(num, {}).get("titulo", stem)
        else:
            title = stem
        out[stem] = to_abc(data["events"], fifths, meter, title)
    json.dump(out, open(CONTENT / "notes_abc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"ABC gerado: {len(out)} → content/notes_abc.json")
    print("amostra cell-C2:\n", out.get("cell-C2", "")[:160])


if __name__ == "__main__":
    main()
