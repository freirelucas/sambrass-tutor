# Notas via OMR — PROVISÓRIO (a conferir)

MusicXML gerados automaticamente pelo **Audiveris** (parte escrita em Si bemol +
`<transpose -2>` injetado, para o concerto ser derivável). São transcrições de máquina
e **contêm erros** — armadura/notas a conferir e corrigir.

- Brutos (`.mxl`/`.omr`/logs): branch `omr/audiveris-raw`.
- QA contra o catálogo: `content/omr_report.csv` (armadura/compasso).
- Pipeline: `content/omr_prep.py` → Actions/Audiveris → `content/omr_import.py` → `build_notes.py`.

**Fluxo de correção:** abrir no MuseScore, corrigir, e salvar a versão final como
`content/notes/sb-NNN.musicxml` (que tem precedência sobre esta pasta provisória).
