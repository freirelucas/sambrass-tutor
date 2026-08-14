#!/usr/bin/env python3
"""Valida as ALTURAS de cada ABC (tom ESCRITO da parte de trompete Bb).

É o irmão do check_bars (que só olha ritmo): pega as "notas absurdas" que o OMR
deixa passar — oitava global errada (cu-005 ficou 1 ano soando uma 8ª acima),
frases fora da tessitura, saltos impossíveis e tom que não bate com o catálogo.

Checagens por peça:
  1. TESSITURA — notas fora da tessitura escrita do trompete Bb
     (content/instruments/trumpet_bb.json: F#3–C6). Abaixo do mínimo = pedal
     (não soa no instrumento); acima do teto = quase sempre 8ª errada do OMR.
  2. OITAVA SUSPEITA — nota a ≥ 15 semitons da mediana da peça cuja versão ±8ª
     cairia perto da mediana: assinatura clássica de erro de oitava do OMR.
  3. SALTO IMPOSSÍVEL — intervalo melódico > 1 oitava entre notas vizinhas do
     MESMO compasso (entre compassos há voltas/repetições achatadas no ABC, que
     criam saltos que não existem na execução — não conta).
  4. TOM — a armadura K: do ABC (escrito − 2 = concert) deve bater com o
     key_concert do catálogo.

Uso: `check_all(abc_dict, expected_concert=None) -> {id: [mensagens]}`;
ou rode direto p/ um relatório dos notes_manual/.
"""
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from abc_events import events_from_abc, key_from_abc

_NOMES = ["Dó", "Dó#", "Ré", "Ré#", "Mi", "Fá", "Fá#", "Sol", "Sol#", "Lá", "Lá#", "Si"]
_PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6,
       "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def _nome(midi):
    return f"{_NOMES[midi % 12]}{midi // 12 - 1}"


def _tessitura():
    inst = json.load(open(HERE.parent / "instruments" / "trumpet_bb.json", encoding="utf-8"))
    t = inst.get("tessitura_escrita", {})
    def midi_of(name):
        # "F#3" -> 54: letra+acidente+oitava (científica: C4=60)
        pc = _PC[name[:-1]]
        return 12 * (int(name[-1]) + 1) + pc
    return midi_of(t.get("min", "F#3")), midi_of(t.get("max", "C6"))


def check_abc(abc, expected_concert_pc=None):
    """Lista de problemas de altura de um ABC escrito (vazia = ok)."""
    lo, hi = _tessitura()
    ev = [e for e in events_from_abc(abc) if "written_midi" in e]
    if not ev:
        return []
    probs = []
    baixo = [e for e in ev if e["written_midi"] < lo]
    alto = [e for e in ev if e["written_midi"] > hi]
    if baixo:
        cs = sorted({e["measure"] for e in baixo})
        notas = ", ".join(sorted({_nome(e["written_midi"]) for e in baixo}))
        probs.append(f"{len(baixo)} nota(s) abaixo da tessitura ({_nome(lo)}): {notas} — c.{', '.join(map(str, cs))}")
    if alto:
        cs = sorted({e["measure"] for e in alto})
        notas = ", ".join(sorted({_nome(e["written_midi"]) for e in alto}))
        probs.append(f"{len(alto)} nota(s) acima da tessitura ({_nome(hi)}): {notas} — c.{', '.join(map(str, cs))}")
    med = statistics.median(e["written_midi"] for e in ev)
    oct_susp = [e for e in ev
                if lo <= e["written_midi"] <= hi                       # fora da tessitura já foi avisado acima
                and abs(e["written_midi"] - med) >= 15
                and min(abs(e["written_midi"] + 12 - med), abs(e["written_midi"] - 12 - med)) <= 7]
    for e in oct_susp[:4]:
        probs.append(f"oitava suspeita: {_nome(e['written_midi'])} no c.{e['measure']} (mediana da peça = {_nome(round(med))})")
    saltos = [(a, b) for a, b in zip(ev, ev[1:])
              if a["measure"] == b["measure"] and abs(b["written_midi"] - a["written_midi"]) > 12]
    for a, b in saltos[:4]:
        probs.append(f"salto impossível no c.{a['measure']}: {_nome(a['written_midi'])}→{_nome(b['written_midi'])} "
                     f"({abs(b['written_midi'] - a['written_midi'])} semitons)")
    if expected_concert_pc is not None:
        kpc = key_from_abc(abc)                       # já devolve pc CONCERT (K: escrito − 2)
        if kpc != expected_concert_pc:
            probs.append(f"tom não bate: ABC em {_NOMES[kpc]} (concert), catálogo diz {_NOMES[expected_concert_pc]}")
    return probs


def check_all(abc_dict, expected_concert=None):
    """{id: [problemas]} só para as peças com problema. expected_concert = {id: 'Bb'…}."""
    out = {}
    for k, v in abc_dict.items():
        if k.startswith("_") or k.startswith("cell-") or not isinstance(v, str):
            continue
        exp = _PC.get((expected_concert or {}).get(k, ""), None) if expected_concert else None
        p = check_abc(v, exp)
        if p:
            out[k] = p
    return out


if __name__ == "__main__":
    manual = {p.stem: p.read_text(encoding="utf-8")
              for p in sorted((HERE / "notes_manual").glob("cu-*.abc"))}
    cat = {f"cu-{p['num']:03d}": p.get("key_concert", "")
           for p in json.load(open(HERE / "pieces_cumbia.json", encoding="utf-8"))["pieces"]}
    warn = check_all(manual, cat)
    for k in sorted(warn):
        for m in warn[k]:
            print(f"  {k}: {m}")
    print(f"--- {sum(len(v) for v in warn.values())} problemas de altura em {len(warn)} peças ---")
