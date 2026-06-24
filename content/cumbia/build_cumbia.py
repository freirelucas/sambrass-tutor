#!/usr/bin/env python3
"""Constrói a Jornada das Cumbias (escada = músicas, com o RIFF destacado).

Para cada cu-NNN.musicxml: compila eventos (build_notes), gera ABC (build_abc),
detecta o riff dominante (phrases) e calcula features (agudo/vel/fôlego/repetição).
Ordena as cumbias por dificuldade em 3 tiers idiomáticos (riff → síncope → fogo) e
emite, nos MESMOS formatos que o app já consome, em content/cumbia/build/:
  pieces, percurso, escada, lotes, abc, quality, pedagogia, cells, aquecimento, tecnica.

A pedagogia de cada peça destaca o riff (pauta verovio) + desafio "toque o riff em
loop" + desafios de salto/pico — a ideia das "frases repetitivas".
Uso: python3 content/cumbia/build_cumbia.py
"""
import json, sys, pathlib, shutil, re
HERE = pathlib.Path(__file__).resolve().parent
CONTENT = HERE.parent
sys.path.insert(0, str(CONTENT)); sys.path.insert(0, str(HERE))
from build_notes import compile_file, load_fingering, name, SHARP
from build_abc import to_abc, get_meta
import phrases

NOTES = CONTENT / "notes" / "cumbia"
OUT = HERE / "build"
NOMES = ["Dó", "Dó#", "Ré", "Ré#", "Mi", "Fá", "Fá#", "Sol", "Sol#", "Lá", "Lá#", "Si"]
INTERV = {1: "segunda menor", 2: "segunda", 3: "terça menor", 4: "terça maior", 5: "quarta",
          6: "trítono", 7: "quinta", 8: "sexta menor", 9: "sexta maior", 12: "oitava"}

try:
    import verovio
    _TK = verovio.toolkit()
except Exception:
    _TK = None


def riff_svg(abc):
    if not _TK or not abc:
        return ""
    try:
        _TK.setOptions({"inputFrom": "abc", "scale": 36, "adjustPageHeight": True, "pageWidth": 1500,
                        "header": "none", "footer": "none", "pageMarginLeft": 6, "pageMarginRight": 6,
                        "pageMarginTop": 2, "pageMarginBottom": 2, "breaks": "none",
                        "xmlIdSeed": 1})        # ids determinísticos → build reproduzível
        _TK.loadData(abc)
        s = _TK.renderToSVG(1)
        s = re.sub(r'width="\d+px"', 'width="100%"', s, count=1)
        s = re.sub(r' height="\d+px"', '', s, count=1)
        return s
    except Exception:
        return ""


def scale6(x, lo, hi):
    if x <= lo:
        return 1
    if x >= hi:
        return 6
    return int(round(1 + 5 * (x - lo) / (hi - lo)))


def features(events):
    wr = [e["written_midi"] for e in events if "written_midi" in e]
    durs = [e.get("dur_beats", 0) for e in events if "written_midi" in e]
    n = len(wr)
    pico = max(wr)
    agudo = scale6(pico, 64, 76)                                   # escrito: C5=72
    frac16 = sum(1 for d in durs if d <= 0.26) / max(1, n)         # densidade de semicolcheia
    vel = scale6(frac16, 0.1, 0.6)
    folego = scale6(n / max(1, max(e["measure"] for e in events)), 2.5, 6)  # notas por compasso
    # maior salto
    salto, s_de, s_para = 0, None, None
    for a, b in zip(wr, wr[1:]):
        if abs(b - a) > salto:
            salto, s_de, s_para = abs(b - a), a, b
    return dict(n=n, pico=pico, pico_nome=NOMES[pico % 12], agudo=agudo, vel=vel, folego=folego,
                salto=salto, s_de=s_de, s_para=s_para)


def build_one(path):
    fing, tr = load_fingering()
    data = compile_file(path, fing, tr)
    events = data["events"]                              # peça INTEIRA
    fifths, meter = get_meta(path)
    abc_full = to_abc(events, fifths, meter, path.stem)
    riff = phrases.extract_riff(events)                  # riff na peça inteira (mais ocorrências = robusto)
    span = phrases.theme_measure_span(events, riff)
    theme_events = phrases.slice_events_by_measure(events, *span) if span else events
    abc_theme = to_abc(theme_events, fifths, meter, path.stem)
    feat = features(theme_events)                        # PERFIL/dificuldade = o TEMA praticado
    feat["repeticao"] = phrases.repeticao_ratio(theme_events)
    rabc = to_abc(phrases.riff_events(riff), fifths, meter, "riff") if riff else ""
    return dict(stem=path.stem, num=int(path.stem.split("-")[1]), fifths=fifths, meter=meter,
                abc=abc_theme, abc_full=abc_full, theme_span=span,
                riff=riff, riff_abc=rabc, feat=feat)


def desafios(b, cat):
    feat, riff = b["feat"], b["riff"]
    out = []
    if riff:
        seq = " ".join(name(m, SHARP)[:-1] for m, _ in riff["notes"])
        out.append(dict(
            t="🔁 O riff desta cumbia",
            d=f"Esta cumbia gira em torno de uma frase de {riff['len']} notas que volta "
              f"{riff['count']}× ({seq}). Toque o riff isolado, 5× seguidas, devagar e no tempo — até ficar automático.",
            w="A cumbia é repetição: quando o riff vira automático, a música inteira destrava. "
              "Decore a frase com o ar, não com a vista.",
            svg=riff_svg(b["riff_abc"])))
    if feat["salto"] >= 5:
        iv = INTERV.get(feat["salto"], f"{feat['salto']} semitons")
        out.append(dict(
            t=f"O salto ({iv})",
            d=f"Há um salto de {iv} ({NOMES[feat['s_de'] % 12]}→{NOMES[feat['s_para'] % 12]}). "
              f"Toque as duas notas ligadas pelo ar, sem empurrar com a língua; depois no tempo.",
            w="Saltos largos pedem apoio de ar constante — pratique-os isolados antes da frase inteira.",
            svg=""))
    if feat["agudo"] >= 4:
        out.append(dict(
            t=f"Chegada ao agudo ({feat['pico_nome']})",
            d=f"O pico é {feat['pico_nome']}. Aproxime-se dele pela nota vizinha, em piano, "
              "repetindo até a afinação assentar.",
            w="Agudo se ganha com ar rápido e relaxamento, não com força.",
            svg=""))
    out.append(dict(t="Tocar inteira, no groove",
                    d="Junte tudo numa passada contínua, no balanço de dança — sem parar nos erros.",
                    w="O todo treina a continuidade e o tempo, não a perfeição.", svg=""))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cat = {p["num"]: p for p in json.load(open(HERE / "pieces_cumbia.json", encoding="utf-8"))["pieces"]}
    # melodias conferidas à mão (vencem o ABC do build e promovem a 'conferida'): notes_manual/cu-*.abc
    MANUAL = HERE / "notes_manual"
    manual_abc = ({p.stem: p.read_text(encoding="utf-8") for p in MANUAL.glob("cu-*.abc")}
                  if MANUAL.exists() else {})
    builds = [build_one(p) for p in sorted(NOTES.glob("cu-*.musicxml"))]
    # dificuldade: agudo pesa 2; mais repetição = mais fácil (entra antes)
    for b in builds:
        f = b["feat"]
        b["dificuldade"] = 2 * f["agudo"] + f["vel"] + f["folego"] - 2 * f["repeticao"]
    builds.sort(key=lambda b: b["dificuldade"])
    TIERS = ["riff", "sincopa", "fogo"]
    TFEAT = {"riff": "riff curto e muito repetido", "sincopa": "síncope e cromatismo", "fogo": "agudo e velocidade"}
    nb = len(builds)
    for i, b in enumerate(builds):
        b["lote"] = min(3, 1 + i * 3 // max(1, nb))
        b["nivel"] = TIERS[b["lote"] - 1]

    pieces, percurso, escada, abc, quality, pedag = {"pieces": []}, [], {"pieces": []}, {}, {}, {}
    lotes_seen = {}
    for b in builds:
        c = cat.get(b["num"], {})
        f = b["feat"]
        pieces["pieces"].append(dict(num=b["num"], id=b["stem"], titulo=c.get("titulo", b["stem"]),
            compositor=c.get("compositor", ""), key_concert=c.get("key_concert", "Bb"),
            compasso=b["meter"], forma=c.get("forma", []), celulas=[], requisitos=[],
            dificuldade=round(b["dificuldade"], 1)))
        percurso.append(dict(num=b["num"], titulo=c.get("titulo", b["stem"]), compositor=c.get("compositor", ""),
            tom=c.get("key_concert", "Bb"), lote=b["lote"], nivel=b["nivel"], agudo=f["agudo"],
            vel=f["vel"], folego=f["folego"], pico_nome=f["pico_nome"], forma=c.get("forma", [])))
        escada["pieces"].append(dict(num=b["num"], id=b["stem"], nivel_minimo=b["nivel"]))
        if b["stem"] in manual_abc:                       # conferida à mão vence tudo
            abc[b["stem"]] = manual_abc[b["stem"]]
            quality[b["stem"]] = "conferida"
        else:
            abc[b["stem"]] = b["abc"]
            quality[b["stem"]] = c.get("quality", "rascunho")
        pedag[str(b["num"])] = dict(
            perfil=dict(
                agudo=f"Pico em {f['pico_nome']} (nível {f['agudo']}/6).",
                vel=f"Densidade de semicolcheia nível {f['vel']}/6 — {'corre' if f['vel']>=4 else 'tranquilo'}.",
                folego=f"{f['n']} notas; frases {'longas' if f['folego']>=4 else 'curtas'} — respire no fim de cada giro do riff."),
            plano=dict(foco="o riff que se repete",
                leitura="Ache o riff e conte quantas vezes ele volta — é o esqueleto da peça.",
                estrategia="Decore o riff devagar; quando ele girar sozinho, encaixe o resto por cima."),
            desafios=desafios(b, c))
        lotes_seen.setdefault(b["lote"], dict(lote=b["lote"], nivel=b["nivel"],
            tom=c.get("key_concert", "Bb"), feat=TFEAT[b["nivel"]]))
    lotes = [lotes_seen[k] for k in sorted(lotes_seen)]
    tecnica = [dict(lote=L["lote"], nivel=L["nivel"], tom=L["tom"], feat=L["feat"], eixos=[]) for L in lotes]

    dump = lambda name, obj: json.dump(obj, open(OUT / name, "w", encoding="utf-8"), ensure_ascii=False)
    dump("pieces.json", pieces); dump("percurso.json", percurso); dump("escada.json", escada)
    dump("lotes.json", lotes); dump("abc.json", abc); dump("quality.json", quality)
    dump("abc_full.json", {b["stem"]: b["abc_full"] for b in builds})   # peça inteira ("tocar inteira")
    dump("pedagogia.json", pedag); dump("tecnica.json", tecnica)
    shutil.copy(CONTENT / "cells.json", OUT / "cells.json")
    if (CONTENT / "pedagogia" / "app_prep.json").exists():
        shutil.copy(CONTENT / "pedagogia" / "app_prep.json", OUT / "aquecimento.json")
    print(f"Jornada das Cumbias: {nb} peças · tiers {[b['nivel'] for b in builds]} · "
          f"riffs {sum(1 for b in builds if b['riff'])}/{nb} · SVG {'on' if _TK else 'off'}")


if __name__ == "__main__":
    main()
