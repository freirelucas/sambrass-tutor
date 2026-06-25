#!/usr/bin/env python3
"""Fundação de BLOCOS — extrai e valida o vocabulário de "blocos de Lego" do MusicXML.

Para cada peça das DUAS jornadas (Sambrass + Cumbias), a partir das notas reais:
  • COR  = tônica + MODO.  Detectados por Krumhansl-Schmuckler (correlação do histograma
           de classes de altura, ponderado por duração, contra os perfis maior/menor em
           12 rotações) — recupera a TÔNICA real (o catálogo só guarda a armadura).
  • FORMA = estrutura. Assinatura: histograma de intervalos, contorno (sobe/desce/repete),
           salto máximo, fração arpejada, tessitura, classe (arpejado/escalar/saltado/misto)
           e o RIFF (reusa phrases.py).
  • VALIDAÇÃO (best-effort): confere se as CÉLULAS marcadas à mão (C2–C6) aparecem no ritmo
           real — casando a FORMA da célula (proporção 1:2:1 da síncope, tercina, etc.) em
           vários níveis métricos. Sinaliza tag marcada-mas-ausente (gap de confiança).
  • BLOCO = (cor · forma). Emite o mapa bloco→peças.

Saída: content/curadoria/build/blocos.json + relatório no stdout. Somente leitura; reproduzível.
Uso: python3 content/curadoria/blocos.py
"""
import json, pathlib, glob, sys
from collections import defaultdict, Counter

HERE = pathlib.Path(__file__).resolve().parent
CONTENT = HERE.parent
sys.path.insert(0, str(CONTENT))
from build_notes import compile_file, load_fingering, name, SHARP  # noqa: E402
sys.path.insert(0, str(CONTENT / "cumbia"))
from phrases import extract_riff, repeticao_ratio  # noqa: E402
from abc_events import events_from_abc, key_from_abc  # noqa: E402

OUT = HERE / "build" / "blocos.json"

PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6,
      "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
PCNAME = {0: "C", 1: "Db", 2: "D", 3: "Eb", 4: "E", 5: "F", 6: "F#", 7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B"}
# perfis de Krumhansl-Kessler (proeminência por grau, tônica = índice 0)
KK_MAJ = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
KK_MIN = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def _corr(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da = sum((x - ma) ** 2 for x in a) ** 0.5; db = sum((x - mb) ** 2 for x in b) ** 0.5
    return num / (da * db) if da and db else 0.0


def detect_mode(events, key_pc, constrain=False):
    """K-S: melhor (tônica, modo) sobre 12 rotações, com viés de CADÊNCIA (a nota final
    e a inicial puxam a tônica — pista forte). conf = margem maior-vs-menor.
    armadura_bate: a tônica detectada é coerente com a armadura do catálogo?
    constrain=True: quando a armadura é CONFIRMADA (K: à mão), só decide entre a tônica
    maior dessa armadura e seu relativo menor — robusto, sem detecção livre ruidosa."""
    npc = [e["concert_midi"] % 12 for e in events if "concert_midi" in e]
    w = [0.0] * 12
    for e in events:
        if "concert_midi" in e:
            w[e["concert_midi"] % 12] += e.get("dur_beats", 0) or 0.25
    if sum(w) == 0:
        return {"tonica": "?", "modo": "?", "conf": 0.0, "nota": "sem notas"}
    last, first = npc[-1], npc[0]

    def bias(c, r):
        return c + (0.15 if r == last else 0) + (0.05 if r == first else 0)   # cadência/início puxam a tônica
    specs = ([(key_pc, "maior"), ((key_pc - 3) % 12, "menor")] if constrain
             else [(r, m) for r in range(12) for m in ("maior", "menor")])
    cands = []
    for r, m in specs:
        rot = w[r:] + w[:r]
        cands.append((bias(_corr(rot, KK_MAJ if m == "maior" else KK_MIN), r), r, m))
    cands.sort(reverse=True)
    best_corr, root, modo = cands[0]
    best_maj = max(c for c, _, m in cands if m == "maior")
    best_min = max(c for c, _, m in cands if m == "menor")
    conf = round(abs(best_maj - best_min) / (abs(best_maj) + abs(best_min) + 1e-9), 3)
    rot = w[root:] + w[:root]; tot = sum(rot) or 1; g = {k: rot[k] / tot for k in range(12)}
    dica = None
    if modo == "menor" and g[9] > g[8] * 1.3 and g[9] > 0.04:
        dica = "dórico"
    elif modo == "maior" and g[10] > g[11] * 1.3 and g[10] > 0.04:
        dica = "mixolídio"
    elif modo == "maior" and g[6] > g[5] and g[6] > 0.05:
        dica = "lídio"
    rel_major = root if modo == "maior" else (root + 3) % 12
    return {"tonica": PCNAME[root], "modo": modo, "dica_modal": dica, "conf": conf,
            "ks_corr": round(best_corr, 3), "armadura_bate": (rel_major == key_pc)}


# ---- células por FORMA (proporção), invariante ao nível métrico ----
def _streak(durs, pat, tol=0.06):
    return any(all(abs(durs[i + j] - pat[j]) <= tol for j in range(len(pat)))
               for i in range(len(durs) - len(pat) + 1))


def _is_triplet(d):
    return abs(d * 3 - round(d * 3)) < 0.06 and abs(d * 2 - round(d * 2)) > 0.06   # múltiplo de 1/3, não de 1/2


DETECTAVEIS = ("C2", "C3", "C4", "C5", "C6")   # C1 ubíquo, C7 anacruse: fora da validação


def cells_present(events):
    notes = [round(e["dur_beats"], 3) for e in events if "written_midi" in e]
    stream = [(round(e.get("dur_beats", 0), 3), "rest" in e) for e in events]
    f = set()
    if any(d in (0.25, 0.5) and abs(notes[i] - notes[i + 1]) <= 0.03
           for i, d in enumerate(notes[:-1])):
        f.add("C1")                                                  # duas iguais
    for d in (0.25, 0.5):                                            # síncope 1:2:1
        if _streak(notes, [d, 2 * d, d]):
            f.add("C2"); break
    if _streak(notes, [0.75, 0.25]) or _streak(notes, [0.375, 0.125]):
        f.add("C3")                                                  # pontuado 3:1
    for i in range(len(notes) - 3):                                  # 4 semicolcheias seguidas
        if all(abs(notes[i + j] - 0.25) <= 0.06 for j in range(4)):
            f.add("C4"); break
    if any(_is_triplet(d) for d in notes):
        f.add("C5")                                                  # tercina (múltiplo de 1/3)
    for i in range(len(stream) - 1):                                 # contratempo: pausa no tempo + nota
        (d0, r0), (d1, r1) = stream[i], stream[i + 1]
        if r0 and not r1 and d0 in (0.25, 0.5) and abs(d1 - d0) <= 0.26:
            f.add("C6"); break
    return f


def structure(events):
    notes = [e["concert_midi"] for e in events if "concert_midi" in e]
    if len(notes) < 2:
        return {}
    iv = [notes[i + 1] - notes[i] for i in range(len(notes) - 1)]
    absiv = [abs(x) for x in iv]; n = len(iv)
    b = {"uníssono": 0, "grau (2ª)": 0, "3ª": 0, "4ª": 0, "5ª": 0, "salto (≥6ª)": 0}
    for a in absiv:
        b["uníssono" if a == 0 else "grau (2ª)" if a <= 2 else "3ª" if a <= 4 else
          "4ª" if a == 5 else "5ª" if a <= 7 else "salto (≥6ª)"] += 1
    sobe = sum(x > 0 for x in iv); desce = sum(x < 0 for x in iv); rep = sum(x == 0 for x in iv)
    arp = sum(1 for i in range(len(notes) - 2)
              if (notes[i + 1] - notes[i]) in (3, 4) and (notes[i + 2] - notes[i + 1]) in (3, 4))
    pct = {k: v / n for k, v in b.items()}
    if pct["3ª"] >= 0.22 or arp >= 3:
        classe = "arpejado"
    elif pct["salto (≥6ª)"] >= 0.12:
        classe = "saltado"
    elif pct["grau (2ª)"] >= 0.55:
        classe = "escalar"
    else:
        classe = "misto"
    return {"intervalos_pct": {k: round(v, 2) for k, v in pct.items()},
            "contorno": {"sobe": round(sobe / n, 2), "desce": round(desce / n, 2), "repete": round(rep / n, 2)},
            "salto_max": max(absiv), "arpejo_frac": round(arp / max(1, len(notes) - 2), 2),
            "tessitura": [name(min(notes), SHARP), name(max(notes), SHARP)],
            "ambito_semitons": max(notes) - min(notes), "classe": classe}


def meter_beats(compasso):
    try:
        num, den = str(compasso).split("/"); return int(num) * 4 / int(den)
    except Exception:
        return 4.0


def onsets_first(events, meter, nbars=2):
    """Posições de ataque (em tempos, dentro do compasso) das ~2 primeiras barras — o 'groove'."""
    pos = 0.0; cur = None; first = None; out = []
    for e in events:
        m = e.get("measure")
        if m != cur:
            cur = m; pos = 0.0
        if first is None and m is not None:
            first = m
        if "written_midi" in e and first is not None and m < first + nbars:
            out.append(round(pos % meter, 3))
        pos += e.get("dur_beats", 0) or 0
    return sorted(set(out))


def find_musicxml(pid):
    cands = glob.glob(str(CONTENT / "notes" / "**" / f"{pid}.musicxml"), recursive=True)
    cands.sort(key=lambda p: ("/omr/" in p))   # prefere não-OMR se houver
    return cands[0] if cands else None


def main():
    fing, tr = load_fingering()
    catalog = [("sambrass", p["id"], p) for p in json.load(open(CONTENT / "pieces.json", encoding="utf-8"))["pieces"]]
    catalog += [("cumbias", f"cu-{p['num']:03d}", p) for p in json.load(open(CONTENT / "cumbia" / "pieces_cumbia.json", encoding="utf-8"))["pieces"]]

    reg, blocos, diverg, sem_xml = {}, defaultdict(list), [], []
    modos = Counter(); classes = Counter()
    MANUAL = CONTENT / "cumbia" / "notes_manual"
    manual_abc = {f.stem: f.read_text(encoding="utf-8") for f in MANUAL.glob("cu-*.abc")} if MANUAL.exists() else {}
    KNAME = {0: "C", 1: "Db", 2: "D", 3: "Eb", 4: "E", 5: "F", 6: "F#", 7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B"}
    for jornada, pid, p in catalog:
        conf_abc = manual_abc.get(pid)
        if conf_abc:                                          # melodia CONFERIDA à mão → legos da fonte real
            ev = events_from_abc(conf_abc); kpc = key_from_abc(conf_abc)
            cor = detect_mode(ev, kpc, constrain=True); key = KNAME[kpc]
        else:
            xml = find_musicxml(pid)
            if not xml:
                sem_xml.append(pid); continue
            ev = compile_file(pathlib.Path(xml), fing, tr)["events"]
            key = p.get("key_concert", "C")
            cor = detect_mode(ev, PC.get(key, 0))
        est = structure(ev)
        presentes = cells_present(ev)
        tags = set(p.get("celulas", []) or [])
        ausentes = sorted(t for t in tags if t in DETECTAVEIS and t not in presentes)
        extras = sorted(c for c in presentes if c not in tags and c in ("C3", "C4", "C5", "C6"))
        riff = extract_riff(ev)
        mb = meter_beats(p.get("compasso", "4/4"))
        ons = onsets_first(ev, mb)
        riff_rec = ({"len": riff["len"], "x": riff["count"], "cobertura": round(repeticao_ratio(ev), 2),
                     "midis": [m for m, _ in riff["notes"]], "durs": [round(dd, 3) for _, dd in riff["notes"]]}
                    if riff else None)
        dom = next((c for c in ["C4", "C5", "C3", "C2", "C6", "C1"] if c in tags), "-")
        modo_lbl = cor["modo"] + (("/" + cor["dica_modal"]) if cor.get("dica_modal") else "")
        cor_lbl = f"{cor['tonica']} {modo_lbl}"
        bloco = f"{cor_lbl} · {est.get('classe', '?')}"
        modos[modo_lbl] += 1; classes[est.get("classe", "?")] += 1
        reg[pid] = {"jornada": jornada, "titulo": p.get("titulo", p.get("title", "")),
                    "armadura": key, "cor": cor, "forma": est, "bloco": bloco, "celula_dominante": dom,
                    "dif": p.get("dificuldade"), "meter": mb, "onsets": ons,
                    "celulas_marcadas": sorted(tags), "celulas_detectadas": sorted(presentes),
                    "tags_nao_confirmadas": ausentes, "celulas_extra_candidatas": extras, "riff": riff_rec}
        blocos[bloco].append(pid)
        if ausentes:
            diverg.append((pid, p.get("titulo", ""), sorted(tags), ausentes))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"_meta": {"sobre": "Índice de blocos (cor=tônica+modo, forma=classe estrutural) + validação best-effort de tags de célula.",
                         "gerado_por": "content/curadoria/blocos.py"},
               "pecas": reg,
               "blocos": {b: ids for b, ids in sorted(blocos.items(), key=lambda kv: -len(kv[1]))}},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------- relatório ----------
    ns = sum(r["jornada"] == "sambrass" for r in reg.values()); nc = len(reg) - ns
    print(f"\n=== FUNDAÇÃO DE BLOCOS — {len(reg)} peças ({ns} sambrass + {nc} cumbias) ===")
    if sem_xml:
        print(f"  sem MusicXML ({len(sem_xml)}): {', '.join(sem_xml[:8])}{'…' if len(sem_xml) > 8 else ''}")
    menor = sum(1 for r in reg.values() if r["cor"]["modo"] == "menor")
    baixa = [pid for pid, r in reg.items() if r["cor"]["conf"] < 0.06]
    naobate = [pid for pid, r in reg.items() if not r["cor"].get("armadura_bate", True)]
    print(f"\nCOR (tônica+modo) — distribuição de modo:")
    for m, n in modos.most_common():
        print(f"  {m:18} {n:3}")
    print(f"  → {menor} peças em MENOR (o catálogo não guardava isso; só a armadura)")
    print(f"  confiança maior/menor baixa (<0.06) p/ ouvido humano: {len(baixa)} {('· ' + ', '.join(baixa[:6])) if baixa else ''}")
    print(f"  tônica detectada NÃO bate com a armadura (revisar tom/peça): {len(naobate)} {('· ' + ', '.join(naobate[:6])) if naobate else ''}")

    print(f"\nFORMA — classe estrutural:")
    for c, n in classes.most_common():
        print(f"  {c:10} {n:3}")

    print(f"\nVALIDAÇÃO DE TAGS (best-effort) — {len(diverg)} peça(s) com célula MARCADA mas não detectada no ritmo:")
    for pid, tit, tags, aus in sorted(diverg)[:40]:
        print(f"  {pid}  {tit[:30]:30}  marcadas={tags}  ⚠ ausentes={aus}")
    if len(diverg) > 40:
        print(f"  … +{len(diverg) - 40}")

    print(f"\nBLOCOS (cor · forma) — {len(blocos)} blocos; maiores:")
    for b, ids in sorted(blocos.items(), key=lambda kv: -len(kv[1]))[:16]:
        print(f"  {len(ids):2}×  {b:24}  {', '.join(ids[:6])}{'…' if len(ids) > 6 else ''}")
    print(f"\n→ {OUT.relative_to(CONTENT.parent)}")


if __name__ == "__main__":
    main()
