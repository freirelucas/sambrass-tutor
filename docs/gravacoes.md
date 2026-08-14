# As gravações reais — dossiê pedagógico

Oito gravações enviadas pela banda (2026-07), decompostas por
`tools/audio_segmenta.py` → `app/audio/segmentos.json` (frases, respirações,
legos, BPM). O app expõe tudo clicável na página de estudo (bloco 🎙): ouvir
frase por frase, o riff em cada volta, devagar (0.7×/0.85× sem mudar a altura)
e em loop. Este documento é a leitura HUMANA desses dados — o que cada
gravação ensina.

Princípio: **a gravação é o modelo; a partitura é o mapa.** O "ouvir o modelo"
sintetizado toca o que está transcrito — a gravação toca o que a banda quer.
Quando diferirem, a gravação manda (e `tools/audio_confere.py` denuncia).

## cu-011 Elsa — modelo 1 (1:18, ~89 BPM) ★ a mais didática

A forma inteira é audível e os números confirmam o desenho da partitura:

| trecho | frases | duração/frase | o que ensina |
|---|---|---|---|
| intro (tema d3-A) | 1 | 4,3 s | o gancho dó#–ré com o gesto pontuado |
| **riff A ×6** | 3–8 | **~2,1 s cada** | o giro "B B B d f2 d f-f f3": 6 voltas idênticas, respiração de ~0,6 s em CADA volta — o riff cabe num fôlego curto e relaxado |
| ponte (B2 B2…) | 10–12 | ~2,0 s | as colcheias repetidas em Lá/Si |
| **seção B** | 13–14 | **9,6–9,7 s!** | frases longas SEM respirar — é aqui que o fôlego do aluno quebra primeiro; treinar com o Cichowicz antes |
| coda | 15 | 2,2 s | fechamento = riff A |

Uso no app: os chips "frases" tocam cada volta; o 🧩 "trecho 1" percorre as
ocorrências do lego principal (12 detectadas). Exercício-modelo: loop na frase
3 a 0.7× → 0.85× → 1× → depois frase 13 medindo o fôlego.

## cu-010 Constelación — modelo 1 (1:01, ~94 BPM)

Duas tiradas longas de semicolcheia (frases 2 e 4: **15–17 s contínuos**, 56–64
notas, nota mediana de 0,16 s — a mais "corredora" das gravações) separadas por
uma seção intermediária calma (frase 3). Ensina: mão direita/dedilhado no
cromatismo ^c–^f e resistência. Os trechos de lego (12 ocorrências) permitem
estudar o giro isolado antes de encarar a tirada inteira.

## cu-010 modelo 2 (0:20, ~62 BPM) — registro grave, "a confirmar"

Duas frases de ~7 s no grave (Si3–Sol4 soando), contorno que NÃO casa com o
tema da 1ª voz (score 0). Hipótese: **2ª voz/tônicas** ou passagem do meio.
Pedagogicamente já serve como estudo de som no grave. Aguarda identificação
da banda.

## cu-001 Sonido Amazónico — modelo (1:09, ~94 BPM)

Uma frase-rio de **25 s** (74 notas, frase 3) — a peça praticamente inteira num
fôlego narrativo — seguida de blocos menores. Casamento melódico com o tema
DSL: 0.68 (o mais alto da dupla em sol menor). As respirações reais (33 s,
38 s, 53 s) mostram onde o modelo corta a frase — bom para marcar vírgulas na
partitura.

## cu-002 A Patrícia — modelo (1:14, ~94 BPM)

A decomposição mais "em frases de cumbia" do lote: **frases 2–9 de ~4 s** com
respirações regulares de ~1,2 s entre elas — a peça respira a cada 2 compassos.
Sobe a Sol5 soando (frases 3 e 5): é a gravação para treinar chegada ao agudo
em degraus curtos. Atribuição Sonido/Patrícia ainda "provável" (0.38).

## cu-011 modelo 2 (0:18, ~85 BPM) — registro grave, "a confirmar"

35 notas contínuas no grave (Lá3–Sol4), sem respiração audível — contorno
próximo do tema mas uma 8ª+ abaixo (2ª voz?). Útil como estudo de legato grave.

## Ensaios da banda completa (play-along)

- `ensaio-banda-1` (3:03, **~94 BPM**): groove estável quase sem seccionamento —
  play-along de resistência: entrar e ficar.
- `ensaio-banda-2` (3:48, **~94 BPM**): marcos de mudança em ~0:04, ~0:29 e
  ~1:46 (chips "seções" no app) — treinar ENTRADAS depois de deixa.
- Peças ainda não identificadas (croma A/D vs B/A#/E não bate limpo com nenhum
  tom do catálogo — pode ser peça nova, ex. El Bombón). Banda confirma → a
  gente ancora na peça e vira play-along oficial dela.

## O que os números dizem para o método

1. **Cumbia respira em ciclos de 2 compassos** (~2–4 s de frase, ~0,6–1,3 s de
   pausa) — exceto as seções "de prova" (Elsa B: 9,7 s; Constelación: 17 s;
   Sonido: 25 s). A escada de dificuldade do app (fôlego) bate com isso.
2. **O riff é a unidade de estudo certa**: nos modelos, o lego principal
   aparece 8–12× por gravação — o professor toca o giro N vezes seguidas, não a
   peça linear. O jogo "monte o riff" + o 🧩 na gravação fecham esse ciclo:
   ver, montar, ouvir de verdade, tocar junto.
3. **~94 BPM é o andamento-mãe do repertório** (4 das 6 gravações solo e os 2
   ensaios) — o Q:1/4=92 padrão dos ABCs está certo; a rampa do tutor deve
   mirar 94.
