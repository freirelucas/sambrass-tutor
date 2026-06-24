#!/usr/bin/env python3
"""Transcrição PROVISÓRIA (tier 'rascunho') do TEMA PRINCIPAL de cada cumbia → MusicXML.

Honestidade: são leituras de melhor-esforço do riff/tema (a parte mais repetida e
idiomática) das partituras em content/cumbia/pdfs/, fiéis ao tom/compasso/contorno —
NÃO conferidas nota a nota. Marcadas 'rascunho' (como o OMR do Sambrass): o app mostra
"⚠ melodia provisória" e o tutor compara por classe de altura (tolerante a oitava).
Conferência à mão depois promove para 'conferida' (content/notes_manual/cu-NNN.abc).

Unidade dos tokens = 1/16 (semínima=4). Ver content/cumbia/mkxml.py para a DSL.
Saídas: content/notes/cumbia/cu-NNN.musicxml + content/cumbia/pieces_cumbia.json.
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mkxml

NOTES = pathlib.Path(__file__).resolve().parents[1] / "notes" / "cumbia"
HERE = pathlib.Path(__file__).resolve().parent

# Cada cumbia: tema principal (riff repetido) em tom ESCRITO de trompete Bb.
TUNES = [
    dict(num=1, titulo="Sonido Amazónico", compositor="Los Mirlos (arr. Lucca Ramalho)",
         key_concert="Bb", fifths=0, beats=2, beat_type=4, forma=["A", "B", "C"],
         # A — frase lírica, colcheias; o gancho da cumbia amazônica (escrito em Dó)
         measures=[
             ["G4:2", "E4:2", "G4:2", "A4:2"],
             ["(G4:2", "E4:2)", "C4:4"],
             ["G4:2", "E4:2", "G4:2", "A4:2"],
             ["(c5:2", "B4:2)", "G4:4"],
             ["A4:2", "G4:2", "E4:2", "G4:2"],
             ["(A4:2", "G4:2)", "E4:4"],
             ["D4:2", "E4:2", "G4:2", "E4:2"],
             ["C4:4", "z:4"],
         ]),
    dict(num=2, titulo="A Patrícia", compositor="Los Destellos",
         key_concert="Bb", fifths=0, beats=2, beat_type=4, forma=["A", "B", "C"],
         # A — colcheias com tercina/galope; vira em torno de Sol–Dó (escrito em Dó)
         measures=[
             ["E4:2", "G4:2", "c5:2", "G4:2"],
             ["(A4:2", "G4:2)", "E4:4"],
             ["E4:2", "G4:2", "c5:2", "e5:2"],
             ["(d5:2", "c5:2)", "G4:4"],
             ["c5:2", "B4:2", "A4:2", "G4:2"],
             ["(A4:2", "G4:2)", "E4:4"],
             ["D4:2", "E4:2", "G4:2", "A4:2"],
             ["G4:4", "z:4"],
         ]),
    dict(num=3, titulo="Cumbia del Monte", compositor="(tradicional / arr. desconhecido)",
         key_concert="F", fifths=1, beats=2, beat_type=4, forma=["A", "B"],
         # A — motivo de semicolcheias subindo ao pico e descendo (escrito em Sol, 1#)
         measures=[
             ["z:2", "D4:2", "G4:1", "A4:1", "B4:1", "c5:1"],
             ["(d5:2", "B4:2)", "G4:4"],
             ["z:2", "D4:2", "G4:1", "A4:1", "B4:1", "c5:1"],
             ["(d5:2", "B4:2)", "G4:4"],
             ["B4:2", "c5:1", "d5:1", "e5:2", "d5:2"],
             ["(c5:2", "B4:2)", "A4:4"],
             ["G4:1", "A4:1", "B4:1", "c5:1", "d5:2", "B4:2"],
             ["G4:4", "z:4"],
         ]),
]


def main():
    NOTES.mkdir(parents=True, exist_ok=True)
    catalog = {"pieces": []}
    for t in TUNES:
        xml = mkxml.build(t["measures"], fifths=t["fifths"], beats=t["beats"], beat_type=t["beat_type"])
        out = NOTES / f"cu-{t['num']:03d}.musicxml"
        out.write_text(xml, encoding="utf-8")
        catalog["pieces"].append(dict(
            num=t["num"], id=f"cu-{t['num']:03d}", titulo=t["titulo"], compositor=t["compositor"],
            key_concert=t["key_concert"], compasso=f"{t['beats']}/{t['beat_type']}", forma=t["forma"],
            quality="rascunho"))
        print(f"  cu-{t['num']:03d}  {t['titulo']:22} {len(t['measures'])} compassos → {out.name}")
    json.dump(catalog, open(HERE / "pieces_cumbia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"catálogo: {len(catalog['pieces'])} cumbias → pieces_cumbia.json")


if __name__ == "__main__":
    main()
