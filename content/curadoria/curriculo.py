#!/usr/bin/env python3
"""Track 3e — currículo expandido a partir da trilha mestra (módulos por habilidade).

Fatia a trilha mestra (110 peças) em módulos de ~9, temados pelas habilidades novas
introduzidas, com peças-foco + leitura à 1ª vista (da escada) + revisão do módulo anterior.
Mantém a rotina diária de 90 min. Saída: content/curriculum/sambrass23-trilha.json.
Uso: python3 content/curadoria/curriculo.py
"""
import json
from lib import ROOT, SKILLS

CUR = ROOT / "curriculum"
ALVO = 9  # peças-foco por módulo


def main():
    tr = json.load(open(ROOT / "curadoria" / "trilha.json", encoding="utf-8"))
    rot = json.load(open(CUR / "sambrass23-6semanas.json", encoding="utf-8"))["rotina_diaria"]
    passos = tr["trilha_mestra"]
    escada = tr["escada_leitura"]

    # fatia a trilha em módulos de ~ALVO peças
    modulos, buf, novas = [], [], []
    for s in passos:
        buf.append(s)
        novas += s["habilidade_nova"]
        if len(buf) >= ALVO:
            modulos.append((buf, novas)); buf, novas = [], []
    if buf:
        modulos.append((buf, novas))

    leitura_idx = 0
    out = []
    for i, (grupo, nov) in enumerate(modulos):
        difs = [g["dificuldade_calc"] for g in grupo]
        # leitura à 1ª vista: peças fáceis da escada, ≤ dif do módulo, não usadas como foco
        teto = max(difs)
        foco_nums = {g["num"] for g in grupo}
        leitura = []
        while len(leitura) < 2 and leitura_idx < len(escada):
            e = escada[leitura_idx]; leitura_idx += 1
            if e["num"] not in foco_nums and e["dificuldade_calc"] <= teto:
                leitura.append({"num": e["num"], "titulo": e["titulo"]})
        out.append({
            "modulo": i + 1,
            "faixa_dificuldade": [min(difs), max(difs)],
            "habilidades_novas": [SKILLS.get(s, s) for s in dict.fromkeys(nov)],
            "foco": [{"num": g["num"], "titulo": g["titulo"], "dif": g["dificuldade_calc"]} for g in grupo],
            "leitura_1avista": leitura,
            "revisao": [g["num"] for g in modulos[i - 1][0]] if i else [],
        })

    json.dump({
        "id": "sambrass23-trilha", "caderno": "sambrass23", "instrumento": "trumpet_bb",
        "_meta": {
            "titulo": "O Caminho do Sambrass — trilha completa (110 peças)",
            "principio": "trilha mestra graded (uma habilidade nova por vez); módulos de ~9 peças; "
                         "dificuldade = recalibrada 1–10; leitura à 1ª vista pela escada.",
            "carga": "1h30/dia",
        },
        "rotina_diaria": rot,
        "modulos": out,
    }, open(CUR / "sambrass23-trilha.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"OK — {len(out)} módulos → {CUR/'sambrass23-trilha.json'}")
    for m in out:
        print(f"  Mód {m['modulo']:2} dif{m['faixa_dificuldade']} "
              f"({len(m['foco'])} foco) novas: {', '.join(m['habilidades_novas']) or '—'}")


if __name__ == "__main__":
    main()
