#!/usr/bin/env python3
"""Gera os recortes de partitura p/ a ferramenta de revisão (app/revisar.html).

Para cada cumbia OMR do catálogo, renderiza o TOPO da página 1 do PDF (a região do
tema = primeiros sistemas) → app/revisao/cu-NNN.png. A página de revisão mostra esse
recorte ao lado da frase renderizada, p/ o dono validar o tema (✓/✗) ouvindo e vendo.

Uso: python3 content/cumbia/make_revisao.py  (precisa de PyMuPDF). Reproduzível.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
PDFS = HERE / "pdfs"
OUT = HERE.parents[1] / "app" / "revisao"
FRAC = 0.60   # fração superior da página 1 (cobre os primeiros sistemas = o tema)
ZOOM = 1.8


def main():
    import fitz
    OUT.mkdir(parents=True, exist_ok=True)
    cat = [p for p in json.load(open(HERE / "pieces_cumbia.json", encoding="utf-8"))["pieces"]
           if p.get("source") == "omr" and p.get("pdf")]
    for p in sorted(cat, key=lambda x: x["num"]):
        pdf = PDFS / p["pdf"]
        if not pdf.exists():
            print(f"  cu-{p['num']:03d}: PDF ausente: {pdf.name}"); continue
        doc = fitz.open(pdf)
        page = doc[0]; r = page.rect
        clip = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * FRAC)
        pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=clip)
        out = OUT / f"cu-{p['num']:03d}.png"
        pix.save(out)
        print(f"  cu-{p['num']:03d}  {p['titulo'][:22]:22} → {out.relative_to(HERE.parents[1])} ({pix.width}x{pix.height})")
        doc.close()
    print(f"recortes → {OUT}")


if __name__ == "__main__":
    main()
