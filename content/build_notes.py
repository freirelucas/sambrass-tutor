#!/usr/bin/env python3
"""Compila MusicXML (notas ESCRITAS em Bb + <transpose>) para JSON de eventos.

A fonte canônica das notas é o MusicXML fiel ao PDF (parte escrita do trompete,
em Si bemol). Daqui derivamos, sem reescrever nada:
  - tom de CONCERTO (sounding = escrito + transpose.chromatic, que é -2 p/ Bb);
  - DIGITAÇÃO do trompete (mapa em instruments/trumpet_bb.json, por nota escrita);
  - durações em tempos (semínima = 1), seção e compasso.
O JSON de eventos é o formato de RUNTIME do app (tocar, transpor p/ outros
instrumentos, comparar com o microfone, desenhar e dar highlight na nota atual).

Uso:  python3 content/build_notes.py [arquivo.musicxml ...]
Sem argumentos, compila todos os content/notes/*.musicxml -> content/notes_runtime/.
"""
import sys, json, pathlib, glob
import xml.etree.ElementTree as ET

CONTENT = pathlib.Path(__file__).resolve().parent
OUT = CONTENT / "notes_runtime"
STEP_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
TYPE_BEATS = {"whole": 4, "half": 2, "quarter": 1, "eighth": 0.5,
              "16th": 0.25, "32nd": 0.125}


def name(midi, table):
    return f"{table[midi % 12]}{midi // 12 - 1}"


def load_fingering():
    inst = json.load(open(CONTENT / "instruments" / "trumpet_bb.json", encoding="utf-8"))
    return inst["fingering"], inst["transpose_semitones"]


def compile_file(path, fingering, inst_transpose):
    root = ET.parse(path).getroot()
    divisions = 1
    chromatic = 0
    events = []
    for measure in root.iter("measure"):
        mnum = int(measure.get("number", 0))
        attr = measure.find("attributes")
        if attr is not None:
            if attr.find("divisions") is not None:
                divisions = int(attr.findtext("divisions"))
            tr = attr.find("transpose")
            if tr is not None:
                chromatic = int(tr.findtext("chromatic", "0"))
        for note in measure.findall("note"):
            dur = int(note.findtext("duration", "0"))
            beats = round(dur / divisions, 4)
            if note.find("rest") is not None:
                events.append({"measure": mnum, "rest": True, "dur_beats": beats})
                continue
            p = note.find("pitch")
            step = p.findtext("step")
            octave = int(p.findtext("octave"))
            alter = int(p.findtext("alter", "0"))
            written = (octave + 1) * 12 + STEP_SEMI[step] + alter
            concert = written + chromatic
            wname = name(written, SHARP)  # nome p/ casar com o mapa de digitação
            events.append({
                "measure": mnum,
                "written_midi": written,
                "written_name": (step + ("b" if alter < 0 else "#" * alter) + str(octave)),
                "concert_midi": concert,
                "concert_name": name(concert, FLAT),
                "fingering": fingering.get(wname),
                "dur_beats": beats,
                "tie": note.find("tie").get("type") if note.find("tie") is not None else None,
            })
    if chromatic != -inst_transpose:
        print(f"  aviso: transpose {chromatic} difere do esperado {-inst_transpose} (Bb) em {path.name}")
    return {"source": path.name, "transpose_chromatic": chromatic, "events": events}


def main():
    fingering, inst_transpose = load_fingering()
    args = sys.argv[1:]
    files = [pathlib.Path(a) for a in args] if args else \
        [pathlib.Path(p) for p in sorted(glob.glob(str(CONTENT / "notes" / "**" / "*.musicxml"), recursive=True))]
    if not files:
        sys.exit("nenhum .musicxml em content/notes/")
    OUT.mkdir(exist_ok=True)
    for f in files:
        data = compile_file(f, fingering, inst_transpose)
        out = OUT / (f.stem + ".json")
        json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        notes = [e for e in data["events"] if "written_midi" in e]
        print(f"{f.name}: {len(data['events'])} eventos ({len(notes)} notas) "
              f"transpose={data['transpose_chromatic']} → {out.name}")
        for e in notes[:6]:
            print(f"    escrito {e['written_name']:4} (dedo {e['fingering'] or '-':>3}) "
                  f"→ soa {e['concert_name']:4}  [{e['dur_beats']} tempo(s)]")


if __name__ == "__main__":
    main()
