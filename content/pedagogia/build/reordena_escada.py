# -*- coding: utf-8 -*-
"""Reordena a trilha pela ESCADA pedagógica (Book 1 → Book 2 → Arban) como eixo
PRIMÁRIO, com a heurística de complexidade ordenando DENTRO de cada nível (sem
cadeado — a ordem é sugestão). Re-bucketiza em 6 lotes ANINHADOS nos níveis
(Book 1 → lotes 1-2 · Book 2 → 3-5 · Arban → 6) e REGENERA a técnica de cada
lote (tom-foco + feature derivados da nova membresia), via Verovio.

Reescreve content/pedagogia/{app_musicas.json, app_tecnica.json}.
Os blocos de exercício (b_escala/b_arpejo/…) são os mesmos de build/super_v2.py.

    pip install verovio --break-system-packages
    python3 content/pedagogia/build/reordena_escada.py
"""
import json, re, pathlib
from collections import Counter
import numpy as np
import verovio

ROOT = pathlib.Path(__file__).resolve().parents[3]
PED = ROOT / "content" / "pedagogia"
CUR = ROOT / "content" / "curadoria"

mus = json.load(open(PED / "app_musicas.json", encoding="utf-8"))
esc = {e["num"]: e for e in json.load(open(CUR / "escada.json", encoding="utf-8"))["pieces"]}
dif = {p["num"]: p for p in json.load(open(CUR / "dificuldade.json", encoding="utf-8"))["pieces"]}

# ---------------- 1) nova ordem + bucketização aninhada ----------------
RANK = {"book1": 0, "book2": 1, "arban": 2}
for i, m in enumerate(mus):
    m["_idx"] = i  # ordem de complexidade atual (heurística já ordenada)
nodes = sorted(mus, key=lambda m: (RANK[esc[m["num"]]["nivel_minimo"]], m["_idx"]))

SPLITS = {"book1": 2, "book2": 3, "arban": 1}   # 6 lotes aninhados nos 3 níveis
by_lvl = {"book1": [], "book2": [], "arban": []}
for m in nodes:
    by_lvl[esc[m["num"]]["nivel_minimo"]].append(m)
lote = 0
lote_membros = {}
for lvl in ("book1", "book2", "arban"):
    for chunk in np.array_split(by_lvl[lvl], SPLITS[lvl]):
        lote += 1
        lote_membros[lote] = [m["num"] for m in chunk]
        for m in chunk:
            m["nivel"] = lvl
            m["lote"] = lote
for m in nodes:
    m.pop("_idx", None)
json.dump(nodes, open(PED / "app_musicas.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"app_musicas.json: {len(nodes)} nós reordenados (Book 1 → Book 2 → Arban)")

# ---------------- 2) tom-foco + feature por lote ----------------
# (mesma lógica de build/super_v2.py: tom mais comum entre os membros; feature dominante)
KEYS = {"C": ("C", "Dó", "C D E F G A B c"), "F": ("F", "Fá", "F G A B c d e f"),
        "G": ("G", "Sol", "G A B c d e ^f g"), "Bb": ("Bb", "Sib", "B, C D E F G A B"),
        "D": ("D", "Ré", "D E ^F G A B ^c d"), "A": ("A", "Lá", "A B ^c d e ^f ^g a"),
        "Eb": ("Eb", "Mib", "E F G A B c d e"), "Ab": ("Ab", "Láb", "A B c d e f g a")}
DOMINANTE = {"C": "G", "F": "C", "G": "D", "Bb": "F", "D": "A", "A": "E", "Eb": "Bb", "Ab": "Eb"}
FEAT_PT = {"sincope": "síncope (C2)", "tercina": "tercina (C5)",
           "semicolcheia": "semicolcheia / staccato duplo (C4)", "contratempo": "contratempo (C6)",
           "cromatismo": "cromatismo de passagem", "extensa": "forma extensa / fôlego",
           "modulacao": "modulação de armadura"}


def kdom(nums):
    c = Counter(esc[n]["tom_escrito"] for n in nums if esc[n]["tom_escrito"] in KEYS)
    return c.most_common(1)[0][0] if c else "F"


def feat(nums):
    f = Counter()
    for n in nums:
        for k in ["tercina", "semicolcheia", "contratempo", "cromatismo", "extensa", "modulacao"]:
            if dif[n]["features"].get(k):
                f[k] += 1
    return f.most_common(1)[0][0] if f else "sincope"


# ---------------- 3) blocos de exercício (verbatim de build/super_v2.py) ----------------
def _terças(k, n):
    return f"K:{k} M:4/4 L:1/8 " + " ".join(sum([[n[i], n[i + 2]] for i in range(len(n) - 2)], [])) + " |]"


def b_escala(k, sc, i):
    n = sc.split(); a = " ".join(n); d = " ".join(reversed(n))
    asc2 = " ".join(f"({n[j]} {n[j+1]})" for j in range(0, len(n) - 1, 2))
    rn = list(reversed(n)); desc2 = " ".join(f"({rn[j]} {rn[j+1]})" for j in range(0, len(rn) - 1, 2))
    ter = _terças(k, n)
    alta = n[7]
    if i == 1:
        return [("Escala · Nível 1 — semínimas", "Uma oitava, uma nota por tempo. Leia a armadura, som cheio, ar constante. Conte 1-2-3-4 em voz alta.", f"K:{k} M:4/4 L:1/4 {a} | {d} |]"),
                ("Escala · Nível 2 — colcheias ligadas", "Duas notas por tempo, sob a mesma ligadura (legato): articule só a primeira de cada par.", f"K:{k} M:4/4 L:1/8 {asc2} {desc2} |]")]
    if i == 2:
        return [("Escala · Nível 1 — colcheias ligadas", "Revisão: a escala em legato, articulando só a primeira de cada par.", f"K:{k} M:4/4 L:1/8 {asc2} {desc2} |]"),
                ("Escala · Nível 2 — em terças", "Padrão 1-3-2-4-3-5… Desenvolve leitura e afinação de intervalos.", ter),
                ("Escala · Nível 3 — ida e volta sem parar", "Suba e desça em colcheias, sem respirar no topo. Um só fôlego se possível.", f"K:{k} M:4/4 L:1/8 {a} {d} |]")]
    if i == 3:
        return [("Escala · Nível 1 — em terças", "Padrão em terças, agora como aquecimento.", ter),
                ("Escala · Nível 2 — articulada (staccato)", "Mesma escala, notas curtas e destacadas (staccato). Ataque seco, ar contínuo por baixo.", f"K:{k} M:4/4 L:1/8 " + " ".join(f".{x}" for x in n) + " " + " ".join(f".{x}" for x in reversed(n)) + " |]"),
                ("Escala · Nível 3 — terça + retorno", "1-3-1, 2-4-2… combina salto de terça e volta ao grau.", f"K:{k} M:4/4 L:1/8 " + " ".join(f"{n[j]} {n[j+2]} {n[j]}" for j in range(0, len(n) - 2, 2)) + " |]")]
    if i == 4:
        return [("Escala · Nível 1 — duas oitavas (ida)", "Estenda o registro: suba do grave ao agudo em duas oitavas.", f"K:{k} M:4/4 L:1/8 {a} {alta} |]".replace(f"{alta} |]", " ".join(x.lower() if x.isupper() else x + "'" for x in n[1:]) + " |]")),
                ("Escala · Nível 2 — staccato rápido", "Escala em colcheias destacadas, leve e rápida.", f"K:{k} M:2/4 L:1/8 " + " ".join(f".{x}" for x in n) + " |]"),
                ("Escala · Nível 3 — terças ligadas", "Terças, agora ligadas de duas em duas — legato nos saltos.", f"K:{k} M:4/4 L:1/8 " + " ".join(f"({n[j]} {n[j+2]})" for j in range(len(n) - 2)) + " |]")]
    if i == 5:
        return [("Escala · Nível 1 — cromática (subida)", "Suba de meio em meio tom (escala cromática). Afinação milimétrica.", f"K:{k} M:4/4 L:1/8 {n[0]} ^{n[0]} {n[1]} ^{n[1]} {n[2]} {n[3]} ^{n[3]} {n[4]} ^{n[4]} {n[5]} ^{n[5]} {n[6]} {n[7]} |]"),
                ("Escala · Nível 2 — diatônica + cromática", "Alterna grau da escala e nota cromática de passagem.", f"K:{k} M:4/4 L:1/8 {n[0]} ^{n[0]} {n[1]} ^{n[1]} {n[2]} {n[3]} ^{n[3]} {n[4]} |]"),
                ("Escala · Nível 3 — terças em colcheias rápidas", "Terças no andamento, sem parar.", ter.replace("L:1/8", "L:1/8 Q:1/4=120"))]
    return [("Escala · Nível 1 — duas oitavas articulada", "Duas oitavas com staccato leve no caminho. Registro e controle.", f"K:{k} M:4/4 L:1/8 " + " ".join(f".{x}" for x in n) + " " + " ".join(f".{x.lower() if x.isupper() else x}" for x in n[1:]) + " |]"),
            ("Escala · Nível 2 — cromática ida e volta", "Cromática subindo e descendo, ligada, em um só gesto.", f"K:{k} M:4/4 L:1/16 ({n[0]} ^{n[0]} {n[1]} ^{n[1]} {n[2]} {n[3]} ^{n[3]} {n[4]} ^{n[4]} {n[5]} ^{n[5]} {n[6]} {n[7]} ^{n[6]} {n[6]} {n[5]}) |]"),
            ("Escala · Nível 3 — padrão misto", "Combina terça, grau e cromatismo: o tecido das peças difíceis.", f"K:{k} M:4/4 L:1/8 {n[0]} {n[2]} ^{n[0]} {n[1]} {n[3]} {n[2]} {n[4]} {n[3]} |]")]


def b_arpejo(k, sc, i):
    n = sc.split(); t = [n[0], n[2], n[4], n[7]]; b7 = "_" + n[7]
    if i == 1:
        return [("Arpejo (A1) · Nível 1 — tríade ↑↓", "Tríade maior subindo e descendo, uma nota por tempo. A base de toda harmonia do samba.", f"K:{k} M:4/4 L:1/4 {t[0]} {t[1]} {t[2]} {t[3]} | {t[3]} {t[2]} {t[1]} {t[0]} |]")]
    if i == 2:
        return [("Arpejo · Nível 1 — tríade em colcheias", "Tríade ligada, mais fluente.", f"K:{k} M:2/4 L:1/8 ({t[0]} {t[1]} {t[2]} {t[3]}) | ({t[3]} {t[2]} {t[1]} {t[0]}) |]"),
                ("Arpejo · Nível 2 — primeira inversão", "Comece pela terça (3-5-8-3): ouça como muda a cor do acorde.", f"K:{k} M:2/4 L:1/8 {t[1]} {t[2]} {t[3]} {t[1]} | {t[2]} {t[1]} {t[0]} z |]")]
    if i == 3:
        return [("Arpejo · Nível 1 — tríade ágil", "Aquecimento: tríade quebrada.", f"K:{k} M:2/4 L:1/8 |: ({t[0]} {t[1]} {t[2]} {t[1]}) :|]"),
                ("Arpejo · Nível 2 — com 7ª (A3)", "Acrescenta a 7ª da dominante. Ouça a tensão que pede resolução.", f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {t[3]} {b7} {t[2]} {t[1]} {t[0]} |]")]
    if i == 4:
        return [("Arpejo · Nível 1 — com 7ª", "Revisão da 7ª, agora ligada.", f"K:{k} M:4/4 L:1/8 ({t[0]} {t[1]} {t[2]} {t[3]} {b7} {t[2]} {t[1]} {t[0]}) |]"),
                ("Arpejo · Nível 2 — arpejo + escala", "Sobe pelo arpejo, desce pela escala. Integra as duas ferramentas.", f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {t[3]} {n[6]} {n[5]} {n[4]} {n[3]} |]")]
    if i == 5:
        return [("Arpejo · Nível 1 — quebrado contínuo", "Arpejo quebrado em colcheias, sem parar — flexibilidade.", f"K:{k} M:2/4 L:1/8 |: ({t[0]} {t[1]} {t[2]} {t[1]}) :| ({t[2]} {t[3]} {t[2]} {t[1]}) |]"),
                ("Arpejo · Nível 2 — relativa menor", "Arpejo do VI grau (relativa menor): outra cor sobre o mesmo tom.", f"K:{k} M:2/4 L:1/8 {n[5]} {n[0]} {n[2]} {n[0]} | {n[5]} {n[2]} {n[0]} z |]")]
    return [("Arpejo · Nível 1 — duas oitavas", "Tríade em duas oitavas: estende o registro com a harmonia.", f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {t[3]} {t[1].lower() if t[1].isupper() else t[1]} {t[2].lower() if t[2].isupper() else t[2]} |]"),
            ("Arpejo · Nível 2 — 7ª + resolução", "Arpejo de 7ª resolvendo na tônica. O gesto cadencial.", f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {b7} {t[2]} {t[1]} {t[0]} {t[0]} |]")]


def b_salto(k, sc, i):
    n = sc.split()
    if i <= 2:
        return [("Saltos · Nível 1 — oitava", "Tônica → oitava → tônica. Centre o som nas duas alturas, sem apertar.", f"K:{k} M:4/4 L:1/4 {n[0]} {n[7]} {n[0]} {n[7]} | {n[7]} {n[0]} {n[7]} {n[0]} |]")]
    if i <= 4:
        return [("Saltos · Nível 1 — quintas e sextas", "Intervalos largos alternados. Sem 'escorregar' entre as notas (sem glissando).", f"K:{k} M:4/4 L:1/4 {n[0]} {n[4]} {n[1]} {n[5]} | {n[2]} {n[6]} {n[0]} {n[7]} |]"),
                ("Saltos · Nível 2 — lip slur", "Lip slur: ligue o grupo SEM articular — só o ar move entre as notas (Schlossberg/Bai Lin).", f"K:{k} M:2/4 L:1/8 ({n[0]} {n[4]} {n[2]} {n[7]}) | ({n[4]} {n[2]} {n[0]}) z |]")]
    return [("Saltos · Nível 1 — lip slur amplo", "Lip slur cobrindo a tríade em duas oitavas, ligado.", f"K:{k} M:2/4 L:1/8 ({n[0]} {n[4]} {n[7]} {n[4]}) | ({n[2]} {n[0]}) z |]"),
            ("Saltos · Nível 2 — saltos com articulação", "Saltos amplos articulados, no andamento. Precisão de ataque em cada altura.", f"K:{k} M:2/4 L:1/8 .{n[0]} .{n[7]} .{n[2]} .{n[5]} | .{n[4]} .{n[0]} z2 |]")]


def b_articulacao(k, sc, i):
    n = sc.split()
    if i == 1:
        return [("Articulação · Nível 1 — ligado × destacado", "A mesma frase duas vezes: primeiro toda ligada, depois toda destacada. Sinta a diferença no ataque.", f"K:{k} M:2/4 L:1/8 ({n[0]} {n[1]} {n[2]} {n[3]}) | .{n[0]} .{n[1]} .{n[2]} .{n[3]} |]")]
    if i == 2:
        return [("Articulação · Nível 1 — acento", "Acente (>) a primeira de cada tempo; as outras, leves.", f"K:{k} M:2/4 L:1/8 !>!{n[0]} {n[1]} !>!{n[2]} {n[3]} | !>!{n[4]} {n[3]} !>!{n[2]} {n[1]} |]")]
    if i == 3:
        return [("Articulação · Nível 1 — staccato leve", "Notas curtas e iguais, leves. O ar não para por baixo.", f"K:{k} M:2/4 L:1/8 .{n[0]} .{n[1]} .{n[2]} .{n[3]} | .{n[4]} .{n[3]} .{n[2]} .{n[1]} |]"),
                ("Articulação · Nível 2 — misto ligado+destacado", "Duas ligadas, duas destacadas — o padrão de articulação mais comum do choro/samba.", f"K:{k} M:2/4 L:1/8 ({n[0]} {n[1]}) .{n[2]} .{n[3]} | ({n[4]} {n[3]}) .{n[2]} .{n[1]} |]")]
    if i == 4:
        return [("Articulação · Nível 1 — tu-ku lento", "Introdução ao duplo staccato: alterne sílabas TU-KU em colcheias, devagar.", f"K:{k} M:2/4 L:1/8 .{n[0]} .{n[0]} .{n[2]} .{n[2]} | .{n[4]} .{n[4]} .{n[2]}2 |]"),
                ("Articulação · Nível 2 — ligado entre saltos", "Ligue na subida, destaque no retorno.", f"K:{k} M:2/4 L:1/8 ({n[0]} {n[2]} {n[4]}) .{n[2]} | .{n[0]} z3 |]")]
    if i == 5:
        return [("Articulação · Nível 1 — tu-ku médio", "Duplo staccato em semicolcheias, andamento médio. TU-KU-TU-KU igual.", f"K:{k} M:2/4 L:1/16 .{n[0]}.{n[0]}.{n[0]}.{n[0]} .{n[2]}.{n[2]}.{n[2]}.{n[2]} |]"),
                ("Articulação · Nível 2 — acento deslocado", "Acento no contratempo, o suingue do samba na articulação.", f"K:{k} M:2/4 L:1/8 {n[0]} !>!{n[2]} {n[1]} !>!{n[4]} | {n[2]} !>!{n[0]} z2 |]")]
    return [("Articulação · Nível 1 — tu-ku rápido", "Duplo staccato veloz e nivelado. Se a língua travar, volte ao tu-ku lento.", f"K:{k} M:2/4 L:1/16 .{n[0]}.{n[1]}.{n[2]}.{n[3]} .{n[4]}.{n[3]}.{n[2]}.{n[1]} |]"),
            ("Articulação · Nível 2 — todas as articulações", "Ligado, acentuado e destacado na mesma frase — controle total.", f"K:{k} M:2/4 L:1/8 ({n[0]} {n[1]}) !>!{n[2]} .{n[3]} | ({n[4]} {n[3]}) !>!{n[2]} .{n[0]} |]")]


def b_dinamica(k, sc, i):
    n = sc.split()
    if i == 1:
        return [("Som · Nível 1 — nota longa", "Sustente cada nota 4 tempos a ~60 bpm. Ataque limpo, som imóvel, corte seco.", f"K:{k} M:4/4 L:1/1 {n[0]} | {n[4]} | {n[2]} | {n[0]} |]")]
    if i == 2:
        return [("Som · Nível 1 — crescendo", "Cresça do piano ao forte ao longo da nota longa. Só o ar muda, o som não 'estoura'.", f'K:{k} M:4/4 L:1/1 "<"{n[0]} | "<"{n[4]} |]')]
    if i == 3:
        return [("Som · Nível 1 — messa di voce", "Pianíssimo → forte no centro → pianíssimo. Controle total do ar numa nota só.", f'K:{k} M:4/4 L:1/1 "<"{n[0]} | ">"{n[0]} |]')]
    if i == 4:
        return [("Som · Nível 1 — sforzando", "Ataque forte e recue imediato (sf). Depois a nota cresce de novo.", f'K:{k} M:4/4 L:1/2 "sf"{n[4]}2 | "<"{n[4]}2 |]')]
    if i == 5:
        return [("Som · Nível 1 — dinâmica na frase", "Faça a frase respirar: cresça na subida, recue na descida.", f'K:{k} M:4/4 L:1/4 "p"{n[0]} {n[2]} "<"{n[4]} {n[7]} | ">"{n[4]} {n[2]} {n[0]}2 |]')]
    return [("Som · Nível 1 — controle extremo", "Nota longa pianíssimo, perfeitamente estável — o teste final do ar. Depois messa di voce.", f'K:{k} M:4/4 L:1/1 "pp"{n[7]} | "<"{n[0]} |]')]


def b_ritmo(k, sc, ft):
    n = sc.split()
    M = {
        "sincope": [("Ritmo · síncope (C2) — Nível 1", "Colcheia–semínima–colcheia. O acento (>) cai na nota longa do meio.", f"K:{k} M:2/4 L:1/8 |: {n[0]}/ !>!{n[2]}2 {n[0]}/ :| {n[2]}/ !>!{n[4]}2 {n[2]}/ |]"),
                     ("Ritmo · síncope — Nível 2 · encadeada", "Síncopes em sequência, sem respirar no meio.", f"K:{k} M:2/4 L:1/8 {n[0]}/ !>!{n[2]}2 {n[0]}/ | {n[2]}/ !>!{n[4]}2 {n[2]}/ | {n[0]}4 |]")],
        "tercina": [("Ritmo · tercina (C5) — Nível 1", "Três notas iguais por tempo. Diga 'tri-o-la', devagar.", f"K:{k} M:2/4 L:1/8 | (3{n[0]}{n[1]}{n[2]} (3{n[2]}{n[1]}{n[0]} | {n[0]}2 z2 |]"),
                    ("Ritmo · tercina — Nível 2 · em arpejo", "Tercinas desenhando a tríade.", f"K:{k} M:2/4 L:1/8 | (3{n[0]}{n[2]}{n[4]} (3{n[7]}{n[4]}{n[2]} | {n[0]}2 z2 |]")],
        "semicolcheia": [("Ritmo · semicolcheias (C4) — Nível 1", "Quatro iguais por tempo. Articule com a sílaba dupla TU-KU-TU-KU (duplo staccato do Arban).", f"K:{k} M:2/4 L:1/16 |: {n[0]}{n[1]}{n[2]}{n[3]} {n[0]}{n[1]}{n[2]}{n[3]} :|]"),
                         ("Ritmo · C3+C4 — Nível 2 · galope + corrida", "Pontuada+semi (galope) alternando com quatro semicolcheias.", f"K:{k} M:2/4 L:1/16 | {n[0]}3 {n[2]} {n[0]}{n[1]}{n[2]}{n[3]} | {n[2]}3 {n[0]} {n[0]}4 |]")],
        "contratempo": [("Ritmo · contratempo (C6) — Nível 1", "Pausa no tempo, ataque no 'e'. Sinta o silêncio antes da nota.", f"K:{k} M:2/4 L:1/8 | z {n[0]} z {n[2]} | z {n[4]} {n[2]}2 |]"),
                        ("Ritmo · contratempo — Nível 2 · contínuo", "Ataques deslocados — o suingue do samba.", f"K:{k} M:2/4 L:1/8 | z !>!{n[0]} z !>!{n[2]} | z !>!{n[4]} z !>!{n[2]} | {n[0]}2 z2 |]")],
        "cromatismo": [("Ritmo · cromatismo (A4) — Nível 1", "Nota → vizinha cromática → nota (bordadura).", f"K:{k} M:2/4 L:1/8 | {n[0]} ^{n[0]} {n[1]}2 | {n[2]} _{n[2]} {n[1]}2 |]"),
                       ("Ritmo · cromatismo — Nível 2 · descida", "Linha que desce de meio em meio tom. Afinação milimétrica.", f"K:{k} M:2/4 L:1/8 | {n[4]} _{n[4]} {n[2]}2 | {n[1]} _{n[1]} {n[0]}2 |]")],
        "extensa": [("Ritmo · fôlego — Nível 1 · longa após corrida", "Toque a corrida e SUSTENTE a longa cheia até o fim, sem desinflar.", f"K:{k} M:4/4 L:1/8 {n[0]} {n[1]} {n[2]} {n[3]} {n[4]}4- | {n[4]}4 z4 |]"),
                    ("Ritmo · respiração — Nível 2 · frase com respiros", "Respire só onde há a vírgula (breath mark). A respiração é parte do ritmo.", f"K:{k} M:2/4 L:1/8 {n[0]} {n[2]} {n[4]} {n[2]} | {n[0]}2 z, | {n[1]} {n[2]} {n[4]} {n[2]} | {n[0]}4 |]")],
        "modulacao": [("Ritmo · síncope — Nível 1", "Fixe a célula-base do samba antes de tratar a modulação.", f"K:{k} M:2/4 L:1/8 {n[0]}/ !>!{n[2]}2 {n[0]}/ | {n[2]}/ !>!{n[4]}2 {n[2]}/ |]"),
                      ("Ritmo · modulação — Nível 2 · troca de armadura", "Releia a armadura na barra dupla: o trecho modula para o tom da dominante.", f"K:{k} M:2/4 L:1/8 {n[0]} {n[2]} {n[4]} {n[2]} | K:{DOMINANTE.get(k,'G')} {n[4]} {n[4]} {n[4]} {n[4]} | {n[4]}4 |]")],
    }
    return M.get(ft, M["sincope"])


# ---------------- 4) Verovio ABC → SVG (de tela, como gerar_pedagogia2.py) ----------------
tk = verovio.toolkit()


def _norm(b):
    b = b.replace("\\n", "\n").strip(); f = {}
    for k in ["M", "L", "Q"]:
        m = re.search(rf'\b{k}:\s*(\S+)', b)
        if m:
            f[k] = m.group(1)
    mk = re.search(r'\bK:\s*([A-Ga-g][b#]?\w*)', b); kv = mk.group(1) if mk else "C"
    mus_ = re.sub(r'\b[MLQK]:\s*\S+', '', b).strip()
    head = [f"{k}:{f[k]}" for k in ["M", "L", "Q"] if k in f] + [f"K:{kv}"]
    return "\n".join(head) + "\n" + mus_


def svg(abc):
    tk.setOptions({"inputFrom": "abc", "scale": 38, "adjustPageHeight": True, "pageWidth": 1400,
                   "header": "none", "footer": "none", "spacingStaff": 1, "spacingSystem": 1,
                   "pageMarginLeft": 6, "pageMarginRight": 6, "pageMarginTop": 4, "pageMarginBottom": 4, "breaks": "none"})
    tk.loadData("X:1\n" + _norm(abc) + "\n")
    s = tk.renderToSVG(1)
    s = re.sub(r'width="\d+px"', 'width="100%"', s, count=1)
    s = re.sub(r' height="\d+px"', '', s, count=1)
    if 'preserveAspectRatio' not in s[:300]:
        s = s.replace('<svg ', '<svg preserveAspectRatio="xMinYMin meet" ', 1)
    return s


# ---------------- 5) regenera app_tecnica.json (6 lotes aninhados) ----------------
def mk(blocos):
    return [{"nome": nm, "dica": dc, "svg": svg(abc)} for nm, dc, abc in blocos]


tecnica = []
NIVEL_DE = {1: "book1", 2: "book1", 3: "book2", 4: "book2", 5: "book2", 6: "arban"}
for i in range(1, 7):
    nums = lote_membros[i]
    k = kdom(nums); abck, nome_tom, sc = KEYS.get(k, ("C", "Dó", "C D E F G A B c"))
    ft = feat(nums)
    eixos = [
        {"eixo": "Som & Dinâmica", "exercicios": mk(b_dinamica(abck, sc, i))},
        {"eixo": "Escala", "exercicios": mk(b_escala(abck, sc, i))},
        {"eixo": "Arpejo", "exercicios": mk(b_arpejo(abck, sc, i))},
        {"eixo": "Articulação", "exercicios": mk(b_articulacao(abck, sc, i))},
        {"eixo": "Saltos", "exercicios": mk(b_salto(abck, sc, i))},
        {"eixo": "Ritmo", "exercicios": mk(b_ritmo(abck, sc, ft))},
    ]
    tecnica.append({"lote": i, "nivel": NIVEL_DE[i], "tom": nome_tom, "feat": FEAT_PT.get(ft, ft), "eixos": eixos})
    print(f"  Lote {i} [{NIVEL_DE[i]}] n={len(nums)} tom={nome_tom} feat={FEAT_PT.get(ft, ft)} "
          f"· {sum(len(e['exercicios']) for e in eixos)} exercícios")

json.dump(tecnica, open(PED / "app_tecnica.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"app_tecnica.json: {len(tecnica)} lotes regenerados")
