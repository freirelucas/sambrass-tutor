#!/usr/bin/env python3
"""Converte as notas (MusicXML em content/notes/**) para ABC, para o player do app
(abcjs: renderiza partitura + toca MIDI + cursor). Saída: content/notes_abc.json
{ id: "<abc>" } — peças (sb-NNN) e células (cell-CX).

ABC em tom ESCRITO (parte do trompete) — é o que o músico lê e toca junto.
Uso: python3 content/build_abc.py
"""
import json, sys, pathlib, glob, collections
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


def units_of(beats, L=16):
    """beats (semínima=1) -> nº de unidades 1/L (1/16)."""
    return max(1, round(beats * (L / 4)))

# comprimentos (em 1/16) que o ABC desenha como UMA cabeça de nota (semínima, pontuadas, etc.)
REPR = [16, 12, 8, 6, 4, 3, 2, 1]

def split_units(u):
    """Quebra uma duração em pedaços representáveis (ex.: 5 -> [4,1], 7 -> [6,1]).
    No corpo, viram a mesma nota LIGADA — evita 'Duration not representable' do abcjs
    e escreve a ligadura/ponto que o OMR deixou implícito na duração."""
    out = []
    for r in REPR:
        while u >= r:
            out.append(r); u -= r
    return out or [1]

def len_str(u):
    return "" if u == 1 else str(u)


def to_abc(events, fifths, meter, title, idx=1):
    head = f"X:{idx}\nT:{title}\nM:{meter}\nL:1/16\nQ:1/4=92\nK:{fifths_to_key(fifths)}\n"
    body, measure, eff = [], None, keysig_acc(fifths)
    depth = 0   # ligaduras (slurs) abertas — fechamos sempre balanceado (OMR pode vir torto)

    def wrap(e, force_units=None):
        nonlocal depth
        opens = int(e.get("slur_start", 0) or 0)
        depth += opens
        closes = min(int(e.get("slur_stop", 0) or 0), depth)
        depth -= closes
        return " " + "(" * opens + note_token(e, fifths, eff, force_units) + ")" * closes

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
            for t in trip: body.append(wrap(t, force_units=2))
            i += 3; continue
        body.append(wrap(e))
        i += 1
    return head + "".join(body) + ")" * depth + " |]\n"   # fecha ligaduras penduradas


def note_token(e, fifths, eff, force_units=None):
    """Token ABC 'nu' da nota (sem espaço à esquerda nem slur — quem envolve é o wrap).
    Durações não representáveis (5/16, 7/16…) viram pedaços LIGADOS, preservando o tempo."""
    if e.get("rest"):
        if force_units:
            return "z" + len_str(force_units)
        return " ".join("z" + len_str(s) for s in split_units(units_of(e.get("dur_beats", 1))))
    L, acc, ch = abc_pitch(e["written_midi"], fifths)
    head = ""
    if acc != eff.get(L, "="):
        head = acc; eff[L] = acc
    tie = "-" if e.get("tie") == "start" else ""
    if force_units:
        return head + ch + len_str(force_units) + tie
    segs = split_units(units_of(e.get("dur_beats", 1)))    # acidente só na 1ª; resto é a mesma nota ligada
    parts = [head + ch + len_str(segs[0])] + [ch + len_str(s) for s in segs[1:]]
    return "-".join(parts) + tie


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
    quality = {}   # por peça: rascunho (OMR cru) < dedos (fusão) < conferida (à mão)
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
        if stem.startswith("sb-"):
            quality[stem] = "rascunho"
    # fusão dedos+OMR (provisória, melhor que o OMR cru): content/notes_auto/*.abc
    for f in sorted(glob.glob(str(CONTENT / "notes_auto" / "*.abc"))):
        stem = pathlib.Path(f).stem
        out[stem] = pathlib.Path(f).read_text(encoding="utf-8")
        quality[stem] = "dedos"
    # melodias conferidas à mão (vencem tudo): content/notes_manual/*.abc
    verified = []
    for f in sorted(glob.glob(str(CONTENT / "notes_manual" / "*.abc"))):
        stem = pathlib.Path(f).stem
        out[stem] = pathlib.Path(f).read_text(encoding="utf-8")
        quality[stem] = "conferida"; verified.append(stem)
    out["_verified"] = verified
    out["_quality"] = quality
    json.dump(out, open(CONTENT / "notes_abc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(quality, open(CONTENT / "notes_quality.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    tiers = collections.Counter(quality.values())
    n_pieces = sum(1 for k in out if k.startswith("sb-"))
    print(f"ABC gerado: {n_pieces} peças → notes_abc.json · tiers {dict(tiers)} · conferidas: {verified}")


if __name__ == "__main__":
    main()
