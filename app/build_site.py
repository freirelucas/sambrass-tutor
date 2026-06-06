#!/usr/bin/env python3
"""Monta _site/ para deploy (GitHub Pages): a PWA (app/) + dados (content/*.json) +
partituras web geradas do PDF. Uso: python3 app/build_site.py
"""
import json, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "app"
SITE = ROOT / "_site"
PDF = ROOT / "Sambrass23 trompete.pdf"


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    # 1) shell da PWA (tudo de app/, menos este script)
    for f in APP.iterdir():
        if f.name == "build_site.py":
            continue
        shutil.copy(f, SITE / f.name) if f.is_file() else None

    # 2) dados
    data = SITE / "data"; data.mkdir()
    shutil.copy(ROOT / "content" / "pieces.json", data / "pieces.json")
    shutil.copy(ROOT / "content" / "cells.json", data / "cells.json")
    shutil.copy(ROOT / "content" / "curriculum" / "sambrass23-trilha.json", data / "curriculum.json")
    shutil.copy(ROOT / "content" / "curadoria" / "trilha.json", data / "trilha.json")
    rot = json.load(open(ROOT / "content" / "curriculum" / "sambrass23-6semanas.json", encoding="utf-8"))["rotina_diaria"]
    json.dump(rot, open(data / "rotina.json", "w", encoding="utf-8"), ensure_ascii=False)

    # 3) partituras web (do PDF; sem a faixa de letras)
    scores = SITE / "scores"; scores.mkdir()
    if PDF.exists():
        import fitz
        doc = fitz.open(PDF)
        for num in range(1, 111):
            page = doc[4 - 1 + (num - 1)]
            r = page.rect
            clip = fitz.Rect(r.x0, r.y0 + r.height * 0.255, r.x1, r.y1)
            page.get_pixmap(dpi=110, clip=clip).save(scores / f"sb-{num:03d}.jpg", jpg_quality=78)
        doc.close()
        n = len(list(scores.glob("*.jpg")))
    else:
        n = 0
        print("AVISO: PDF ausente — site sem partituras")

    nbytes = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file())
    print(f"_site pronto: {len(list(SITE.rglob('*')))} arquivos, {n} partituras, {nbytes // 1024} KB")


if __name__ == "__main__":
    main()
