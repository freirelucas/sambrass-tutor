# Leitura da digitação (dedos) — cobertura nas 110

A **digitação impressa** (dedos de trompete: dígitos grandes em negrito acima da pauta) é
o **canal de altura mais limpo** das partituras do caderno Sambrass23. O OMR (Audiveris)
erra a altura nesses scans de ~200 dpi, mas os dedos são nítidos e seguem uma gramática
rígida — então lê-los dá a **classe de altura exata** de cada nota, sem depender do OMR.

Este diretório contém o leitor, os templates e a **extração das 110 páginas** como dado
revisável. **Não altera nenhuma melodia do produto** — é a base para a fusão (dedos = altura,
OMR = oitava/ritmo, catálogo = tom) que vem depois.

## Números

| | |
|---|---|
| Páginas lidas | **110 / 110** (nenhuma falha de detecção) |
| Dedilhados extraídos | **12.255** (mediana 105/peça) |
| Confiança **alta** | **76 / 110** |
| A **revisar** | 34 / 110 |
| Tempo | ~11 s para as 110 |

Confiança por nº de sistemas (páginas mais densas comprimem a notação → mais difícil):

| sistemas | páginas | alta |
|---|---|---|
| 3 | 7 | 5 |
| 4 | 60 | 45 |
| 5 | 34 | 20 |
| 6 | 7 | 5 |
| 7 | 2 | 1 |

## Validação

Na **011** ("Preciso Me Encontrar"), o Sistema A sai
`12 0 2 … 2 12 2 12 0 12` — **idêntico** à ditadura do Lucas
(abertura *mi-sol-si*; cadência *si-lá-fá#-lá-sol-mi*). É o teste de aceitação do leitor
(`read_fingerings.py` falha o CI se a 011 regredir).

## Como funciona (robusto p/ as 110)

1. **Binarização adaptativa** (Otsu por página) — scans variam de claros a escuros.
2. **Pauta por morfologia horizontal** — acha linhas longas; resiste à barra de título
   lateral e a páginas de 3 a 7 sistemas; valida o espaçamento (pula réguas espúrias).
3. **Detecção de dígito com escala adaptativa** — o tamanho do dedo escala com a pauta
   (páginas com mais sistemas têm notação menor).
4. **Classificação por template** (0/1/2/3) — fonte fixa do caderno → templates 1x, reuso 110x.
5. **Agrupamento pela gramática** — dígitos de um dedilhado sobem (1<2<3) e o `0` é sozinho,
   então `2` seguido de `1` é sempre uma nova nota (sem chutar espaçamento).

## Limites honestos (o que ainda NÃO está resolvido)

- **Oitava e ritmo**: o canal de dedos dá a *classe* de altura, não a oitava nem a duração.
  A fusão com o OMR (oitava/ritmo) é o próximo passo — ver `transcribe.py`.
- **Páginas "a revisar" (34)**: scans mais claros/comprimidos degradam a classificação
  (3 vira 2, pares se quebram). O escore de confiança as separa para revisão dirigida.
- Este dado **não está ligado ao produto** — nenhuma melodia das 110 foi sobrescrita.
  Zero risco de publicar nota errada.

Páginas a revisar: 1, 2, 9, 12, 13, 15, 22, 27, 29, 30, 31, 32, 39, 42, 47, 48, 52, 53,
55, 58, 62, 64, 66, 68, 69, 70, 75, 76, 77, 84, 88, 89, 90, 92.

## Reproduzir

```
python3 content/fingering/extract_all.py        # → reads/sb-NNN.json + _summary.json
python3 content/fingering/read_fingerings.py content/scores/sb-011.jpg   # leitura de 1 página
```
