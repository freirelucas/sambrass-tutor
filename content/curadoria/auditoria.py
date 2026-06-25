#!/usr/bin/env python3
"""Auditoria de qualidade dos dados (ambas as jornadas) — roda checagens, não opinião.

Dimensões: cobertura · verificação (proveniência) · confiança da extração (blocos) ·
consistência (tônica×catálogo, tags de célula) · completude de campos · integridade
referencial · validade · unicidade. Emite build/auditoria.json + um placar legível.

Uso: python3 content/curadoria/auditoria.py
"""
import json, os, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "content/curadoria/build/auditoria.json"
PCNAME = {"C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,"F":5,"F#":6,"Gb":6,"G":7,"G#":8,"Ab":8,"A":9,"A#":10,"Bb":10,"B":11}


def L(p, default=None):
    fp = ROOT / p
    if not fp.exists():
        return default
    try:
        return json.load(open(fp, encoding="utf-8"))
    except Exception:
        return default


def pct(a, b):
    return round(100 * a / b, 1) if b else 0.0


def main():
    SB = (L("content/pieces.json", {}) or {}).get("pieces", [])
    CU = (L("content/cumbia/build/pieces.json", {}) or {}).get("pieces", [])
    sb_abc = L("content/notes_abc.json", {}) or {}
    cu_abc = L("content/cumbia/build/abc.json", {}) or {}
    cu_full = L("content/cumbia/build/abc_full.json", {}) or {}
    sb_q = L("content/notes_quality.json", {}) or {}
    cu_q = L("content/cumbia/build/quality.json", {}) or {}
    sb_esc = (L("content/curadoria/escada.json", {}) or {}).get("pieces", [])
    cu_esc = (L("content/cumbia/build/escada.json", {}) or {}).get("pieces", [])
    blocos = (L("content/curadoria/build/blocos.json", {}) or {}).get("pecas", {})
    sb_cells = L("content/cells.json", {}) or {}
    cu_cells = L("content/cumbia/build/cells.json", {}) or {}

    def cell_ids(cd):
        out = set()
        for grp in ("celulas_ritmicas", "arpejos"):
            g = cd.get(grp)
            if isinstance(g, dict):
                out |= {k for k in g if not k.startswith("_")}
            elif isinstance(g, list):
                out |= {it.get("id") for it in g if isinstance(it, dict) and it.get("id")}
        return out
    valid_cells = {"sambrass": cell_ids(sb_cells), "cumbias": cell_ids(cu_cells)}

    rep = {"resumo": {}, "dimensoes": {}, "achados": []}
    add = lambda sev, dim, msg, ids=None: rep["achados"].append(
        {"sev": sev, "dim": dim, "msg": msg, "ids": (ids or [])[:25], "n": len(ids or [])})

    journeys = {"sambrass": (SB, sb_abc, sb_q, sb_esc), "cumbias": (CU, cu_abc, cu_q, cu_esc)}

    # ---------- 1. cobertura + verificação ----------
    cob, ver = {}, {}
    for jn, (P, abc, q, esc) in journeys.items():
        ids = [p["id"] for p in P]
        with_abc = sum(1 for i in ids if abc.get(i))
        with_blk = sum(1 for i in ids if i in blocos)
        with_riff = sum(1 for i in ids if blocos.get(i, {}).get("riff"))
        with_ons = sum(1 for i in ids if blocos.get(i, {}).get("onsets"))
        with_cel = sum(1 for p in P if p.get("celulas"))
        cob[jn] = {"pecas": len(P), "tema_abc": with_abc, "blocos": with_blk,
                   "riff": with_riff, "onsets": with_ons, "celulas_marcadas": with_cel}
        tiers = collections.Counter(q.get(i, "rascunho") for i in ids)
        conf = tiers.get("conferida", 0)
        ver[jn] = {"tiers": dict(tiers), "conferida": conf, "pct_conferida": pct(conf, len(ids)),
                   "provisorias": len(ids) - conf}
        if with_cel == 0 and len(P):
            add("alto", "cobertura", f"[{jn}] 0/{len(P)} peças têm células marcadas — dimensão de célula ausente.",
                ids)
        if pct(conf, len(ids)) < 50:
            add("alto" if jn == "sambrass" else "médio", "verificação",
                f"[{jn}] só {conf}/{len(ids)} ({pct(conf,len(ids))}%) conferidas por ouvido; o resto é provisório (OMR/dedos).",
                [i for i in ids if q.get(i, 'rascunho') != 'conferida'])
    rep["dimensoes"]["cobertura"] = cob
    rep["dimensoes"]["verificacao"] = ver

    # ---------- 2. confiança da extração (blocos) ----------
    confs = [(i, b) for i, b in blocos.items()]
    low = [i for i, b in confs if b.get("cor", {}).get("conf", 1) < 0.06]
    unknown = [i for i, b in confs if b.get("cor", {}).get("modo") not in ("maior", "menor")]
    arm_no = [i for i, b in confs if b.get("cor", {}).get("armadura_bate") is False]
    rep["dimensoes"]["confianca_extracao"] = {
        "n_blocos": len(confs), "modo_baixa_conf": len(low), "modo_desconhecido": len(unknown),
        "armadura_nao_bate": len(arm_no), "modo_no_catalogo": 0}
    add("alto", "confiança", f"modo musical não existe no catálogo (0%) — 100% derivado; {len(low)} com confiança baixa (<0.06) pedem ouvido.", low)
    if arm_no:
        add("médio", "consistência", f"{len(arm_no)} blocos cuja armadura detectada NÃO bate com a do catálogo.", arm_no)

    # ---------- 3. consistência: recuperação de modo (esperada) + tags de célula ----------
    cat_key = {p["id"]: p.get("key_concert") for P, *_ in journeys.values() for p in P}
    rel_minor = []          # tônica = relativo menor do tom + armadura bate = recuperação ESPERADA (não-erro)
    for i, b in confs:
        cor = b.get("cor", {}); kc = cat_key.get(i)
        if cor.get("modo") == "menor" and kc in PCNAME and cor.get("tonica") in PCNAME \
           and PCNAME[cor["tonica"]] == (PCNAME[kc] - 3) % 12 and cor.get("armadura_bate"):
            rel_minor.append(i)
    tag_marcada_nao_det = [i for i, b in confs if b.get("tags_nao_confirmadas")]
    tag_extra = [i for i, b in confs if b.get("celulas_extra_candidatas")]
    rep["dimensoes"]["consistencia"] = {
        "recuperacao_relativo_menor_ok": len(rel_minor),
        "tags_marcadas_nao_detectadas": len(tag_marcada_nao_det),
        "celulas_detectadas_nao_marcadas": len(tag_extra)}
    if tag_marcada_nao_det:
        add("médio", "consistência", f"{len(tag_marcada_nao_det)} peças com célula MARCADA no catálogo mas NÃO detectada nas notas (tag à mão vs notas).", tag_marcada_nao_det)

    # ---------- 4. completude de campos ----------
    REQ = ["compositor", "key_concert", "compasso", "forma", "dificuldade"]
    comp = {}
    for jn, (P, *_ ) in journeys.items():
        miss = {f: [p["id"] for p in P if not p.get(f)] for f in REQ}
        comp[jn] = {f: len(v) for f, v in miss.items()}
        for f, v in miss.items():
            if v:
                add("baixo" if f != "key_concert" else "médio", "completude",
                    f"[{jn}] campo '{f}' vazio em {len(v)} peças.", v)
    rep["dimensoes"]["completude"] = comp

    # ---------- 5. integridade referencial ----------
    ri = {}
    for jn, (P, abc, q, esc) in journeys.items():
        ids = {p["id"] for p in P}
        orphan_tags = sorted({c for p in P for c in p.get("celulas", []) if c not in valid_cells[jn]})
        esc_ids = {e["id"] for e in esc}
        esc_orfa = sorted(esc_ids - ids)
        sem_esc = sorted(ids - esc_ids)
        sem_abc = sorted(i for i in ids if not abc.get(i))
        ri[jn] = {"tags_orfas": orphan_tags, "escada_aponta_inexistente": esc_orfa,
                  "pecas_fora_da_escada": len(sem_esc), "pecas_sem_tema_abc": len(sem_abc)}
        if orphan_tags:
            add("médio", "integridade", f"[{jn}] tags de célula sem definição em cells.json: {orphan_tags}", orphan_tags)
        if esc_orfa:
            add("alto", "integridade", f"[{jn}] escada aponta para ids inexistentes: {esc_orfa}", esc_orfa)
        if sem_abc:
            add("médio", "cobertura", f"[{jn}] {len(sem_abc)} peças sem melodia (tema ABC).", sem_abc)
    blk_orfa = sorted(set(blocos) - set(cat_key))
    if blk_orfa:
        add("baixo", "integridade", f"{len(blk_orfa)} blocos sem peça correspondente no catálogo.", blk_orfa)
    rep["dimensoes"]["integridade_referencial"] = ri

    # ---------- 6. validade: escala de dificuldade ----------
    def rng(P):
        ds = [p["dificuldade"] for p in P if isinstance(p.get("dificuldade"), (int, float))]
        return (min(ds), max(ds), all(isinstance(p.get("dificuldade"), int) for p in P)) if ds else (None, None, None)
    sb_r, cu_r = rng(SB), rng(CU)
    rep["dimensoes"]["validade"] = {"dif_sambrass": sb_r[:2], "dif_cumbias": cu_r[:2],
                                    "escala_consistente": sb_r[1] and cu_r[1] and abs((sb_r[1] or 0) - (cu_r[1] or 0)) < 3}
    if sb_r[1] and cu_r[1] and abs(sb_r[1] - cu_r[1]) >= 3:
        add("médio", "validade", f"escala de dificuldade INCONSISTENTE entre jornadas: sambrass {sb_r[0]}–{sb_r[1]} vs cumbias {cu_r[0]}–{cu_r[1]} (não comparáveis).")

    # ---------- 7. unicidade ----------
    allp = SB + CU
    dup_id = [k for k, v in collections.Counter(p["id"] for p in allp).items() if v > 1]
    dup_tit = [k for k, v in collections.Counter((p.get("titulo") or "").lower() for p in allp).items() if v > 1 and k]
    rep["dimensoes"]["unicidade"] = {"ids_duplicados": dup_id, "titulos_duplicados": dup_tit}
    if dup_id:
        add("alto", "unicidade", f"ids duplicados: {dup_id}", dup_id)

    # ---------- placar ----------
    tot = len(allp)
    conf_tot = ver["sambrass"]["conferida"] + ver["cumbias"]["conferida"]
    sev_count = collections.Counter(a["sev"] for a in rep["achados"])
    rep["resumo"] = {"pecas_total": tot, "conferidas_total": conf_tot, "pct_conferida": pct(conf_tot, tot),
                     "blocos": len(blocos), "achados_por_severidade": dict(sev_count)}
    rep["achados"].sort(key=lambda a: {"alto": 0, "médio": 1, "baixo": 2}[a["sev"]])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(rep, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------- print ----------
    print(f"\n{'='*64}\n  AUDITORIA DE QUALIDADE — {tot} peças ({len(SB)} sambrass + {len(CU)} cumbias)\n{'='*64}")
    print(f"  CONFERIDAS por ouvido: {conf_tot}/{tot} ({pct(conf_tot,tot)}%)  ← o eixo crítico")
    for jn in journeys:
        v, c = ver[jn], cob[jn]
        print(f"  · {jn:9}: tiers={v['tiers']} | tema {c['tema_abc']}/{c['pecas']} | células {c['celulas_marcadas']}/{c['pecas']}")
    ce = rep["dimensoes"]["confianca_extracao"]
    print(f"  EXTRAÇÃO (blocos): {ce['n_blocos']} | modo 100% derivado · {ce['modo_baixa_conf']} baixa conf · {ce['armadura_nao_bate']} armadura≠catálogo")
    cs = rep["dimensoes"]["consistencia"]
    print(f"  CONSISTÊNCIA: {cs['recuperacao_relativo_menor_ok']} recuperações de relativo menor (esperado, ok) · {cs['tags_marcadas_nao_detectadas']} tags de célula divergentes")
    print(f"  ACHADOS: {dict(sev_count)}")
    print(f"{'-'*64}")
    for a in rep["achados"]:
        tag = {"alto": "🔴", "médio": "🟡", "baixo": "⚪"}[a["sev"]]
        ex = f"  ex: {a['ids'][:4]}" if a["ids"] else ""
        print(f"  {tag} [{a['dim']}] {a['msg']}{ex}")
    print(f"\n  → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
