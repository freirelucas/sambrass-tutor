#!/usr/bin/env python3
"""Cheatsheet das frases das cumbias (partitura por dificuldade) → HTML imprimível.

Para cada cumbia, renderiza o TEMA (a frase praticada) com verovio (mesma altura concert
que o app mostra por padrão), ordenado da MAIS FÁCIL p/ a mais difícil, com as 5 primeiras
marcadas "comece aqui". Mostra tom, células (com nome), riff (×N) e o tier (conferida/rascunho).

Uso: python3 content/cumbia/cheatsheet.py   → content/cumbia/build/cheatsheet.html
(depois: playwright imprime em PDF — ver cheatsheet via build_site/CI ou passo manual)
"""
import json, pathlib, verovio

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "build"
CUR = HERE.parent / "curadoria" / "build"


def L(p):
    return json.load(open(p, encoding="utf-8"))


def main():
    P = {p["id"]: p for p in L(OUT / "pieces.json")["pieces"]}
    Q = L(OUT / "quality.json")
    ABC = L(OUT / "abc.json")
    CELLS = {c["id"]: c["nome"] for c in L(OUT / "cells.json")["celulas_ritmicas"]}
    BL = L(CUR / "blocos.json")["pecas"] if (CUR / "blocos.json").exists() else {}

    tk = verovio.toolkit()

    def svg(abc):
        tk.setOptions({"inputFrom": "abc", "scale": 32, "adjustPageHeight": True, "pageWidth": 2100,
                       "pageMarginLeft": 30, "pageMarginRight": 30, "pageMarginTop": 16, "pageMarginBottom": 16,
                       "header": "none", "footer": "none", "breaks": "auto"})
        body = "\n".join(ln for ln in abc.splitlines() if not ln.startswith("T:"))
        tk.loadData(body)
        return tk.renderToSVG(1)

    order = sorted(P.values(), key=lambda p: p["dificuldade"])
    cards = []
    for r, p in enumerate(order, 1):
        pid = p["id"]
        abc = ABC.get(pid)
        notac = svg(abc) if abc else "<p style='color:#a00'>(sem melodia)</p>"
        tier = Q.get(pid, "?")
        riff = (BL.get(pid, {}) or {}).get("riff") or {}
        riff_txt = f"riff de {riff['len']} notas × {riff['x']}" if riff else "—"
        cels = " · ".join(f"<b>{c}</b> {CELLS.get(c, '')}" for c in p["celulas"]) or "—"
        top = r <= 5
        badge = ('<span class="t ok">conferida ✓</span>' if tier == "conferida"
                 else '<span class="t rasc">rascunho (em revisão)</span>')
        cards.append(f"""
        <section class="card{' top' if top else ''}">
          <div class="hd">
            <span class="rk">{'⭐ ' if top else ''}{r}</span>
            <div class="ti"><h2>{p['titulo']}</h2><div class="by">{p.get('compositor','')}</div></div>
            <div class="meta">
              <span class="t">tom <b>{p['key_concert']}</b></span>
              <span class="t">compasso <b>{p['compasso']}</b></span>
              <span class="t">dif <b>{p['dificuldade']}</b></span>
              {badge}
            </div>
          </div>
          <div class="cels">coração: {cels} &nbsp;·&nbsp; {riff_txt} — <i>decore o riff e looping devagar</i></div>
          <div class="staff">{notac}</div>
        </section>""")

    html = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Cheatsheet — Cumbias (frases por dificuldade)</title>
<style>
  @page {{ size: A4; margin: 12mm 10mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font: 13px/1.4 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color:#1a1a1a; margin:0; }}
  .top-h {{ border-bottom:2px solid #111; padding-bottom:8px; margin-bottom:14px; }}
  .top-h h1 {{ font-family: Georgia, serif; font-size:22px; margin:0 0 2px; }}
  .top-h p {{ margin:0; color:#555; font-size:12px; }}
  .card {{ border:1px solid #ddd; border-radius:8px; padding:10px 12px; margin:0 0 12px; break-inside:avoid; }}
  .card.top {{ border-color:#caa043; box-shadow:inset 4px 0 0 #e8b850; background:#fffdf6; }}
  .hd {{ display:flex; align-items:flex-start; gap:10px; }}
  .rk {{ font-family:Georgia,serif; font-size:20px; font-weight:700; color:#caa043; min-width:34px; }}
  .ti {{ flex:1; }} .ti h2 {{ font-family:Georgia,serif; font-size:17px; margin:0; }}
  .by {{ color:#666; font-size:11.5px; font-style:italic; }}
  .meta {{ display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end; max-width:46%; }}
  .t {{ background:#f2efe8; border-radius:5px; padding:2px 7px; font-size:11px; white-space:nowrap; }}
  .t.ok {{ background:#e6f4ea; color:#1f7a44; }} .t.rasc {{ background:#fdeede; color:#9a5a00; }}
  .cels {{ font-size:11.5px; color:#444; margin:7px 0 4px; }}
  .staff svg {{ max-width:100%; height:auto; }}
  .legend {{ font-size:11px; color:#666; margin-top:4px; }}
</style></head><body>
  <div class="top-h">
    <h1>Cheatsheet — Jornada das Cumbias</h1>
    <p>As frases (temas) ordenadas da <b>mais fácil</b> p/ a mais difícil · ⭐ = comece aqui (5 primeiras) ·
       altura em <b>concert</b> (como o app mostra por padrão). Gerado de <code>content/cumbia/build</code>.</p>
  </div>
  {''.join(cards)}
  <p class="legend">conferida ✓ = melodia confirmada à mão · rascunho = leitura automática (OMR) em revisão.
     O "coração" lista as células rítmicas a internalizar antes da melodia.</p>
</body></html>"""

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cheatsheet.html").write_text(html, encoding="utf-8")
    print(f"→ {(OUT / 'cheatsheet.html').relative_to(HERE.parents[1])}  ({len(order)} frases)")


if __name__ == "__main__":
    main()
