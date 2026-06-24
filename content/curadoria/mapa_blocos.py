#!/usr/bin/env python3
"""Visualiza as DUAS geometrias do 'bloco de Lego' a partir de build/blocos.json.

Painel A — COR: círculo de quintas. Cada peça é um ponto no seu tom+modo detectado
            (maior = anel externo; relativo menor = anel interno). Mostra a descoberta
            do modo (anel menor povoado) e como o acervo se espalha no espaço tonal.
Painel B — FORMA: mapa estrutural. x = quão arpejado (3ªs/arpejo), y = quão saltado
            (saltos ≥6ª). Peças escalares ficam perto da origem; arpejadas à direita;
            saltadas no alto. Cor do ponto = modo. (= o eixo 'forma' do bloco.)

Pontos esmaecidos = confiança maior/menor baixa (pedem ouvido humano).
Saída: content/curadoria/build/mapa_blocos.png  ·  Uso: python3 content/curadoria/mapa_blocos.py
"""
import json, pathlib, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "build" / "blocos.json"
OUT = HERE / "build" / "mapa_blocos.png"

PC = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
COF = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]            # ordem do círculo de quintas (C no topo, horário)
COF_POS = {pc: i for i, pc in enumerate(COF)}
MAJ_LBL = {0: "C", 7: "G", 2: "D", 9: "A", 4: "E", 11: "B", 6: "F#/Gb", 1: "Db", 8: "Ab", 3: "Eb", 10: "Bb", 5: "F"}
MIN_LBL = {0: "Am", 7: "Em", 2: "Bm", 9: "F#m", 4: "C#m", 11: "G#m", 6: "Ebm", 1: "Bbm", 8: "Fm", 3: "Cm", 10: "Gm", 5: "Dm"}
WARM, COOL = "#e8932e", "#2f8fd0"                        # maior / menor


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    pecas = d["pecas"]
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(16, 8.2))
    fig.patch.set_facecolor("#faf7f1")

    # ---------- Painel A: círculo de quintas ----------
    axA.set_aspect("equal"); axA.axis("off")
    axA.set_xlim(-1.45, 1.45); axA.set_ylim(-1.45, 1.45)
    for r in (1.0, 0.62):                                # anéis externo (maior) e interno (menor)
        axA.add_artist(plt.Circle((0, 0), r, fill=False, color="#d8cdb8", lw=1))
    for pos in range(12):                                # raios + rótulos de setor
        ang = math.radians(90 - 30 * pos)
        axA.plot([0.5 * math.cos(ang), 1.2 * math.cos(ang)], [0.5 * math.sin(ang), 1.2 * math.sin(ang)], color="#ece3d1", lw=0.8, zorder=0)
        pcm = COF[pos]
        axA.text(1.32 * math.cos(ang), 1.32 * math.sin(ang), MAJ_LBL[pcm], ha="center", va="center", fontsize=12, weight="bold", color="#5b4a2a")
        axA.text(0.5 * math.cos(ang), 0.5 * math.sin(ang), MIN_LBL[pcm], ha="center", va="center", fontsize=8.5, color="#9a8aa0")

    groups = {}                                          # (setor, anel) -> lista
    for pid, r in pecas.items():
        c = r["cor"]
        if c["modo"] not in ("maior", "menor"):
            continue
        tpc = PC.get(c["tonica"]);
        if tpc is None:
            continue
        sector = COF_POS[tpc] if c["modo"] == "maior" else COF_POS[(tpc + 3) % 12]
        ring = "out" if c["modo"] == "maior" else "in"
        groups.setdefault((sector, ring), []).append((pid, r))

    nmaj = nmin = nfaint = 0
    for (sector, ring), items in groups.items():
        base = 1.0 if ring == "out" else 0.62
        ang0 = 90 - 30 * sector
        k = len(items); cols = max(1, math.ceil(math.sqrt(k)))
        for idx, (pid, r) in enumerate(items):
            row, col = divmod(idx, cols)
            da = (col - (cols - 1) / 2) * 6.5            # leque angular dentro do setor
            dr = 0.085 + row * 0.075                     # empilha em raio
            ang = math.radians(ang0 + da)
            rad = base - dr if ring == "out" else base - dr + 0.18
            x, y = rad * math.cos(ang), rad * math.sin(ang)
            maior = r["cor"]["modo"] == "maior"
            faint = r["cor"]["conf"] < 0.06
            nfaint += faint; nmaj += maior; nmin += not maior
            axA.scatter([x], [y], s=58, c=WARM if maior else COOL, alpha=0.35 if faint else 0.92,
                        edgecolors="white", linewidths=0.7, zorder=3)
    axA.set_title("COR — círculo de quintas (tom + modo)\nexterno = maior · interno = relativo menor · esmaecido = pede ouvido",
                  fontsize=13, weight="bold", color="#3a2f1a", pad=12)
    axA.text(0, -1.4, f"{nmaj} maiores · {nmin} menores  (o catálogo só tinha a armadura)", ha="center", fontsize=10.5, color="#6b5a36")

    # ---------- Painel B: mapa de forma ----------
    for pid, r in pecas.items():
        f = r.get("forma", {})
        ipct = f.get("intervalos_pct", {})
        if not ipct:
            continue
        x = ipct.get("3ª", 0) + r["forma"].get("arpejo_frac", 0) * 0.5
        y = ipct.get("salto (≥6ª)", 0)
        maior = r["cor"]["modo"] == "maior"
        faint = r["cor"]["conf"] < 0.06
        axB.scatter([x], [y], s=60, c=WARM if maior else COOL, alpha=0.3 if faint else 0.9,
                    edgecolors="white", linewidths=0.7, zorder=3)
    axB.set_xlabel("→ mais ARPEJADO (3ªs / arpejo)", fontsize=11, color="#3a2f1a")
    axB.set_ylabel("→ mais SALTADO (saltos ≥6ª)", fontsize=11, color="#3a2f1a")
    axB.set_title("FORMA — assinatura estrutural\nescalar fica junto da origem · arpejado à direita · saltado no alto",
                  fontsize=13, weight="bold", color="#3a2f1a", pad=12)
    axB.set_facecolor("#fffdf8"); axB.grid(True, color="#eee4d2", lw=0.7)
    for sp in axB.spines.values():
        sp.set_color("#d8cdb8")
    axB.annotate("escalar", (0.02, 0.02), fontsize=10, color="#9a8a60", style="italic")

    leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=WARM, markersize=11, label="maior"),
           Line2D([0], [0], marker="o", color="w", markerfacecolor=COOL, markersize=11, label="menor"),
           Line2D([0], [0], marker="o", color="w", markerfacecolor="#999", markersize=11, alpha=0.4, label="confiança baixa")]
    axB.legend(handles=leg, loc="upper right", frameon=True, fontsize=10)

    fig.suptitle("As duas geometrias do bloco de Lego — acervo Sambrass + Cumbias (125 peças)",
                 fontsize=15.5, weight="bold", color="#2a2212", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=130, facecolor=fig.get_facecolor())
    print(f"→ {OUT.relative_to(HERE.parents[1])}  ({nmaj} maiores, {nmin} menores, {nfaint} esmaecidas)")


if __name__ == "__main__":
    main()
