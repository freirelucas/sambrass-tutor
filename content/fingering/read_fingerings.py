#!/usr/bin/env python3
"""Lê a DIGITAÇÃO impressa (dedos de trompete) das partituras do caderno Sambrass23.
A digitação é o canal de altura mais limpo da página (dígitos grandes em negrito);
serve para corrigir as alturas do OMR. Fonte fixa em todo o caderno → templates 1x, reuso 110x.

Saída por página: para cada sistema (pauta), a sequência ordenada de dedilhados
[(x_centro, "12"), ...]. Dígitos sobem sempre (1<2<3) → '2' seguido de '1' = nova nota.

Robustez (todas as 110): binarização adaptativa por página (Otsu, p/ scans claros e
escuros) + detecção de pauta por morfologia horizontal (resiste a barra lateral de
título e a páginas com 3/4/5 sistemas).
"""
import sys, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage
import cv2

ROOT = pathlib.Path(__file__).resolve().parent
TPL = ROOT / "templates"


def binarize(gray):
    """Tinta=True. Limiar Otsu por página (scans variam de claros a escuros)."""
    thr, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return bw > 0, int(thr)


def staff_systems(ink, x0=300, x1=2100):
    """Linhas de pauta = estruturas horizontais longas. Agrupa em sistemas de 5."""
    bw = (ink * 255).astype(np.uint8)
    hor = cv2.erode(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (80, 1)))
    rowsum = hor[:, x0:x1].sum(axis=1) / 255
    isline = rowsum > 700
    ys = [y for y in range(len(isline)) if isline[y]]
    groups, cur = [], []
    for y in ys:
        if cur and y - cur[-1] <= 4:
            cur.append(y)
        else:
            if cur: groups.append(sum(cur) // len(cur))
            cur = [y]
    if cur: groups.append(sum(cur) // len(cur))
    # agrupa em pautas de 5 linhas IGUALMENTE espaçadas (gap real ~12-24px); pula
    # linhas espúrias (réguas de texto, etc.) em vez de deslocar todo o agrupamento.
    systems, i = [], 0
    while i + 4 < len(groups):
        g = groups[i:i + 5]
        gaps = [g[k + 1] - g[k] for k in range(4)]
        gap = (g[4] - g[0]) / 4.0
        if 9 <= gap <= 25 and max(gaps) - min(gaps) <= 6:
            systems.append(g); i += 5
        else:
            i += 1
    return systems


def detect_glyphs(ink, y0, y1, gap, x0=390, x1=2230):
    """gap = espaçamento entre linhas da pauta (escala da página). O tamanho do
    dígito de dedilhado escala com a notação (páginas com +sistemas são menores)."""
    band = ink[y0:y1, x0:x1]
    lab, n = ndimage.label(band)
    hmin, hmax = 1.4 * gap, 2.5 * gap
    wmin, wmax = 0.5 * gap, 1.8 * gap
    out = []
    for s in ndimage.find_objects(lab):
        ys, xs = s; h = ys.stop - ys.start; w = xs.stop - xs.start
        if hmin <= h <= hmax and wmin <= w <= wmax:
            out.append((xs.start + x0, ys.start + y0, w, h))
    return sorted(out, key=lambda c: c[0])


def load_templates():
    tpl = {}
    for f in sorted(TPL.glob("*.png")):
        tpl[f.stem.split("_")[0]] = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
    return tpl


def classify(crop_ink, tpl):
    cb = (crop_ink * 255).astype(np.uint8)
    best, bs = "?", -1.0
    for d, t in tpl.items():
        r = cv2.resize(cb, (t.shape[1], t.shape[0]))
        score = cv2.matchTemplate(r, t, cv2.TM_CCOEFF_NORMED)[0][0]
        if score > bs: bs, best = score, d
    return best, bs


def group(digits):
    """digits: [(x, d)] em ordem → lista de (x_centro, fingering).
    Dígitos de um dedilhado sobem (1<2<3); '0' é sempre sozinho → fronteiras claras."""
    out, cur, cx = [], [], []
    def flush():
        if cur: out.append((sum(cx) // len(cx), "".join(cur)))
    last = None
    for x, d in digits:
        if d == "0":
            flush(); out.append((x, "0")); cur, cx, last = [], [], None; continue
        if cur and (last is None or int(d) <= int(last)):
            flush(); cur, cx = [d], [x]
        else:
            cur.append(d); cx.append(x)
        last = d
    flush()
    return out


def read_page(img_path):
    gray = np.array(Image.open(img_path).convert("L"))
    ink, _ = binarize(gray)
    systems = staff_systems(ink)
    tpl = load_templates()
    results, prev_bottom = [], 0
    for lines in systems:
        top = lines[0]
        gap = (lines[-1] - lines[0]) / 4.0          # escala da página (px por degrau)
        y0 = max(prev_bottom + 2, top - int(9 * gap))
        y1 = top - 4
        digits = []
        for (x, y, w, h) in detect_glyphs(ink, y0, y1, gap):
            d, sc = classify(ink[y:y + h, x:x + w], tpl)
            if sc < 0.28:                            # descarta clave/letra de seção residual
                continue
            digits.append((x + w // 2, d))
        results.append(group(digits))
        prev_bottom = lines[-1]
    return results


if __name__ == "__main__":
    for p in sys.argv[1:]:
        res = read_page(p)
        print(pathlib.Path(p).stem)
        for i, sysf in enumerate(res):
            print(f"  sys{i+1} ({len(sysf):2d}):", " ".join(f for _, f in sysf))
