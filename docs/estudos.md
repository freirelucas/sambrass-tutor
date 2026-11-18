# Estudos — o painel multi-domínio

`app/estudos.html` é a casa nova: um plano diário que atravessa **cinco domínios** —
trompete, violão, piano, cibernética (*homo gubernator*) e línguas — com cronômetro,
revisão espaçada e histórico.

A estrutura veio de um protótipo de Claude Design (Hoje · Prática · Revisão · Histórico).
**A pele não veio**: o protótipo é escuro e roxo; o app já tem identidade (papel quente e
vinho) e ela ganhou. O que se importou foi o esqueleto, não o visual.

## O que mexeu e o que não

**Não mexeu:** o app de trompete. `index.html` segue sendo o app inteiro — trilha, banco,
aquecer, Chops, metrônomo, progresso — com os mesmos dados e os mesmos testes. Ele ganhou
só duas coisas: um link `◴ Estudos` no cabeçalho e a capacidade de abrir numa aba
específica pela URL (`index.html#chops`), que é como o painel entra nele.

**Domínio ≠ jornada.** Cumbias e Sambrass continuam sendo repertório *dentro* do trompete
(`JORNADAS`, chaves `cu2_`/`sb2_`). `DOMINIOS` é a camada acima, e vive noutro lugar do
localStorage (`est_`), sem colidir.

**Violão e piano começam sem partitura** — plano, cronômetro e cards. Montar pipeline de
repertório para eles é projeto à parte, não foi pedido, e seria enorme.

## Os arquivos são seus

Nada em `app/estudos/` é gerado por script. Edite à mão:

| arquivo | o que é |
|---|---|
| `estudos/dominios.json` | os 5 domínios, suas tarefas, minutos, blocos, cores e a meta diária |
| `estudos/baralhos/*.json` | as cartas, no formato `f` (frente), `l` (leitura/fonte), `t` (trás), `ex` (exemplo) |
| `estudos/baralhos/index.json` | a lista dos baralhos que o app carrega |

Um baralho novo precisa de três coisas: o arquivo, uma linha no `index.json`, e um
`dominio` que exista. Se faltar qualquer uma, **`tools/check_contrato.py` falha no CI** —
inclusive se o arquivo existir e não estar no índice, caso em que o app nunca o carregaria.

### Os baralhos que já vêm

- **`cibernetica-vsm`** — 15 cartas escritas à mão: os sistemas 1 a 5, canal algedônico,
  variedade requisita, atenuar/amplificar, recursão, homeostato, POSIWID, intenção estável
  (Bratman) e o próprio *homo gubernator*. São semente: corte e acrescente à vontade.
- **`linguas-exemplo`** — 4 cartas que só mostram o formato. **Troque.** Diga qual idioma
  e eu monto o baralho de verdade. O método que o baralho vai seguir está levantado em
  [`linguas-ciencia.md`](linguas-ciencia.md) — revisão da literatura sobre o que funciona
  para um adulto aprendendo vários idiomas.

## A revisão espaçada

Leitner simples, cinco caixas, intervalos de **1 · 2 · 4 · 8 · 16 dias**. Três respostas:

| botão | o que faz |
|---|---|
| **de novo** | caixa volta a zero, a carta reaparece ainda hoje |
| **quase** | mantém a caixa, volta amanhã |
| **fácil** | sobe uma caixa, volta mais longe |

Estado em `est_cards`, por carta (`baralho#índice`). Vale notar: o app de trompete **já
tinha** lógica de revisão espaçada (`reviewDue`, a regra dos 7 treinos) e nenhuma tela
para ela. Esta é a tela — e é a única das quatro do protótipo que preencheu um buraco real
em vez de duplicar algo que já existia.

## Estado

Tudo em `localStorage`, prefixo `est_`:
`est_min_<data>` · `est_feitas_<data>` · `est_dias` · `est_logs` · `est_cards`.
Nenhum servidor, nenhuma conta — igual ao resto do app.

## O que foi conferido

Quatro telas dirigidas em Chromium a 390px: abrir tarefa com blocos, trocar Foco/Blocos,
avançar bloco, cronômetro andando, encerrar somando minutos e marcando feito, carta virada
e agendada nas três respostas, calendário com 31 dias em outubro e o dia de hoje marcado.
Zero erro de console, zero overflow horizontal.

Quatro specs novas, conferidas por teste negativo (tirar um domínio derruba a contagem).
E dois guards pegaram bug real de primeira: o `#chops` não funcionava porque o app de
trompete não lia `location.hash`, e a classe `.q1` existia sem estilo.

## Em aberto

- ~~Qual idioma~~ — chinês e japonês. O plano da rotina 5 × 15 e o que falta construir
  estão em [`proximos-passos.md`](proximos-passos.md).
- **`start_url` do manifesto** ainda aponta para o app de trompete. Trocar para
  `estudos.html` muda o que abre no celular de quem já instalou — decisão sua.
- **O nome do repositório** (`sambrass-tutor`) ficou estreito para o que isto virou.
