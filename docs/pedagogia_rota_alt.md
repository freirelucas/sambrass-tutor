# O Caminho do Sambrass — a camada pedagógica (fusão da rota alternativa)

Este documento registra a fusão da **rota alternativa** ("O Caminho do Sambrass", um app HTML
autocontido construído em paralelo) com a nossa PWA. O resultado é **uma versão só com o melhor
dos dois**: nossa base técnica (tutor de escuta, pipeline de notas real, escada Book1/2/Arban) +
a camada de UX/pedagogia da rota alternativa (trilha Duolingo, Stories por música, desafios de
prática deliberada).

## Reconciliação (o que tornou a fusão barata)

- **Dados idênticos.** A rota alternativa foi construída sobre o **mesmo** `notes_abc.json` que o
  nosso (110/110 ABCs batem; mesmos tiers `_quality`; `_verified: [sb-011]`). Não houve snapshot
  velho a migrar.
- **Notação pré-assada.** Os micro-exercícios em pauta são **SVG gerado no build** (Verovio em
  Python, `content/pedagogia/build/gerar_pedagogia2.py`), embutidos em `app_pedagogia.json`. No
  cliente são injetados como SVG puro — **sem Verovio/abcjs** para os desafios (a melodia da peça
  segue no abcjs, no tutor).
- **Dois eixos de ordenação, complementares.** A trilha ordena pela **heurística de complexidade**
  (abaixo); cada nó mostra **também** o **nível da escada** (Book1/2/Arban — pré-requisitos
  pedagógicos) e o **tier de qualidade** da melodia. "Quão difícil de tocar" × "que pré-requisitos".

## Dados publicados (de `content/pedagogia/` → `app/data/` via `build_site.py`)

| origem (`content/pedagogia/`) | publicado (`data/`) | carga | conteúdo |
|---|---|---|---|
| `app_musicas.json` | `percurso.json` | eager (58 KB) | nós da trilha: num/título/lote/agudo/vel/fôlego/pico |
| `app_pedagogia.json` | `pedagogia.json` | **lazy** (1,5 MB) | por peça: `perfil`, `plano`, `desafios[{t,d,w,svg}]` |
| `app_prep.json` | `aquecimento.json` | lazy | 12 aquecimentos `{nome,dica,svg}` |
| `app_tecnica.json` | `tecnica.json` | lazy | técnica por lote (eixos × exercícios) |
| (derivado) | `lotes.json` | eager | resumo dos 6 lotes (tom + foco) p/ os cabeçalhos |

`pedagogia.json` é grande → só carrega ao abrir a 1ª Story; o service worker (v6) a cacheia para
offline na 1ª visita (fora do SHELL).

## Heurística de complexidade (LIMPA E AUDITADA — não regredir)

Três marcadores, definidos pelo usuário: **agudo (peso 2×), velocidade, fôlego**. A auditoria
achou **erros de oitava** no OMR (`notes_abc.json`) — ex.: falso Fá6 em sb-093 — então:

- **Agudo** usa **teto Si4 (72)** (acima é erro comprovado) + régua de faixas; nunca percentil/máximo cru.
- **Velocidade**: semicolcheia/densidade/tercina → 1–6 (corr. 0,61 com a dificuldade curada).
- **Fôlego**: extensão + nº de seções → 1–6.
- `SCORE = 2·agudo + vel + fôlego` → ordenação → **6 lotes**. Em `content/pedagogia/heuristica_limpa.json`.

A heurística **age em silêncio** (a UI não comenta que "o agudo do caderno quase não varia").

## Pedagogia (Self-Determination Theory — não regredir)

Base: prática deliberada (Ericsson) + UX Duolingo (chunking, caminho, streak sem pressão) + SDT
(Deci & Ryan). Princípios materializados no app:

- **Sem bloqueio de conteúdo** (cadeado mina autonomia → menos prática). A trilha é "caminho
  SUGERIDO"; tudo clicável; bandeira **SUGERIDA** na próxima não-dominada.
- **Sem XP/moedas** (recompensa externa mina motivação intrínseca). HUD factual: 📅 dias · 🎺 X/110.
- **Racional em tudo** ("💡 Por quê") — SDT: rationales sustentam motivação em tarefa árida.
- **Desafios concretos** com dados reais da peça (salto nomeado, pico, corrida) + micro-exercício
  autoral em pauta (2–4 notas derivadas, nunca trecho da melodia do caderno).
- **Autoavaliação 1–5** descritiva (1=trava na leitura … 5=de cor) como metacognição, não placar.
  **Nível ≥4 ⇒ dominada** (✓ na trilha; `sb2_logs` no localStorage).

## A síntese (o que nenhuma das duas rotas tinha)

Cada desafio e o fim de cada Story trazem **"🎤 tocar no tutor (ele ouve você)"** → abre
`estudo.html?id=sb-NNN`, o **tutor de escuta real** (mic, agulha de cents, verde/vermelho, loop,
rampa). A rota alternativa estruturava a prática deliberada mas tocava só playback sintético; a
nossa ouvia o aluno mas não estruturava a sessão. Agora a estrutura **desemboca** no ouvido.

## Arquitetura no app (vanilla, como o resto da PWA)

- `app/trilha.js` — `telaTrilha()` (home): HUD + lotes + nós zigue-zague + bandeira SUGERIDA.
- `app/story.js` — engine de Stories (capa/perfil/plano/desafios/diário; aquecimento; técnica do
  lote). Faz merge do nó (`percurso`) com `pedagogia[num]` (lazy) ao abrir.
- `app/app.js` — progresso SDT (`store` sb2_*, `bestLevel`/`isDone`/`streakCount`) + migração única
  do `sambrass_prog` antigo ('dominada'→log nível 4); rota `trilha`; filtros de esforço no Banco.

## Regenerar a pedagogia (opcional — os dados já estão versionados)

```
pip install verovio numpy --break-system-packages
cd content/pedagogia/build
python3 gerar_pedagogia2.py   # lê o fonte (idêntico ao nosso) → app_pedagogia.json (SVGs assados)
```
Fora do `build_all` (deps pesadas), como a fusão de dedos. `super_v2.py` guarda os blocos de
exercício (b_escala/b_arpejo/…) e a heurística; não faz parte do app.

## Créditos

A rota alternativa ("O Caminho do Sambrass", `Sambrass_App.html` + handout) foi construída em
sessão paralela; este repo absorve sua camada de UX/pedagogia nativamente. Artefato educacional
pessoal — sem partituras do caderno nem material de terceiros (só dados derivados e exercícios
autorais).
