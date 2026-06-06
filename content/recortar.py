#!/usr/bin/env python3
"""Recorta as 110 partituras do PDF-fonte em alta resolução, removendo a faixa
superior com as letras (material protegido). Usa PyMuPDF (não depende de poppler).

Saída: content/scores/sb-NNN.jpg  (NNN = página − 3, ou seja 001..110).
Uso:   python3 content/recortar.py [--dpi 200] [--top 0.255]

O PDF-fonte ('Sambrass23 trompete.pdf') está versionado no branch main; se não
estiver no diretório, traga-o (ex.: git show origin/main:'Sambrass23 trompete.pdf').
"""
import pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / "Sambrass23 trompete.pdf"
OUT = ROOT / "content" / "scores"
FIRST_PAGE = 4   # 1-based: página 4 = peça 001 (rodapé "001")
N = 110


def main():
    import fitz  # PyMuPDF
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--top", type=float, default=0.255,
                    help="fração superior cortada (faixa de letras)")
    ap.add_argument("--quality", type=int, default=82)
    a = ap.parse_args()
    if not PDF.exists():
        raise SystemExit(f"PDF-fonte não encontrado: {PDF}")
    OUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)
    for i in range(N):
        page = doc[FIRST_PAGE - 1 + i]
        r = page.rect
        clip = fitz.Rect(r.x0, r.y0 + r.height * a.top, r.x1, r.y1)
        pix = page.get_pixmap(dpi=a.dpi, clip=clip)
        pix.save(OUT / f"sb-{i + 1:03d}.jpg", jpg_quality=a.quality)
    doc.close()
    print(f"recortadas {N} partituras → {OUT} (dpi={a.dpi}, top={a.top})")


if __name__ == "__main__":
    main()
