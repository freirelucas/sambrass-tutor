# -*- coding: utf-8 -*-
"""Pedagogia v2: perfis concretos (nota máxima, régua explicada), plano enxuto,
micro-desafios com dados reais da peça + micro-exercícios autorais em SVG."""
import json, csv, re, verovio
R="sambrass-tutor-main"
esc={p['num']:p for p in json.load(open(f"{R}/content/curadoria/escada.json"))['pieces']}
difj={p['num']:p for p in json.load(open(f"{R}/content/curadoria/dificuldade.json"))['pieces']}
rows={int(r['num']):r for r in csv.DictReader(open(f"{R}/content/catalog.csv"))}
notes=json.load(open(f"{R}/content/notes_abc.json"))
mus=json.load(open("app_musicas.json"))
MUS={m['num']:m for m in mus}

val={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
NOMES=["Dó","Dó#","Ré","Ré#","Mi","Fá","Fá#","Sol","Sol#","Lá","Lá#","Si"]
def nm(m): return f"{NOMES[m%12]}{m//12-1}"
def nm_s(m): return NOMES[m%12]
INTERV={2:"segunda",3:"terça menor",4:"terça maior",5:"quarta",6:"trítono",7:"quinta",
        8:"sexta menor",9:"sexta maior",10:"sétima menor",11:"sétima maior",12:"oitava",13:"nona menor",14:"nona"}
def pos_txt(f): return "no primeiro terço" if f<0.33 else ("no meio da peça" if f<0.67 else "no trecho final")
ABCTOK=["C","^C","D","^D","E","F","^F","G","^G","A","^A","B"]
def tok(m):
    o=m//12-1; base=ABCTOK[m%12]
    if o<=3: return base+","
    if o==4: return base
    if o==5: return base.lower()
    return base.lower()+"'"

tk=verovio.toolkit()
def svg(abc):
    tk.setOptions({"inputFrom":"abc","scale":38,"adjustPageHeight":True,"pageWidth":1400,
      "header":"none","footer":"none","spacingStaff":1,"spacingSystem":1,
      "pageMarginLeft":6,"pageMarginRight":6,"pageMarginTop":4,"pageMarginBottom":4,"breaks":"none"})
    tk.loadData("X:1\n"+abc+"\n")
    s=tk.renderToSVG(1)
    s=re.sub(r'width="\d+px"','width="100%"',s,count=1)
    s=re.sub(r' height="\d+px"','',s,count=1)
    if 'preserveAspectRatio' not in s[:300]:
        s=s.replace('<svg ','<svg preserveAspectRatio="xMinYMin meet" ',1)
    return s

def analise(num):
    key=f"sb-{num:03d}"
    if key not in notes: return {}
    abc=notes[key]; L=1/16
    mL=re.search(r'L:(\d+)/(\d+)',abc)
    if mL: L=int(mL.group(1))/int(mL.group(2))
    corpo="\n".join(l for l in abc.split("\n") if not re.match(r'^[A-Za-z]:',l))
    seq=[]
    for m in re.finditer(r"([\^_=]*)([A-Ga-gz])([,']*)(\d*)(/?\d*)", corpo):
        acc,nt,oit,dur,half=m.groups()
        if nt=='z': continue
        octv=(5 if nt.islower() else 4)+oit.count("'")-oit.count(",")
        mid=val[nt.upper()]+12*octv
        if not(50<=mid<=74): continue
        d=float(dur) if dur else 1.0
        if half.startswith('/'): d=d/(float(half[1:]) if len(half)>1 else 2)
        seq.append((mid,d*L))
    if len(seq)<6: return {}
    p=[s[0] for s in seq]; dr=[s[1] for s in seq]; n=len(p)
    bi=max(range(n-1), key=lambda i:abs(p[i+1]-p[i]))
    best=cur=0; bs=cs=0
    for i,d in enumerate(dr):
        if d<=1/16+1e-9:
            if cur==0: cs=i
            cur+=1
            if cur>best: best,bs=cur,cs
        else: cur=0
    li=max(range(n), key=lambda i:dr[i])
    return dict(salto=abs(p[bi+1]-p[bi]), s_de=p[bi], s_para=p[bi+1], s_pos=bi/n,
      pico=max(p), pico_pos=p.index(max(p))/n,
      run=best, run_nota=p[bs] if best else 0, run_pos=bs/n if best else 0,
      longa=p[li], longa_t=dr[li]/0.25, longa_pos=li/n)

# ---------- PERFIL concreto por dimensão (com régua e significado) ----------
REGUA_AG=["até Ré4","Mi4","Fá4","Sol4","Lá4","Si4 ou mais"]
SIG_AG=["registro central, zero esforço de subida",
 "ainda confortável; só não aperte ao chegar no Mi",
 "o Fá4 pede apoio de ar firme — é a primeira fronteira",
 "Sol4 exige embocadura assentada; aqueça antes",
 "Lá4 já é trabalho de registro: ar rápido, sem pressão de lábio",
 "topo do caderno; chegue nele crescendo pelos exercícios de subida"]
SIG_VEL=["só valores calmos — nenhuma corrida",
 "movimento leve, colcheias tranquilas",
 "passagens ágeis pontuais; nada contínuo",
 "tem corridas de verdade — semicolcheias ou densidade alta",
 "rápida quase o tempo todo; a língua precisa de tu-ku",
 "velocidade máxima do caderno; só depois de dominar o tu-ku"]
SIG_FOL=["frases curtas com respiros óbvios",
 "fôlego tranquilo, forma enxuta",
 "frases médias; já vale marcar respirações",
 "forma com 3+ seções — planeje onde respirar",
 "peça longa; respiração planejada é obrigatória",
 "forma extensa sem descanso — o desafio é chegar inteiro ao fim"]

def perfil(m, a):
    ag,ve,fo=m['agudo'],m['vel'],m['folego']
    pa=f"Nota mais aguda: <b>{nm(a['pico'])}</b>, {pos_txt(a['pico_pos'])}. " if a else ""
    p_ag=f"{pa}Nível {ag} de 6 (a régua sobe de \u201caté Ré4\u201d a \u201cSi4+\u201d): {SIG_AG[ag-1]}."
    extra_v=""
    if a and a['run']>=4:
        extra_v=f" A corrida mais longa tem {a['run']} notas e começa no {nm_s(a['run_nota'])}, {pos_txt(a['run_pos'])}."
    p_ve=f"Nível {ve} de 6: {SIG_VEL[ve-1]}.{extra_v}"
    p_fo=f"Nível {fo} de 6: {SIG_FOL[fo-1]}. Forma {m['forma']}."
    return {"agudo":p_ag,"vel":p_ve,"folego":p_fo}

# ---------- DESAFIOS com dados + SVG autoral ----------
def desafios(m, a):
    f=difj[m['num']]['features']; r=rows[m['num']]
    out=[]
    if not a:
        out.append({"t":"Toque inteira, lenta","d":"Uma passada contínua, devagar, sem parar nos erros. O alvo é a continuidade.",
                    "w":"A passada contínua treina o que a prática por trechos não treina: seguir em frente."})
        return out
    # salto (se relevante)
    if a['salto']>=7:
        de,pa=a['s_de'],a['s_para']
        ex=f"M:2/4\nL:1/4\nK:C\n({tok(de)} {tok(pa)}) | ({tok(pa)} {tok(de)}) | ({tok(de)} {tok(pa)}) | {tok(pa)}2 |]"
        out.append({"t":f"O salto {nm_s(de)}→{nm_s(pa)}",
          "d":f"O maior salto da peça é uma {INTERV.get(a['salto'],'distância grande')} ({nm(de)}→{nm(pa)}), {pos_txt(a['s_pos'])}. Toque o exercício abaixo ligado, 4 vezes: encha o ar antes e mire a nota de cima já com o som aberto.",
          "w":"Repetir só o trecho difícil é o coração da prática deliberada — o ganho mora aqui.",
          "svg":svg(ex)})
    # pico (se exige)
    if m['agudo']>=3:
        pk=a['pico']; viz=pk-2
        ex=f"M:4/4\nL:1/4\nK:C\n{tok(viz)} {tok(pk)}2 z | {tok(viz)} {tok(pk)}3 |]"
        out.append({"t":f"Chegar no {nm_s(pk)}",
          "d":f"A nota mais aguda ({nm(pk)}) aparece {pos_txt(a['pico_pos'])}. Pratique a chegada: {nm_s(viz)} → {nm_s(pk)}, sustentando. Se apertar o lábio, pare, respire e refaça com mais ar e menos pressão.",
          "w":"Chegar no agudo a partir da vizinha treina o caminho do ar — não a força.",
          "svg":svg(ex)})
    # corrida
    if a['run']>=4:
        out.append({"t":f"A corrida de {a['run']} notas",
          "d":f"Ache na partitura a corrida que começa no {nm_s(a['run_nota'])}, {pos_txt(a['run_pos'])}. Toque-a na metade da velocidade com tu-ku, 3 vezes perfeitas; só então acelere.",
          "w":"O cérebro automatiza o que repete certo, não o que repete rápido."})
    # tercina
    if f.get('tercina'):
        out.append({"t":"As tercinas","d":"Bata o pé na semínima e fale \u201ctri-o-la\u201d sobre cada tercina, sem tocar. Quando a boca acertar, o trompete acerta.",
          "w":"Contar antes de tocar passa o ritmo ao corpo antes de envolver o instrumento."})
    # contratempo
    if f.get('contratempo') and a['salto']<7:
        out.append({"t":"O contratempo","d":"Bata o pé no tempo e toque só as notas que caem fora dele. Sinta o silêncio antes de cada ataque.",
          "w":"O silêncio antes do ataque é onde mora o suingue."})
    # modulação
    if f.get('modulacao') or r.get('modula'):
        out.append({"t":"A troca de tom","d":"A peça muda de armadura no meio. Toque só os dois compassos em volta da troca, devagar, até a emenda ficar lisa.",
          "w":"Transições são pontos de falha; isoladas, deixam de ser."})
    # forma longa
    ns=f.get('n_secoes',2)
    if f.get('extensa') or ns>=4:
        out.append({"t":"Uma seção por vez","d":f"A forma é {r['forma']}. Hoje, só a seção A: repita até sair de cor. As outras ficam para as próximas sessões.",
          "w":"Peças longas se montam de pedaços firmes — qualidade antes de quantidade."})
    # fechamento
    longa=""
    if a['longa_t']>=3:
        longa=f" Atenção à nota longa ({nm_s(a['longa'])}, {a['longa_t']:.0f} tempos, {pos_txt(a['longa_pos'])}): sustente cheia até o fim."
    out.append({"t":"Toque inteira, lenta","d":f"Agora junte tudo numa passada contínua, devagar, sem parar nos erros.{longa}",
      "w":"Depois das partes, o todo: a passada contínua treina a continuidade, não a perfeição."})
    return out[:5]

# ---------- PLANO (treinar+dominar enxuto) ----------
def plano(m, a):
    f=difj[m['num']]['features']; r=rows[m['num']]; ns=f.get('n_secoes',2)
    if f.get('semicolcheia'): foco="a velocidade — as corridas só ficam limpas com tu-ku começando lento"
    elif f.get('tercina'): foco="as tercinas — três notas iguais no tempo, sem virar duas"
    elif f.get('contratempo'): foco="o contratempo — atacar fora do tempo com o pulso firme dentro"
    elif a and a['salto']>=11: foco=f"o salto largo ({nm_s(a['s_de'])}→{nm_s(a['s_para'])}) — chegar em cima centrado"
    elif f.get('extensa') or ns>=4: foco="o fôlego e a memória — a peça é longa e cobra planejamento"
    else: foco="o fraseado — som ligado e cheio do início ao fim"
    if f.get('extensa') or ns>=4: estrategia=f"Estude seção por seção (forma {r['forma']}); junte duas só quando cada uma sair de cor."
    elif f.get('semicolcheia'): estrategia="Metade da velocidade até a perfeição; metrônomo sobe de 10 em 10."
    else: estrategia="Passadas inteiras e lentas; depois isole só o que travou."
    return {"foco":foco,"estrategia":estrategia,
            "leitura":f"Antes de tudo, leia a peça uma vez sem tocar, de olho na armadura de {m['tom']}."}

OUT={}
for m in mus:
    a=analise(m['num'])
    OUT[m['num']]={"perfil":perfil(m,a),"plano":plano(m,a),"desafios":desafios(m,a)}
json.dump(OUT, open("app_pedagogia.json","w"), ensure_ascii=False)
nsvg=sum(1 for v in OUT.values() for d in v['desafios'] if 'svg' in d)
import os
print(f"pedagogia v2: {len(OUT)} músicas, {sum(len(v['desafios']) for v in OUT.values())} desafios, {nsvg} com pauta")
print("tamanho:", os.path.getsize("app_pedagogia.json")//1024, "KB")
# amostra editorial
v=OUT[55]
print("\n=== 055 ===")
print("PERFIL agudo:", v['perfil']['agudo'])
print("PLANO:", v['plano'])
for d in v['desafios']: print("DESAFIO:", d['t'], "|", d['d'][:90])
