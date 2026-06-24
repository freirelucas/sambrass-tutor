#!/usr/bin/env python3
"""Monta _site/ para deploy (GitHub Pages): a PWA (app/) + dados por JORNADA.
Sambrass → _site/data/ (flat, intacto). Cumbias → _site/data/cumbias/ (se houver).
Uso: python3 app/build_site.py
"""
import json, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "app"
SITE = ROOT / "_site"
C = ROOT / "content"


def _cp_opt(src, dst):
    if src and pathlib.Path(src).exists():
        shutil.copy(src, dst)
        return True
    return False


def emit_sambrass():
    """Jornada Sambrass: dados em _site/data/ (formato histórico, intocado)."""
    dest = SITE / "data"; dest.mkdir(exist_ok=True)
    shutil.copy(C / "pieces.json", dest / "pieces.json")
    shutil.copy(C / "cells.json", dest / "cells.json")
    shutil.copy(C / "curriculum" / "sambrass23-trilha.json", dest / "curriculum.json")
    shutil.copy(C / "curadoria" / "trilha.json", dest / "trilha.json")
    shutil.copy(C / "curadoria" / "escada.json", dest / "escada.json")
    _cp_opt(C / "notes_abc.json", dest / "abc.json")
    _cp_opt(C / "notes_quality.json", dest / "quality.json")
    rot = json.load(open(C / "curriculum" / "sambrass23-6semanas.json", encoding="utf-8"))["rotina_diaria"]
    json.dump(rot, open(dest / "rotina.json", "w", encoding="utf-8"), ensure_ascii=False)
    ped = C / "pedagogia"
    if ped.exists():
        shutil.copy(ped / "app_musicas.json", dest / "percurso.json")    # nós da trilha (eager)
        shutil.copy(ped / "app_pedagogia.json", dest / "pedagogia.json")  # perfil/plano/desafios (lazy)
        shutil.copy(ped / "app_prep.json", dest / "aquecimento.json")     # 12 aquecimentos (lazy)
        shutil.copy(ped / "app_tecnica.json", dest / "tecnica.json")      # técnica por lote (lazy)
        tec = json.load(open(ped / "app_tecnica.json", encoding="utf-8"))
        lotes = [{"lote": t["lote"], "nivel": t.get("nivel"), "tom": t["tom"], "feat": t["feat"]} for t in tec]
        json.dump(lotes, open(dest / "lotes.json", "w", encoding="utf-8"), ensure_ascii=False)


def emit_cumbias():
    """Jornada Cumbias: dados em _site/data/cumbias/ (saídas de content/cumbia/build/)."""
    cdir = C / "cumbia" / "build"
    if not cdir.exists():
        return False
    dest = SITE / "data" / "cumbias"; dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in ["pieces.json", "percurso.json", "escada.json", "lotes.json", "abc.json",
              "abc_full.json", "quality.json", "pedagogia.json", "cells.json", "aquecimento.json", "tecnica.json", "rotina.json"]:
        n += _cp_opt(cdir / f, dest / f)
    return n > 0


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    # 1) shell da PWA inteiro (inclui vendor/abcjs), menos este script
    shutil.copytree(APP, SITE, ignore=shutil.ignore_patterns("build_site.py", "__pycache__"))
    # 2) dados por jornada
    emit_sambrass()
    tem_cumbia = emit_cumbias()

    nbytes = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file())
    print(f"_site pronto: {len(list(SITE.rglob('*')))} arquivos, {nbytes // 1024} KB · "
          f"jornadas: sambrass{' + cumbias' if tem_cumbia else ''}")


if __name__ == "__main__":
    main()
