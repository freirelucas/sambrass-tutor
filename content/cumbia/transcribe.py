#!/usr/bin/env python3
"""Catálogo das cumbias + transcrição PROVISÓRIA (tier 'rascunho') do TEMA via DSL → MusicXML.

Duas fontes de melodia convivem, decididas pelo campo `source` de cada peça:
  - source="dsl"    → transcrição à mão (lista `TUNES`); este script gera o cu-NNN.musicxml.
  - source="omr"    → vem do Audiveris (content/cumbia/omr_import.py, pós-CI); aqui é só metadata.
  - source="manual" → melodia conferida à mão em content/cumbia/notes_manual/cu-NNN.abc.
Este script é o DONO do catálogo content/cumbia/pieces_cumbia.json: mescla TUNES (dsl) +
CATALOG_EXTRA (omr/manual) sem se sobrescreverem. O omr_import.py só LÊ o catálogo.

Honestidade: as melodias DSL são leituras de melhor-esforço do riff/tema (a parte mais
repetida) das partituras em content/cumbia/pdfs/, fiéis ao tom/compasso/contorno — NÃO
conferidas nota a nota. Marcadas 'rascunho': o app mostra "⚠ melodia provisória" e o tutor
compara por classe de altura. Conferência à mão depois promove para 'conferida'.

Unidade dos tokens = 1/16 (semínima=4). Ver content/cumbia/mkxml.py para a DSL.
Saídas: content/notes/cumbia/cu-NNN.musicxml (só dsl) + content/cumbia/pieces_cumbia.json.
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mkxml

NOTES = pathlib.Path(__file__).resolve().parents[1] / "notes" / "cumbia"
HERE = pathlib.Path(__file__).resolve().parent

# tom de concerto → nº de acidentes da armadura ESCRITA do trompete Bb (igual a omr_merge/omr_check).
PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
      "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
FIFTHS = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 5: -1, 10: -2, 3: -3, 8: -4, 1: -5}


def expected_fifths(concert):
    return FIFTHS[(PC[concert] + 2) % 12]


# Cada cumbia DSL: tema principal (riff repetido) em tom ESCRITO de trompete Bb.
TUNES = [
    dict(num=1, titulo="Sonido Amazónico", compositor="Los Mirlos (arr. Lucca Ramalho)",
         pdf="Sonido Amazonico - Trompete Bb.pdf", source="dsl",
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
         pdf="A Patricia - Trompete Bb.pdf", source="dsl",
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
         pdf="Cumbia Del Monte Trompete.pdf", source="dsl",
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

# Cumbias vindas do Audiveris (OMR): só METADATA aqui; o cu-NNN.musicxml vem do omr_import.py
# (pós-CI). key_concert fica "" até o omr_check revelar a armadura lida pelo Audiveris — daí
# preenche-se e o omr_import injeta a armadura certa. compasso/compositor são melhor-esforço.
CATALOG_EXTRA = [
    # key_concert preenchido a partir da revisão do OMR (omr_check + conferência do render).
    # cu-013 e cu-017 ficam "" (NÃO importadas): Audiveris perdeu a armadura (013, peça em 4#)
    # / foto torta de papel (017, não-cumbia) — OMR não confiável, marcadas p/ re-OMR/conferência.
    dict(num=4,  titulo="Cariñito",                  compositor="Ángel Aníbal Rosado",       pdf="Carinito - Trompete Bb.pdf",                      source="omr", key_concert="C",  beats=4, beat_type=4, forma=["A", "B", "C", "D"]),
    dict(num=5,  titulo="Llorando se Fue",           compositor="Los Kjarkas (G. Hermosa)",  pdf="Llorando se Fue_Cumbias_TrompBb.pdf",             source="omr", key_concert="Bb", beats=4, beat_type=4, forma=["A", "B"]),
    dict(num=6,  titulo="Danza de los Mirlos",       compositor="Los Mirlos",                pdf="Danza de los mirlos - Trompete 1_melodia.pdf",    source="omr", key_concert="C",  beats=4, beat_type=4, forma=["A", "B"]),
    dict(num=7,  titulo="La Danza del Petrolero",    compositor="(cumbia colombiana)",       pdf="La Danza del Petrolero-Trumpet_in_Bb.pdf",        source="omr", key_concert="G",  beats=4, beat_type=4, forma=["A", "B"]),
    dict(num=8,  titulo="Cumbia Sobre el Mar",       compositor="Rafael Mendoza",            pdf="Cumbia Sobre EL Mar - Trompete.pdf",              source="omr", key_concert="F",  beats=4, beat_type=4, forma=["A", "B"]),
    dict(num=9,  titulo="El Diablo",                 compositor="(cumbia)",                  pdf="El Diablo - Trompete Bb.pdf",                     source="omr", key_concert="F",  beats=4, beat_type=4, forma=["A", "B"]),
    dict(num=10, titulo="Constelación",              compositor="Los Destellos (arr. Lucca Ramalho)", pdf="Constelacion - Trompete Bb.pdf",         source="omr", key_concert="Bb", beats=2, beat_type=4, forma=["A", "B", "C", "D"]),
    dict(num=11, titulo="Elsa",                      compositor="(cumbia)",                  pdf="Elsa - Trompete Bb.pdf",                          source="omr", key_concert="C",  beats=4, beat_type=4, forma=["A", "B"]),
    dict(num=12, titulo="Cumbia da Praia",           compositor="(cumbia)",                  pdf="Cumbia da Praia - Trumpet in Bb.pdf",             source="omr", key_concert="F",  beats=2, beat_type=4, forma=["A", "B"]),
    dict(num=13, titulo="Cumbia del Desierto",       compositor="Los Destellos",             pdf="Cumbia del Desierto_Cumbias_TrompBB1.pdf",        source="omr", key_concert="",   beats=2, beat_type=4, forma=["A", "B"]),
    dict(num=14, titulo="Lobos al Escape",           compositor="Los Mirlos",                pdf="Lobos al escape-Trumpet_in_Bb.pdf",               source="omr", key_concert="C",  beats=2, beat_type=4, forma=["A", "B"]),
    dict(num=15, titulo="Baião do Deserto",          compositor="(baião)",                   pdf="Baiao Do Deserto- Trompete.pdf",                  source="omr", key_concert="G",  beats=2, beat_type=4, forma=["A", "B"]),
    dict(num=16, titulo="Ya se ha Muerto mi Abuelo", compositor="(cumbia)",                  pdf="Ya se ha muerto mi abuelo - Trompete Bb.pdf",     source="omr", key_concert="F",  beats=2, beat_type=4, forma=["A", "B"]),
    dict(num=17, titulo="Yekermo Sew",               compositor="Mulatu Astatke",            pdf="Yekermo Sew - Trompete Bb.pdf",                   source="omr", key_concert="",   beats=4, beat_type=4, forma=["A", "B"]),
]


def _entry(d, source):
    """Entrada do catálogo (mesma forma p/ dsl e omr/manual)."""
    return dict(
        num=d["num"], id=f"cu-{d['num']:03d}", titulo=d["titulo"],
        compositor=d.get("compositor", ""), key_concert=d.get("key_concert", ""),
        compasso=f"{d.get('beats', 2)}/{d.get('beat_type', 4)}", forma=d.get("forma", []),
        pdf=d.get("pdf"), source=source,
        quality=("conferida" if source == "manual" else "rascunho"))


def main():
    NOTES.mkdir(parents=True, exist_ok=True)
    catalog = {"pieces": []}
    for t in TUNES:                                  # DSL: gera musicxml + entrada no catálogo
        ef = expected_fifths(t["key_concert"])
        assert t["fifths"] == ef, (f"cu-{t['num']:03d}: fifths={t['fifths']} não casa com "
                                    f"key_concert={t['key_concert']} (esperado {ef})")
        xml = mkxml.build(t["measures"], fifths=t["fifths"], beats=t["beats"], beat_type=t["beat_type"])
        out = NOTES / f"cu-{t['num']:03d}.musicxml"
        out.write_text(xml, encoding="utf-8")
        catalog["pieces"].append(_entry(t, t.get("source", "dsl")))
        print(f"  cu-{t['num']:03d}  {t['titulo']:24} {len(t['measures'])} compassos → {out.name}")
    for c in CATALOG_EXTRA:                          # OMR/manual: só entrada (musicxml vem de fora)
        catalog["pieces"].append(_entry(c, c.get("source", "omr")))
        print(f"  cu-{c['num']:03d}  {c['titulo']:24} (source={c.get('source','omr')}, pdf={c.get('pdf')})")
    catalog["pieces"].sort(key=lambda p: p["num"])
    json.dump(catalog, open(HERE / "pieces_cumbia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n_dsl = sum(1 for p in catalog["pieces"] if p["source"] == "dsl")
    print(f"catálogo: {len(catalog['pieces'])} cumbias ({n_dsl} dsl + {len(catalog['pieces'])-n_dsl} omr/manual) → pieces_cumbia.json")


if __name__ == "__main__":
    main()
