# -*- coding: utf-8 -*-
"""
SUPER-PDF — O CAMINHO DO SAMBRASS · CURSO COMPLETO (A4 paisagem)
Estrutura:
  [I]   Capa + recapitulação pedagógica (como funciona, 80/20, fading, ciência da prática, diário, referências)
  [II]  Guia de divisão do samba
  [III] Aquecimento Chicowiz (flow + long tones)
  [IV]  6 LOTES. Cada lote:
          - abertura (tom-foco, técnica-foco, rotina interleaved, DIÁRIO CONSOLIDADO listando músicas)
          - Técnica I (escala+arpejo em níveis, no tom-foco; andaime decrescente por lote)
          - Técnica II (saltos+ritmo do samba no tom-foco)
          - página(s) reais do Essential Elements intercaladas (âncora da técnica do lote)
          - partituras originais do Sambrass, cada uma com OVERLAY de mini-diário (data + 5 níveis)
  [V]   Apêndices (índices + referências abertas)
Notação: Verovio (ABC->SVG->PNG). Partituras: PyMuPDF. EE: PyMuPDF (páginas reais).
"""
import verovio, fitz, os, json, csv, html, hashlib, re, cairosvg
import numpy as np
from weasyprint import HTML
from collections import Counter

WORK="/home/claude/sambrass"; R=f"{WORK}/sambrass-tutor-main"
SRC=f"{WORK}/sambrass.pdf"; EE=f"{WORK}/ee.pdf"
OUT="/mnt/user-data/outputs/Sambrass_Curso_Completo.pdf"
os.makedirs(f"{WORK}/b3", exist_ok=True)

# ---------------- dados ----------------
esc={p['num']:p for p in json.load(open(f"{R}/content/curadoria/escada.json"))['pieces']}
difj={p['num']:p for p in json.load(open(f"{R}/content/curadoria/dificuldade.json"))['pieces']}
rows={int(r['num']):r for r in csv.DictReader(open(f"{R}/content/catalog.csv"))}
raw={n:difj[n]['raw'] for n in range(1,111)}
order=sorted(range(1,111), key=lambda n:(esc[n]['dificuldade_calc'],raw[n],n))
# --- HEURÍSTICA LIMPA E AUDITADA: agudo (régua de faixas) prioritário + velocidade + fôlego ---
NOTES_ABC_RAW=json.load(open(f"{R}/content/notes_abc.json"))
def _pico_limpo(num):
    """Nota mais aguda REAL (teto Si4=72; acima é erro de OMR comprovado na partitura)."""
    key=f"sb-{num:03d}"
    if key not in NOTES_ABC_RAW: return 60
    corpo="\n".join(l for l in NOTES_ABC_RAW[key].split("\n") if not re.match(r'^[A-Za-z]:',l))
    val={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}; A=[]
    for m in re.finditer(r"([\^_=]*)([A-Ga-g])([,']*)", corpo):
        _,nota,oit=m.groups()
        octv=(5 if nota.islower() else 4)+oit.count("'")-oit.count(",")
        midi=val[nota.upper()]+12*octv
        if 52<=midi<=72: A.append(midi)
    return max(A) if A else 60
def _niv_agudo(p):
    # régua: até Ré4=1, Mi4=2, Fá4=3, Sol4=4, Lá4=5, Si4+=6
    if p<=62: return 1
    if p<=64: return 2
    if p<=65: return 3
    if p<=67: return 4
    if p<=69: return 5
    return 6
def _niv_vel(n):
    f=difj[n]['features']; r=rows[n]
    s=(2 if f.get('semicolcheia') else 0)+(1.5 if r['densidade']=='alta' else 1 if r['densidade']=='média-alta' else 0)+(0.5 if f.get('tercina') else 0)
    return min(int(s/0.9)+1,6)
def _niv_fol(n):
    f=difj[n]['features']
    s=(2 if f.get('extensa') else 0)+f.get('n_secoes',2)*0.5
    return min(int(s/0.9)+1,6)
AGUDO_NV={n:_niv_agudo(_pico_limpo(n)) for n in range(1,111)}
VEL_NV={n:_niv_vel(n) for n in range(1,111)}
FOL_NV={n:_niv_fol(n) for n in range(1,111)}
PICO={n:_pico_limpo(n) for n in range(1,111)}
SCORE={n:2*AGUDO_NV[n]+VEL_NV[n]+FOL_NV[n] for n in range(1,111)}
order=sorted(range(1,111), key=lambda n:(SCORE[n],AGUDO_NV[n],n))
CHUNKS=[list(map(int,c)) for c in np.array_split(order,6)]
PICO_NOME=["Dó","Dó#","Ré","Ré#","Mi","Fá","Fá#","Sol","Sol#","Lá","Lá#","Si"]
def pico_label(n):
    p=PICO[n]; return f"{PICO_NOME[p%12]}{p//12-1}"
PG=lambda n:n+3
def H(s): return html.escape(str(s))

# ---------------- escala de autoavaliação (descritiva) ----------------
ESCALA=[(1,"tive dificuldade na leitura"),(2,"leio, mas paro/erro"),
        (3,"toco seguido, lento"),(4,"toco no andamento"),(5,"toco de cor")]
ESCALA_TXT=" · ".join(f"{n} {d}" for n,d in ESCALA)

# ---------------- frases reais das músicas (notes_abc.json, OMR) ----------------
NOTES_ABC=json.load(open(f"{R}/content/notes_abc.json"))
def frase_real(num, ncomp=4):
    key=f"sb-{num:03d}"
    if key not in NOTES_ABC: return None
    abc=NOTES_ABC[key]
    head=[l for l in abc.split("\n") if re.match(r'^[MLQK]:',l) and not l.startswith("Q:")]  # tira tempo (warning)
    corpo=" ".join(l for l in abc.split("\n") if not re.match(r'^[A-Za-z]:',l)).strip()
    comps=[c.strip() for c in corpo.split("|") if c.strip()]
    i=0
    while i<len(comps) and re.fullmatch(r'[z0-9\s\-]+',comps[i]): i+=1
    comps=comps[i:i+ncomp]
    if not comps: return None
    return "\n".join(head)+"\n "+" | ".join(comps)+" |]\n"

# ---------------- EE: páginas reais por técnica (índice PDF = página impressa) ----------------
EE_PAGES={  # técnica -> lista de índices de página no ee.pdf
 "colcheias":[10],          # Eighth Notes #40-45
 "sincope":[14],            # Tie / Fit to be Tied #59
 "lipslur":[24],            # Special Trumpet Exercise – Lip Slurs
 "escala":[28],             # Concert Bb Scale / Arpeggio
 "rubank":[40],             # Rubank scale studies
 "dotted":[22],             # Dotted Quarter & Eighth (C3)
 "cromatismo":[33],         # Half-Steppin' / Chromatic
 "ritmo":[42],              # Rhythm Studies
}
# técnica-foco do lote -> páginas EE a intercalar
EE_FOR_FEAT={
 "sincope":["sincope","colcheias"],
 "cromatismo":["cromatismo","escala"],
 "contratempo":["sincope","ritmo"],
 "semicolcheia":["dotted","ritmo"],
 "tercina":["escala","lipslur"],
 "extensa":["rubank","lipslur"],
 "modulacao":["escala","cromatismo"],
}

# ---------------- Verovio ABC->PNG ----------------
def _norm(b):
    b=b.replace("\\n","\n").strip(); f={}
    for k in ["M","L","Q"]:
        m=re.search(rf'\b{k}:\s*(\S+)',b)
        if m: f[k]=m.group(1)
    mk=re.search(r'\bK:\s*([A-Ga-g][b#]?\w*)',b); kv=mk.group(1) if mk else "C"
    mus=re.sub(r'\b[MLQK]:\s*\S+','',b).strip()
    head=[f"{k}:{f[k]}" for k in ["M","L","Q"] if k in f]+[f"K:{kv}"]
    return "\n".join(head)+"\n"+mus
def png(abc,width=2200,scale=31):
    tk=verovio.toolkit(); a="X:1\n"+_norm(abc)+"\n"
    tk.setOptions({"inputFrom":"abc","scale":scale,"adjustPageHeight":True,"pageWidth":width,
      "header":"none","footer":"none","spacingStaff":1,"spacingSystem":1,
      "pageMarginLeft":10,"pageMarginRight":10,"pageMarginTop":10,"pageMarginBottom":10,"breaks":"none"})
    tk.loadData(a); svg=tk.renderToSVG(1)
    p=f"{WORK}/b3/x_{hashlib.md5(a.encode()).hexdigest()[:10]}.png"
    cairosvg.svg2png(bytestring=svg.encode(),write_to=p,output_width=1600); return p

# ---------------- tom-foco + feature ----------------
KEYS={"C":("C","Dó","C D E F G A B c"),"F":("F","Fá","F G A B c d e f"),
 "G":("G","Sol","G A B c d e ^f g"),"Bb":("Bb","Sib","B, C D E F G A B"),
 "D":("D","Ré","D E ^F G A B ^c d"),"A":("A","Lá","A B ^c d e ^f ^g a"),
 "Eb":("Eb","Mib","E F G A B c d e"),"Ab":("Ab","Láb","A B c d e f g a")}
DOMINANTE={"C":"G","F":"C","G":"D","Bb":"F","D":"A","A":"E","Eb":"Bb","Ab":"Eb"}
def kdom(nums):
    c=Counter(esc[n]['tom_escrito'] for n in nums if esc[n]['tom_escrito'] in KEYS)
    return c.most_common(1)[0][0] if c else "F"
def feat(nums):
    f=Counter()
    for n in nums:
        for k in ['tercina','semicolcheia','contratempo','cromatismo','extensa','modulacao']:
            if difj[n]['features'].get(k): f[k]+=1
    return f.most_common(1)[0][0] if f else "sincope"
FEAT_PT={"sincope":"síncope (C2)","tercina":"tercina (C5)","semicolcheia":"semicolcheia / staccato duplo (C4)",
 "contratempo":"contratempo (C6)","cromatismo":"cromatismo de passagem","extensa":"forma extensa / fôlego",
 "modulacao":"modulação de armadura"}
CORES=["#2e6b4f","#5a7a1f","#8a5a1f","#a3431f","#7a1f1f","#444444"]

# ---------------- exercícios em níveis (com andaime decrescente) ----------------
def _terças(k,n): return f"K:{k} M:4/4 L:1/8 "+" ".join(sum([[n[i],n[i+2]] for i in range(len(n)-2)],[]))+" |]"

# ---- ESCALA: cresce com o lote (oitava→colcheias→terças→articulada→cromática→mista rápida) ----
def b_escala(k,sc,i):
    n=sc.split(); a=" ".join(n); d=" ".join(reversed(n))
    asc2=" ".join(f"({n[j]} {n[j+1]})" for j in range(0,len(n)-1,2))
    rn=list(reversed(n)); desc2=" ".join(f"({rn[j]} {rn[j+1]})" for j in range(0,len(rn)-1,2))
    ter=_terças(k,n)
    lo=n[0]; alta=n[7]
    if i==1:
        return [("Escala · Nível 1 — semínimas","Uma oitava, uma nota por tempo. Leia a armadura, som cheio, ar constante. Conte 1-2-3-4 em voz alta.",f"K:{k} M:4/4 L:1/4 {a} | {d} |]"),
                ("Escala · Nível 2 — colcheias ligadas","Duas notas por tempo, sob a mesma ligadura (legato): articule só a primeira de cada par.",f"K:{k} M:4/4 L:1/8 {asc2} {desc2} |]")]
    if i==2:
        return [("Escala · Nível 1 — colcheias ligadas","Revisão: a escala em legato, articulando só a primeira de cada par.",f"K:{k} M:4/4 L:1/8 {asc2} {desc2} |]"),
                ("Escala · Nível 2 — em terças","Padrão 1-3-2-4-3-5… Desenvolve leitura e afinação de intervalos.",ter),
                ("Escala · Nível 3 — ida e volta sem parar","Suba e desça em colcheias, sem respirar no topo. Um só fôlego se possível.",f"K:{k} M:4/4 L:1/8 {a} {d} |]")]
    if i==3:
        return [("Escala · Nível 1 — em terças","Padrão em terças, agora como aquecimento.",ter),
                ("Escala · Nível 2 — articulada (staccato)","Mesma escala, notas curtas e destacadas (staccato). Ataque seco, ar contínuo por baixo.",f"K:{k} M:4/4 L:1/8 "+" ".join(f".{x}" for x in n)+" "+" ".join(f".{x}" for x in reversed(n))+" |]"),
                ("Escala · Nível 3 — terça + retorno","1-3-1, 2-4-2… combina salto de terça e volta ao grau.",f"K:{k} M:4/4 L:1/8 "+" ".join(f"{n[j]} {n[j+2]} {n[j]}" for j in range(0,len(n)-2,2))+" |]")]
    if i==4:
        return [("Escala · Nível 1 — duas oitavas (ida)","Estenda o registro: suba do grave ao agudo em duas oitavas.",f"K:{k} M:4/4 L:1/8 {a} {alta} |]".replace(f"{alta} |]", " ".join(x.lower() if x.isupper() else x+"'" for x in n[1:])+" |]")),
                ("Escala · Nível 2 — staccato rápido","Escala em colcheias destacadas, leve e rápida.",f"K:{k} M:2/4 L:1/8 "+" ".join(f".{x}" for x in n)+" |]"),
                ("Escala · Nível 3 — terças ligadas","Terças, agora ligadas de duas em duas — legato nos saltos.",f"K:{k} M:4/4 L:1/8 "+" ".join(f"({n[j]} {n[j+2]})" for j in range(len(n)-2))+" |]")]
    if i==5:
        return [("Escala · Nível 1 — cromática (subida)","Suba de meio em meio tom (escala cromática). Afinação milimétrica.",f"K:{k} M:4/4 L:1/8 {n[0]} ^{n[0]} {n[1]} ^{n[1]} {n[2]} {n[3]} ^{n[3]} {n[4]} ^{n[4]} {n[5]} ^{n[5]} {n[6]} {n[7]} |]"),
                ("Escala · Nível 2 — diatônica + cromática","Alterna grau da escala e nota cromática de passagem.",f"K:{k} M:4/4 L:1/8 {n[0]} ^{n[0]} {n[1]} ^{n[1]} {n[2]} {n[3]} ^{n[3]} {n[4]} |]"),
                ("Escala · Nível 3 — terças em colcheias rápidas","Terças no andamento, sem parar.",ter.replace("L:1/8","L:1/8 Q:1/4=120"))]
    # i==6
    return [("Escala · Nível 1 — duas oitavas articulada","Duas oitavas com staccato leve no caminho. Registro e controle.",f"K:{k} M:4/4 L:1/8 "+" ".join(f".{x}" for x in n)+" "+" ".join(f".{x.lower() if x.isupper() else x}" for x in n[1:])+" |]"),
            ("Escala · Nível 2 — cromática ida e volta","Cromática subindo e descendo, ligada, em um só gesto.",f"K:{k} M:4/4 L:1/16 ({n[0]} ^{n[0]} {n[1]} ^{n[1]} {n[2]} {n[3]} ^{n[3]} {n[4]} ^{n[4]} {n[5]} ^{n[5]} {n[6]} {n[7]} ^{n[6]} {n[6]} {n[5]}) |]"),
            ("Escala · Nível 3 — padrão misto","Combina terça, grau e cromatismo: o tecido das peças difíceis.",f"K:{k} M:4/4 L:1/8 {n[0]} {n[2]} ^{n[0]} {n[1]} {n[3]} {n[2]} {n[4]} {n[3]} |]")]

# ---- ARPEJO: tríade→inversão→7ª→quebrado→arpejo+escala→2 oitavas ----
def b_arpejo(k,sc,i):
    n=sc.split(); t=[n[0],n[2],n[4],n[7]]; b7="_"+n[7]
    if i==1:
        return [("Arpejo (A1) · Nível 1 — tríade ↑↓","Tríade maior subindo e descendo, uma nota por tempo. A base de toda harmonia do samba.",f"K:{k} M:4/4 L:1/4 {t[0]} {t[1]} {t[2]} {t[3]} | {t[3]} {t[2]} {t[1]} {t[0]} |]")]
    if i==2:
        return [("Arpejo · Nível 1 — tríade em colcheias","Tríade ligada, mais fluente.",f"K:{k} M:2/4 L:1/8 ({t[0]} {t[1]} {t[2]} {t[3]}) | ({t[3]} {t[2]} {t[1]} {t[0]}) |]"),
                ("Arpejo · Nível 2 — primeira inversão","Comece pela terça (3-5-8-3): ouça como muda a cor do acorde.",f"K:{k} M:2/4 L:1/8 {t[1]} {t[2]} {t[3]} {t[1]} | {t[2]} {t[1]} {t[0]} z |]")]
    if i==3:
        return [("Arpejo · Nível 1 — tríade ágil","Aquecimento: tríade quebrada.",f"K:{k} M:2/4 L:1/8 |: ({t[0]} {t[1]} {t[2]} {t[1]}) :|]"),
                ("Arpejo · Nível 2 — com 7ª (A3)","Acrescenta a 7ª da dominante. Ouça a tensão que pede resolução.",f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {t[3]} {b7} {t[2]} {t[1]} {t[0]} |]")]
    if i==4:
        return [("Arpejo · Nível 1 — com 7ª","Revisão da 7ª, agora ligada.",f"K:{k} M:4/4 L:1/8 ({t[0]} {t[1]} {t[2]} {t[3]} {b7} {t[2]} {t[1]} {t[0]}) |]"),
                ("Arpejo · Nível 2 — arpejo + escala","Sobe pelo arpejo, desce pela escala. Integra as duas ferramentas.",f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {t[3]} {n[6]} {n[5]} {n[4]} {n[3]} |]")]
    if i==5:
        return [("Arpejo · Nível 1 — quebrado contínuo","Arpejo quebrado em colcheias, sem parar — flexibilidade.",f"K:{k} M:2/4 L:1/8 |: ({t[0]} {t[1]} {t[2]} {t[1]}) :| ({t[2]} {t[3]} {t[2]} {t[1]}) |]"),
                ("Arpejo · Nível 2 — relativa menor","Arpejo do VI grau (relativa menor): outra cor sobre o mesmo tom.",f"K:{k} M:2/4 L:1/8 {n[5]} {n[0]} {n[2]} {n[0]} | {n[5]} {n[2]} {n[0]} z |]")]
    return [("Arpejo · Nível 1 — duas oitavas","Tríade em duas oitavas: estende o registro com a harmonia.",f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {t[3]} {t[1].lower() if t[1].isupper() else t[1]} {t[2].lower() if t[2].isupper() else t[2]} |]"),
            ("Arpejo · Nível 2 — 7ª + resolução","Arpejo de 7ª resolvendo na tônica. O gesto cadencial.",f"K:{k} M:4/4 L:1/8 {t[0]} {t[1]} {t[2]} {b7} {t[2]} {t[1]} {t[0]} {t[0]} |]")]

# ---- SALTOS: oitava→quintas→lip slur→saltos amplos→arpejo saltado→registro extremo ----
def b_salto(k,sc,i):
    n=sc.split()
    if i<=2:
        return [("Saltos · Nível 1 — oitava","Tônica → oitava → tônica. Centre o som nas duas alturas, sem apertar.",f"K:{k} M:4/4 L:1/4 {n[0]} {n[7]} {n[0]} {n[7]} | {n[7]} {n[0]} {n[7]} {n[0]} |]")]
    if i<=4:
        return [("Saltos · Nível 1 — quintas e sextas","Intervalos largos alternados. Sem 'escorregar' entre as notas (sem glissando).",f"K:{k} M:4/4 L:1/4 {n[0]} {n[4]} {n[1]} {n[5]} | {n[2]} {n[6]} {n[0]} {n[7]} |]"),
                ("Saltos · Nível 2 — lip slur","Lip slur: ligue o grupo SEM articular — só o ar move entre as notas (Schlossberg/Bai Lin).",f"K:{k} M:2/4 L:1/8 ({n[0]} {n[4]} {n[2]} {n[7]}) | ({n[4]} {n[2]} {n[0]}) z |]")]
    return [("Saltos · Nível 1 — lip slur amplo","Lip slur cobrindo a tríade em duas oitavas, ligado.",f"K:{k} M:2/4 L:1/8 ({n[0]} {n[4]} {n[7]} {n[4]}) | ({n[2]} {n[0]}) z |]"),
            ("Saltos · Nível 2 — saltos com articulação","Saltos amplos articulados, no andamento. Precisão de ataque em cada altura.",f"K:{k} M:2/4 L:1/8 .{n[0]} .{n[7]} .{n[2]} .{n[5]} | .{n[4]} .{n[0]} z2 |]")]

# ---- ARTICULAÇÃO (eixo NOVO): legato/staccato → acento → tu-ku, crescente ----
def b_articulacao(k,sc,i):
    n=sc.split()
    if i==1:
        return [("Articulação · Nível 1 — ligado × destacado","A mesma frase duas vezes: primeiro toda ligada, depois toda destacada. Sinta a diferença no ataque.",f"K:{k} M:2/4 L:1/8 ({n[0]} {n[1]} {n[2]} {n[3]}) | .{n[0]} .{n[1]} .{n[2]} .{n[3]} |]")]
    if i==2:
        return [("Articulação · Nível 1 — acento","Acente (>) a primeira de cada tempo; as outras, leves.",f"K:{k} M:2/4 L:1/8 !>!{n[0]} {n[1]} !>!{n[2]} {n[3]} | !>!{n[4]} {n[3]} !>!{n[2]} {n[1]} |]")]
    if i==3:
        return [("Articulação · Nível 1 — staccato leve","Notas curtas e iguais, leves. O ar não para por baixo.",f"K:{k} M:2/4 L:1/8 .{n[0]} .{n[1]} .{n[2]} .{n[3]} | .{n[4]} .{n[3]} .{n[2]} .{n[1]} |]"),
                ("Articulação · Nível 2 — misto ligado+destacado","Duas ligadas, duas destacadas — o padrão de articulação mais comum do choro/samba.",f"K:{k} M:2/4 L:1/8 ({n[0]} {n[1]}) .{n[2]} .{n[3]} | ({n[4]} {n[3]}) .{n[2]} .{n[1]} |]")]
    if i==4:
        return [("Articulação · Nível 1 — tu-ku lento","Introdução ao duplo staccato: alterne sílabas TU-KU em colcheias, devagar.",f"K:{k} M:2/4 L:1/8 .{n[0]} .{n[0]} .{n[2]} .{n[2]} | .{n[4]} .{n[4]} .{n[2]}2 |]"),
                ("Articulação · Nível 2 — ligado entre saltos","Ligue na subida, destaque no retorno.",f"K:{k} M:2/4 L:1/8 ({n[0]} {n[2]} {n[4]}) .{n[2]} | .{n[0]} z3 |]")]
    if i==5:
        return [("Articulação · Nível 1 — tu-ku médio","Duplo staccato em semicolcheias, andamento médio. TU-KU-TU-KU igual.",f"K:{k} M:2/4 L:1/16 .{n[0]}.{n[0]}.{n[0]}.{n[0]} .{n[2]}.{n[2]}.{n[2]}.{n[2]} |]"),
                ("Articulação · Nível 2 — acento deslocado","Acento no contratempo, o suingue do samba na articulação.",f"K:{k} M:2/4 L:1/8 {n[0]} !>!{n[2]} {n[1]} !>!{n[4]} | {n[2]} !>!{n[0]} z2 |]")]
    return [("Articulação · Nível 1 — tu-ku rápido","Duplo staccato veloz e nivelado. Se a língua travar, volte ao tu-ku lento.",f"K:{k} M:2/4 L:1/16 .{n[0]}.{n[1]}.{n[2]}.{n[3]} .{n[4]}.{n[3]}.{n[2]}.{n[1]} |]"),
            ("Articulação · Nível 2 — todas as articulações","Ligado, acentuado e destacado na mesma frase — controle total.",f"K:{k} M:2/4 L:1/8 ({n[0]} {n[1]}) !>!{n[2]} .{n[3]} | ({n[4]} {n[3]}) !>!{n[2]} .{n[0]} |]")]

# ---- NOTA LONGA / DINÂMICA (eixo NOVO): longa → cresc → messa → sf → frase dinâmica ----
def b_dinamica(k,sc,i):
    n=sc.split(); t=n[0]
    if i==1:
        return [("Som · Nível 1 — nota longa","Sustente cada nota 4 tempos a ~60 bpm. Ataque limpo, som imóvel, corte seco.",f"K:{k} M:4/4 L:1/1 {n[0]} | {n[4]} | {n[2]} | {n[0]} |]")]
    if i==2:
        return [("Som · Nível 1 — crescendo","Cresça do piano ao forte ao longo da nota longa. Só o ar muda, o som não 'estoura'.",f'K:{k} M:4/4 L:1/1 "<"{n[0]} | "<"{n[4]} |]')]
    if i==3:
        return [("Som · Nível 1 — messa di voce","Pianíssimo → forte no centro → pianíssimo. Controle total do ar numa nota só.",f'K:{k} M:4/4 L:1/1 "<"{n[0]} | ">"{n[0]} |]')]
    if i==4:
        return [("Som · Nível 1 — sforzando","Ataque forte e recue imediato (sf). Depois a nota cresce de novo.",f'K:{k} M:4/4 L:1/2 "sf"{n[4]}2 | "<"{n[4]}2 |]')]
    if i==5:
        return [("Som · Nível 1 — dinâmica na frase","Faça a frase respirar: cresça na subida, recue na descida.",f'K:{k} M:4/4 L:1/4 "p"{n[0]} {n[2]} "<"{n[4]} {n[7]} | ">"{n[4]} {n[2]} {n[0]}2 |]')]
    return [("Som · Nível 1 — controle extremo","Nota longa pianíssimo, perfeitamente estável — o teste final do ar. Depois messa di voce.",f'K:{k} M:4/4 L:1/1 "pp"{n[7]} | "<"{n[0]} |]')]

# ---- RITMO: feature do lote, com 2 níveis (mantém variação por feature) ----
def b_ritmo(k,sc,ft):
    n=sc.split()
    M={
     "sincope":[("Ritmo · síncope (C2) — Nível 1","Colcheia–semínima–colcheia. O acento (>) cai na nota longa do meio.",f"K:{k} M:2/4 L:1/8 |: {n[0]}/ !>!{n[2]}2 {n[0]}/ :| {n[2]}/ !>!{n[4]}2 {n[2]}/ |]"),
                ("Ritmo · síncope — Nível 2 · encadeada","Síncopes em sequência, sem respirar no meio.",f"K:{k} M:2/4 L:1/8 {n[0]}/ !>!{n[2]}2 {n[0]}/ | {n[2]}/ !>!{n[4]}2 {n[2]}/ | {n[0]}4 |]")],
     "tercina":[("Ritmo · tercina (C5) — Nível 1","Três notas iguais por tempo. Diga 'tri-o-la', devagar.",f"K:{k} M:2/4 L:1/8 | (3{n[0]}{n[1]}{n[2]} (3{n[2]}{n[1]}{n[0]} | {n[0]}2 z2 |]"),
                ("Ritmo · tercina — Nível 2 · em arpejo","Tercinas desenhando a tríade.",f"K:{k} M:2/4 L:1/8 | (3{n[0]}{n[2]}{n[4]} (3{n[7]}{n[4]}{n[2]} | {n[0]}2 z2 |]")],
     "semicolcheia":[("Ritmo · semicolcheias (C4) — Nível 1","Quatro iguais por tempo. Articule com a sílaba dupla TU-KU-TU-KU (duplo staccato do Arban).",f"K:{k} M:2/4 L:1/16 |: {n[0]}{n[1]}{n[2]}{n[3]} {n[0]}{n[1]}{n[2]}{n[3]} :|]"),
                ("Ritmo · C3+C4 — Nível 2 · galope + corrida","Pontuada+semi (galope) alternando com quatro semicolcheias.",f"K:{k} M:2/4 L:1/16 | {n[0]}3 {n[2]} {n[0]}{n[1]}{n[2]}{n[3]} | {n[2]}3 {n[0]} {n[0]}4 |]")],
     "contratempo":[("Ritmo · contratempo (C6) — Nível 1","Pausa no tempo, ataque no 'e'. Sinta o silêncio antes da nota.",f"K:{k} M:2/4 L:1/8 | z {n[0]} z {n[2]} | z {n[4]} {n[2]}2 |]"),
                ("Ritmo · contratempo — Nível 2 · contínuo","Ataques deslocados — o suingue do samba.",f"K:{k} M:2/4 L:1/8 | z !>!{n[0]} z !>!{n[2]} | z !>!{n[4]} z !>!{n[2]} | {n[0]}2 z2 |]")],
     "cromatismo":[("Ritmo · cromatismo (A4) — Nível 1","Nota → vizinha cromática → nota (bordadura).",f"K:{k} M:2/4 L:1/8 | {n[0]} ^{n[0]} {n[1]}2 | {n[2]} _{n[2]} {n[1]}2 |]"),
                ("Ritmo · cromatismo — Nível 2 · descida","Linha que desce de meio em meio tom. Afinação milimétrica.",f"K:{k} M:2/4 L:1/8 | {n[4]} _{n[4]} {n[2]}2 | {n[1]} _{n[1]} {n[0]}2 |]")],
     "extensa":[("Ritmo · fôlego — Nível 1 · longa após corrida","Toque a corrida e SUSTENTE a longa cheia até o fim, sem desinflar.",f"K:{k} M:4/4 L:1/8 {n[0]} {n[1]} {n[2]} {n[3]} {n[4]}4- | {n[4]}4 z4 |]"),
                ("Ritmo · respiração — Nível 2 · frase com respiros","Respire só onde há a vírgula (breath mark). A respiração é parte do ritmo.",f"K:{k} M:2/4 L:1/8 {n[0]} {n[2]} {n[4]} {n[2]} | {n[0]}2 z, | {n[1]} {n[2]} {n[4]} {n[2]} | {n[0]}4 |]")],
     "modulacao":[("Ritmo · síncope — Nível 1","Fixe a célula-base do samba antes de tratar a modulação.",f"K:{k} M:2/4 L:1/8 {n[0]}/ !>!{n[2]}2 {n[0]}/ | {n[2]}/ !>!{n[4]}2 {n[2]}/ |]"),
                ("Ritmo · modulação — Nível 2 · troca de armadura","Releia a armadura na barra dupla: o trecho modula para o tom da dominante.",f"K:{k} M:2/4 L:1/8 {n[0]} {n[2]} {n[4]} {n[2]} | K:{DOMINANTE.get(k,'G')} {n[4]} {n[4]} {n[4]} {n[4]} | {n[4]}4 |]")],
    }
    return M.get(ft,M["sincope"])

# ---------------- HTML helpers ----------------
def card(i,nm,ins,abc,cor):
    p=png(abc)
    return f'<div class="ex"><div class="exhd"><span class="exn" style="background:{cor}">{i}</span><b>{H(nm)}</b></div><p class="instr">{H(ins)}</p><img class="score" src="file://{p}"></div>'

BASE_CSS="""*{box-sizing:border-box} body{margin:0;font-family:Georgia,serif;color:#1a1a1a;font-size:10pt;line-height:1.4}
h2.sec{font-family:Helvetica,Arial,sans-serif;font-size:11.5pt;letter-spacing:1px;text-transform:uppercase;color:#7a1f1f;border-bottom:2px solid #7a1f1f;padding-bottom:4px;margin:0 0 9px}
p{margin:0 0 7px}"""

def tecnica_page(lnum,titulo,sub,cards_html,cor):
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>
@page{{size:A4 landscape;margin:11mm 13mm}} {BASE_CSS}
.head{{border-top:7mm solid {cor};margin:-11mm -13mm 6mm;padding:5mm 13mm 0}}
.kick{{font-family:Helvetica,Arial,sans-serif;letter-spacing:3px;text-transform:uppercase;font-size:8.5pt;color:#6b6456}}
.lnum{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#fff;background:{cor};border-radius:4px;padding:3px 12px;font-size:11pt;display:inline-block;margin-bottom:5px}}
h1{{font-size:18pt;margin:3px 0 1px}} .sub{{font-family:Helvetica,Arial,sans-serif;font-size:10pt;font-weight:bold;color:{cor};margin:2px 0}}
.exer{{column-count:2;column-gap:10mm;margin-top:3mm}}
.ex{{break-inside:avoid;margin-bottom:3.5mm;border:1px solid #d8d2c4;border-radius:5px;padding:5px 8px;background:#fff}}
.exhd{{display:flex;align-items:center;gap:7px;margin-bottom:1px}}
.exn{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#fff;width:18px;height:18px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:9.5pt}}
.exhd b{{font-size:9.6pt}} .instr{{font-size:8.2pt;color:#6b6456;font-style:italic;margin:1px 0 3px}}
.score{{width:100%;height:auto;max-height:30mm}}
</style></head><body>
<div class="head"><div class="kick">O Caminho do Sambrass · Curso completo · Técnica aplicada</div>
<span class="lnum">{H(lnum)}</span><h1>{H(titulo)}</h1><div class="sub">{H(sub)}</div></div>
<div class="exer">{cards_html}</div></body></html>"""

# render WeasyPrint -> arquivo pdf
def render(htmlstr,path): HTML(string=htmlstr).write_pdf(path); return path

# ---------------- página de FRASES REAIS do repertório do lote ----------------
def frases_page(i, nums, cor, nome_tom):
    """Extrai frases das músicas-âncora do lote (menor dificuldade) como exercício de leitura real."""
    ancoras=sorted(nums, key=lambda n:esc[n]['dificuldade_calc'])[:4]
    cards=[]; j=1
    for n in ancoras:
        fr=frase_real(n,4)
        if not fr: continue
        try:
            p=png(fr, scale=30)
        except Exception:
            continue
        tit=rows[n]['titulo']; comp=rows[n]['compositor']; d=esc[n]['dificuldade_calc']
        cards.append(f'<div class="ex"><div class="exhd"><span class="exn" style="background:{cor}">{j}</span>'
                     f'<b>{H(tit)}</b> <span class="src">{H(comp)} · dif {d}</span></div>'
                     f'<p class="instr">Trecho inicial da música. Toque lento, sinta a divisão antes de juntar à peça completa.</p>'
                     f'<img class="score" src="file://{p}"></div>')
        j+=1
    cards_html="".join(cards)
    extra_css=".src{font-family:Helvetica,Arial,sans-serif;font-size:7.5pt;color:#6b6456;font-weight:normal;margin-left:4px}"
    htmlstr=tecnica_page(f"Lote {i}", f"Lote {i} · Técnica III — Frases do repertório",
        f"Trechos REAIS das músicas do lote, no tom de {nome_tom}. A técnica vira música: leia, depois aplique na peça inteira.",
        cards_html, cor).replace("</style>", extra_css+"\n</style>")
    # nota de rodapé sobre OMR
    htmlstr=htmlstr.replace("</body>",
        '<p style="font-size:8pt;color:#9a9384;font-style:italic;margin-top:4mm;font-family:Helvetica">'
        'Frases extraídas automaticamente das partituras (OMR) — confira contra a partitura original do lote, que é a fonte definitiva.</p></body>')
    return render(htmlstr, f"{WORK}/b3/l{i}_TIII.pdf")

# ============================================================================
# RECAPITULAÇÃO PEDAGÓGICA (multipágina) — fundamentada na pesquisa
# ============================================================================
def recap_pdf():
    # --- dados da escada pedagógica detalhada ---
    EE_LABEL={"sincope":"Tie #59","cromatismo":"Chromatic","contratempo":"Rhythm","semicolcheia":"Dotted #110",
              "tercina":"Scale/Arpeggio","extensa":"Rubank","modulacao":"Scale"}
    CELULA={"sincope":"C2 síncope","cromatismo":"A4 cromatismo","contratempo":"C6 contratempo",
            "semicolcheia":"C4 semicolcheia","tercina":"C5 tercina","extensa":"forma A/B/C/D","modulacao":"modulação"}
    linhas=[]; diag_rows=[]
    smax=max(SCORE.values())
    NOTA_PT={59:"Mib",60:"Mi",62:"Fá#",64:"Sol#",65:"Lá",67:"Si",69:"Dó#",84:"Dó agudo"}
    def nota_nome(midi):
        # nome aproximado da nota escrita mais aguda
        nomes=["Dó","Dó#","Ré","Ré#","Mi","Fá","Fá#","Sol","Sol#","Lá","Lá#","Si"]
        return nomes[int(round(midi))%12]
    for i,nums in enumerate(CHUNKS,1):
        k=kdom(nums); _,nome_tom,_=KEYS.get(k,(k,k,"")); ft=feat(nums)
        picos=[PICO[n] for n in nums]; ves=[VEL_NV[n] for n in nums]; fos=[FOL_NV[n] for n in nums]
        scs=[SCORE[n] for n in nums]
        ancoras=sorted(nums,key=lambda n:SCORE[n])[:3]
        exemplos=", ".join(rows[n]['titulo'] for n in ancoras)
        andaime="completo" if i<=2 else ("reduzido" if i<=4 else "mínimo")
        cor=CORES[i-1]
        agudo_lbl=f"até {nota_nome(max(picos))}{max(picos)//12-1}"
        vel_lbl="baixa" if max(ves)<=2 else ("média" if max(ves)<=4 else "alta")
        fol_lbl="curto" if max(fos)<=2 else ("médio" if max(fos)<=4 else "longo")
        linhas.append(f"<tr><td class='ln' style='color:{cor}'><b>{i}</b></td>"
                      f"<td>{agudo_lbl}</td><td>{vel_lbl}</td><td>{fol_lbl}</td>"
                      f"<td><b>{nome_tom}</b></td><td>{FEAT_PT.get(ft,ft)}</td>"
                      f"<td>{andaime}</td><td class='ex2'>{H(exemplos)}</td></tr>")
        w=int(min(scs)/smax*100); w2=int(max(scs)/smax*100)
        diag_rows.append(f"<div class='drow'><span class='dlbl' style='background:{cor}'>Lote {i}</span>"
                         f"<div class='dbar'><div class='dfill' style='left:{w}%;width:{max(w2-w,6)}%;background:{cor}'></div>"
                         f"<span class='dtxt'>{nome_tom} · agudo {agudo_lbl} · veloc. {vel_lbl} · fôlego {fol_lbl}</span></div></div>")
    escada_linhas="".join(linhas)
    escada_diagrama="<div class='diag'>"+"".join(diag_rows)+"<div class='daxis'><span>mais confortável</span><span>mais exigente</span></div></div>"

    doc=f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>
@page{{size:A4 landscape;margin:0}}
@page conteudo{{size:A4 landscape;margin:13mm 16mm; @bottom-center{{content:"O Caminho do Sambrass · Curso Completo"; font-family:Helvetica;font-size:8pt;color:#9a9384}} @bottom-right{{content:counter(page); font-family:Helvetica;font-size:8pt;color:#9a9384}}}}
{BASE_CSS}
.capa{{height:210mm;display:flex;flex-direction:column;justify-content:center;padding:0 32mm;border-left:16mm solid #7a1f1f;page-break-after:always}}
.capa .k{{font-family:Helvetica,Arial,sans-serif;letter-spacing:5px;text-transform:uppercase;font-size:11pt;color:#6b6456}}
.capa h1{{font-size:44pt;line-height:1.02;margin:14px 0 6px}} .capa .sub{{font-size:15pt;font-style:italic;color:#7a1f1f}}
.capa .meta{{margin-top:22px;font-size:10.5pt;color:#3a3a3a;max-width:80%}}
.conteudo{{page:conteudo}}
.cols2{{column-count:2;column-gap:14mm}} .cols2 p{{margin:0 0 6px}}
.box{{border:1px solid #d8d2c4;border-left:5px solid #2e6b4f;border-radius:5px;padding:8px 11px;margin:0 0 8px;background:#faf9f6;break-inside:avoid}}
.box b{{font-family:Helvetica,Arial,sans-serif}}
h3{{font-family:Helvetica,Arial,sans-serif;font-size:11pt;color:#1a1a1a;margin:10px 0 5px}}
.ref{{font-size:8.6pt;color:#555;line-height:1.45}} .ref li{{margin-bottom:3px}}
table.flow{{width:100%;border-collapse:collapse;font-size:9pt;margin:4px 0 8px}}
table.flow td,table.flow th{{border:1px solid #d8d2c4;padding:4px 7px;text-align:left}}
table.flow th{{background:#f2efe6;font-family:Helvetica,Arial,sans-serif;font-size:8pt;text-transform:uppercase;letter-spacing:.5px;color:#6b6456}}
.rmin{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#2e6b4f}}
table.esc{{width:100%;border-collapse:collapse;font-size:8.4pt;margin:4px 0 6px}}
table.esc th,table.esc td{{border:1px solid #d8d2c4;padding:4px 6px;text-align:left;vertical-align:top}}
table.esc th{{background:#f2efe6;font-family:Helvetica,Arial,sans-serif;font-size:7.5pt;text-transform:uppercase;letter-spacing:.4px;color:#6b6456}}
table.esc .ln{{text-align:center;font-size:11pt}} table.esc .ee{{font-size:7.6pt;color:#555}} table.esc .ex2{{font-size:7.7pt;color:#3a3a3a}}
.diag{{margin:8px 0 12px}}
.drow{{display:flex;align-items:center;gap:8px;margin-bottom:5px}}
.dlbl{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#fff;font-size:8pt;padding:3px 9px;border-radius:3px;min-width:54px;text-align:center}}
.dbar{{position:relative;flex:1;height:20px;background:#f2efe6;border-radius:3px;border:1px solid #e2ddd0}}
.dfill{{position:absolute;top:0;height:100%;border-radius:3px;opacity:.45}}
.dtxt{{position:absolute;left:8px;top:3px;font-size:8pt;color:#1a1a1a}}
.daxis{{display:flex;justify-content:space-between;font-size:7.5pt;color:#9a9384;font-family:Helvetica,Arial,sans-serif;margin-top:2px;padding:0 2px}}
</style></head><body>

<section class="capa">
  <div class="k">Trompete Bb · método completo de estudo · 110 sambas</div>
  <h1>O Caminho<br>do Sambrass</h1>
  <div class="sub">Curso completo autocontido · aquecimento, seis lotes progressivos e repertório integral</div>
  <div class="meta">Um método para atravessar o caderno Sambrass23 inteiro. 80% repertório real, 20% técnica —
  e a técnica sempre aplicada ao tom e às dificuldades das músicas de cada lote. Inclui aquecimento diário,
  exercícios em níveis, páginas de referência do Essential Elements, guia de divisão do samba e diário de prática.</div>
</section>

<section class="conteudo">
  <h2 class="sec">Recapitulação pedagógica — como este curso funciona</h2>
  <div class="cols2">
    <p>Este caderno não é uma coletânea: é um <b>curso sequenciado</b>. As 110 músicas foram ordenadas por
    três <b>marcadores de dificuldade física</b> do trompete — quão <b>agudo</b> é o registro, quão <b>longas</b>
    são as frases (fôlego) e quão <b>rápidas</b> são as notas — com peso maior no registro agudo. Divididas em
    <b>seis lotes progressivos</b> (precedidos de um capítulo preparatório), você atravessa o caderno do mais
    confortável ao mais exigente, e a cada passo a técnica que você treina é a que as próximas músicas pedem.</p>

    <div class="box"><b>A proporção 80 / 20.</b> Cerca de 20% do material é técnica; 80% é repertório.
    A técnica nunca é abstrata: a escala, o arpejo, os saltos e o ritmo de cada lote estão no <b>tom-foco</b>
    daquele lote e preparam suas músicas. É o princípio de Pareto aplicado ao estudo — concentrar o esforço
    nos poucos elementos que destravam a maior parte do repertório.</p></div>

    <div class="box" style="border-left-color:#8a5a1f"><b>Andaimes que diminuem (fading).</b> No Lote 1 os
    exercícios trazem contagem e instruções detalhadas; conforme você avança, esses apoios são retirados de
    propósito. No fim, você lê e respira sozinho. Sentir que ficou "mais nu" é sinal de progresso, não de erro.</p></div>

    <p><b>Intercalar, não empilhar.</b> A pesquisa em aprendizado motor mostra que alternar tarefas
    (técnica ↔ repertório ↔ ritmo) dá <b>melhor retenção</b> do que esgotar uma coisa antes da outra — mesmo
    que repetir em bloco <i>pareça</i> render mais no momento. Por isso a rotina diária mistura os blocos.</p>

    <h3>A rotina diária (90 min)</h3>
    <table class="flow">
      <tr><th>Tempo</th><th>Bloco</th><th>O quê</th></tr>
      <tr><td><span class="rmin">15</span></td><td>Aquecimento</td><td>Flow studies + notas longas (páginas de abertura)</td></tr>
      <tr><td><span class="rmin">20</span></td><td>Técnica do lote</td><td>Escala/arpejo/salto/ritmo no tom-foco, devagar</td></tr>
      <tr><td><span class="rmin">35</span></td><td>Música em foco</td><td>Uma partitura do lote, seção por seção</td></tr>
      <tr><td><span class="rmin">15</span></td><td>Leitura à 1ª vista</td><td>Uma partitura nova do lote, lenta, sem parar</td></tr>
      <tr><td><span class="rmin">5</span></td><td>Revisão</td><td>Uma peça já dominada, em andamento de roda</td></tr>
    </table>

    <div class="box" style="border-left-color:#a3431f"><b>Prática lenta — com alternância.</b> Toque devagar para
    a precisão, mas não suba o metrônomo só de forma linear: <b>alterne</b> tempos lento e rápido. A evidência de
    aprendizado motor sugere que alternar é mais eficiente que a rampa gradual monotônica.</p></div>

    <h3>O diário de prática</h3>
    <p>Há dois registros, deliberadamente mínimos. <b>No pé de cada partitura</b>, um mini-diário: data e a
    dificuldade percebida em 5 níveis. <b>Na abertura de cada lote</b>, um quadro consolidado com as músicas do
    lote e cinco linhas de sessão (data · fez completo? · dificuldade). Anotar a dificuldade percebida força a
    metacognição — o monitoramento e a autoavaliação são o que mais distingue quem aprende sozinho com eficácia.
    Mantenha curto: a constância vale mais que o detalhe.</p>

    <div class="box"><b>Quando avançar de lote.</b> Se em duas sessões seguidas você marcar "fez completo" e
    dificuldade ≤ 2 nas músicas do lote, siga adiante. Se uma música ficar em dificuldade ≥ 4 por três sessões,
    volte ao bloco técnico e isole a microhabilidade daquele trecho (a síncope, o salto, o cromatismo).</p></div>

    <h3>Fundamentação (leituras de referência)</h3>
    <ul class="ref">
      <li><b>Som e respiração:</b> Vincent Cichowicz, <i>Flow Studies</i>; James Stamp, <i>Warm-Ups</i>; Carmine Caruso, <i>Musical Calisthenics</i>.</li>
      <li><b>Técnica (domínio público, IMSLP):</b> Arban, <i>Méthode Complète</i> (escalas, intervalos, tu-ku/duplo staccato p.175, lip slurs p.39); Clarke, <i>Technical Studies</i> (digitação, cromatismo); Schlossberg, <i>Daily Drills</i> (flexibilidade, registro); Saint-Jacome, <i>Grand Method</i>.</li>
      <li><b>Sequenciamento:</b> Essential Elements 2000, Book 1–2 (Hal Leonard) — páginas de referência intercaladas em cada lote.</li>
      <li><b>Ciência da prática:</b> Ericsson (prática deliberada); Carter &amp; Grahn 2016 (interleaving); Bjork (dificuldades desejáveis); Zimmerman (autorregulação).</li>
      <li><b>Divisão do samba:</b> Carlos Sandroni, <i>Feitiço Decente</i>; Mário Sève, <i>Vocabulário do Choro</i>.</li>
      <li><b>Ferramentas abertas:</b> notação gerada com Verovio / ABC; tipografia musical livre.</li>
    </ul>
    <p class="ref" style="margin-top:6px">Material de estudo pessoal. As partituras do repertório e as páginas de
    referência do Essential Elements são reproduzidas para uso individual de estudo.</p>
  </div>

  <h2 class="sec" style="page-break-before:always">A escada pedagógica — visão detalhada dos seis lotes</h2>
  <p>Os seis lotes formam uma progressão em três marcadores físicos que avançam juntos: o <b>registro</b>
  (quão agudo você sobe), o <b>fôlego</b> (quão longas são as frases) e a <b>velocidade</b> (quão rápidas são
  as notas). O registro pesa mais no início — por isso o Lote 1 vive na zona média confortável, e o agudo só
  aparece de verdade nos lotes finais. Antes do Lote 1, o <b>capítulo preparatório</b> assenta o corpo.</p>
  {escada_diagrama}
  <h3>Tabela detalhada por lote</h3>
  <table class="esc">
    <tr><th>Lote</th><th>Agudo</th><th>Velocidade</th><th>Fôlego</th><th>Tom-foco</th><th>Técnica-foco</th><th>Andaime</th><th>Músicas-exemplo</th></tr>
    {escada_linhas}
  </table>
  <p class="ref" style="margin-top:8px"><b>Como ler:</b> "Agudo" é a nota escrita mais alta que o lote alcança;
  "Velocidade" e "Fôlego" indicam o quão rápidas e longas são as frases. "Andaime" é a ajuda impressa (contagem,
  instruções), que diminui de propósito ao longo do curso. O registro pesa mais na ordenação — por isso o agudo
  cresce devagar e só os lotes finais sobem de verdade.</p>
</section>
</body></html>"""
    return render(doc,f"{WORK}/b3/00_recap.pdf")

# ============================================================================
# GUIA DE DIVISÃO DO SAMBA (1 página)
# ============================================================================
def samba_guide_pdf():
    cards="".join([
      card(1,"Sinta o motor — moto perpetuo","Antes da melodia, toque a peça em colcheias contínuas e iguais: o samba tem um motor que nunca para. Depois devolva os silêncios.","K:F M:2/4 L:1/8 F F A A | c c A A | G G B B | A A F F |]","#7a1f1f"),
      card(2,"Acente o contratempo, solte o forte","O acento (>) cai FORA do tempo. Ataque a nota do contratempo e 'fantasme' (solte) a do tempo forte — não cave todas igualmente.","K:F M:2/4 L:1/8 z !>!F z !>!A | z !>!c z !>!A | z !>!G z !>!B | A2 z2 |]","#7a1f1f"),
      card(3,"A célula-mãe: semi-colcheia-semi","A figura semicolcheia–colcheia–semicolcheia é o coração do choro e do samba. Escrita assim, mas tocada com balanço.","K:F M:2/4 L:1/16 F2 A4 F2 | c2 A4 F2 |]","#7a1f1f"),
      card(4,"A partitura é ponto de partida","O que se escreve nem sempre é o que se toca (Sève). O balanço da divisão se aprende ouvindo gravações — use a partitura como mapa, não como verdade rítmica.","K:F M:2/4 L:1/8 F/ A2 F/ | c/ A2 F/ |]","#7a1f1f"),
    ])
    return render(tecnica_page("Divisão","A divisão do samba — antes de tocar as notas",
      "Bater pé na semínima, palma no contratempo. Corpo primeiro, instrumento depois. (Sandroni · Sève)",
      cards,"#7a1f1f"), f"{WORK}/b3/00_samba.pdf")

# ============================================================================
# AQUECIMENTO CHICOWICZ (2 páginas)
# ============================================================================
def chico_pdfs():
    flows=[("Flow 1 — descida ligada","Inspire fundo. Tudo sob uma ligadura, sem língua entre as notas. Som contínuo como uma onda.","K:C M:4/4 L:1/4 (G F E D | C4) | (A G F E | D4) |]"),
     ("Flow 2 — onda em torno do Sol","Oscile em torno do Sol, ligado. Foque na constância do ar, não na força.","K:C M:4/4 L:1/4 (G A G F | E F G2) | (A G F E | D C D2) |]"),
     ("Flow 3 — expansão suave","Amplie o âmbito aos poucos, tudo ligado. A passagem entre registros deve ser invisível.","K:C M:4/4 L:1/8 (G A B c d c B A | G F E F G4) |]"),
     ("Flow 4 — descida longa","Uma só ligadura e uma só respiração para a frase. Termine a longa cheia.","K:C M:4/4 L:1/4 (c B A G | F E D2) | (E F G A | c4) |]")]
    c1="".join(card(i+1,n,ins,a,"#2e6b4f") for i,(n,ins,a) in enumerate(flows))
    p1=render(tecnica_page("Aquecimento","Aquecimento · Flow Studies (Cichowicz)",
        "Comece TODO dia por aqui: piano, ligado, som antes de técnica. (escola Vincent Cichowicz)",c1,"#2e6b4f"),
        f"{WORK}/b3/00_chico1.pdf")
    longs=[("Notas longas — sustentação","Cada nota 8 tempos a ~60 bpm. Ataque limpo, som imóvel, corte seco.","K:C M:4/4 L:1/1 G | A | F | c |]"),
     ("Notas longas descendentes","Descendo por graus. Ouça a afinação de cada nota contra a anterior.","K:C M:4/4 L:1/1 c | B | A | G |]"),
     ("Respiração medida (4-4-4)","Inspire 4, sustente 4, descanse 4. A pausa também é exercício.","K:C M:4/4 L:1/1 G | z | A | z |]"),
     ("Messa di voce — controle do ar","Comece pianíssimo, cresça ao centro, volte ao pianíssimo. Tudo no ar.","K:C M:4/4 L:1/1 \"<\"G | \">\"G |]")]
    c2="".join(card(i+1,n,ins,a,"#2e6b4f") for i,(n,ins,a) in enumerate(longs))
    p2=render(tecnica_page("Aquecimento","Aquecimento · Notas Longas e Respiração",
        "Depois dos flows, fixe som e ar (escola Stamp / Caruso). Nunca pule — é o alicerce do tom.",c2,"#2e6b4f"),
        f"{WORK}/b3/00_chico2.pdf")
    return [p1,p2]

print("super.py parte 2 carregada")

# ============================================================================
# ABERTURA DE LOTE — capa do lote + DIÁRIO CONSOLIDADO (lista músicas + 5 sessões)
# ============================================================================
def lote_abertura_pdf(i,nums,cor):
    k=kdom(nums); _,nome_tom,_=KEYS.get(k,(k,k,"")); ft=feat(nums)
    ds=[esc[n]['dificuldade_calc'] for n in nums]
    # --- texto de CRUX e aprendizados, por feature-foco do lote ---
    CRUX={
     "sincope":("A síncope do samba",
       f"O <b>crux</b> deste lote é a síncope (C2): a célula colcheia–semínima–colcheia, com o peso na nota do meio, fora do tempo forte. É o gesto que define o balanço do samba. Em {nome_tom}, com poucos acidentes, você pode concentrar a atenção no ritmo e não na leitura.",
       "Tocar a síncope sem perder a pulsação, ler casas de repetição com naturalidade, e sentir o acento no contratempo como algo natural, não forçado."),
     "contratempo":("O ataque no contratempo",
       f"O <b>crux</b> é o contratempo (C6): atacar a nota no \u2018e\u2019 do tempo, depois do silêncio. O corpo precisa sentir o tempo forte mesmo quando você não toca nele. Tom-foco {nome_tom}.",
       "Atacar com precisão fora do tempo, manter o pulso interno durante as pausas, e começar a soltar (fantasmar) as notas fracas para o suingue aparecer."),
     "cromatismo":("O cromatismo de passagem",
       f"O <b>crux</b> é o cromatismo: notas fora da armadura que ligam os graus da escala. Exigem afinação milimétrica e leitura atenta de acidentes. Tom-foco {nome_tom}, onde as alterações aparecem com frequência.",
       "Ler acidentes de passagem sem hesitar, afinar as notas cromáticas contra as vizinhas, e usar o cromatismo como tempero, não como obstáculo."),
     "tercina":("A tercina",
       f"O <b>crux</b> é a tercina (C5): dividir o tempo em três partes iguais, contra a divisão binária habitual do samba. O contraste entre dois e três é o desafio. Tom-foco {nome_tom}.",
       "Tocar tercinas perfeitamente iguais, alternar entre divisão binária e ternária sem tropeçar, e encaixar tercinas dentro do andamento da roda."),
     "semicolcheia":("A semicolcheia e o staccato duplo",
       f"O <b>crux</b> são as semicolcheias rápidas (C4) e a articulação de língua dupla (tu-ku) que elas exigem. A língua sozinha trava; o tu-ku resolve. Tom-foco {nome_tom}.",
       "Articular quatro semicolcheias por tempo com igualdade, dominar o tu-ku do lento ao rápido, e ler o galope (colcheia pontuada + semi) com firmeza."),
     "extensa":("A forma longa e o fôlego",
       f"O <b>crux</b> deixa de ser a nota e passa a ser a <b>resistência</b> e a <b>memória</b>: peças longas (A/B/C/D, às vezes 100+ compassos) que exigem planejar respiração e sustentar o som até o fim. Tom-foco {nome_tom}.",
       "Sustentar o som numa forma longa sem desinflar, planejar onde respirar antes de tocar, e memorizar estruturas extensas seção por seção."),
     "modulacao":("A modulação de armadura",
       f"O <b>crux</b> é a modulação: a peça troca de tom no meio, e você precisa reler a armadura mentalmente na barra dupla. Tom-foco {nome_tom}.",
       "Trocar de armadura dentro da peça sem hesitar, antecipar a nova tonalidade, e manter o fraseado através da mudança."),
    }
    crux_titulo, crux_texto, aprendizados = CRUX.get(ft, CRUX["sincope"])
    # lista de músicas com checkbox + comentário individualizado (derivado das features)
    mus_rows=[]
    for n in nums:
        r=rows[n]; d=esc[n]['dificuldade_calc']
        com=comentario_musica(n)
        mus_rows.append(f"<tr><td class='ck'>☐</td><td class='mn'>{n:03d}</td>"
                        f"<td class='mt'><b>{H(r['titulo'])}</b> <span class='cp'>{H(r['compositor'])}</span>"
                        f"<div class='com'>{H(com)}</div></td><td class='dd'>{d}</td></tr>")
    mus_html="".join(mus_rows)
    # 5 linhas de diário de sessão
    diary_rows="".join("<tr><td>&nbsp;</td><td class='sn'>☐ sim&nbsp;&nbsp;☐ não</td>"
                       "<td class='lv'>1&nbsp;&nbsp;2&nbsp;&nbsp;3&nbsp;&nbsp;4&nbsp;&nbsp;5</td><td>&nbsp;</td></tr>" for _ in range(5))
    escala_legenda="".join(f"<b>{n}</b> {H(d)}&nbsp;&nbsp; " for n,d in ESCALA)
    doc=f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>
@page{{size:A4 landscape;margin:12mm 15mm}} {BASE_CSS}
.head{{border-top:9mm solid {cor};margin:-12mm -15mm 7mm;padding:6mm 15mm 0}}
.lnum{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#fff;background:{cor};border-radius:5px;padding:4px 16px;font-size:15pt;display:inline-block;margin-bottom:6px}}
h1{{font-size:24pt;margin:4px 0 2px}} .sub{{font-family:Helvetica,Arial,sans-serif;font-size:11pt;color:{cor};font-weight:bold}}
.grid{{display:flex;gap:14mm;margin-top:4mm}} .grid>div{{flex:1}}
.meta{{display:flex;gap:8px;margin:6px 0 10px}}
.chip{{background:#f2efe6;border:1px solid #d8d2c4;border-radius:4px;padding:5px 10px;font-size:9pt}}
.chip b{{display:block;font-family:Helvetica,Arial,sans-serif;font-size:7.5pt;text-transform:uppercase;letter-spacing:.5px;color:#6b6456;margin-bottom:1px}}
h3{{font-family:Helvetica,Arial,sans-serif;font-size:10pt;text-transform:uppercase;letter-spacing:1px;color:{cor};margin:6px 0 5px;border-bottom:1px solid #d8d2c4;padding-bottom:3px}}
table.mus{{width:100%;border-collapse:collapse;font-size:8.4pt}}
table.mus td{{border-bottom:1px solid #ececec;padding:2.4px 5px}}
.ck{{width:14px;color:{cor}}} .mn{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:{cor};width:30px}}
.cp{{color:#6b6456;font-size:7.7pt}} .dd{{text-align:center;width:20px;font-weight:bold}} .nv{{font-size:7pt;color:#999;width:34px}}
table.diary{{width:100%;border-collapse:collapse;font-size:9pt;margin-top:3px}}
table.diary th,table.diary td{{border:1px solid #c8c2b4;padding:6px 8px;text-align:left}}
table.diary th{{background:{cor};color:#fff;font-family:Helvetica,Arial,sans-serif;font-size:8pt;text-transform:uppercase;letter-spacing:.5px}}
.lv{{letter-spacing:3px;font-size:12pt;color:#888}} .sn{{font-size:8.5pt;color:#666}}
.note{{font-size:8.6pt;color:#5a5346;margin-top:6px}}
.crux{{font-size:10pt;line-height:1.5;color:#2a2a2a;margin:2px 0 4px}}
.crux b{{color:{cor}}}
.cruxbox{{border:1px solid #d8d2c4;border-left:5px solid {cor};border-radius:5px;padding:9px 12px;background:#faf9f6;margin-bottom:8px}}
table.mus td.mt{{padding:4px 5px}} .com{{font-size:7.8pt;color:#5a5346;margin-top:1px;line-height:1.3}}
.mt b{{font-size:9pt}}
.contpg{{page-break-before:always}}
</style></head><body>
<div class="head"><span class="lnum">Lote {i}</span>
<h1>Lote {i} — {H(crux_titulo)}</h1>
<div class="sub">Tom-foco {nome_tom} · técnica do lote: {FEAT_PT.get(ft,ft)} · dificuldade {min(ds)}–{max(ds)} · navegação: hachura {HATCH_NOME[i]}</div></div>
<div class="meta">
  <div class="chip"><b>Músicas</b>{len(nums)} sambas</div>
  <div class="chip"><b>Tom-foco</b>{nome_tom}</div>
  <div class="chip"><b>Técnica-foco</b>{FEAT_PT.get(ft,ft)}</div>
  <div class="chip"><b>Dificuldade</b>{min(ds)}–{max(ds)} / 10</div>
</div>
<div class="grid">
  <div style="flex:1.15">
    <h3>O que este lote trabalha</h3>
    <div class="cruxbox"><p class="crux">{crux_texto}</p></div>
    <h3>O que se espera ao fim do lote</h3>
    <p class="note" style="font-size:9.2pt;color:#2a2a2a">{aprendizados}</p>
  </div>
  <div>
    <h3>Diário do lote — registre suas sessões</h3>
    <table class="diary">
      <tr><th style="width:22%">Data</th><th style="width:30%">Fez completo?</th><th style="width:30%">Nível (1–5)</th><th>Nota</th></tr>
      {diary_rows}
    </table>
    <p class="note" style="font-size:8.2pt"><b>Nível:</b> {escala_legenda}</p>
    <p class="note" style="font-size:8.2pt">Avance quando marcar "completo" e nível ≥4 por duas sessões. Se uma música travar (nível ≤2 por três sessões), volte ao bloco técnico e isole o trecho.</p>
  </div>
</div>
<div class="contpg">
  <h3>As {len(nums)} músicas do lote — em ordem de dificuldade · marque ao dominar</h3>
  <table class="mus">{mus_html}</table>
</div>
</body></html>"""
    return render(doc,f"{WORK}/b3/lote{i}_abre.pdf")

# ============================================================================
# OVERLAY de mini-diário no rodapé de uma página do Sambrass
# ============================================================================
def overlay_diary(page, cor_rgb):
    W,Hh=page.rect.width,page.rect.height
    x0,y0,x1,y1 = W-372, Hh-30, W-14, Hh-9
    page.draw_rect(fitz.Rect(x0,y0,x1,y1), color=cor_rgb, width=0.8, fill=(1,1,1), fill_opacity=0.92)
    page.insert_text((x0+8, y0+14), "Diário", fontsize=8, color=cor_rgb, fontname="hebo")
    page.insert_text((x0+50, y0+14), "Data ___/___   Nível (1 leitura → 5 de cor):  1  2  3  4  5",
                     fontsize=8.5, color=(0.18,0.18,0.18))

HEXRGB=lambda h:(int(h[1:3],16)/255,int(h[3:5],16)/255,int(h[5:7],16)/255)

# ============================================================================
# COMENTÁRIO por música (derivado das features da curadoria)
# ============================================================================
TOM_PT={"C":"Dó","F":"Fá","G":"Sol","Bb":"Sib","D":"Ré","A":"Lá","Eb":"Mib","Ab":"Láb",
        "Db":"Réb","Gb":"Solb","B":"Si","E":"Mi"}
def comentario_musica(n):
    f=difj[n]['features']; r=rows[n]; e=esc[n]
    tom=e['tom_escrito']; tom_pt=TOM_PT.get(tom,tom); ac=f.get('acidentes',0)
    P=[]
    if ac>=3: P.append(f"armadura exigente ({tom_pt}, {ac} acidentes) — fixe a leitura primeiro")
    elif ac==0: P.append(f"sem acidentes ({tom_pt}), leitura limpa")
    else: P.append(f"em {tom_pt}")
    ns=f.get('n_secoes',0)
    if f.get('extensa') or ns>=4: P.append(f"forma longa ({r['forma']}) — planeje respiração e memória")
    elif r['forma']: P.append(f"forma {r['forma']}")
    rit=[]
    if f.get('tercina'): rit.append("tercinas")
    if f.get('semicolcheia'): rit.append("semicolcheias rápidas")
    if f.get('contratempo'): rit.append("contratempo marcado")
    if rit: P.append("; ".join(rit))
    if f.get('cromatismo'): P.append("cromatismo de passagem (atenção à afinação)")
    if f.get('modulacao') or r.get('modula'): P.append("muda de tom no meio — releia a armadura")
    if f.get('quatro_quartos'): P.append("em 4/4")
    if r.get('densidade')=='alta': P.append("densa")
    return "; ".join(P)

# ============================================================================
# HACHURAS de navegação (preto-e-branco) — 1 padrão por lote
# ============================================================================
HATCH={
 1:'<pattern id="P" width="6" height="6" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="0" y2="6" stroke="#1a1a1a" stroke-width="2"/></pattern>',
 2:'<pattern id="P" width="7" height="7" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="7" y2="7" stroke="#1a1a1a" stroke-width="1.6"/></pattern>',
 3:'<pattern id="P" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.5" fill="#1a1a1a"/></pattern>',
 4:'<pattern id="P" width="8" height="8" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="8" y2="8" stroke="#1a1a1a" stroke-width="1.4"/><line x1="8" y1="0" x2="0" y2="8" stroke="#1a1a1a" stroke-width="1.4"/></pattern>',
 5:'<pattern id="P" width="10" height="6" patternUnits="userSpaceOnUse"><path d="M0 3 Q 2.5 0 5 3 T 10 3" stroke="#1a1a1a" stroke-width="1.4" fill="none"/></pattern>',
 6:'<pattern id="P" width="6" height="6" patternUnits="userSpaceOnUse"><line x1="0" y1="3" x2="6" y2="3" stroke="#1a1a1a" stroke-width="2"/></pattern>',
}
HATCH_NOME={1:"vertical",2:"diagonal",3:"pontos",4:"grade",5:"ondas",6:"horizontal"}

def overlay_hatch_tab(page, lote):
    """Aba de hachura na borda externa direita + número do lote, formando índice no corte."""
    import cairosvg, tempfile
    W,Hh=page.rect.width,page.rect.height
    # posição vertical da aba = escalonada por lote (cria 'degraus' no corte)
    band_h=Hh/6.0
    y0=(lote-1)*band_h; y1=y0+band_h
    tab_w=22
    # gerar PNG da hachura
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(tab_w)}" height="{int(band_h)}"><defs>{HATCH[lote]}</defs><rect width="100%" height="100%" fill="url(#P)"/><rect width="100%" height="100%" fill="none" stroke="#1a1a1a" stroke-width="1.2"/></svg>'
    pth=f"{WORK}/b3/hatch_{lote}.png"
    cairosvg.svg2png(bytestring=svg.encode(),write_to=pth,output_width=int(tab_w*3))
    rect=fitz.Rect(W-tab_w, y0, W, y1)
    page.insert_image(rect, filename=pth, overlay=True)
    # número do lote em branco sobre a aba
    page.insert_text((W-tab_w+5, (y0+y1)/2+4), str(lote), fontsize=12, color=(1,1,1), fontname="hebo")
    page.draw_rect(fitz.Rect(W-tab_w+3,(y0+y1)/2-9,W-tab_w+17,(y0+y1)/2+5), color=None, fill=(0.1,0.1,0.1), fill_opacity=0.55, overlay=True)
    page.insert_text((W-tab_w+5, (y0+y1)/2+4), str(lote), fontsize=12, color=(1,1,1), fontname="hebo")


# ============================================================================
# PÁGINA "COMECE AQUI EM 5 MINUTOS" (baixo atrito, logo após a capa)
# ============================================================================
def comece_aqui_pdf():
    cor="#7a1f1f"
    # 3 frases mais fáceis para tocar já
    faceis=sorted(range(1,111), key=lambda n:SCORE[n])[:3]
    flist="".join(f"<li><b>{rows[n]['titulo']}</b> <span style='color:#6b6456'>({rows[n]['compositor']})</span></li>" for n in faceis)
    doc=f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>
@page{{size:A4 landscape;margin:14mm 18mm}} {BASE_CSS}
h1{{font-size:30pt;margin:0 0 4px;color:{cor}}}
.lead{{font-size:12pt;color:#3a3a3a;margin-bottom:10mm}}
.steps{{display:flex;gap:8mm}}
.step{{flex:1;border:1px solid #d8d2c4;border-top:5px solid {cor};border-radius:6px;padding:12px 14px;background:#fff}}
.step .n{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#fff;background:{cor};width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13pt;margin-bottom:6px}}
.step h3{{font-family:Helvetica,Arial,sans-serif;font-size:12pt;margin:0 0 5px}}
.step p{{font-size:9.5pt;line-height:1.45;margin:0}}
.step ul{{margin:4px 0 0;padding-left:16px;font-size:9.5pt}} .step li{{margin-bottom:2px}}
.foot{{margin-top:10mm;font-size:9.5pt;color:#6b6456;border-top:1px solid #d8d2c4;padding-top:7px}}
</style></head><body>
<h1>Comece aqui — em 5 minutos</h1>
<p class="lead">Sem ler nada antes. Pegue o trompete e siga os três passos. O resto do caderno explica os detalhes depois.</p>
<div class="steps">
  <div class="step"><div class="n">1</div><h3>Aqueça (2 min)</h3>
    <p>Vá ao <b>Capítulo Preparatório</b> e toque os exercícios 1 a 4: respire, faça o bocal, toque notas longas e cinco notas ligadas. Devagar, som calmo.</p></div>
  <div class="step"><div class="n">2</div><h3>Toque uma música (2 min)</h3>
    <p>Abra o <b>Lote 1</b> e escolha uma destas três — as mais fáceis do caderno:</p>
    <ul>{flist}</ul>
    <p style="margin-top:4px">Toque lento, sem parar nos erros.</p></div>
  <div class="step"><div class="n">3</div><h3>Anote (1 min)</h3>
    <p>No rodapé da partitura que tocou, marque a <b>data</b> e seu <b>nível</b> (1 = ainda lendo → 5 = de cor). Só isso. Amanhã você volta e vê o progresso.</p></div>
</div>
<p class="foot"><b>É só isso para começar.</b> Quando quiser entender o método — os lotes, a técnica, o diário, a divisão do samba — leia a <i>Recapitulação pedagógica</i> nas próximas páginas. Mas não precisa: você já pode tocar hoje.</p>
</body></html>"""
    return render(doc,f"{WORK}/b3/00_comece.pdf")

# ============================================================================
# CAPÍTULO PREPARATÓRIO (antes do Lote 1)
# ============================================================================
def preparatorio_pdfs():
    cor="#555555"; pdfs=[]
    # Página 1 — apresentação + por que preparar
    intro=f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>
@page{{size:A4 landscape;margin:13mm 16mm}} {BASE_CSS}
.head{{border-top:9mm solid {cor};margin:-13mm -16mm 8mm;padding:6mm 16mm 0}}
.lnum{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#fff;background:{cor};border-radius:5px;padding:4px 16px;font-size:13pt;display:inline-block;margin-bottom:6px}}
h1{{font-size:26pt;margin:4px 0 2px}}
.cols2{{column-count:2;column-gap:14mm;margin-top:5mm}}
.box{{border:1px solid #d8d2c4;border-left:5px solid {cor};border-radius:5px;padding:9px 12px;background:#faf9f6;margin-bottom:8px;break-inside:avoid}}
.box b{{font-family:Helvetica,Arial,sans-serif}}
h3{{font-family:Helvetica,Arial,sans-serif;font-size:11pt;color:{cor};margin:8px 0 5px}}
</style></head><body>
<div class="head"><span class="lnum">Capítulo 0 · Preparatório</span>
<h1>Antes de começar — preparar o corpo</h1></div>
<div class="cols2">
<p>Este caderno está ordenado por <b>três marcadores de dificuldade física</b> do trompete: o quão
<b>agudo</b> você precisa subir, o quão <b>longas</b> são as frases (fôlego) e o quão <b>rápidas</b> são as
notas. Os lotes crescem nessas três frentes — e por isso, antes do Lote 1, vale preparar o corpo.</p>
<div class="box"><b>Registro confortável primeiro.</b> Todo o repertório inicial vive no registro médio,
onde o som sai sem esforço. Não force o agudo: ele vem com o tempo, depois que a embocadura e o ar
estiverem firmes. Se uma nota aguda "racha", você subiu cedo demais — volte ao médio.</p></div>
<div class="box"><b>O ar antes da nota.</b> Som bonito é ar constante, não força de lábio. Os exercícios
desta página trabalham respiração e sustentação — a base de tudo que vem depois.</p></div>
<div class="box"><b>Devagar é progresso.</b> Toque tudo lento primeiro. Velocidade é consequência da
precisão, não o contrário. Quando a frase sai limpa devagar, o rápido vem sozinho.</p></div>
<h3>Como usar este capítulo</h3>
<p>Faça os exercícios de preparação como aquecimento estendido nos primeiros dias. Depois toque as
<b>frases curtas</b> das músicas mais fáceis do caderno — elas vivem no registro médio, têm fôlego curto
e poucas notas rápidas. Quando essas frases saírem confortáveis, você está pronto para o Lote 1.</p>
<p style="font-size:8.6pt;color:#6b6456;margin-top:6px">As frases vêm das músicas de menor agudo/velocidade/fôlego
do caderno inteiro. São transcrições automáticas (OMR) — confira contra a partitura.</p>
</div></body></html>"""
    pdfs.append(render(intro,f"{WORK}/b3/00prep0.pdf"))

    # Página 2 — exercícios de preparação do CORPO (sequência de aquecimento completa)
    prep=[("1 · Respiração — só o ar","Sem instrumento: inspire 4 tempos, solte em 'sss' contínuo por 8. A base de tudo é o ar, não o lábio.","K:C M:4/4 L:1/1 z | z |]"),
     ("2 · Buzzing no bocal","Só o bocal (sem trompete): faça uma sirene grave→agudo→grave, ligada. Acorda os lábios sem pressão.","K:C M:4/4 L:1/2 (G c) | (c G) |]"),
     ("3 · Nota longa — som","Cada nota 4 tempos a ~60 bpm. Ataque limpo, som imóvel do início ao fim, corte seco.","K:C M:4/4 L:1/1 G | A | F |]"),
     ("4 · Cinco notas ligadas","Sobe e desce cinco notas, tudo ligado, num só ar. A base do registro médio.","K:C M:4/4 L:1/4 (G A B A | G2) z2 | (G F E F | G2) z2 |]"),
     ("5 · Flexibilidade — lip slur","Duas notas com o mesmo dedilhado, ligadas só pelo ar (sem trocar pistão). Devagar, sem forçar.","K:C M:4/4 L:1/2 (G c) | (c G) | (E G) | (G E) |]"),
     ("6 · Saltos pequenos — terças","Pula de terça em terça, ligado. Centre cada nota antes de pular.","K:C M:2/4 L:1/4 (C E) | (D F) | (E G) | (C2) |]"),
     ("7 · Subida gradual (sem forçar)","Suba um grau de cada vez, com longa no topo. Se 'rachar', pare e volte — o agudo vem com o tempo.","K:C M:4/4 L:1/4 (C D E F | G2) z2 | (D E F G | A2) z2 |]"),
     ("8 · Descida tranquila","Cinco notas descendo, ligadas, terminando numa longa. Sem pressa.","K:C M:4/4 L:1/4 (G F E D | C2) z2 |]"),
     ("9 · Notas repetidas — articulação","Mesma nota, língua leve (di-di-di). Som igual do começo ao fim.","K:C M:2/4 L:1/8 G G G G | G2 z2 | A A A A | A2 z2 |]"),
     ("10 · Ligado × destacado","A frase ligada, depois destacada. Sinta a diferença, sem mudar o ar.","K:C M:2/4 L:1/8 (G A B A) | .G .A .B .A |]"),
     ("11 · Dinâmica — crescendo","Cresça do piano ao forte na nota longa. Só o ar muda; o som não 'estoura'.","K:C M:4/4 L:1/1 \"<\"G | \"<\"A |]"),
     ("12 · Escala completa — devagar","A escala de Dó inteira, ligada, lenta. Junta tudo: ar, som, dedos, leitura.","K:C M:4/4 L:1/4 (C D E F | G A B c) | (c B A G | F E D C) |]")]
    cards="".join(card(j+1,nm,ins,abc,cor) for j,(nm,ins,abc) in enumerate(prep))
    pg2=tecnica_page("Capítulo 0","Preparatório · Aquecimento do corpo (sequência completa)",
       "Faça na ordem: ar → bocal → som → flexibilidade → registro → articulação → dinâmica. Esta é a rotina de aquecimento de todos os dias.",
       cards,cor)
    pdfs.append(render(pg2,f"{WORK}/b3/00prep1.pdf"))

    # Página 3 — frases curtas das músicas mais fáceis do caderno inteiro
    faceis=sorted(range(1,111), key=lambda n:SCORE[n])[:6]
    fcards=[]; j=1
    for n in faceis:
        fr=frase_real(n,3)
        if not fr: continue
        try: p=png(fr,scale=30)
        except Exception: continue
        a=pico_label(n)
        fcards.append(f'<div class="ex"><div class="exhd"><span class="exn" style="background:{cor}">{j}</span>'
                      f'<b>{H(rows[n]["titulo"])}</b> <span class="src">{H(rows[n]["compositor"])} · pico {a}</span></div>'
                      f'<p class="instr">Frase do registro médio, fôlego curto. Toque lento e ligado; é uma boa porta de entrada.</p>'
                      f'<img class="score" src="file://{p}"></div>'); j+=1
    extra=".src{font-family:Helvetica,Arial,sans-serif;font-size:7.5pt;color:#6b6456;font-weight:normal;margin-left:4px}"
    pg3=tecnica_page("Capítulo 0","Preparatório · Primeiras frases reais",
       "As músicas mais confortáveis do caderno inteiro (menor agudo, fôlego e velocidade). Quando saírem fáceis, vá ao Lote 1.",
       "".join(fcards),cor).replace("</style>",extra+"\n</style>")
    pg3=pg3.replace("</body>",'<p style="font-size:8pt;color:#9a9384;font-style:italic;margin-top:4mm;font-family:Helvetica">Transcrições automáticas (OMR) — a partitura original é a fonte definitiva.</p></body>')
    pdfs.append(render(pg3,f"{WORK}/b3/00prep2.pdf"))
    return pdfs

# ============================================================================
# MONTAGEM FINAL
# ============================================================================
def build():
    print("Recap..."); recap=recap_pdf()
    print("Comece aqui..."); comeca=comece_aqui_pdf()
    print("Guia samba..."); samba=samba_guide_pdf()
    print("Chicowicz..."); chicos=chico_pdfs()
    print("Preparatório..."); preps=preparatorio_pdfs()

    final=fitz.open(); src=fitz.open(SRC); ee=fitz.open(EE)
    # capa é a 1ª página do recap; inserir recap, depois comece-aqui logo após a capa seria ideal,
    # mas para simplicidade: capa+recap, depois comece-aqui, depois o resto.
    final.insert_pdf(fitz.open(recap))
    n_capa_recap=final.page_count
    final.insert_pdf(fitz.open(comeca))    # comece aqui
    final.insert_pdf(fitz.open(samba))     # guia divisão
    for c in chicos: final.insert_pdf(fitz.open(c))
    prep_start=final.page_count
    for p in preps: final.insert_pdf(fitz.open(p))   # capítulo preparatório

    indice=[]  # (rótulo, nível, página_0idx) para o sumário
    indice.append(("Capítulo Preparatório", 0, prep_start))

    for i,nums in enumerate(CHUNKS,1):
        cor=CORES[i-1]; cor_rgb=HEXRGB(cor)
        k=kdom(nums); abck,nome_tom,sc=KEYS.get(k,("C","Dó","C D E F G A B c")); ft=feat(nums)
        lote_start=final.page_count
        indice.append((f"Lote {i} — {nome_tom} · {FEAT_PT.get(ft,ft)}", 0, lote_start))

        final.insert_pdf(fitz.open(lote_abertura_pdf(i,nums,cor)))
        blocoI = b_dinamica(abck,sc,i)+b_escala(abck,sc,i)+b_arpejo(abck,sc,i)
        cI="".join(card(j+1,nm,ins,abc,cor) for j,(nm,ins,abc) in enumerate(blocoI))
        final.insert_pdf(fitz.open(render(tecnica_page(f"Lote {i}",
            f"Lote {i} · Técnica I — Som, Escala e Arpejo de {nome_tom}",
            f"Tom-foco {nome_tom} · a complexidade cresce a cada lote",
            cI,cor), f"{WORK}/b3/l{i}_TI.pdf")))
        blocoII = b_articulacao(abck,sc,i)+b_salto(abck,sc,i)+b_ritmo(abck,sc,ft)
        cII="".join(card(j+1,nm,ins,abc,cor) for j,(nm,ins,abc) in enumerate(blocoII))
        final.insert_pdf(fitz.open(render(tecnica_page(f"Lote {i}",
            f"Lote {i} · Técnica II — Articulação, Saltos e Ritmo",
            f"Técnica-foco do lote: {FEAT_PT.get(ft,ft)} · no tom de {nome_tom}",
            cII,cor), f"{WORK}/b3/l{i}_TII.pdf")))
        final.insert_pdf(fitz.open(frases_page(i, nums, cor, nome_tom)))
        ee_keys=EE_FOR_FEAT.get(ft,["sincope","escala"]); ee_idx=[]
        for key in ee_keys: ee_idx+=EE_PAGES.get(key,[])
        for idx in ee_idx:
            final.insert_pdf(ee, from_page=idx, to_page=idx)
        for n in nums:
            start=final.page_count
            final.insert_pdf(src, from_page=PG(n)-1, to_page=PG(n)-1)
            overlay_diary(final[start], cor_rgb)
            indice.append((f"{n:03d} {rows[n]['titulo']}", 1, start))
        for pidx in range(lote_start, final.page_count):
            overlay_hatch_tab(final[pidx], i)
        print(f"  Lote {i}: {nome_tom} · {ft} · {len(nums)} músicas · hachura '{HATCH_NOME[i]}'")

    # ---- SEGUNDA PASSADA: gerar ÍNDICE e inseri-lo após o comece-aqui ----
    # O índice será inserido na posição n_capa_recap (após capa+recap), empurrando tudo.
    # Precisamos compensar os números somando n_idx_pages.
    # Estimar páginas do índice: ~ len(indice)/40 por página + 1
    n_entries=len(indice)
    idx_pages_est=max(1, (n_entries+44)//45)
    insert_at=n_capa_recap  # logo após a recap (antes do comece-aqui? não — após capa+recap)
    # gerar índice com páginas COMPENSADAS (cada destino desloca +idx_pages_est se vier depois de insert_at)
    def disp(pidx):  # número exibido (1-based) já compensado
        return pidx + idx_pages_est + 1
    idx_html=indice_html(indice, idx_pages_est, insert_at, disp)
    idx_pdf=fitz.open(render(idx_html, f"{WORK}/b3/00_indice.pdf"))
    # se o índice gerou nº diferente de páginas do estimado, reajustar uma vez
    if idx_pdf.page_count!=idx_pages_est:
        idx_pages_est=idx_pdf.page_count
        idx_html=indice_html(indice, idx_pages_est, insert_at, lambda pidx: pidx+idx_pages_est+1)
        idx_pdf=fitz.open(render(idx_html, f"{WORK}/b3/00_indice.pdf"))
    final.insert_pdf(idx_pdf, start_at=insert_at)

    # ---- numerar TODAS as páginas (rodapé direito), exceto a capa ----
    total=final.page_count
    for pidx in range(total):
        if pidx==0: continue  # capa
        pg=final[pidx]; W,Hh=pg.rect.width,pg.rect.height
        num=str(pidx+1)
        pg.draw_rect(fitz.Rect(W-46,Hh-20,W-22,Hh-6), color=None, fill=(1,1,1), fill_opacity=0.7, overlay=True)
        pg.insert_text((W-42,Hh-10), num, fontsize=8, color=(0.55,0.5,0.42), fontname="helv")

    final.save(OUT, deflate=True, garbage=4)
    print("SALVO:", OUT, "—", final.page_count, "páginas")

def indice_html(indice, idx_pages, insert_at, disp):
    linhas=[]
    for rotulo,nivel,pidx in indice:
        npag = disp(pidx)
        cls = "i0" if nivel==0 else "i1"
        linhas.append(f'<div class="row {cls}"><span class="lbl">{H(rotulo)}</span><span class="dots"></span><span class="pg">{npag}</span></div>')
    rows_html="".join(linhas)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>
@page{{size:A4 landscape;margin:14mm 18mm}} {BASE_CSS}
h2.sec{{font-family:Helvetica,Arial,sans-serif;font-size:13pt;letter-spacing:1px;text-transform:uppercase;color:#7a1f1f;border-bottom:2px solid #7a1f1f;padding-bottom:5px;margin:0 0 8px}}
.cols{{column-count:2;column-gap:14mm}}
.row{{display:flex;align-items:baseline;font-size:9pt;margin-bottom:2.5px;break-inside:avoid}}
.row.i0{{font-family:Helvetica,Arial,sans-serif;font-weight:bold;color:#7a1f1f;margin-top:7px;font-size:9.5pt}}
.row.i1{{padding-left:10px;color:#2a2a2a}}
.lbl{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:78%}}
.dots{{flex:1;border-bottom:1px dotted #c8c2b4;margin:0 5px;transform:translateY(-3px)}}
.pg{{font-variant-numeric:tabular-nums;color:#6b6456}}
</style></head><body>
<h2 class="sec">Índice — onde está cada coisa</h2>
<div class="cols">{rows_html}</div>
</body></html>"""

build()
