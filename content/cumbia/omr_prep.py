#!/usr/bin/env python3
"""Pré-processa as PDFs das cumbias para OMR (Audiveris): PDF → PNG(s).

Diferente do Sambrass (content/omr_prep.py, um caderno mestre com offset de página e
recorte agressivo): aqui cada cumbia é um PDF individual em content/cumbia/pdfs/, com
1–3 páginas e layout variável por editora. Por isso: renderiza a PÁGINA INTEIRA a 300 DPI,
SEM recorte por padrão (recorte costuma comer a 1ª pauta da cumbia; vire knob por --crop-*).
O mapeamento PDF→num vem do catálogo (campo `pdf`), só para entradas `source=="omr"`.

Saída: omr/input/cu-NNN.png (1 página) ou omr/input/cu-NNN-pK.png (multi-página).
Uso: python3 content/cumbia/omr_prep.py [--dpi 300] [--crop-top 0] [--crop-left 0] [N ...]
(sem N = todas as cumbias `source=="omr"` do catálogo). omr/ é git-ignored; o CI recria.
"""
import json, pathlib, argparse

HERE = pathlib.Path(__file__).resolve().parent
PDFS = HERE / "pdfs"
REPO = HERE.parents[1]
OUT = REPO / "omr" / "input"


def load_omr_catalog():
    cat = json.load(open(HERE / "pieces_cumbia.json", encoding="utf-8"))["pieces"]
    return {p["num"]: p for p in cat if p.get("pdf") and p.get("source") == "omr"}


def render_one(doc, num, dpi, crop_top, crop_left):
    import fitz
    outs = []
    for pi in range(doc.page_count):
        page = doc[pi]
        r = page.rect
        clip = (fitz.Rect(r.x0 + r.width * crop_left, r.y0 + r.height * crop_top, r.x1, r.y1)
                if (crop_top or crop_left) else None)
        pix = page.get_pixmap(dpi=dpi, clip=clip)
        suffix = "" if doc.page_count == 1 else f"-p{pi + 1}"
        out = OUT / f"cu-{num:03d}{suffix}.png"
        pix.save(out)
        outs.append(out)
    return outs


def main():
    import fitz
    ap = argparse.ArgumentParser()
    ap.add_argument("nums", nargs="*", type=int)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--crop-top", type=float, default=0.0, help="fração superior cortada (ex.: 0.12)")
    ap.add_argument("--crop-left", type=float, default=0.0, help="fração esquerda cortada")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cat = load_omr_catalog()
    nums = a.nums or sorted(cat)
    total = 0
    for num in nums:
        p = cat.get(num)
        if not p:
            print(f"  cu-{num:03d}: sem pdf/source=omr no catálogo — pulado")
            continue
        pdf = PDFS / p["pdf"]
        if not pdf.exists():
            print(f"  cu-{num:03d}: PDF não encontrado: {pdf.name}")
            continue
        outs = render_one(fitz.open(pdf), num, a.dpi, a.crop_top, a.crop_left)
        total += len(outs)
        print(f"  cu-{num:03d}  {p['titulo'][:24]:24} {len(outs)} página(s) → {', '.join(o.name for o in outs)}")
    print(f"pré-processadas {len(nums)} cumbias ({total} PNG) → {OUT} (dpi={a.dpi}, "
          f"crop_top={a.crop_top}, crop_left={a.crop_left})")


if __name__ == "__main__":
    main()
