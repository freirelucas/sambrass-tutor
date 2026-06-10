# Piloto gravar→transcrever — sb-011 "Preciso Me Encontrar"

**Pergunta**: dá pra resolver o som das 110 com o motor que já temos — Lucas grava cada peça
uma vez e o app transcreve — em vez de continuar corrigindo OMR?

**Resposta do piloto: sim.** Na única peça com gabarito conferido no ouvido (sb-011, Seção A,
26 notas, 8 compassos, com quiáltera e salto de oitava), a transcrição por áudio acerta
**26/26 notas com ritmo e duração** nos dois perfis; o OMR cru, na mesma régua, acerta 10/26.

| fonte | nota+ritmo | duração ok | melodia (edit dist.) |
|---|---|---|---|
| áudio (limpo) | **26/26** | 26/26 | **100%** |
| áudio (sujo: +18c desafinado, jitter ±25ms, SNR 22dB, dinâmica ±4dB) | **26/26** | 26/26 | **100%** |
| OMR cru (Audiveris, scan 200dpi) | 10/26 | 8/10 | 77% |

De quebra, a transcrição **mede** a performance: estimou a desafinação global injetada
(14c dos 18c reais) e a latência de ataque — sinais que o tutor já usa.

## Como o bench funciona (`node tools/transcricao/bench_sb011.mjs`)

1. **Gabarito**: `notes_manual/sb-011.abc` (ditadura do Lucas) parseado em eventos exatos
   (célula = 1/12 de tempo → semicolcheia=3, colcheia de quiáltera=4; validação de soma por compasso).
2. **"Performance" sintética**: samples **reais de trompete** (o soundfont do app) agendados
   em `OfflineAudioContext` com humanização: desafinação global+por nota, jitter de ataque,
   articulação de língua (~25ms), dinâmica variável e ruído de sala **relativo ao sinal** (SNR).
3. **Transcrição**: `pitch-detector.js` de produção (NSDF), quadro a quadro (janela 2048,
   hop 256; **RMS em sub-janela curta** de 12ms — é ela que enxerga o buraco de língua entre
   notas repetidas) → `note-segmenter.js` (novo, `app/vendor/`): agrupa, remove a afinação
   global (mediana), separa notas repetidas por re-ataque de RMS → quantiza no grid do
   metrônomo (andamento conhecido: o app dá o click).
4. **Métrica**: casamento (mesma nota MIDI, onset ±1 célula) + distância de edição da melodia.

Os WAVs do que foi transcrito ficam em `out/` (ouça: é o som do app "tocando" a página).

## Limites honestos

- **Sintético ≠ Lucas gravando**: sem respiração, glissandos de entrada, sala real, deriva de
  andamento. O perfil "sujo" aproxima (desafinação, jitter, ruído, dinâmica), mas a validação
  real é gravar a sb-011 de verdade e medir — o bench já aceita qualquer fonte de samples.
- **Andamento conhecido e estável** (gravação com click do app). Rubato real quebra a
  quantização — por desenho: a captura é "toque com o metrônomo", como no estudo.
- **Notas repetidas em legato puro** (sem língua) não separam — no samba a articulação é de
  língua, então o caso é raro; fica documentado no segmentador.
- **Uma peça, 8 compassos.** O piloto prova o motor, não as 110. Próximo passo é o modo
  "gravar" no app (mic → mesmas funções) e rodar nas peças que o Lucas gravar.

## Por que isso muda o produto

A cadeia OMR (scan 200dpi → Audiveris → fusão por dedos → revisão manual) produz melodia
**provisória** e cara de revisar. A cadeia áudio (Lucas toca 1×, com click → transcrição)
produz melodia **certa + uma gravação de referência de verdade** (play-along) por ~2min/peça.
O mesmo motor que escuta o aluno (Pilar 4) é o que transcreve — um investimento, dois usos.
