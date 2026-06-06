#!/usr/bin/env python3
"""Track 2 — Analytics do caderno. Gera content/analytics.json + content/analise.html
(arquivo único, fontes de sistema, barras em CSS, sem build/deps).

Distribuições (tom/compasso/dificuldade/densidade), frequência de habilidades e células,
matriz célula × tom, correlações e outliers. Uso: python3 content/analytics.py
"""
import json, html, collections, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "curadoria"))
from lib import (load_pieces, features, piece_skills, difficulty_table,
                 written_acc, SKILLS, PC, ROOT)

NAME_BY_PC = {0: "C", 1: "Db", 2: "D", 3: "Eb", 4: "E", 5: "F",
              6: "F#", 7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B"}


def written_name(concert):
    return NAME_BY_PC[(PC[concert] + 2) % 12]


def esc(s):
    return html.escape(str(s))


def bars(items, unit=""):
    """items: lista de (label, valor). Barras horizontais em CSS."""
    mx = max((v for _, v in items), default=1) or 1
    out = ['<div class="chart">']
    for lab, v in items:
        w = round(100 * v / mx, 1)
        out.append(f'<div class="row"><span class="lab">{esc(lab)}</span>'
                   f'<span class="bar"><span style="width:{w}%"></span></span>'
                   f'<span class="val">{v}{unit}</span></div>')
    out.append("</div>")
    return "".join(out)


def main():
    P = load_pieces()
    calc, raw = difficulty_table(P)
    skills_by = {p["num"]: piece_skills(p) for p in P}

    def count(vals):
        return collections.Counter(vals)

    tom_w = count(written_name(p["key_concert"]) for p in P)
    tom_order = ["C", "G", "D", "A", "E", "F#", "F", "Bb", "Eb", "Ab", "Db"]
    comp = count(p["compasso"] for p in P)
    dens = count(p["densidade"] for p in P)
    dman = count(p["dificuldade"] for p in P)
    dcal = count(calc[p["num"]] for p in P)
    cel = count(c for p in P for c in p["celulas"])
    skl = count(s for p in P for s in skills_by[p["num"]])
    composers = count(p["compositor"].split(" / ")[0] for p in P)

    # matriz célula × tom escrito
    keys = [k for k in tom_order if k in tom_w]
    cells_list = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    matrix = {c: {k: 0 for k in keys} for c in cells_list}
    for p in P:
        k = written_name(p["key_concert"])
        for c in p["celulas"]:
            if c in matrix and k in matrix[c]:
                matrix[c][k] += 1

    outliers = {
        "mais_dificeis": sorted(P, key=lambda p: -calc[p["num"]])[:6],
        "mais_faceis": sorted(P, key=lambda p: calc[p["num"]])[:6],
        "modulantes": [p for p in P if p["modulates_to_concert"]],
        "quatro_quartos": [p for p in P if p["compasso"] == "4/4"],
    }

    json.dump({
        "tom_escrito": dict(tom_w), "compasso": dict(comp), "densidade": dict(dens),
        "dificuldade_manual": dict(sorted(dman.items())),
        "dificuldade_calc": dict(sorted(dcal.items())),
        "celulas": dict(cel), "habilidades": dict(skl),
        "matriz_celula_tom": matrix,
        "outliers": {k: [p["num"] for p in v] for k, v in outliers.items()},
    }, open(ROOT / "analytics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # ---- HTML ----
    def mtable():
        head = "".join(f"<th>{k}</th>" for k in keys)
        rows = []
        mx = max(max(r.values()) for r in matrix.values()) or 1
        for c in cells_list:
            tds = []
            for k in keys:
                v = matrix[c][k]
                a = round(v / mx, 2)
                tds.append(f'<td style="background:rgba(122,31,31,{a})">{v or ""}</td>')
            rows.append(f"<tr><th>{c}</th>{''.join(tds)}</tr>")
        return f'<table class="mx"><tr><th></th>{head}</tr>{"".join(rows)}</table>'

    def olist(ps, extra=lambda p: f"dif {calc[p['num']]}"):
        return "".join(f'<li><b>{p["num"]:03d}</b> {esc(p["titulo"])} '
                       f'<small>{esc(p["compositor"].split(" / ")[0])} · {esc(extra(p))}</small></li>' for p in ps)

    dman_items = [(str(k), dman.get(k, 0)) for k in range(1, 11)]
    dcal_items = [(str(k), dcal.get(k, 0)) for k in range(1, 11)]

    H = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sambrass — Analytics do caderno</title><style>
:root{{--t:#1a1a1a;--p:#fbfaf7;--l:#d8d2c4;--d:#7a1f1f;--s:#6b6456;--c:#f2efe6;--g:#2e6b4f}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--p);color:var(--t);font:16px/1.5 Georgia,serif;padding:0 16px}}
.wrap{{max-width:980px;margin:0 auto}}h1{{font-size:26px;margin:28px 0 2px}}.sub{{color:var(--s);font-family:Arial,sans-serif;font-size:13px}}
h2{{font-family:Arial,sans-serif;font-size:13px;letter-spacing:1px;text-transform:uppercase;color:var(--d);border-bottom:1px solid var(--l);padding-bottom:5px;margin:34px 0 12px}}
.grid{{display:flex;gap:26px;flex-wrap:wrap}}.grid>div{{flex:1;min-width:280px}}
.card{{background:#fff;border:1px solid var(--l);border-radius:8px;padding:14px 16px;margin:10px 0}}
.chart .row{{display:flex;align-items:center;gap:8px;margin:3px 0;font-family:Arial,sans-serif;font-size:13px}}
.lab{{min-width:64px;text-align:right;color:var(--s)}}.val{{min-width:30px;color:var(--s)}}
.bar{{flex:1;background:var(--c);border-radius:4px;height:14px;overflow:hidden}}.bar span{{display:block;height:100%;background:var(--d)}}
table.mx{{border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px}}table.mx th,table.mx td{{border:1px solid var(--l);width:38px;height:30px;text-align:center}}table.mx th{{background:var(--c);color:var(--s)}}
ul{{list-style:none;padding:0;font-size:14px}}ul li{{padding:3px 0;border-bottom:1px dotted var(--l)}}small{{color:var(--s);font-family:Arial,sans-serif;font-size:12px}}
.kpi{{display:flex;gap:18px;flex-wrap:wrap;margin:14px 0}}.kpi div{{background:var(--c);border-radius:6px;padding:8px 14px;font-family:Arial,sans-serif}}.kpi b{{font-size:22px;color:var(--d);display:block}}
</style></head><body><div class="wrap">
<h1>Analytics — caderno Sambrass23 (trompete)</h1>
<div class="sub">110 peças catalogadas · gerado de content/pieces.json · dificuldade_calc = fórmula recalibrada 1–10</div>
<div class="kpi"><div><b>{len(P)}</b>peças</div><div><b>{len(keys)}</b>tons</div>
<div><b>{comp.get('4/4',0)}</b>em 4/4</div><div><b>{len(outliers['modulantes'])}</b>modulações</div>
<div><b>{sum(1 for p in P if 'C4' in p['celulas'])}</b>com semicolcheia</div></div>

<h2>Tonalidades (escritas) e compasso</h2><div class="grid">
<div class="card"><b>Tom escrito</b>{bars([(k, tom_w[k]) for k in keys])}</div>
<div class="card"><b>Compasso</b>{bars(sorted(comp.items(), key=lambda x:-x[1]))}
<b style="display:block;margin-top:10px">Densidade</b>{bars(sorted(dens.items(), key=lambda x:-x[1]))}</div></div>

<h2>Dificuldade — manual × recalibrada</h2><div class="grid">
<div class="card"><b>Manual (estimada)</b>{bars(dman_items)}</div>
<div class="card"><b>Recalibrada (fórmula)</b>{bars(dcal_items)}</div></div>
<p class="sub">A manual aglomerava em 6; a recalibrada espalha pela escala — use-a como referência objetiva.</p>

<h2>Habilidades mais frequentes</h2><div class="card">{bars(skl.most_common())}</div>

<h2>Células rítmicas e matriz célula × tom</h2><div class="grid">
<div class="card"><b>Frequência de células</b>{bars(sorted(cel.items()))}</div>
<div class="card"><b>Célula × tom (peças-treino por habilidade/tom)</b><br><br>{mtable()}</div></div>

<h2>Outliers</h2><div class="grid">
<div class="card"><b>Mais difíceis</b><ul>{olist(outliers['mais_dificeis'])}</ul></div>
<div class="card"><b>Mais fáceis</b><ul>{olist(outliers['mais_faceis'])}</ul></div></div>
<div class="grid">
<div class="card"><b>Modulações</b><ul>{olist(outliers['modulantes'], lambda p: (p['key_concert']+'→'+(p['modulates_to_concert'] or '')))}</ul></div>
<div class="card"><b>Compositores (top)</b>{bars(composers.most_common(8))}</div></div>

<p class="sub" style="margin:40px 0">Sambrass tutor · analytics estático · regenerar com <code>python3 content/analytics.py</code></p>
</div></body></html>"""
    (ROOT / "analise.html").write_text(H, encoding="utf-8")
    print(f"OK — analytics.json + analise.html ({len(H)} bytes) em {ROOT}")
    print("tom escrito:", dict(tom_w))
    print("dificuldade calc:", dict(sorted(dcal.items())))
    print("habilidades top:", skl.most_common(5))


if __name__ == "__main__":
    main()
