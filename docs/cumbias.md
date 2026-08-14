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
O catálogo `content/cumbia/pieces_cumbia.json` é o **dono da metadata** e de um campo
`source` por peça que decide de ONDE vem a melodia (`cu-NNN.musicxml`):
- `source="dsl"`  → transcrição à mão na lista `TUNES` de `transcribe.py` (gera o musicxml);
- `source="omr"`  → vem do Audiveris (`omr_import.py`, pós-CI); aqui é só metadata + o `pdf`;
- `source="manual"` → conferida à mão em `content/cumbia/notes_manual/cu-NNN.abc`.
`transcribe.py` **mescla** `TUNES` (dsl) + `CATALOG_EXTRA` (omr/manual) sem se sobrescreverem;
`omr_import.py` só **lê** o catálogo. Cada `cu-NNN.musicxml` é escrito por UM pipeline (o que
`source` nomeia), então o glob de `build_cumbia.py` nunca vê dois arquivos para o mesmo num.
```
content/cumbia/pdfs/*.pdf                      (partituras-fonte, trompete Bb)
   │  transcribe.py  (mkxml.py: lista de notas → MusicXML, transpose -2, armadura, ties/slurs)
   │  …ou Audiveris (OMR) → omr_import.py  (ver "OMR para fidelidade" abaixo)
   ▼
content/notes/cumbia/cu-NNN.musicxml           (tema principal / riff — tier 'rascunho')
   │  build_cumbia.py
   │    ├─ build_notes.compile_file  → eventos (dedos, concerto)
   │    ├─ build_abc.to_abc          → ABC (player abcjs)
   │    ├─ phrases.extract_riff      → riff dominante (n-gramas) + cobertura
   │    ├─ features + ordenação por dificuldade → 3 tiers (riff → síncope → fogo)
   │    ├─ check_bars.check_all      → bars_warn.json  (compassos que não fecham a métrica)
   │    └─ check_pitch.check_all     → pitch_warn.json (tessitura/8ª/salto/tom — "notas absurdas")
   ▼
content/cumbia/build/*.json   →  build_site.py  →  _site/data/cumbias/*.json
```

### Convenção de altura do pipeline (IMPORTANTE)
Todo ABC do pipeline (`build_abc.to_abc` e `notes_manual/*.abc`) está em **tom
ESCRITO** da parte de trompete Bb (K:C p/ peça em Bb concert). `abc_events.
events_from_abc` devolve `written_midi` = o midi lido e `concert_midi` = escrito − 2.
(Até 2026-08 assumia-se ABC concert e somava-se +2 — riff/perfil/dificuldade das
peças conferidas saíam um tom acima do real. Corrigido.)

## Validação de alturas + gravações de referência
Duas camadas contra "notas absurdas":
- **`check_pitch.py`** (no build): tessitura escrita do trompete
  (`content/instruments/trumpet_bb.json`, F#3–C6), outlier de oitava vs a mediana
  da peça, salto > 8ª dentro do compasso, e tom do ABC vs `key_concert` do
  catálogo. Sai em `pitch_warn.json`; o app mostra o aviso honesto na página de
  estudo (junto do `bars_warn`). Avisos podem ser **herdados do arranjo** (ex.:
  cu-009 El Diablo desce a Mi3 escrito no próprio PDF — abaixo da tessitura; toca-se
  8ª acima) — o aviso documenta, não necessariamente indica transcrição errada.
- **`tools/audio_confere.py`** (local; `pip install numpy soundfile`): compara o
  ABC com as **gravações reais** de `app/audio/` (modelo no trompete enviado pela
  banda) — desvio de mediana ≥7 semitons = oitava global errada (foi assim que o
  cu-005 ficou 1 ano soando 8ª acima: o "modelo" sintetizado vem do MESMO dado, só
  gravação independente denuncia). Entradas `"conf": true` em
  `app/audio/referencia.json` reprovam o check se desviarem.

As gravações aparecem no app (página de estudo das cumbias): "🎙 a gravação real"
por peça + "🎧 ensaio da banda" (play-along, com controle devagar 0.7×/0.85×).

## Tema vs peça inteira ("os dois")
Cada cumbia OMR tem **duas** representações: o **tema** (abertura, ~8–16 compassos — `abc.json`,
o que se **pratica/avalia** no tutor e abre a Story) e a **peça inteira** (`abc_full.json`, atrás
do botão "▶ tocar a peça inteira" no estudo e no player do Banco). `build_cumbia.py` extrai o tema
com `phrases.theme_measure_span()` (compassos inteiros, ancorado no riff, clamp [8,16]) e computa
perfil/dificuldade **no tema**. As 3 cumbias DSL (≤8 comp.) têm tema == peça inteira (botão escondido).
Sambrass não tem `abc_full.json` → o app degrada limpo. O tier (`quality.json`) descreve o **tema
praticado**; a peça inteira é sempre leitura OMR crua.

## "Frases repetitivas" (o coração da jornada)
`phrases.py` acha, por cumbia, a **frase mais repetida** (a sequência de
`(altura, duração)` mais longa que volta ≥2×, sem sobreposição). Usada para:
- **destacar o riff** na Story (pauta verovio + desafio "🔁 toque o riff em loop, 5×");
- **ordenar a escada**: mais repetição = mais fácil de decorar = entra antes
  (`dificuldade = 2·agudo + vel + fôlego − 2·repetição`).

## Qualidade (honestidade)
Tiers: `rascunho` (leitura OMR/à-mão não conferida — o tutor avalia por **classe de altura**,
tolerante a oitava) e `conferida` (tema conferido nota a nota contra a partitura — o tutor avalia
por **oitava exata**). Estado atual: os **12 temas OMR estão `conferida`**; as **4 cumbias DSL
seguem `rascunho`** (cu-001/002/003 + cu-017 Yekermo, transcrita à mão de uma FOTO de partitura).
A **peça inteira** (`abc_full.json`) é sempre OMR cru, qualquer que seja o tier do tema.
Para conferir/promover: criar `content/cumbia/notes_manual/cu-NNN.abc` (vence o ABC do build e marca
`conferida`); `build_cumbia.py` aplica o override (inerte enquanto o diretório não existe).

**Definition of done de uma peça "conferida":**
1. `check_bars` e `check_pitch` limpos (ou avisos justificados pelo arranjo, anotados);
2. conferência visual em `app/revisar.html` (ABC lado a lado com o recorte do PDF);
3. quando houver gravação da banda: `tools/audio_confere.py` sem desvio de oitava
   (e aí marca-se `"conf": true` no `referencia.json`).

## Adicionar uma cumbia
Coloque o PDF em `content/cumbia/pdfs/` e escolha a fonte da melodia:

**Caminho A — DSL (rápido, local):** adicione uma entrada em `TUNES`
(`content/cumbia/transcribe.py`) com `pdf`, `source="dsl"`, tom/compasso e a lista de
compassos/notas do tema (DSL em `mkxml.py`). Depois:
`python3 content/cumbia/transcribe.py && python3 content/cumbia/build_cumbia.py && python3 app/build_site.py`.

**Caminho B — OMR (Audiveris, fidelidade):** adicione uma entrada metadata-only em
`CATALOG_EXTRA` (`transcribe.py`) com `pdf` e `source="omr"` (deixe `key_concert=""` até o
`omr_check` revelar a armadura). Veja a seção abaixo.

## OMR (Audiveris) para fidelidade
O Audiveris só roda no **CI** (build Java pesado). O fluxo:
1. `python3 content/cumbia/transcribe.py` — registra a cumbia (`source="omr"`) no catálogo.
2. **Dispare** o workflow `.github/workflows/omr-cumbia.yml` (Actions → *OMR Cumbias* → Run,
   ou `workflow_dispatch` via API). Ele roda `content/cumbia/omr_prep.py` (PDF→PNG, página
   inteira 300 DPI) + Audiveris em lote e **commita os MusicXML no branch `omr/cumbia-raw`**
   (compartilha o cache do build do Audiveris com o `omr.yml` do Sambrass).
3. `git fetch origin omr/cumbia-raw && git checkout origin/omr/cumbia-raw -- omr/out`.
4. `python3 content/cumbia/omr_check.py` — confere armadura/compasso e, para `key_concert`
   vazio, **reporta o tom de concerto implícito** (`content/cumbia/omr_report.csv`). Copie
   esses tons para os `key_concert` vazios em `CATALOG_EXTRA` e rode `transcribe.py` de novo.
5. `python3 content/cumbia/omr_import.py` — junta páginas, **reduz à voz-líder** (1ª parte,
   voz 1, nota superior de acordes — passo *lossy*, com aviso de notas descartadas), injeta a
   armadura do catálogo + `<transpose -2>` e grava `content/notes/cumbia/cu-NNN.musicxml`
   (tier `rascunho`). Depois `build_cumbia.py` + `build_site.py` como sempre.
6. **Conferência** (opcional, p/ `conferida`): edite `content/cumbia/notes_manual/cu-NNN.abc`
   contra o PDF e rebuild (ver "Qualidade").

## Deploy
`.github/workflows/pages.yml` regenera a jornada no deploy (`pip install verovio` +
`build_cumbia.py`), então editar uma transcrição atualiza o site sozinho.

## Direitos autorais
Os PDFs são arranjos de terceiros, versionados por escolha explícita do dono do repo.
Se o repositório for público, isso é um risco a revisar (mesma ressalva da auditoria):
manter os PDFs fora do repo e versionar só os dados derivados é o caminho mais seguro.
