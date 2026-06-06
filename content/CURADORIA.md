# Curadoria pedagógica + analytics

Camada derivada do catálogo (`pieces.json` + `cells.json`), reprodutível por scripts.
Tudo em tom de concerto na base; a dificuldade e as habilidades são calculadas por
fórmula transparente (`content/curadoria/lib.py`).

## Como regenerar
```
python3 content/curadoria/recalibrar.py   # dificuldade.json (1–10 recalibrada)
python3 content/curadoria/trilha.py       # skills.json, piece_skills.json, trilha.json
python3 content/curadoria/curriculo.py    # curriculum/sambrass23-trilha.json (13 módulos)
python3 content/analytics.py              # analise.html + analytics.json
```

## Analytics — `content/analise.html` (+ `analytics.json`)
Dashboard de arquivo único (sem build). Distribuições de tom/compasso/densidade,
dificuldade **manual × recalibrada**, frequência de **habilidades** e **células**,
**matriz célula × tom** (acha peça-treino por habilidade/tom) e outliers.
Achados: **síncope em 98/110**; tons escritos F/G/D/C dominam; 18 peças em 4/4; 8 modulações.

## Dificuldade recalibrada — `content/curadoria/dificuldade.json`
`dificuldade_calc` (1–10) por features: acidentes (tom) → densidade → cromatismo →
extensão da forma, + semicolcheia/tercina/contratempo/modulação; normalizada para a
escala cheia. **Não** sobrescreve a `dificuldade` manual (o app/você escolhe qual usar).
Corrige o aglomerado em 6–7 da estimativa manual (013/039 = 9, 009 = 1).

## Habilidades — `skills.json` + `piece_skills.json`
Taxonomia normalizada (escada de tonalidade, síncope, tercina, colcheia-pontuada,
semicolcheia, contratempo, anacruse, casas, D.S./D.C., modulação, forma longa/extensa,
cromatismo, 4/4) e as habilidades exigidas por cada peça.

## Trilha — `content/curadoria/trilha.json`
- **trilha_mestra**: as 110 ordenadas introduzindo **≤1 habilidade nova por passo**
  (greedy com pré-requisitos + dificuldade recalibrada). 93 passos com 0 nova, 16 com 1.
- **trilhas_por_habilidade**: por habilidade, fácil→difícil (peças-treino).
- **escada_leitura**: ordem de leitura à 1ª vista por dificuldade/tom/densidade.

## Currículo expandido — `content/curriculum/sambrass23-trilha.json`
13 módulos de ~9 peças a partir da trilha mestra, temados pelas habilidades novas, com
foco + leitura à 1ª vista + revisão, mantendo a rotina de 90 min. Convive com o
`sambrass23-6semanas.json` (versão curta original).

## A conferir
Ver `REVISAR.md`: a `dificuldade` manual e as `celulas` são análise minha; a recalibrada
é uma referência objetiva — ajuste os pesos em `lib.raw_difficulty` ao seu gosto.
