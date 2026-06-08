# Escada pedagógica do caderno Sambrass

Mapeamento do repertório Sambrass23 (trompete) contra três métodos importados + uma 4ª
camada idiomática do samba. Origem: handoff de pedagogia (conversa que cruzou o caderno com os
métodos). Este documento **materializa** aquela análise no código — a regra mora em
[`content/curadoria/lib.py`](../content/curadoria/lib.py) e gera
[`content/curadoria/escada.json`](../content/curadoria/escada.json) via
[`escada.py`](../content/curadoria/escada.py).

## As 4 camadas

1. **Essential Elements Book 1 — fundação.** Som/embocadura, C1 (#40–45), C6 (#158–164),
   C7 (#36), arpejos A1/A2 (#147–149), bordadura cromática A4 (#174); tons **Dó/Fá/Sol/Sib**.
   *Não cobre:* C3, C4, C5, tom de Ré como tonalidade de trabalho, 3♯, ornamentos, staccato múltiplo.
2. **Essential Elements Book 2 — células órfãs + tons.** Semicolcheias, síncope formal, 6/8,
   cut time, **tercinas**, novas armaduras **Ré/Lá/Mib**, extensão de registro. Preenche
   exatamente **C3, C4, C5** e os tons de 2♯.
3. **Arban — topo técnico.** Único que formaliza **ornamentos** (apojatura, grupeto, trinado —
   seção IV), **staccato duplo "tu-ku"** (VI), **arpejo de 7ª da dominante = A3** (V) e a
   **resistência de forma extensa** (études + ária).
4. **Camada idiomática Sambrass — o valor do app.** O que NENHUM método importado cobre:
   **suingue / divisão do samba** (o acento no "e" com a levada é interpretação, não notação →
   é o Pilar 4: detecção de tom + play-along com groove), **modulação de armadura dentro da
   peça** (vive na entidade `piece`/`curriculum`) e **mapa de respiração** para formas de 100+
   compassos.

## Tabela-mestre (requisito × método)

| Requisito | Book 1 | Book 2 | Arban |
|---|---|---|---|
| C1 colcheias em grupo | ✓ #40–45 | rev | I |
| C2 síncope | parcial (tie #59) | ✓ formal | I |
| C3 colcheia pontuada+semi | ✗ | ✓ | I (pontuadas) |
| C4 quatro semicolcheias | ✗ | ✓ | V |
| C5 tercina | ✗ | ✓ | III / V |
| C6 contratempo | ✓ #158–164 | rev | I |
| C7 anacruse | ✓ #36 | rev | I |
| A1/A2 tríade ↑↓ | ✓ #147–149 | reforço | V |
| A3 arpejo de 7ª | ✗ | parcial | V |
| A4 bordadura cromática | ✓ #174 | escala crom. | III |
| Tons Fá/Sol/Sib/Dó | ✓ | + Ré/Lá/Mib | III |
| Ornamentos | ✗ | ✗ | IV |
| Staccato duplo (tu-ku) | ✗ | ✗ | VI |
| Forma extensa / resistência | ✗ | estudos longos | études + ária |

## A regra (transparente, em `lib.py`)

`nivel_minimo(peça)` = maior nível entre os três eixos (critério **estrito**: um requisito
órfão sobe o nível inteiro):

- **Tom escrito** (trompete Bb = concerto +2 semitons; *sharp/flat-aware*):
  `{C, F, G, Bb}` → Book 1 · `{D, A, Eb, E}` → Book 2 · `{F#, B}` → Arban.
  Inclui o tom da **modulação** quando há. *(Por isso Sib 2♭ é Book 1 mas Ré 2♯ é Book 2 —
  contagem de acidentes sozinha não distingue.)*
- **Células:** `{C3, C4, C5}` exigem Book 2.
- **Marcadores qualitativos** (só Arban formaliza), por token de `requisitos`:
  `ornamentos`, `resistência`, `forma-extensa-101c`, `forma-muito-longa`, `tercina-contínua`,
  `cromatismo-denso`, `contratempo-intenso`.

`prerequisitos` lista, por camada, as âncoras que a peça encontra em cada método + a camada
idiomática. `requisito_orfao_book1` lista o que impede tocá-la só com o Book 1.

## Resultado (110 peças)

Funil de cobertura (nível mínimo → acumulado tocável):

| | Book 1 | + Book 2 | + Arban |
|---|---|---|---|
| nível mínimo | 30 | 67 | 13 |
| **acumulado tocável** | **30** | **97** | **110** |

## Validação contra a handoff (oráculo das 30)

A handoff trazia 30 peças hand-curadas com um funil estrito (Book 1 → 10, +Book 2 → ~23,
+Arban → 6 do ápice). Casando **por título** (ver drift abaixo), a regra reproduz **27/29**.
As 2 divergências são justificadas:

- **Fita Amarela** — regra: Book 1 · handoff §4: Book 2. A peça só tem C1/C7 + tom **Sib (2♭)**,
  que a **própria tabela-mestre §3 classifica como Book 1**. O §4 da handoff se contradiz; a
  regra segue o §3. *(Divergência a favor da regra.)*
- **Preciso Me Encontrar** — regra: Book 2 · handoff: Arban. **Drift de numeração e metadados:**
  na handoff é "010 · Lá (3♯) · tercina-contínua · dif 7"; no catálogo atual é **sb-011 · Sol
  (1♯) · C5 · dif 4**. Pela metadata atual (autoritativa, é a peça-vitrine do app), Book 2 está
  correto.

### Drift de numeração

A numeração do `site_preview` (fonte da handoff, 30 peças) **não bate** com o `pieces.json`
atual (110, numerado pelo rodapé do caderno; bug 010/011 corrigido). Ex.: handoff `010` =
`sb-011` hoje. Por isso a validação casa por **título normalizado**, não por número.

## Regenerar

```
python3 content/curadoria/escada.py      # só a escada → escada.json
python3 content/build_all.py             # tudo (inclui escada + funil no analise.html)
```

A escada é publicada em `data/escada.json` (via `app/build_site.py`) e a página de estudo
mostra o **nível** da peça como badge ("nível Book 2 · destrava: C5").
