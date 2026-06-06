#!/usr/bin/env python3
"""Gera os snippets das células rítmicas C1–C7 como MusicXML (Fase 2 — 'célula do dia').

Conteúdo EXATO e genérico (a rítmica definida em cells.json, sem direito autoral):
cada célula vira um compasso 2/4 com o ritmo tocado na tônica (Fá4 escrito = Mi♭4
concerto), pronto para loop com metrônomo. Sai em content/notes/cell-CX.musicxml,
que o build_notes.py compila para JSON de eventos como qualquer peça.

Uso:  python3 content/build_snippets.py  &&  python3 content/build_notes.py
divisions=12 (semínima=12; colcheia=6; semicolcheia=3; colcheia-de-tercina=4).
"""
import pathlib

CONTENT = pathlib.Path(__file__).resolve().parent
NOTES = CONTENT / "notes"
DIV = 12

# (duração, tipo, pontuada?, pausa?, tercina?) — uma volta da célula preenchendo 2/4.
CELES = {
    "C1": [(6, "eighth", 0, 0, 0)] * 4,
    "C2": [(6, "eighth", 0, 0, 0), (12, "quarter", 0, 0, 0), (6, "eighth", 0, 0, 0)],
    "C3": [(9, "eighth", 1, 0, 0), (3, "16th", 0, 0, 0)] * 2,
    "C4": [(3, "16th", 0, 0, 0)] * 8,
    "C5": [(4, "eighth", 0, 0, 1)] * 6,                       # 2 tercinas
    "C6": [(6, "eighth", 0, 1, 0), (6, "eighth", 0, 0, 0)] * 2,  # contratempo
    "C7": [(6, "eighth", 0, 0, 0), (18, "quarter", 1, 0, 0)],  # anacruse + nota longa
}
NOMES = {"C1": "colcheias", "C2": "síncope", "C3": "colcheia pontuada + semi",
         "C4": "4 semicolcheias", "C5": "tercina", "C6": "contratempo", "C7": "anacruse"}


def note_xml(dur, typ, dot, rest, trip, idx, total):
    body = "<rest/>" if rest else "<pitch><step>F</step><octave>4</octave></pitch>"
    dotx = "<dot/>" if dot else ""
    tm = "<time-modification><actual-notes>3</actual-notes><normal-notes>2</normal-notes></time-modification>" if trip else ""
    notations = ""
    if trip:  # marca início/fim de cada grupo de tercina (a cada 3)
        if idx % 3 == 0:
            notations = '<notations><tuplet type="start"/></notations>'
        elif idx % 3 == 2:
            notations = '<notations><tuplet type="stop"/></notations>'
    return (f'<note>{body}<duration>{dur}</duration><voice>1</voice>'
            f'<type>{typ}</type>{dotx}{tm}{notations}</note>')


def build(cid):
    notes = CELES[cid]
    notes_xml = "".join(note_xml(*n, i, len(notes)) for i, n in enumerate(notes))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<!-- Snippet da célula {cid} ({NOMES[cid]}). Ritmo na tônica (Fá4 escrito). Loop p/ metrônomo. -->
<score-partwise version="4.0">
  <work><work-title>Célula {cid} — {NOMES[cid]}</work-title></work>
  <part-list><score-part id="P1"><part-name>Trompete Bb</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>{DIV}</divisions><key><fifths>-1</fifths></key>
        <time><beats>2</beats><beat-type>4</beat-type></time>
        <clef><sign>G</sign><line>2</line></clef>
        <transpose><diatonic>-1</diatonic><chromatic>-2</chromatic></transpose></attributes>
      {notes_xml}
    </measure>
  </part>
</score-partwise>
'''


def main():
    (NOTES / "cells").mkdir(parents=True, exist_ok=True)
    for cid in CELES:
        (NOTES / "cells" / f"cell-{cid}.musicxml").write_text(build(cid), encoding="utf-8")
    print(f"gerados {len(CELES)} snippets de célula em {NOTES/'cells'}")


if __name__ == "__main__":
    main()
