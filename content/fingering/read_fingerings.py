#!/usr/bin/env python3
"""Lê a DIGITAÇÃO impressa (dedos de trompete) das partituras do caderno Sambrass23.
A digitação é o canal de altura mais limpo da página (dígitos grandes em negrito);
serve para corrigir as alturas do OMR. Fonte fixa em todo o caderno → templates 1x, reuso 110x.

Saída por página: para cada sistema (pauta), a sequência ordenada de dedilhados
[(x_centro, "12"), ...]. Dígitos sobem sempre (1<2<3) → '2' seguido de '1' = nova nota.
"""
import sys, pathlib, glob, json
import numpy as np
from PIL import Image
from scipy import ndimage
import cv2

ROOT = pathlib.Path(__file__).resolve().parent
TPL = ROOT / "templates"

def staff_rows(gray, x0=200, x1=2200, frac=0.55):
    dark = gray < 110
    prof = dark[:, x0:x1].sum(axis=1)
    thr = frac * (x1 - x0)
    rows = [y for y in range(len(prof)) if prof[y] > thr]
    groups, cur = [], []
    for y in rows:
        if cur and y - cur[-1] <= 3: cur.append(y)
        else:
            if cur: groups.append(sum(cur)//len(cur))
            cur = [y]
    if cur: groups.append(sum(cur)//len(cur))
    # cluster into systems of 5 lines
    systems = [groups[i:i+5] for i in range(0, len(groups)-4, 5)]
    return [s for s in systems if len(s) == 5]

def detect_glyphs(gray, y0, y1, x0=280, x1=2200):
    band = (gray[y0:y1, x0:x1] < 110)
    lab, n = ndimage.label(band)
    out = []
    for s in ndimage.find_objects(lab):
        ys, xs = s; h = ys.stop-ys.start; w = xs.stop-xs.start
        if 30 <= h <= 44 and 12 <= w <= 32:        # tamanho de dígito de dedilhado
            out.append((xs.start+x0, ys.start+y0, w, h))
    return sorted(out, key=lambda c: c[0])

def load_templates():
    tpl = {}
    for f in sorted(TPL.glob("*.png")):
        tpl[f.stem.split("_")[0]] = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
    return tpl

def classify(crop, tpl):
    cb = (crop < 110).astype('uint8') * 255
    best, bs = "?", -1
    for d, t in tpl.items():
        r = cv2.resize(cb, (t.shape[1], t.shape[0]))
        score = cv2.matchTemplate(r, t, cv2.TM_CCOEFF_NORMED)[0][0]
        if score > bs: bs, best = score, d
    return best, bs

def group(digits):
    """digits: [(x, d)] em ordem → lista de (x_centro, fingering)."""
    out, cur, cx = [], [], []
    def flush():
        if cur: out.append((sum(cx)//len(cx), "".join(cur)))
    last = None
    for x, d in digits:
        if d == "0":
            flush(); cur, cx = ["0"], [x]; flush(); cur, cx = [], []; last = None; continue
        if cur and (last is None or int(d) <= int(last)):
            flush(); cur, cx = [d], [x]
        else:
            cur.append(d); cx.append(x)
        last = d
    flush()
    return out

def read_page(img_path):
    img = Image.open(img_path).convert("L")
    gray = np.array(img)
    systems = staff_rows(gray)
    tpl = load_templates()
    results = []
    prev_bottom = 0
    for si, lines in enumerate(systems):
        top = lines[0]
        y0 = max(prev_bottom + 5, top - 175)
        y1 = top - 6
        glyphs = detect_glyphs(gray, y0, y1)
        src = np.array(Image.open(img_path).convert("L"))
        digits = []
        for (x, y, w, h) in glyphs:
            crop = src[y:y+h, x:x+w]
            d, sc = classify(crop, tpl)
            digits.append((x + w//2, d))
        results.append(group(digits))
        prev_bottom = lines[-1]
    return results

if __name__ == "__main__":
    for p in sys.argv[1:]:
        res = read_page(p)
        print(pathlib.Path(p).stem)
        for i, sysf in enumerate(res):
            print(f"  sys{i+1}:", " ".join(f for _, f in sysf))
