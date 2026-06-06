#!/usr/bin/env python3
"""Importa os MusicXML do Audiveris (omr/out/*.mxl) para a camada de notas.

O Audiveris lê a pauta ESCRITA (trompete Bb) e não marca transposição; injetamos
<transpose -2> para o concerto ficar derivável, e gravamos como
content/notes/omr/sb-NNN.musicxml (PROVISÓRIO — a conferir/corrigir). Depois,
build_notes.py compila tudo para JSON de eventos.

Uso: python3 content/omr_import.py  &&  python3 content/build_notes.py
"""
import zipfile, sys, pathlib, glob
import xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "curadoria"))
from lib import ROOT
REPO = ROOT.parent
OUTDIR = ROOT / "notes" / "omr"


def main():
    files = sorted(glob.glob(str(REPO / "omr" / "out" / "sb-*.mxl")))
    if not files:
        sys.exit("nenhum .mxl em omr/out/ (traga o branch omr/audiveris-raw)")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in files:
        stem = pathlib.Path(f).stem  # sb-NNN
        z = zipfile.ZipFile(f)
        member = [m for m in z.namelist() if not m.startswith("META-INF") and m.endswith(".xml")][0]
        root = ET.fromstring(z.read(member))
        att(root)  # injeta transpose no 1º attributes
        xml = ET.tostring(root, encoding="unicode")
        header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                  '<!-- OMR Audiveris (PROVISÓRIO — escrito Bb + transpose -2 injetado; conferir). -->\n')
        (OUTDIR / f"{stem}.musicxml").write_text(header + xml, encoding="utf-8")
        n += 1
    print(f"importados {n} MusicXML do OMR → {OUTDIR} (provisórios)")


def att(root):
    a = root.find(".//attributes")
    if a is None:
        return
    if a.find("transpose") is not None:
        return
    tr = ET.SubElement(a, "transpose")
    ET.SubElement(tr, "diatonic").text = "-1"
    ET.SubElement(tr, "chromatic").text = "-2"


if __name__ == "__main__":
    main()
