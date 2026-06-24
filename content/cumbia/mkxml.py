#!/usr/bin/env python3
"""Helper: lista de notas (DSL curta) -> MusicXML da parte ESCRITA do trompete Bb.

Gera MusicXML que o pipeline existente (build_notes/build_abc) já entende: divisões,
armadura (fifths), compasso, <transpose chromatic=-2> (Bb->concerto) e, por nota,
<duration>, <pitch>, <tie> e <notations><slur>. A transcrição vira só uma lista de
compassos com tokens — o XML correto fica por conta daqui.

DSL de token (unidade = 1/16; semínima = 4):
  "G4:4"      Sol4, semínima
  "F#4:2"     Fá#4, colcheia        (acidente: # ou b ; ex.: "Bb3:2")
  "z:2"       pausa de colcheia
  "(G4:1"     inicia ligadura de expressão (slur) nesta nota
  "c5:4)"     fecha a ligadura nesta nota
  "A4:4-"     ligadura de prolongamento (tie) para a próxima (mesma altura)
Marcadores podem combinar: "(F#4:1", "G4:2)", "B4:8-".
"""
import re

STEP_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
TYPE = {1: "16th", 2: "eighth", 3: "eighth", 4: "quarter", 6: "quarter",
        8: "half", 12: "half", 16: "whole"}
DOT = {3, 6, 12}   # durações pontuadas (colcheia pont., semínima pont., mínima pont.)


def parse_token(tok):
    """'(F#4:2)' -> dict(rest?, step, alter, octave, dur, slur_start, slur_stop, tie)."""
    slur_start = tok.startswith("(")
    t = tok[1:] if slur_start else tok
    slur_stop = t.endswith(")")
    if slur_stop:
        t = t[:-1]
    tie = t.endswith("-")
    if tie:
        t = t[:-1]
    body, dur = t.split(":")
    dur = int(dur)
    if body == "z":
        return dict(rest=True, dur=dur, slur_start=False, slur_stop=False, tie=False)
    m = re.match(r"^([A-Ga-g])([#b]?)(\d)$", body)
    if not m:
        raise ValueError(f"token inválido: {tok}")
    step, acc, octv = m.group(1).upper(), m.group(2), int(m.group(3))
    alter = 1 if acc == "#" else (-1 if acc == "b" else 0)
    return dict(rest=False, step=step, alter=alter, octave=octv, dur=dur,
                slur_start=slur_start, slur_stop=slur_stop, tie=tie)


def note_xml(n, divisions=4):
    dur = n["dur"] * (divisions // 4)
    typ = TYPE.get(n["dur"], "quarter")
    dotx = "<dot/>" if n["dur"] in DOT else ""
    if n["rest"]:
        return f'      <note><rest/><duration>{dur}</duration><type>{typ}</type>{dotx}</note>'
    acc = "" if n["alter"] == 0 else f"<alter>{n['alter']}</alter>"
    tie_snd = '<tie type="start"/>' if n["tie"] else ""
    notations = []
    if n["tie"]:
        notations.append('<tied type="start"/>')
    if n["slur_start"]:
        notations.append('<slur type="start" number="1"/>')
    if n["slur_stop"]:
        notations.append('<slur type="stop" number="1"/>')
    notx = f"<notations>{''.join(notations)}</notations>" if notations else ""
    return (f'      <note><pitch><step>{n["step"]}</step>{acc}<octave>{n["octave"]}</octave></pitch>'
            f'<duration>{dur}</duration>{tie_snd}<type>{typ}</type>{dotx}{notx}</note>')


def build(measures, fifths, beats, beat_type, divisions=4, transpose=-2):
    """measures: lista de listas de tokens. Retorna string MusicXML."""
    head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
            '"http://www.musicxml.org/dtds/partwise.dtd">\n'
            '<score-partwise version="4.0"><part-list><score-part id="P1">'
            '<part-name>Bb Trumpet</part-name></score-part></part-list><part id="P1">\n')
    body = []
    for i, toks in enumerate(measures, 1):
        attrs = ""
        if i == 1:
            attrs = (f'<attributes><divisions>{divisions}</divisions>'
                     f'<key><fifths>{fifths}</fifths></key>'
                     f'<time><beats>{beats}</beats><beat-type>{beat_type}</beat-type></time>'
                     f'<clef><sign>G</sign><line>2</line></clef>'
                     f'<transpose><chromatic>{transpose}</chromatic></transpose></attributes>')
        notes = "\n".join(note_xml(parse_token(t), divisions) for t in toks)
        body.append(f'    <measure number="{i}">{attrs}\n{notes}\n    </measure>')
    return head + "\n".join(body) + "\n</part></score-partwise>\n"


if __name__ == "__main__":
    # auto-teste: um riff de 2 compassos em Dó escrito (Sib concerto)
    xml = build([["(G4:2", "A4:2", "B4:2", "c5:2)"], ["(B4:2", "A4:2)", "G4:4"]], fifths=0, beats=2, beat_type=4)
    print(xml[:400])
    assert "<transpose><chromatic>-2" in xml and "<slur type=\"start\"" in xml
    print("\nok mkxml")
