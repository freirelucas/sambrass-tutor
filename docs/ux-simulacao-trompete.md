# Simulação — 10 trompetistas (iniciante → mestre) + brainstorm de melhorias

Simulação do uso do app **no estado atual** (trilha de cumbias default, estudo
Coração/Frase/Praticar + tutor de mic, Lego, Respira/Cichowicz, blocos, metrônomo).
Aterrada nos números reais: **cumbias 12/15 conferidas** (faltam cu-001/002/003),
**sambas 1/110 conferida** (75 "dedos", 34 rascunho), e o detalhe que muda tudo:
**as cumbias "mais fáceis" (lote 1) já pedem agudo 6 (Dó6)** — `vel` separa o lote 1,
não o registro.

## Os 10 trompetistas

| # | Quem | Faz no app | ❤ Funciona | ⚠ Atrito | Pede |
|---|------|-----------|-----------|----------|------|
| 1 | **Duda, 11** · semana 1 | abre Sonido Amazónico | aperta o **Lego** (lúdico, soa) | melodia no agudo que não alcança; mic mudo; não lê. **Não toca nenhuma cumbia** | nota zero, som longo, alcance médio, afinar |
| 2 | **Raimundo, 58** · voltando após 30 anos | vai no **Respira** | Cichowicz é o que o lábio precisa; BPM/loop | agudo cansa o lábio em 30s; sem gestão de fôlego | rotina de chops, versão 8ª abaixo |
| 3 | **Bianca, 15** · 1 ano banda marcial | lote 1 lento | **válvulas acendendo digitação**, loop+rampa | toca **sozinha, sem groove**; clave seco; ritmo não avaliado | backing de cumbia + contagem |
| 4 | **Theo, 19** · Book1/Arban (alvo) | o loop principal | tudo feito pra ele: loop/rampa/mic/transpor | "minha síncope atrasa e o app não diz" | feedback de tempo + metrônomo estiloso |
| 5 | **Marina, 24** · choro/samba de ouvido | toca sambas | Stories/contexto, **Legos/geometrias** | **estranha os sambas** (tier dedos/rascunho); desconfia | melodias conferidas + "toque o que ouviu" |
| 6 | **Caio, 22** · graduando erudito | sight-reads cumbia | transpor concerto/Sib | toca **"quadrado"**; estilo latino não ensinado; melodia dry | guia de fraseado + áudio de referência |
| 7 | **Pedro, 28** · freela de baile, lead | toca a peça inteira | peça inteira, transpor | sem play-along com banda, sem **cifras**, sem export | changes + backing + export setlist |
| 8 | **Lucía, 34** · pro de cumbia (Lima) | explora | **honestidade dos tiers**, Telar/Puel Kona | mesmo conferida = notas certas, **fraseado/feel ausente** | camada de fraseado + validação nativa |
| 9 | **Jonas, 41** · estúdio MPB/latin | testa o mic | detector robusto à oitava, rampa | **latência Android** trava agudo/semicolcheia; sem grade de tempo | play-along sem avaliação + calibrar latência |
| 10 | **Aurélio, 60** · professor/pedagogo | avalia como ferramenta | **escada honesta**, tiers, sem gamificação tóxica | lote 1 começa com agudo 6 (contradiz "fácil"); grade só altura, não **tom/tempo** | dificuldade por registro+fôlego; rubrica de som |

## Brainstorm (agrupado, prioridade 🔴 alta · 🟡 média · 🟢 depois)

### A. A porta de entrada que hoje não existe (níveis 1–3) 🔴
- **Modo Zero / Fundamentos**: primeira nota, sons longos, embocadura, alcance médio. (Respira é intermediário **pra cima** — falta o degrau abaixo.)
- **Afinador/drone** isolado (reaproveita o pitch-detector + agulha de cents).
- **"Versão fácil" — 8ª abaixo / registro confortável** (estende o motor de transpor que já existe).

### B. O registro É a dificuldade real (insight dos dados) 🔴
- **Reordenar/ponderar dificuldade por agudo+fôlego**, não só `vel` (hoje Lobos/Sobre el Mar = agudo 6 no lote 1).
- **Perfil de alcance do aluno** → sugere só o que cabe no bico; mostra o **pico** de cada peça.

### C. Groove & acompanhamento — o maior pedido, todos os níveis 🔴
- **Backing de cumbia** (güira + baixo + stab off-beat) no tom/BPM da peça → "tocar com a banda". Cumbia é música de conjunto; tocar o riff sozinho é o maior buraco.
- **Metrônomo estiloso**: padrão de clave/güira, subdivisão, contagem de entrada.

### D. Avaliar o que importa no trompete: tempo e tom 🟡
- **Grade rítmica (pocket)**: o app já tem TimingCallbacks + mic — medir se o ataque caiu no tempo.
- **Rubrica de tom/long-tone**: estabilidade de afinação e som.
- **Calibrar latência** (Android) p/ grade rítmica e "esperar por mim".

### E. Fidelidade & confiança (níveis 5–10) 🟡
- **Subir sambas dedos/rascunho → conferida** (hoje 1/110).
- **Fechar cu-001/002/003** (precisa do áudio do dono).
- **Camada de fraseado/articulação** + áudio de referência real.

### F. Estilo, improviso & profissional (6–10) 🟢
- **"Como soar cumbia"** (articulação latina, adornos), validado por músico do estilo.
- **Cifras/changes** + escalas p/ solar; **play-along sem avaliação**; **export setlist/partes**.

### G. Ear training 🟢
- Reaproveitar o **query-by-humming** (achou a cu-008 cantando) como feature.

## Se priorizar (impacto × esforço)
1. **Backing de cumbia** (groove) — todos; médio.
2. **Dificuldade por registro + "8ª abaixo"** — níveis 1–3; baixo.
3. **Grade rítmica (pocket)** — 4–10; médio.
4. **Modo Zero + drone** — a porta que falta; baixo-médio.
5. **Fidelidade dos sambas + fraseado** — confiança dos 5–10; alto.

**O fio que conecta os 10 níveis:** o app ensina a *nota*, mas cumbia (e trompete)
é *groove + som + registro*. Iniciantes batem no agudo; avançados sentem falta de
banda, feel e fidelidade — e ninguém tem acompanhamento nem feedback de tempo.
