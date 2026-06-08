# Melodias conferidas à mão (tier "conferida")

O app mostra a **qualidade** de cada melodia em 3 níveis (badge no banco e rótulo no estudo):

- **rascunho** (`~`): leitura automática crua do OMR (Audiveris). As notas podem errar.
- **dedos** (`♪`): **fusão** — a *classe de altura* veio da **digitação impressa** lida da
  página (`content/notes_auto/*.abc`, gerado por `content/fingering/fuse_melodies.py`), com
  oitava/ritmo do OMR. Bem melhor que o cru, ainda provisória. **75 peças** hoje.
- **conferida** (`✓`): melodia revisada à mão — **vence tudo**. Hoje: `sb-011`.

A precedência no build é **conferida > dedos > rascunho** (`content/build_abc.py`), e o tier
por peça sai em `content/notes_quality.json` → `data/quality.json` (consumido pelo app).

## Promover a faixa que você mais ensina a "conferida"

1. Pegue o ABC provisório que o app já toca como ponto de partida:
   ```
   python3 -c "import json;print(json.load(open('content/notes_abc.json'))['sb-044'])" \
     > content/notes_manual/sb-044.abc
   ```
2. Corrija `content/notes_manual/sb-044.abc` lendo a partitura — notas, oitavas, ligaduras.
   Mantenha o cabeçalho em **tom escrito**: `X: / T: / M: / L:1/16 / Q:1/4=92 / K:`.
3. Regenere e publique:
   ```
   python3 content/build_abc.py && python3 app/build_site.py
   ```
   A peça vira **`conferida ✓`** automaticamente (override sobre dedos/OMR).

## Regenerar a camada "dedos" (fusão)

```
python3 content/fingering/extract_all.py      # lê a digitação das 110 → reads/ (+ _summary.json)
python3 content/fingering/fuse_melodies.py    # funde dedos+OMR → content/notes_auto/*.abc
python3 content/build_abc.py                  # serve dedos>OMR e recalcula os tiers
```
(O `notes_auto/` já está versionado; só regenere se mudar o leitor ou o OMR. `extract_all`
precisa de `opencv`/`scipy`/`Pillow` e dos scores recortados — por isso fica fora do `build_all`.)
