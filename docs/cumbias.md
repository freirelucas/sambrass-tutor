# Jornada das Cumbias

Segunda **jornada** do app, ao lado de "O Caminho do Sambrass". Selecionável no menu
inicial (topo da Trilha). Escada **por música** (um nó por cumbia), com o **riff
repetido** destacado em cada Story — a cumbia/chicha vive de frases repetitivas.

## Arquitetura multi-jornada (aditiva)
O Sambrass fica **intacto** (`data/` flat, progresso em `sb2_*`). As cumbias entram
ao lado, sem risco ao que já funciona:
- `app/app.js`: `JORNADAS` (registro) + `JORNADA` (ativa, em `localStorage.jornada_ativa`)
  + `JCFG()`. `carregar()` busca `./data/<base>/`, `store` prefixa por jornada
  (`sb2_*` vs `cu2_*` → progresso isolado), `idOf()`/`loadAbc()` usam o prefixo da jornada.
  `trocarJornada(id)` limpa o `DB` e recarrega.
- `app/trilha.js`: seletor "Sambrass · Cumbias" + HUD/intro por jornada.
- `app/story.js` / `app/estudo.js`: base-path da jornada; o tutor abre por
  `estudo.html?jornada=cumbias&id=cu-NNN` (casa a peça por `x.id`).
- `app/build_site.py`: `emit_sambrass()` → `data/`, `emit_cumbias()` → `data/cumbias/`.

## Pipeline de conteúdo
```
content/cumbia/pdfs/*.pdf                      (partituras-fonte, trompete Bb)
   │  transcribe.py  (mkxml.py: lista de notas → MusicXML, transpose -2, armadura, ties/slurs)
   ▼
content/notes/cumbia/cu-NNN.musicxml           (tema principal / riff — tier 'rascunho')
   │  build_cumbia.py
   │    ├─ build_notes.compile_file  → eventos (dedos, concerto)
   │    ├─ build_abc.to_abc          → ABC (player abcjs)
   │    ├─ phrases.extract_riff      → riff dominante (n-gramas) + cobertura
   │    └─ features + ordenação por dificuldade → 3 tiers (riff → síncope → fogo)
   ▼
content/cumbia/build/*.json   →  build_site.py  →  _site/data/cumbias/*.json
```

## "Frases repetitivas" (o coração da jornada)
`phrases.py` acha, por cumbia, a **frase mais repetida** (a sequência de
`(altura, duração)` mais longa que volta ≥2×, sem sobreposição). Usada para:
- **destacar o riff** na Story (pauta verovio + desafio "🔁 toque o riff em loop, 5×");
- **ordenar a escada**: mais repetição = mais fácil de decorar = entra antes
  (`dificuldade = 2·agudo + vel + fôlego − 2·repetição`).

## Qualidade (honestidade)
As melodias das cumbias são **provisórias** (tier `rascunho`): leituras de
melhor-esforço do **tema principal** (não a partitura inteira, não conferidas nota a
nota). O app mostra "⚠ melodia provisória" e o tutor compara por **classe de altura**
(tolerante a oitava), igual ao OMR do Sambrass. Para promover a `conferida`: criar
`content/notes_manual/cu-NNN.abc` à mão (vence tudo) — ou usar Audiveris (OMR) como no
Sambrass e conferir.

## Adicionar uma cumbia
1. Coloque o PDF em `content/cumbia/pdfs/`.
2. Adicione uma entrada em `TUNES` no `content/cumbia/transcribe.py` (tom, compasso e a
   lista de compassos/notas do tema — DSL em `mkxml.py`).
3. `python3 content/cumbia/transcribe.py && python3 content/cumbia/build_cumbia.py && python3 app/build_site.py`.

## Deploy
`.github/workflows/pages.yml` regenera a jornada no deploy (`pip install verovio` +
`build_cumbia.py`), então editar uma transcrição atualiza o site sozinho.

## Direitos autorais
Os PDFs são arranjos de terceiros, versionados por escolha explícita do dono do repo.
Se o repositório for público, isso é um risco a revisar (mesma ressalva da auditoria):
manter os PDFs fora do repo e versionar só os dados derivados é o caminho mais seguro.
