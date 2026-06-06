#!/usr/bin/env python3
"""Fase 0 — mescla OMR + catálogo: notas/ritmo do Audiveris + ARMADURA do catálogo.

Para cada omr/out/sb-NNN.mxl: força a armadura escrita esperada (do tom de concerto
catalogado) e injeta <transpose -2> (parte Bb → concerto derivável). Grava
content/notes/omr/sb-NNN.musicxml (PROVISÓRIO — notas do OMR podem ter erros; o tom
fica correto). Depois, build_notes.py compila para JSON de eventos.

Uso: python3 content/omr_merge.py  &&  python3 content/build_notes.py
"""
import zipfile, sys, pathlib, glob
import xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "curadoria"))
from lib import load_pieces, PC, ROOT
REPO = ROOT.parent
OUTDIR = ROOT / "notes" / "omr"
FIFTHS = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 5: -1, 10: -2, 3: -3, 8: -4, 1: -5}


def expected_fifths(concert):
    return FIFTHS[(PC[concert] + 2) % 12]


def fix_attributes(root, fifths):
    a = root.find(".//attributes")
    if a is None:
        return False
    # armadura: cria/ajusta key/fifths
    key = a.find("key")
    if key is None:
        key = ET.Element("key")
        div = a.find("divisions")
        a.insert(list(a).index(div) + 1 if div is not None else 0, key)
    f = key.find("fifths")
    if f is None:
        f = ET.SubElement(key, "fifths")
    f.text = str(fifths)
    # transpose -2 (Bb)
    if a.find("transpose") is None:
        tr = ET.SubElement(a, "transpose")
        ET.SubElement(tr, "diatonic").text = "-1"
        ET.SubElement(tr, "chromatic").text = "-2"
    return True


def main():
    cat = {p["num"]: p for p in load_pieces()}
    files = sorted(glob.glob(str(REPO / "omr" / "out" / "sb-*.mxl")))
    if not files:
        sys.exit("sem .mxl em omr/out/ (extraia do branch omr/audiveris-raw)")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    n = forced = 0
    for fpath in files:
        num = int(pathlib.Path(fpath).stem.split("-")[1])
        p = cat.get(num)
        if not p:
            continue
        z = zipfile.ZipFile(fpath)
        member = [m for m in z.namelist() if not m.startswith("META-INF") and m.endswith(".xml")][0]
        root = ET.fromstring(z.read(member))
        ef = expected_fifths(p["key_concert"])
        cur = root.findtext(".//attributes/key/fifths")
        if str(cur) != str(ef):
            forced += 1
        fix_attributes(root, ef)
        header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                  f'<!-- OMR Audiveris + tom do catálogo (PROVISÓRIO; notas a conferir). '
                  f'Tom escrito = {ef} acidentes; transpose -2. -->\n')
        (OUTDIR / f"sb-{num:03d}.musicxml").write_text(header + ET.tostring(root, encoding="unicode"), encoding="utf-8")
        n += 1
    print(f"mescladas {n} peças → {OUTDIR} (armadura corrigida do catálogo em {forced})")


if __name__ == "__main__":
    main()
