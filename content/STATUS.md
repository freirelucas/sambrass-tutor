# STATUS — piloto automático

_Branch `claude/busy-cori-QXkHR`. Atualizado a cada lote._

## Progresso
- **Catalogadas: 110 / 110 ✅** (meta: 110)
- Notas MusicXML: pipeline provado (demo) + **7 snippets de célula C1–C7** (Fase 2). Transcrição das músicas: handoff (ver abaixo).

## Pronto e versionado
- Fase 0: modelo agnóstico (peça em concerto + camada de instrumento).
- Pipeline de recorte do PDF (`recortar.py`, PyMuPDF, 200 dpi).
- Metodologia de notas (`build_notes.py`: MusicXML escrito-Bb + `<transpose>` → JSON de eventos).
- Correção do bug 010 "Peito Vazio" / 011 "Preciso Me Encontrar" + 012 "Tive Sim".

## Achados
- **Numeração autoritativa = rodapé da página** (índice da capa diverge na faixa 010–012).
- **OMR automático (oemer) inviável** aqui: quebra na detecção de armadura
  (`IndexError em get_key`); digitações sobre a pauta atrapalham. Notas: transcrição
  manual semeada agora; recomendação futura = Audiveris offline.

## Log
- (início) 32/110. Começando a catalogar os 78 faltantes por rodapé, em lotes.
- 50/110. Catalogados 007,014–016,018–021,023,024,026,029–032,037–039 (Cartola,
  Nelson, Zé Kéti, Adoniran, Ivone, Martinho, Beth, Jorge Aragão). Achados de tom:
  023/026 são 4/4; 039 "Eu e Você Sempre" em Fá# (6 sustenidos!). Tons ambíguos
  confirmados por zoom do clef+armadura.
- 68/110. + batches 4–6: 040–043,045–048,050–053,056–060,062 (Jorge Aragão,
  Alcione/Marrom, Zeca/Monarco, Paulinho da Viola, Chico Buarque). Achados: 045
  'Sufoco' modula Sib→Ré; vários 4/4 (041,046,051,056,060).
- 86/110. + batches 7–9: 063,065–066,069–083 (Vinicius, bloco Sambrass,
  Aldir Blanc/João Bosco, Gonzaguinha). Achados: 073 modula Fá→Sol, 074 Fá→Lá;
  índice volta a divergir a partir de 077 (rodapé 077='Desde Que o Samba é Samba',
  078='Cicatrizes') — catalogado pelo rodapé.
- **110/110 ✅ banco completo e validado.** + batches 10–13: 086–110
  (Ataulfo, João Nogueira, bloco Pagode: Revelação/Xande, Raça Negra, Art Popular…).
  Distribuição (concert): Eb24 F23 C20 Bb20 Ab9 G9 Db4 E1 · 2/4=92, 4/4=18 · 8 modulações.
  Export `content/catalog.csv` gerado. Próximo: Track B (semear MusicXML) + relatório.

## Relatório final (piloto automático)
Tudo no branch `claude/busy-cori-QXkHR`, validado e pushado:
- **Banco 110/110** catalogado pelo rodapé (tom em concerto + camada de instrumento);
  `content/catalog.csv` para revisão rápida.
- **Metodologia de notas** MusicXML (escrito Bb + `<transpose>`) → JSON de eventos,
  provada (`_demo_pipeline`) e aplicada aos **7 snippets de célula C1–C7** em
  `content/notes/cells/` (conteúdo do bloco 'célula do dia', Fase 2).
- **Pipeline de recorte** do PDF em alta resolução (`recortar.py`).
- **Correções de integridade**: bug 010/011 (Peito Vazio × Preciso Me Encontrar),
  numeração pelo rodapé (índice diverge), 8 modulações, 18 peças em 4/4.

### Handoff — próximos passos sugeridos
1. **Transcrever as melodias** para `content/notes/sb-NNN.musicxml` (escrito Bb +
   `<transpose -2>`): melhor por entrada manual no MuseScore a partir dos scores, ou
   Audiveris OMR offline (oemer falhou aqui). `build_notes.py` já consome. Comece pelas
   fáceis: 009, 035, 025, 001.
2. **Recalibrar a `dificuldade`** (tende a 6–7 na metade pagode) e conferir células — ver `REVISAR.md`.
3. **Conferir** modulações/formas/compositores sinalizados em `REVISAR.md`.
4. Banco a seu gosto → **scaffold do app Flutter** (Fase 1: metrônomo + rotina), depois snippets e microfone.

### Fora de escopo nesta sessão (por decisão)
- Deploy/GitHub Pages; app Flutter; transcrição MusicXML das 110 músicas.

## Madrugada — OMR + analytics + curadoria (no main)
- **OMR FUNCIONA** via GitHub Actions + Audiveris (Java 25). Piloto: 5 peças → MusicXML;
  validação contra o catálogo: **4/5 armaduras OK**, 5/5 compassos. Saídas brutas no
  branch `omr/audiveris-raw`; `content/omr_check.py` + `omr_report.csv`; importador
  `content/omr_import.py` (injeta transpose -2 → notas provisórias). Run das 110 disparado.
- **Analytics**: `content/analise.html` (dashboard único) + `analytics.json`. Síncope em 98/110.
- **Curadoria**: dificuldade recalibrada 1–10 (`dificuldade.json`), habilidades por peça,
  **trilha mestra** (1 habilidade nova/passo), trilhas por habilidade, escada de leitura,
  **currículo de 13 módulos**. Doc em `content/CURADORIA.md`.
- Trabalhando no **main** (autorizado). OMR-bruto fora do main (branch/artefato).

