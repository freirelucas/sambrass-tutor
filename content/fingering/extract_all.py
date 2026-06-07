#!/usr/bin/env python3
"""Extrai a DIGITAÇÃO das 110 páginas → content/fingering/reads/sb-NNN.json.
Inclui um escore de CONFIANÇA por página (honesto: separa o que está limpo do que
precisa de revisão), pois o canal de dedos é exato em páginas nítidas e degrada em
scans claros/comprimidos. NÃO toca nas melodias do produto — é dado para fundir depois.
"""
import sys, json, pathlib, glob
import numpy as np
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import read_fingerings as R

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "content" / "fingering" / "reads"
RUNTIME = ROOT / "content" / "notes_runtime"


def read_detailed(img_path):
    gray = np.array(Image.open(img_path).convert("L"))
    ink, thr = R.binarize(gray)
    systems = R.staff_systems(ink)
    tpl = R.load_templates()
    out_sys, scores, prev_bottom = [], [], 0
    for lines in systems:
        top = lines[0]; gap = (lines[-1] - lines[0]) / 4.0
        y0 = max(prev_bottom + 2, top - int(9 * gap)); y1 = top - 4
        digits = []
        for (x, y, w, h) in R.detect_glyphs(ink, y0, y1, gap):
            d, sc = R.classify(ink[y:y + h, x:x + w], tpl)
            if sc < 0.28:
                continue
            digits.append((x + w // 2, d)); scores.append(sc)
        out_sys.append([{"x": int(x), "f": f} for x, f in R.group(digits)])
        prev_bottom = lines[-1]
    return out_sys, scores, len(systems), thr


def omr_count(num):
    p = RUNTIME / f"sb-{num:03d}.json"
    if not p.exists():
        return None
    d = json.load(open(p))
    return sum(1 for e in d["events"] if "written_midi" in e)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    for img in sorted(glob.glob(str(ROOT / "content" / "scores" / "sb-*.jpg"))):
        num = int(pathlib.Path(img).stem.split("-")[1])
        systems, scores, nsys, thr = read_detailed(img)
        nf = sum(len(s) for s in systems)
        oc = omr_count(num)
        mean_sc = round(float(np.mean(scores)), 3) if scores else 0.0
        ratio = round(nf / oc, 2) if oc else None
        conf = "alta" if (mean_sc >= 0.5 and ratio and 0.7 <= ratio <= 1.4) else "revisar"
        rec = {"num": num, "n_systems": nsys, "n_fingerings": nf, "omr_notes": oc,
               "count_ratio": ratio, "mean_score": mean_sc, "otsu": thr,
               "confidence": conf, "systems": systems}
        json.dump(rec, open(OUT / f"sb-{num:03d}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        summary.append(rec)
    json.dump([{k: r[k] for k in ("num", "n_systems", "n_fingerings", "omr_notes",
               "count_ratio", "mean_score", "confidence")} for r in summary],
              open(OUT / "_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    alta = sum(1 for r in summary if r["confidence"] == "alta")
    tot_f = sum(r["n_fingerings"] for r in summary)
    print(f"110 páginas → {tot_f} dedilhados extraídos")
    print(f"confiança alta: {alta}/110 ; a revisar: {110-alta}/110")
    sc = sorted(r["mean_score"] for r in summary)
    print(f"mean_score: min {sc[0]} mediana {sc[len(sc)//2]} max {sc[-1]}")
    return summary


if __name__ == "__main__":
    main()
