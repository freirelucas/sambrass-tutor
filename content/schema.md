# Modelo de dados — Fundação (Fase 0)

Fonte da verdade do conteúdo do app. **Agnóstico de instrumento**: o conteúdo
musical é guardado em **tom de concerto**; cada instrumento aplica sua própria
transposição, clave e digitação. É isso que permite "trompete hoje, trombone/sax
amanhã" sem reescrever o repertório.

```
piece (tom de concerto)  ──aplica──►  instrument (transpõe + digita)  ──►  render
```

## Convenções
- **Notas:** nomes internacionais por classe de altura (`C, C#, D, Eb, F, G, Ab, Bb…`),
  maior assumido. Display em PT-BR (Fá, Sol, Mi♭…) fica na camada de UI.
- **Trompete Bb:** soa uma 2ª maior **abaixo** do escrito. Logo
  `concert = escrito − 2 semitons` e `escrito = concert + 2 semitons`.
  Ex.: escrito **Fá (F)** ⇒ concert **Mi♭ (Eb)**.

## Entidades

### `piece` — `pieces.json`
Conteúdo musical, sem nada específico de instrumento.
| campo | sentido |
|---|---|
| `id` | `sb-009` (estável) |
| `num` | número no caderno (1–110) |
| `titulo`, `compositor` | display |
| `compasso` | ex. `2/4` |
| `key_concert` | tom em concerto (international) |
| `modulates_to_concert` | tom final se modula, senão `null` |
| `densidade`, `forma`, `celulas`, `arpejos`, `requisitos`, `dificuldade` | análise (1–10) |
| `melodia` | **opcional/faseado**: `[{pitch_concert,dur,…}]`; só Fases 4–5 precisam |
| `dominio_publico` | gate de distribuição (Fase 6). Default `false` = tratar como protegido até verificar |
| `verificada` | metadado lido direto da partitura |
| `score` | arquivo da partitura recortada |

### `instrument` — `instruments/<id>.json`
Camada que materializa a peça para um instrumento.
| campo | sentido |
|---|---|
| `id` | `trumpet_bb` |
| `transpose_semitones` | escrito = concert + este valor (Bb tpt = `+2`) |
| `clave`, `tessitura` | clave e extensão escrita |
| `fingering` | mapa `nota_escrita → combinação` (válvulas/posição) |

### `cell` — `cells.json`
Vocabulário **abstrato e genérico** (sem direito autoral), renderizável e tocável.
Células rítmicas C1–C7 (padrão de durações em 2/4) e arpejos A1–A4 (graus da escala).
Alturas entram só no render.

### `caderno` — `cadernos/<id>.json`
Coleção/naipe: ordem das peças + instrumento padrão.

### `curriculum` — `curriculum/<id>.json`
A jornada: rotina diária + semanas, referenciando `piece.id` e `cell.id`.

## Geração e validação
- `build_content.py` deriva `pieces.json`, `cadernos/…` e `curriculum/…` a partir do
  curso legado (zip), convertendo escrito→concert e **validando o round-trip**
  (concert→escrito tem de bater com o tom original do caderno).
- `validate.py` checa integridade referencial do conteúdo já versionado.
