# Superchops — a aba da conversão de embocadura

Aba **Chops** do app (`app/superchops.js` + `app/superchops.css`): um **plano diário
de no máximo 15 minutos** para treinar a conversão para a embocadura de **língua à
frente** — a TCE (*tongue-controlled embouchure*) do método **Super Chops**, de
Jerome Callet.

## O que este plano é — e o que não é

**É** uma rotina montada sobre os *princípios* do método, dosada em 15 min/dia e
organizada em 4 fases com sinais objetivos de passagem.

**Não é** o livro de Callet, nem uma transcrição dele: nenhum exercício foi copiado
de *Super Chops* (1987) nem de *Trumpet Secrets*. Quem quiser o método na íntegra
compra os livros — e, de preferência, procura um professor que trabalhe com TCE.

**Não é** consenso. A TCE é **controversa** entre professores de trompete: a maior
parte da pedagogia corrente (Farkas, Stamp, Caruso, Cichowicz — este último já no
app, na aba *Aquecer*) trabalha com a língua recuada e o queixo chato, ou seja, o
**oposto** de vários pontos abaixo. O app não escolhe por você; ele dá a rotina e
avisa do risco.

## Os princípios que a rotina treina

| Princípio | Como aparece nos exercícios |
|---|---|
| A ponta da **língua fica à frente**, tocando entre os lábios, em cada ataque | espelho, spit-buzz, todos os ataques |
| Ataque é **cuspido** ("tu", como quem cospe um grão de arroz) — não vem da garganta | spit-buzz, ataques repetidos, staccato |
| Quem **comprime o ar** é a língua, não o lábio apertado | notas longas, ligaduras de harmônico |
| Lábios **pra frente** (como quem diz "M"), cantos pra dentro — nunca o sorriso esticado | espelho, em toda fase |
| **Queixo empurrado pra cima** e maxilar à frente (o contrário do "queixo chato") | espelho |
| **Pressão mínima** do bocal — o trompete quase não encosta | notas longas, subida por semitons |

## As 4 fases

| Fase | Quando | Alvo | Sinal de que pode subir |
|---|---|---|---|
| **1 — A língua acha o lugar** | semanas 1–2 | montar o set-up e sentir a língua em cada ataque; som bonito *não* é a meta | monta a embocadura sem pensar e o "tu" sai sem abrir os cantos |
| **2 — O som fica** | semanas 3–4 | som limpo no registro médio, inclusive ligando notas | a escala de Dó sobe e desce ligada sem a língua recuar |
| **3 — Flexibilidade e agudo pela compressão** | semanas 5–8 | trocar de harmônico e subir sem apertar nem empurrar o bocal | Dó–Sol–Dó limpo; a nota do dia sai sem pressão |
| **4 — Levar pro repertório** | da semana 9 | tocar um riff da trilha com a embocadura nova, no andamento | o riff inteiro sai no andamento e você para de pensar na embocadura |

As semanas são **referência**, não regra: a fase que vale é a do *sinal*. A aba
sugere uma fase pelo número de dias praticados (0 / 7 / 21 / 42) e marca a sugerida
com "·", mas quem escolhe é você — repetir a fase 1 por um mês é normal.

Cada fase fecha em **exatamente 15:00** (há um teste que garante isso:
`superchops: a aba abre com o plano do dia fechando em 15:00`). Os **descansos são
exercícios** e entram na conta — numa conversão, é o descanso que evita inflamação.

## As três regras de segurança (ficam no topo da aba)

1. **15 minutos por dia, e só.** Mais tempo não acelera: inflama.
2. **Guarde a embocadura antiga para tocar.** Ensaio e roda continuam no jeito velho
   até o novo aguentar. Trocar no palco é o jeito mais rápido de desistir.
3. **Dor, dormência ou inchaço = parar no dia.** Cansaço é normal; dor não é.

## Como funciona por dentro

- **Sem build e sem dados novos**: o plano é constante no próprio JS (`SC_FASES`),
  porque é conteúdo autoral do app, não transcrição de partitura.
- **Estado em `localStorage`, fora das jornadas** (chaves `sc_*`) — embocadura não é
  repertório, então não muda quando você troca Cumbias ↔ Sambrass:
  `sc_fase` (fase escolhida, 0 = usar a sugerida) · `sc_days` (dias com sessão, para
  o streak) · `sc_logs` (diário 1–5 por dia) · `sc_feitos_AAAA-MM-DD` (passos do dia).
- **Sessão guiada**: cronômetro com anel, auto-avanço entre os passos, bipe curto na
  virada e `wakeLock` (quando o navegador tem) pra tela não apagar no meio.
- A sessão **morre ao trocar de aba** (`ir()` chama `scPararSessao()`): o relógio não
  fica correndo escondido.

## Fontes

- Jerome Callet, *Super Chops: Trumpet Technique for the 21st Century* (1987).
- Jerome Callet & Bahb Civiletti, *Trumpet Secrets* (2002).

Os princípios da tabela acima são a leitura desses métodos; **os exercícios e a
dosagem em 15 min são deste app**.
