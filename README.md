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
| **Cumbias** (principal, default) | cumbias / chicha latinas | **15** |
| **Sambrass** | sambas · Book 1 → Arban | **110** |
| **Total** | | **125** |

Além das peças, cada linha traz **12 aquecimentos** (Flow do Cichowicz) e cartões
de técnica.

## Números canônicos (a fonte da verdade são os dados)

- **110 sambas** · **15 cumbias** · **125 peças no total**.
- As contagens exibidas na UI são **dinâmicas** — vêm de
  `app/data/**/pieces.json` (`ms.length`), então **nunca** ficam defasadas: some
  ou entre uma peça e a trilha, o HUD e o Progresso se ajustam sozinhos. Não há
  contagem de peça fixada no código.

### Numeração das cumbias (por que vai até 16 mas são 15)

As cumbias são numeradas **1–12, 14, 15, 16** (15 peças; **o número 13 não
existe**). Histórico:

- **cu-013** e **cu-017** foram **removidas** (o OMR/Audiveris falhou de forma
  irrecuperável na partitura — ver `content/cumbia/transcribe.py`).
- **cu-016 "Ya se ha Muerto mi Abuelo"** **entrou** (é a mais recente).

Ou seja: o maior número é 16, mas a **contagem é 15**. Não é 16 nem 95 — é **15
cumbias**.

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
