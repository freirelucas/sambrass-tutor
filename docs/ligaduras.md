# Ligaduras, ties e ritmo — revisão do corpus (2026-06-16)

Análise criteriosa do acompanhamento (player abcjs, timbre de trompete) e correção
das **ligações entre notas** que faltavam em todo o corpus.

## Diagnóstico (o que estava certo × o que faltava)

| Item | Estado antes | Evidência |
|---|---|---|
| **Ties** (mesma nota, sustentada) | ✅ já funcionava | parser lê `<tie>` (nível nota) em `build_notes.py`; **5351** notas ligadas no runtime |
| **Notas pontuadas** | ✅ já vinham pela `<duration>` | 0.75 / 1.5 / 3.0 tempos → ABC `3` / `6` / `12`; **964** notas |
| **Slurs** (ligadura de expressão / legato) | ❌ **faltavam** | `compile_file` ignorava `<notations>`; `to_abc` nunca emitia `(...)`. **53 peças** tinham slur na partitura e **nenhuma** chegava ao player |
| **Durações irregulares** | ❌ bug | 5/16, 7/16 (1.25 / 1.75 tempos) saíam como `B5` → abcjs *"Duration not representable"*, desenho e áudio errados |

No trompete a diferença é audível: nota **ligada (slur) não se articula** — só o ar/lábio
move entre as notas (lip/valve slur); nota separada é "tu"-cada. Sem slurs, todo o
acompanhamento soava picado/robótico.

## Correções

- **`content/build_notes.py`** — lê `<slur type="start|stop">` de `<notations>` e grava
  `slur_start` / `slur_stop` nos eventos (entra no `notes_runtime`, que alimenta o
  player **e** o `fuse_melodies`).
- **`content/build_abc.py`**
  - `to_abc` emite slurs **balanceados** por profundidade — slur torto do OMR (start sem
    stop) **não quebra** o ABC; o que sobra fecha no fim do compasso/peça.
  - `note_token` **decompõe** durações não representáveis em pedaços **ligados**
    (5/16 → semínima ligada à semicolcheia `B4-B`), preservando o tempo total e
    escrevendo a ligadura/ponto que o OMR deixou implícito na duração.
- Regenera nos **dois** caminhos do corpus: OMR cru (`to_abc`) e as 75 melodias
  "dedos" (`fuse_melodies.py` → `to_abc`).

## Verificação (headless, abcjs real)

- **110/110** peças renderizam · **107** desenham ligadura · **zero** avisos do abcjs
  (antes havia vários *"Duration not representable"*).
- `validate.py` OK (110 peças) · e2e Playwright **8/8**.

## Sampler / MIDI de trompete

O timbre já é um **soundfont público de trompete** (abcjs `program:56`,
`./vendor/soundfont/trumpet-mp3/`) e carrega normalmente. O ganho real de "MIDI"
aqui é a **articulação correta**: legato (slur) + sustentação (tie) + ritmo pontuado
certo — é isso que faz a linha soar como trompete, não a troca de amostra.

**Caveat honesto:** o synth do abcjs re-dispara cada nota mesmo sob slur (não faz
portamento de verdade). A ligadura agora está **correta na partitura e no
agrupamento**; o "não articular" de fato depende do motor. Opções futuras: soundfont
MusyngKite (trompete mais rico) ou síntese por nota com sobreposição (note-overlap).

## Precisão / pendências

- `sb-011` é a única melodia **conferida à mão** — já tem slurs próprios; não foi tocada.
- As demais são **provisórias** (OMR / dedos): as ligaduras herdam a precisão do OMR.
  Onde o OMR não marcou o slur, ele não aparece — candidatas a conferência manual.
