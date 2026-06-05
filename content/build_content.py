#!/usr/bin/env python3
"""Fase 0 — Fundação de dados.

Deriva o conteúdo agnóstico de instrumento (pieces/caderno/curriculum) a partir
do curso legado (caderno Sambrass23, trompete Bb). Converte o tom ESCRITO do
trompete para TOM DE CONCERTO e valida o round-trip (concert + 2 semitons tem de
voltar ao tom escrito original).

Uso:  python3 content/build_content.py
Fonte legada: _extracted/sambrass_course/data/{musicas,jornada}.json
(descompacte o zip do curso antes de rodar).
"""
import json, pathlib, sys, zipfile, glob

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"


def load_legacy(name):
    """Lê data/<name> do curso legado: do zip versionado (preferido) ou de _extracted/."""
    zips = sorted(glob.glob(str(ROOT / "sambrass_course*.zip")))
    if zips:
        with zipfile.ZipFile(zips[0]) as z:
            with z.open(f"sambrass_course/data/{name}") as f:
                return json.load(f)
    alt = ROOT / "_extracted" / "sambrass_course" / "data" / name
    if alt.exists():
        return json.load(open(alt, encoding="utf-8"))
    sys.exit(f"fonte legada não encontrada (zip do curso ou _extracted/): data/{name}")

PT_TO_INTL = {
    "Dó": "C", "Ré": "D", "Mi": "E", "Fá": "F", "Sol": "G", "Lá": "A", "Si": "B",
    "Dó#": "C#", "Ré#": "D#", "Fá#": "F#", "Sol#": "G#", "Lá#": "A#",
    "Réb": "Db", "Mib": "Eb", "Solb": "Gb", "Láb": "Ab", "Sib": "Bb",
}
PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
      "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
SPELL = {0: "C", 1: "Db", 2: "D", 3: "Eb", 4: "E", 5: "F",
         6: "Gb", 7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B"}

TRUMPET_BB_TRANSPOSE = 2  # escrito = concert + 2 semitons


def written_to_concert(pt_key):
    """'Fá' -> 'Eb'. Aceita modulação 'Sol→Lá' -> ('F','G')."""
    parts = [p.strip() for p in pt_key.replace("->", "→").split("→")]
    out = []
    for p in parts:
        if p not in PT_TO_INTL:
            raise ValueError(f"tom desconhecido: {p!r}")
        intl = PT_TO_INTL[p]
        out.append((intl, SPELL[(PC[intl] - TRUMPET_BB_TRANSPOSE) % 12]))
    return out  # [(escrito_intl, concert), ...]


def intl_written_to_concert(intl_key):
    """'F' -> ('F','Eb'). Aceita modulação 'G->A'."""
    out = []
    for p in [x.strip() for x in str(intl_key).replace("→", "->").split("->")]:
        if p not in PC:
            raise ValueError(f"tom escrito intl desconhecido: {p!r}")
        out.append((p, SPELL[(PC[p] - TRUMPET_BB_TRANSPOSE) % 12]))
    return out


def piece_from(num, titulo, compositor, compasso, conv, densidade, forma,
               celulas, arpejos, dificuldade, requisitos, verificada, obs,
               dominio_publico=False):
    """Monta a peça no schema final; valida o round-trip escrito↔concert."""
    for (escrito_intl, concert) in conv:
        if (PC[concert] + TRUMPET_BB_TRANSPOSE) % 12 != PC[escrito_intl]:
            raise ValueError(f"round-trip falhou em {num}: {escrito_intl}/{concert}")
    return {
        "id": f"sb-{num:03d}", "num": num, "titulo": titulo, "compositor": compositor,
        "compasso": compasso, "key_concert": conv[0][1],
        "modulates_to_concert": conv[1][1] if len(conv) > 1 else None,
        "densidade": densidade, "forma": forma, "celulas": celulas, "arpejos": arpejos,
        "dificuldade": dificuldade, "requisitos": requisitos,
        "dominio_publico": dominio_publico, "verificada": verificada, "obs": obs,
        "score": f"sb-{num:03d}.jpg",
    }


def main():
    musicas = load_legacy("musicas.json")["musicas"]
    jornada = load_legacy("jornada.json")

    by_num = {}
    # Fonte 1 — 30 legados (tom escrito em PT → concert)
    for m in musicas:
        by_num[m["num"]] = piece_from(
            m["num"], m["titulo"], m["compositor"], m["compasso"],
            written_to_concert(m["tom"]), m["densidade"], m["forma"], m["celulas"],
            m["arpejos"], m["dificuldade"], m["requisitos"], m["verificada"], m["obs"])

    # Fonte 2 — catálogo das demais (análise visual; tom escrito em intl) — extra vence
    extra_path = CONTENT / "catalog_extra.json"
    if extra_path.exists():
        for e in json.load(open(extra_path, encoding="utf-8")):
            by_num[e["num"]] = piece_from(
                e["num"], e["titulo"], e["compositor"], e.get("compasso", "2/4"),
                intl_written_to_concert(e["tom_escrito"]), e.get("densidade", "?"),
                e.get("forma", []), e.get("celulas", []), e.get("arpejos", []),
                e.get("dificuldade"), e.get("requisitos", []),
                e.get("verificada", False), e.get("obs", ""),
                e.get("dominio_publico", False))

    pieces = [by_num[n] for n in sorted(by_num)]
    nums = [p["num"] for p in pieces]
    caderno = {
        "id": "sambrass23",
        "nome": "Caderno de naipe Sambrass23",
        "instrumento_padrao": "trumpet_bb",
        "total_caderno": 110,
        "catalogadas": len(pieces),
        "ordem": [f"sb-{n:03d}" for n in nums],
    }

    def ref(n):
        return f"sb-{n:03d}"

    curriculum = {
        "id": "sambrass23-6semanas",
        "caderno": "sambrass23",
        "instrumento": "trumpet_bb",
        "_meta": jornada["_meta"],
        "rotina_diaria": jornada["rotina_diaria"],
        "semanas": [{
            "n": s["n"], "tema": s["tema"], "tom": s["tom"],
            "celula_alvo": s["celula_alvo"], "requisito": s["requisito"],
            "pieces_foco": [ref(n) for n in s["musicas_foco"]],
            "leitura_1avista": [ref(n) for n in s["leitura_1avista"]],
            "licao": s["licao"],
        } for s in jornada["semanas"]],
    }

    (CONTENT / "cadernos").mkdir(parents=True, exist_ok=True)
    (CONTENT / "curriculum").mkdir(parents=True, exist_ok=True)
    json.dump({"pieces": pieces}, open(CONTENT / "pieces.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump(caderno, open(CONTENT / "cadernos" / "sambrass23.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump(curriculum, open(CONTENT / "curriculum" / "sambrass23-6semanas.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    ver = sum(1 for p in pieces if p.get("verificada"))
    print(f"OK — {len(pieces)} peças montadas ({ver} verificadas), round-trip de tom validado.")
    print(f"     caderno.ordem: {len(nums)} ids · faltam catalogar: {110 - len(pieces)}")


if __name__ == "__main__":
    main()
