#!/usr/bin/env python3
"""Importa a saída do Audiveris (omr/out/cu-NNN[-pK].mxl) → content/notes/cumbia/cu-NNN.musicxml.

Roda DEPOIS do workflow omr-cumbia.yml (que enche o branch omr/cumbia-raw):
    git fetch origin omr/cumbia-raw
    git checkout origin/omr/cumbia-raw -- omr/out   # ou baixe o artefato 'cumbia-musicxml'
    python3 content/cumbia/omr_import.py  &&  python3 content/cumbia/build_cumbia.py

Para cada cumbia `source=="omr"` do catálogo (content/cumbia/pieces_cumbia.json) com
`key_concert` PREENCHIDO (use o omr_check.py para descobrir e preencher antes):
  1. junta as páginas (cu-NNN.mxl ou cu-NNN-p1/p2…) em ordem;
  2. REDUZ à voz-líder (1ª <part>, voz 1, nota superior de acordes) — passo LOSSY, com aviso;
  3. injeta a armadura ESCRITA do catálogo + <transpose chromatic=-2> (igual ao omr_merge);
  4. grava cu-NNN.musicxml (PROVISÓRIO, tier 'rascunho' — notas a conferir).
NÃO toca nas cumbias source=="dsl" (cu-001..003) nem promove a 'conferida'.
"""
import zipfile, json, glob, pathlib, re, sys
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
NOTES = REPO / "content" / "notes" / "cumbia"
OUTRAW = REPO / "omr" / "out"
STEP_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
# tom de concerto → fifths da armadura ESCRITA (Bb), idêntico a omr_merge/omr_check/transcribe.
PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
      "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
FIFTHS = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 5: -1, 10: -2, 3: -3, 8: -4, 1: -5}


def expected_fifths(concert):
    return FIFTHS[(PC[concert] + 2) % 12]


def _midi(note):
    p = note.find("pitch")
    if p is None:
        return -1
    return (int(p.findtext("octave")) + 1) * 12 + STEP_SEMI[p.findtext("step")] + int(p.findtext("alter", "0"))


def _member_root(mxl_path):
    z = zipfile.ZipFile(mxl_path)
    name = [n for n in z.namelist() if not n.startswith("META-INF") and n.endswith(".xml")][0]
    return ET.fromstring(z.read(name))


def reduce_to_lead(root):
    """Mantém só a 1ª <part>; em cada compasso, só a voz 1 e a nota superior de acordes.
    LOSSY: descarta harmonia / 2ª voz. Retorna (part_element, n_notas_descartadas)."""
    parts = root.findall("part")
    if not parts:
        return None, 0
    keep = parts[0]
    for extra in parts[1:]:
        root.remove(extra)
    dropped = 0
    for measure in keep.findall("measure"):
        # cursores de tempo só fazem sentido com polifonia; numa linha única, fora.
        for tag in ("backup", "forward"):
            for el in measure.findall(tag):
                measure.remove(el)
        # 1) descarta vozes != 1 (Audiveris numera <voice>; ausência = voz 1)
        for n in measure.findall("note"):
            v = n.findtext("voice")
            if v is not None and v.strip() not in ("", "1"):
                measure.remove(n); dropped += 1
        # 2) colapsa acordes: grupo = nota sem <chord/> + seguintes com <chord/>; fica a + aguda
        groups, cur = [], []
        for n in measure.findall("note"):
            if n.find("chord") is not None and cur:
                cur.append(n)
            else:
                if cur:
                    groups.append(cur)
                cur = [n]
        if cur:
            groups.append(cur)
        for g in groups:
            if len(g) <= 1:
                continue
            top = max(g, key=_midi)
            for n in g:
                if n is not top:
                    measure.remove(n); dropped += 1
            ch = top.find("chord")          # a que sobrou vira nota simples
            if ch is not None:
                top.remove(ch)
    return keep, dropped


def concat_pages(paths):
    """Junta as páginas em ordem numérica; renumera os compassos sequencialmente.
    Retorna (root_score_partwise, n_descartadas)."""
    base = _member_root(paths[0])
    base_part, dropped = reduce_to_lead(base)
    if base_part is None:
        return None, 0
    mnum = len(base_part.findall("measure"))
    for extra in paths[1:]:
        pe_part, d2 = reduce_to_lead(_member_root(extra))
        dropped += d2
        if pe_part is None:
            continue
        for measure in pe_part.findall("measure"):
            mnum += 1
            measure.set("number", str(mnum))
            base_part.append(measure)
    return base, dropped


def fix_attributes(root, fifths):
    """Idêntico a content/omr_merge.py: garante key/fifths e <transpose -2> no 1º <attributes>."""
    a = root.find(".//attributes")
    if a is None:
        return False
    key = a.find("key")
    if key is None:
        key = ET.Element("key")
        div = a.find("divisions")
        a.insert(list(a).index(div) + 1 if div is not None else 0, key)
    f = key.find("fifths")
    if f is None:
        f = ET.SubElement(key, "fifths")
    f.text = str(fifths)
    if a.find("transpose") is None:
        tr = ET.SubElement(a, "transpose")
        ET.SubElement(tr, "diatonic").text = "-1"
        ET.SubElement(tr, "chromatic").text = "-2"
    return True


def find_mxl(num):
    files = glob.glob(str(OUTRAW / f"cu-{num:03d}.mxl")) + glob.glob(str(OUTRAW / f"cu-{num:03d}-p*.mxl"))
    def pageno(f):
        m = re.search(r"-p(\d+)\.mxl$", f)
        return int(m.group(1)) if m else 0
    return sorted(set(files), key=pageno)


def load_catalog():
    return json.load(open(HERE / "pieces_cumbia.json", encoding="utf-8"))["pieces"]


def main():
    NOTES.mkdir(parents=True, exist_ok=True)
    cat = [p for p in load_catalog() if p.get("source") == "omr"]
    if not list(OUTRAW.glob("cu-*.mxl")):
        sys.exit(f"sem .mxl em {OUTRAW} — rode o workflow omr-cumbia.yml e traga o branch "
                 f"omr/cumbia-raw (git checkout origin/omr/cumbia-raw -- omr/out).")
    n = skip_key = skip_mxl = 0
    for p in cat:
        num = p["num"]
        if not p.get("key_concert"):
            print(f"  cu-{num:03d}: key_concert vazio — preencha (veja omr_check.py) e rode de novo. PULADO.")
            skip_key += 1
            continue
        paths = find_mxl(num)
        if not paths:
            print(f"  cu-{num:03d}: sem .mxl em omr/out — pulado")
            skip_mxl += 1
            continue
        root, dropped = concat_pages(paths)
        if root is None:
            print(f"  cu-{num:03d}: MusicXML sem <part> — pulado"); skip_mxl += 1; continue
        ef = expected_fifths(p["key_concert"])
        fix_attributes(root, ef)
        measures = len(root.findall(".//measure"))
        notes = len(root.findall(".//note/pitch"))
        header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                  f'<!-- OMR Audiveris (cumbia) + tom do catálogo. PROVISÓRIO: notas a conferir. '
                  f'Reduzido à voz-líder; tom escrito = {ef} acidentes; transpose -2. '
                  f'Páginas: {len(paths)}; descartadas {dropped} nota(s) de acorde/2ª voz. -->\n')
        (NOTES / f"cu-{num:03d}.musicxml").write_text(header + ET.tostring(root, encoding="unicode"), encoding="utf-8")
        flag = "  ⚠ redução agressiva" if dropped > notes * 0.15 else ""
        print(f"  cu-{num:03d}  {p['titulo'][:22]:22} {len(paths)}pág · {notes} notas / {measures} comp · "
              f"armadura {ef:+d} · descartadas {dropped}{flag}")
        n += 1
    print(f"importadas {n} cumbias → {NOTES} · sem key_concert: {skip_key} · sem .mxl: {skip_mxl}")
    if skip_key:
        print("→ preencha os key_concert vazios no catálogo (transcribe.py CATALOG_EXTRA) a partir do omr_report.csv.")


if __name__ == "__main__":
    main()
