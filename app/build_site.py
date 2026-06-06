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
    # 1) shell da PWA inteiro (inclui vendor/abcjs), menos este script
    shutil.copytree(APP, SITE, ignore=shutil.ignore_patterns("build_site.py", "__pycache__"))

    # 2) dados
    data = SITE / "data"; data.mkdir()
    shutil.copy(ROOT / "content" / "pieces.json", data / "pieces.json")
    shutil.copy(ROOT / "content" / "cells.json", data / "cells.json")
    shutil.copy(ROOT / "content" / "curriculum" / "sambrass23-trilha.json", data / "curriculum.json")
    shutil.copy(ROOT / "content" / "curadoria" / "trilha.json", data / "trilha.json")
    abc = ROOT / "content" / "notes_abc.json"
    if abc.exists():
        shutil.copy(abc, data / "abc.json")
    rot = json.load(open(ROOT / "content" / "curriculum" / "sambrass23-6semanas.json", encoding="utf-8"))["rotina_diaria"]
    json.dump(rot, open(data / "rotina.json", "w", encoding="utf-8"), ensure_ascii=False)

    # (sem PDF no produto: a notação é renderizada nativamente pelo abcjs)
    nbytes = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file())
    print(f"_site pronto: {len(list(SITE.rglob('*')))} arquivos, {nbytes // 1024} KB (notação nativa, sem PDF)")


if __name__ == "__main__":
    main()
