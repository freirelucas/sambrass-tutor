#!/usr/bin/env python3
"""Pré-processa as partituras do PDF para OMR (Audiveris).

Renderiza cada peça em alta resolução e remove o que atrapalha o OMR: a faixa
superior de letras, a margem esquerda (título vertical + tampinha do número).
Mantém os sistemas de pauta (a digitação acima das notas fica; o Audiveris trata
números soltos como texto). Saída: omr/input/sb-NNN.png (página N+3 = peça NNN).

Uso:  python3 content/omr_prep.py [--dpi 300] [--top 0.22] [--left 0.095] [N ...]
(sem N = todas as 110). PDF-fonte: 'Sambrass23 trompete.pdf' (vem do branch main).
"""
import pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / "Sambrass23 trompete.pdf"
OUT = ROOT / "omr" / "input"
FIRST_PAGE = 4
N = 110


def main():
    import fitz
    ap = argparse.ArgumentParser()
    ap.add_argument("nums", nargs="*", type=int)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--top", type=float, default=0.22, help="fração superior cortada (letras)")
    ap.add_argument("--left", type=float, default=0.095, help="fração esquerda cortada (título/cap)")
    a = ap.parse_args()
    if not PDF.exists():
        raise SystemExit(f"PDF-fonte não encontrado: {PDF}")
    OUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)
    nums = a.nums or range(1, N + 1)
    for num in nums:
        page = doc[FIRST_PAGE - 1 + (num - 1)]
        r = page.rect
        clip = fitz.Rect(r.x0 + r.width * a.left, r.y0 + r.height * a.top, r.x1, r.y1)
        pix = page.get_pixmap(dpi=a.dpi, clip=clip)
        pix.save(OUT / f"sb-{num:03d}.png")
    doc.close()
    print(f"pré-processadas {len(list(nums))} partituras → {OUT} (dpi={a.dpi}, top={a.top}, left={a.left})")


if __name__ == "__main__":
    main()
