# Tutor de Trompete

PWA (vanilla JS, offline-first) para aprender **trompete** tocando por cima de
repertório real, com uma **língua visual** única (cor por nota — padrão
[Chromatone](https://chromatone.center) —, contorno, rolo de alturas, roda de
ritmo e o jogo "monte o riff"). Publicado no GitHub Pages:
https://freirelucas.github.io/sambrass-tutor/

## As duas linhas

O app tem **duas linhas** (jornadas). "Sambrass" deixou de ser o nome do app e é
**uma das linhas**.

| Linha | O que é | Peças |
|------|---------|------:|
| **Cumbias** (principal, default) | cumbias / chicha latinas (+ 1 ethio-jazz) | **16** |
| **Sambrass** | sambas · Book 1 → Arban | **110** |
| **Total** | | **126** |

Além das peças, cada linha traz **12 aquecimentos** (Flow do Cichowicz) e cartões
de técnica.

## Números canônicos (a fonte da verdade são os dados)

- **110 sambas** · **16 cumbias** · **126 peças no total**.
- As contagens exibidas na UI são **dinâmicas** — vêm de
  `app/data/**/pieces.json` (`ms.length`), então **nunca** ficam defasadas: some
  ou entre uma peça e a trilha, o HUD e o Progresso se ajustam sozinhos. Não há
  contagem de peça fixada no código.

### Numeração das cumbias (por que vai até 17 mas são 16)

As cumbias são numeradas **1–12, 14, 15, 16, 17** (16 peças; **o número 13 não
existe**). Histórico:

- **cu-013** foi **removida** (o OMR/Audiveris falhou de forma irrecuperável na
  partitura — ver `content/cumbia/transcribe.py`).
- **cu-017 "Yekermo Sew"** (Mulatu Astatke, ethio-jazz do repertório da banda)
  também tinha caído no OMR (o PDF é foto de celular), mas **voltou em 2026-08**
  transcrita à mão via DSL (tier rascunho, a conferir com a banda).

Ou seja: o maior número é 17, mas a **contagem é 16**.

### Gravações reais (app/audio/)

Oito gravações enviadas pela banda (2026-07): 6 **modelos no trompete**
(cu-001, cu-002, cu-010 ×2, cu-011 ×2) e 2 **ensaios da banda completa** (peças a
identificar). Aparecem na página de estudo das cumbias ("🎙 a gravação real" +
"🎧 ensaio da banda", com controle de velocidade) e servem de **referência
independente** para validar as transcrições: `tools/audio_confere.py` compara o
pitch-track da gravação com o ABC (pega erro de oitava global do OMR — caso
cu-005). Validação de alturas no build: `content/cumbia/check_pitch.py` →
`pitch_warn.json` (tessitura/8ª/salto/tom).

## Rodar / buildar

```bash
python3 content/cumbia/build_cumbia.py   # dados das cumbias (+ validação de compassos)
python3 app/build_site.py                # copia app/ → _site/ e injeta os dados por linha
python3 -m http.server 8099 --directory _site
```

Testes (navegador): `npx playwright test` (9 specs) + `node tests/pitch-core.test.js`.
Deploy: GitHub Actions (`.github/workflows/pages.yml`) a cada push no `main` —
roda os builds em Python e publica no Pages.

## Estrutura

- `app/` — o site estático (HTML/CSS/JS vanilla). Módulos visuais: `chroma.js`
  (cor Chromatone), `proll.js` (rolo de alturas + Espelho), `roda.js` (roda de
  ritmo), `montariff.js` (jogo), `lego.js`/`grafismo.js` (Legos), `groove.js`
  (banda de cumbia).
- `content/` — pipeline de dados em Python (transcrição, currículo, blocos).
- `docs/` — planos e auditorias de UX/pedagogia.
