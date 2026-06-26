# Simulação de 15 usuários intermediários + plano de melhoria

> **Método (honesto):** avaliação heurística com **15 personas** de trompetistas
> intermediários percorrendo os fluxos reais no celular (Samsung/Android), **ancorada no
> estado atual do app** (pós-redesign: trilha vertical, estudo em 3 passos, voltar, Respira).
> É *simulação* — não teste com gente real. Serve para priorizar, não para concluir.

## As 15 personas e a dor #1 de cada uma

| # | Persona | Atrito principal | Encantou |
|---|---|---|---|
| 1 | **Rafa**, 28, autodidata, só celular | tocou o nó e caiu numa **Story de 4 telas** antes de tocar — "cadê o play?" | o riff/play-along |
| 2 | **Cleus**, 54, banda da igreja | navegação; texto pequeno em alguns pontos | voltar + escada clara |
| 3 | **Téo**, 19, estudante, técnico/cético | desconfia das **3 rascunho** ("essa nota tá certa?") | aquecimento Cichowicz (legítimo) |
| 4 | **Bia**, 35, mãe, 15 min/dia | caminho longo até a música (Story) | o **anel** do Respira |
| 5 | **Marcão**, 41, toca à noite sem fone | demorou a achar o **modo praticar** (clave-só) entre muitos botões | tocar sem fone |
| 6 | **Seu Antônio**, 60, voltando | se perdeu na Story — "só quero a música" | voltar resolveu |
| 7 | **Lara**, 31, semi-pro, gig de chicha | faltou **transpor afinação** fácil | peça inteira + BPM |
| 8 | **Gabriel**, 24, trava no agudo | — | a **ponte Cichowicz→lote** ("aqueça Bloco X") |
| 9 | **Cris**, 38, toca de ouvido | Story é "blá blá" pra quem não lê | riff + coração |
| 10 | **Prof. Sérgio**, 45, avalia p/ alunos | quer escada **unificada** sambas↔cumbias | tiers honestos + escada |
| 11 | **Duda**, 22, desconfiada de dados | quer as 15 **todas conferidas**; dificuldade estranha | transparência do tier |
| 12 | **Igor**, 33, celular mediano + 4G | sentiu o **18 MB do Respira** baixando | — |
| 13 | **Nina**, 27, perfeccionista do mic | grader é só verde/vermelho — quer **qual nota errou** | o cursor + dedos |
| 14 | **Léo**, 30, só quer zoar junto | pedagogia/Story demais — "abrir e tocar" | play-along |
| 15 | **Sam**, 26, quer ler mais | **só 15 cumbias** é pouco | a curadoria |

## Temas (frequência entre as 15)

1. 🔴 **A Story está no caminho da prática** (≈6: Rafa, Bia, Antônio, Cris, Léo, +) — o atrito nº1. Pra tocar, atravessa capa→perfil→plano→desafios. "Quero tocar, não ler."
2. 🟡 **Repertório raso / confiança** (≈4: Téo, Sérgio, Duda, Sam) — só 15, **3 rascunho**, dificuldade não comparável.
3. 🟡 **Descoberta de funções** (≈3: Marcão, Antônio, Nina) — modo praticar e controles escondidos; Selos/Blocos/Revisão sem porta de entrada.
4. 🟡 **Peso do 1º load** (Igor) — 18 MB de áudio do Respira pesam no 4G.
5. 🟢 **Encantamentos consistentes** — riff/play-along, o **coração**, o **anel** do Respira + a **ponte** Cichowicz, os **tiers honestos**, e (pós-fix) a **trilha vertical** + **voltar**.

## Plano de melhoria (priorizado)

### P0 — alta fricção, alcance amplo
1. **Atalho "▶ tocar agora"** no nó da trilha (e na capa da Story) que vai **direto** ao `estudo.html`, pulando capa/perfil/plano. A Story vira opcional ("ver o plano"). *Resolve o tema #1 e a tua própria objeção aos Stories.* — `trilha.js`/`story.js`, pequeno.
2. **Garantir 1º load leve:** o áudio do Respira já é `preload=none`; revisar para que **nenhuma tela inicial** puxe os 18 MB, e avisar no card "áudio carrega ao tocar". — verificação + 1 linha.

### P1 — pedagogia e confiança
3. **Stories → dicas no fluxo:** colapsar capa/perfil/plano num cartão enxuto e mover os desafios para **prompts curtos dentro dos 3 passos** do estudo. Mantém a pedagogia, tira o "blá blá".
4. **Fechar as 3 rascunho** (cu-001/002/003) → **15/15 conferidas** = a confiança que Téo/Duda pedem. *(precisa do teu ouvido: cantarola, eu transcrevo.)*
5. **Porta de entrada das ferramentas:** um menu discreto ligando **Selos/Blocos/Revisão**, e um **onboarding de 1 linha** do modo 🎤 praticar (clave-só, sem fone).

### P2 — refinos
6. **Transpor afinação** em 1 toque (Bb/concert já existe parcial — expor melhor) — Lara.
7. **Grader mais rico:** dizer **qual** nota saiu da clave + um mini-histórico — Nina.
8. **Mais repertório + escada unificada** (dificuldade comparável sambas↔cumbias — o 🟡 da auditoria) — Sérgio/Sam.

## Veredito

O redesign recente **já matou as duas piores dores** (não-cabe-na-tela e sem-voltar). A
fricção que sobra e mais aparece é **a Story barrando a prática** — o **P0 #1** é o maior
ganho por esforço. Depois, **fechar as 3 rascunho** e **dissolver a Story em dicas** alinham
a confiança e o "quero tocar" que aparecem em mais da metade das personas.
