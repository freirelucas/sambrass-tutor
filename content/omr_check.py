#!/usr/bin/env python3
"""Track 1 (validação) — confere a saída do Audiveris (.mxl) contra o catálogo.

Para cada omr/out/sb-NNN.mxl: descompacta, lê armadura (fifths), compasso, nº de notas
e compara a armadura ESCRITA esperada (derivada do tom de concerto do catálogo).
Gera omr/report.csv. Uso: python3 content/omr_check.py
"""
import zipfile, sys, pathlib, glob, csv
import xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "curadoria"))
from lib import load_pieces, PC, ROOT
REPO = ROOT.parent  # lib.ROOT = content/ ; omr/ fica na raiz do repo

FIFTHS_BY_PC = {0: 0, 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 5: -1, 10: -2, 3: -3, 8: -4, 1: -5}


def expected_fifths(concert):
    return FIFTHS_BY_PC[(PC[concert] + 2) % 12]


def parse_mxl(path):
    z = zipfile.ZipFile(path)
    name = [n for n in z.namelist() if not n.startswith("META-INF") and n.endswith(".xml")][0]
    root = ET.fromstring(z.read(name))
    fifths = root.findtext(".//attributes/key/fifths")
    beats = root.findtext(".//attributes/time/beats")
    bt = root.findtext(".//attributes/time/beat-type")
    notes = root.findall(".//note")
    pitched = [n for n in notes if n.find("pitch") is not None]
    return {"fifths": int(fifths) if fifths not in (None, "") else None,
            "time": f"{beats}/{bt}" if beats else "?",
            "notes": len(pitched), "measures": len(root.findall(".//measure"))}


def main():
    cat = {p["num"]: p for p in load_pieces()}
    files = sorted(glob.glob(str(REPO / "omr" / "out" / "sb-*.mxl")))
    if not files:
        sys.exit("nenhum .mxl em omr/out/ (rode o workflow e traga o branch omr/audiveris-raw)")
    rows, ok = [], 0
    for f in files:
        num = int(pathlib.Path(f).stem.split("-")[1])
        info = parse_mxl(f)
        p = cat.get(num, {})
        exp = expected_fifths(p["key_concert"]) if p.get("key_concert") else None
        key_ok = info["fifths"] == exp
        comp_ok = info["time"] == p.get("compasso")
        ok += key_ok
        rows.append([num, p.get("titulo", "?"), info["fifths"], exp, "sim" if key_ok else "NÃO",
                     info["time"], p.get("compasso", "?"), "sim" if comp_ok else "não",
                     info["notes"], info["measures"]])
        print(f"sb-{num:03d} {p.get('titulo','?')[:22]:22} | armadura OMR {str(info['fifths']):>3} "
              f"vs esperada {str(exp):>3} {'✓' if key_ok else '✗'} | compasso {info['time']} "
              f"(cat {p.get('compasso')}) {'✓' if comp_ok else '✗'} | {info['notes']} notas / {info['measures']} comp.")
    with open(ROOT / "omr_report.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["num", "titulo", "fifths_omr", "fifths_esperado", "armadura_ok",
                    "compasso_omr", "compasso_cat", "compasso_ok", "n_notas", "n_compassos"])
        w.writerows(rows)
    print(f"\nArmadura conferida: {ok}/{len(files)} batem com o catálogo. report → omr/report.csv")


if __name__ == "__main__":
    main()
