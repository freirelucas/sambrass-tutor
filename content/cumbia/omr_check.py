#!/usr/bin/env python3
"""QA da saída do Audiveris (omr/out/cu-*.mxl) das cumbias, contra o catálogo.

Análogo do content/omr_check.py (Sambrass), mas: catálogo é content/cumbia/pieces_cumbia.json
(entradas source=="omr"), glob é cu-* e agrega multi-página (cu-NNN-pK) por num. Quando o
`key_concert` do catálogo está VAZIO (o caso na 1ª rodada), NÃO compara: REPORTA a armadura lida
pelo Audiveris e o TOM DE CONCERTO IMPLÍCITO — é o número que você copia para o catálogo
(transcribe.py CATALOG_EXTRA) antes de rodar o omr_import.py.

Saída: content/cumbia/omr_report.csv. Uso: python3 content/cumbia/omr_check.py
"""
import zipfile, sys, pathlib, glob, csv, re, json
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTRAW = REPO / "omr" / "out"
PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
      "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
FIFTHS = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 5: -1, 10: -2, 3: -3, 8: -4, 1: -5}
KEY_NAME = {0: "C", 1: "G", 2: "D", 3: "A", 4: "E", 5: "B", 6: "F#",
            -1: "F", -2: "Bb", -3: "Eb", -4: "Ab", -5: "Db", -6: "Gb"}


def expected_fifths(concert):
    return FIFTHS[(PC[concert] + 2) % 12]


def implied_concert(omr_fifths):
    """Tom de concerto implícito por uma armadura ESCRITA lida pelo Audiveris (concerto = -2 semitons
    = -2 acidentes na armadura)."""
    if omr_fifths is None:
        return "?"
    return KEY_NAME.get(omr_fifths - 2, "?")


def parse_mxl(path):
    z = zipfile.ZipFile(path)
    name = [n for n in z.namelist() if not n.startswith("META-INF") and n.endswith(".xml")][0]
    root = ET.fromstring(z.read(name))
    fifths = root.findtext(".//attributes/key/fifths")
    beats = root.findtext(".//attributes/time/beats")
    bt = root.findtext(".//attributes/time/beat-type")
    pitched = [n for n in root.findall(".//note") if n.find("pitch") is not None]
    return {"fifths": int(fifths) if fifths not in (None, "") else None,
            "time": f"{beats}/{bt}" if beats else "?",
            "notes": len(pitched), "measures": len(root.findall(".//measure"))}


def pages_of(num):
    files = glob.glob(str(OUTRAW / f"cu-{num:03d}.mxl")) + glob.glob(str(OUTRAW / f"cu-{num:03d}-p*.mxl"))
    return sorted(set(files), key=lambda f: (int(re.search(r"-p(\d+)\.mxl$", f).group(1))
                                             if re.search(r"-p(\d+)\.mxl$", f) else 0))


def main():
    cat = {p["num"]: p for p in
           json.load(open(HERE / "pieces_cumbia.json", encoding="utf-8"))["pieces"]
           if p.get("source") == "omr"}
    if not list(OUTRAW.glob("cu-*.mxl")):
        sys.exit(f"nenhum cu-*.mxl em {OUTRAW} (rode omr-cumbia.yml e traga o branch omr/cumbia-raw)")
    rows, ok, unknown = [], 0, 0
    for num in sorted(cat):
        paths = pages_of(num)
        if not paths:
            continue
        first = parse_mxl(paths[0])
        notes = sum(parse_mxl(p)["notes"] for p in paths)
        measures = sum(parse_mxl(p)["measures"] for p in paths)
        omr_f = first["fifths"]
        p = cat[num]
        cat_key = p.get("key_concert") or ""
        impl = implied_concert(omr_f)
        if cat_key:
            exp = expected_fifths(cat_key)
            key_ok = omr_f == exp
            ok += key_ok
            status = "✓" if key_ok else "✗"
            keycol = f"cat {cat_key} (esp {exp:+d})"
        else:
            exp, key_ok, status = None, None, "—"
            unknown += 1
            keycol = f"PREENCHER → {impl}"
        rows.append([num, p.get("titulo", "?"), len(paths), omr_f, impl, cat_key,
                     exp, ("sim" if key_ok else "não") if key_ok is not None else "—",
                     first["time"], notes, measures])
        print(f"cu-{num:03d} {p.get('titulo','?')[:22]:22} | {len(paths)}pág | "
              f"armadura OMR {str(omr_f):>3} → concerto impl. {impl:>3} | {keycol:18} {status} | "
              f"compasso {first['time']:>4} | {notes:>3} notas / {measures:>2} comp.")
    with open(HERE / "omr_report.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["num", "titulo", "paginas", "fifths_omr", "concerto_implicito", "key_concert_cat",
                    "fifths_esperado", "armadura_ok", "compasso_omr", "n_notas", "n_compassos"])
        w.writerows(rows)
    print(f"\n{len(rows)} cumbias lidas. Armadura confere: {ok} · a preencher (key_concert vazio): "
          f"{unknown}. report → content/cumbia/omr_report.csv")
    if unknown:
        print("→ copie 'concerto_implicito' para os key_concert vazios (transcribe.py CATALOG_EXTRA), "
              "rode transcribe.py, depois omr_import.py.")


if __name__ == "__main__":
    main()
