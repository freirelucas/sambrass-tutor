# Tutor de Sambrass — Plano do Produto de Tecnologia

Documento de planejamento. Transforma o caderno digital atual
("O Caminho do Sambrass — Trompete") num **app tutor** que conduz a prática,
toca, escuta e acompanha o progresso — e que nasce pessoal mas é arquitetado
para virar plataforma multi-instrumento.

## Decisões tomadas

| Eixo | Escolha | Implicação |
|---|---|---|
| **Escopo** | Pessoal **+** plataforma multi-instrumento | Começa só p/ o Lucas (trompete), mas o modelo de dados generaliza p/ sax, trombone, outros cadernos. |
| **Funções** | Todas as quatro | Metrônomo+rotina · snippets de células · jornada+progresso · detecção de tom (mic). |
| **Stack** | App nativo (loja) | iOS+Android. Recomendação: **Flutter** (ver §3). |

Reconciliação: a opção "PWA" do escopo era sobre *audiência* (pessoal primeiro);
a tecnologia escolhida é **nativa**. O app é offline-first, sem backend na fase
pessoal; backend só entra na fase plataforma.

---

## 1. Elementos extraídos

### A) DNA musical
Caderno **homogêneo** (ótimo para ensinar progressivamente): **2/4**, tons
**Fá / Sol / Ré** dominantes (Sib, Dó, Lá são exceção), **trompete Bb**.
Eixos de dificuldade, nesta ordem:
**tonalidade → densidade rítmica → cromatismo → extensão da forma**.

### B) Vocabulário reutilizável
Dominar isto **é** ler o caderno à primeira vista.

- **Células rítmicas:** C1 colcheias · C2 síncope · C3 colcheia pontuada+semi ·
  C4 quatro semicolcheias · C5 tercina · C6 contratempo · C7 anacruse.
- **Arpejos:** A1 tríade ↑ · A2 tríade ↓ · A3 dominante c/ 7ª · A4 bordadura cromática.

### C) Método pedagógico
- **Meta dupla:** tocar a peça inteira **+** ler à primeira vista com fluência.
- **Rotina diária 90 min:** aquecimento 15 · célula do dia 20 · música em foco 35 ·
  leitura à 1ª vista 15 · revisão/roda 5.
- **6 semanas**, princípio "uma dificuldade nova por vez".

### D) Ativo escondido (decisivo)
As partituras recortadas **já trazem a digitação do trompete** impressa sobre cada
nota (0, 1, 2, 12, 13, 23, 123) + marcações de seção, casas e tercinas. Mais os
metadados por peça (tom, forma, células, requisitos, dif 1–10). É exatamente o
insumo das funções interativas — **sem precisar de OMR nem reproduzir letra**.

---

## 2. Visão do produto

**"Companheiro de Prática Sambrass"** — um app que **conduz** o treino de 90 min em
vez de só exibir o caderno: pulsa, toca a célula, escuta você, marca o progresso
e empurra a jornada das 6 semanas para frente.

---

## 3. Arquitetura

### Princípio central: conteúdo em tom de concerto + camada de instrumento
Esta separação é o que faz "pessoal hoje, plataforma amanhã" funcionar:

```
Conteúdo musical (agnóstico)        Camada de instrumento
- peça em TOM DE CONCERTO            - transposição (Bb=+2, Eb=-3, C=0…)
- forma, células, melodia            - clave + tessitura
                                     - digitação/posição (válvulas, vara)
        \________________  aplica  ________________/
                          v
            Render p/ trompete hoje, trombone amanhã
```

A mesma peça serve qualquer naipe; troca-se só a camada de instrumento.

### Stack recomendada: Flutter
- **Por quê:** um só código iOS+Android; `CustomPainter` é ideal para desenhar
  notação e o ponteiro de leitura no tempo; bom áudio de baixa latência
  (Oboe no Android, AVAudioEngine no iOS via plugins); **FFI p/ C** permite rodar
  o DSP de detecção de tom (YIN) com performance.
- **Alternativa — React Native:** vale se quisermos **manter também uma versão web**
  (reaproveita o JSON atual e o VexFlow num WebView) e o ecossistema JS. Trade-off:
  render de notação e áudio de baixa latência são mais trabalhosos que no Flutter.
- **Decisão em aberto:** Flutter (melhor app nativo único) **vs** RN (se web
  compartilhada for prioridade).

### Backend
- **Fase pessoal:** nenhum. Conteúdo embarcado no app; progresso em SQLite/local.
- **Fase plataforma:** contas + sync + entrega de conteúdo (ex.: Supabase/Firebase).

---

## 4. Modelo de dados (evolução do atual)

Hoje `data/musicas.json` é só metadado. Evolui para entidades separadas:

- **`piece`** — `id, titulo, compositor, compasso, tom_concert, forma[], celulas[],
  dominio_publico, melodia[]?`. `melodia[]` = `{pitch_concert, duração, ligadura,
  seção}` — **opcional e faseado** (só as funções de áudio/mic precisam dela).
- **`instrument`** — `id (trompete_bb…), transposição, clave, tessitura,
  digitação{nota→combinações}`. Extrai p/ dados a digitação que hoje vive só na
  imagem do score.
- **`cell`** (C1–C7) — padrão rítmico abstrato, **renderizável e tocável** (genérico,
  sem direitos autorais).
- **`caderno/naipe`** (sambrass23) — ordem das 110 + instrumento padrão.
- **`curriculum`** — as 6 semanas referenciando peças e células (≈ `jornada.json`).
- **`user_progress`** — por peça: `a_ler / em_foco / dominada`, bpm atingido, data.

> Sequenciamento esperto: **Fases 1–3 não precisam da `melodia[]`** (célula é
> genérica, metrônomo é só tempo, progresso é metadado). Só Fases 4–5 exigem
> transcrever melodias — então entregamos muito valor antes desse esforço.

---

## 5. Os quatro pilares (como cada um funciona)

1. **Metrônomo + rotina do dia** — scheduler de áudio *sample-accurate* (não
   `Timer`), tempo-alvo por peça e **rampa lento→roda**. Monta os 5 blocos de 90 min
   a partir do `curriculum`.
2. **Snippets de células C1–C7** — desenha a notação (CustomPainter) e toca em loop
   com clique; é o bloco "célula do dia". Genérico ⇒ zero risco autoral.
3. **Jornada + progresso** — estado por peça, sequência das 6 semanas, persistência
   local. Tela "treino de hoje".
4. **Detecção de tom (microfone)** — trompete é **monofônico** ⇒ tratável.
   Pipeline: mic → frames → **YIN** (f0) → suavização → Hz→MIDI → transpõe p/
   concert → compara à nota esperada → cents + acerto. Entrega em camadas:
   **(a) afinador → (b) acerto de nota num loop de célula → (c) nota da leitura à 1ª vista**.

---

## 6. Roadmap em fases

| Fase | Entrega | Pilar | Precisa de melodia transcrita? |
|---|---|---|---|
| **0 — Fundação** | Shell do app nativo; modelo concert-pitch + camada de instrumento; importar as 30 catalogadas; telas de banco/jornada (port do site) | — | Não |
| **1 — Metrônomo + Rotina** | Metrônomo sample-accurate, tempo-alvo + rampa; gerador do treino de 90 min | 1 | Não |
| **2 — Snippets de células** | Render + áudio em loop dos C1–C7 | 2 | Não |
| **3 — Progresso + Jornada** | Estado por peça, sequência das 6 semanas, persistência | 3 | Não |
| **4 — Play-along + Leitura assistida** | Groove de samba + ponteiro de leitura no tempo | (1/2) | **Sim** |
| **5 — Detecção de tom** | Afinador → acerto de nota → leitura à 1ª vista pontuada | 4 | **Sim** |
| **6 — Plataforma** | Contas, sync, multi-instrumento/multi-caderno, licença, lojas | — | — |

---

## 7. Partes difíceis (honestidade técnica)

- **Transcrição das melodias** — esforço manual; a digitação já impressa nos scores
  ajuda muito. É o gate das Fases 4–5 (não antes).
- **Latência de áudio** — exige engine nativa para clique e mic; `Timer` do Dart não
  serve para o metrônomo.
- **Licenciamento (loja)** — melodias de compositores vivos (Djavan, Chico, Jorge
  Aragão…) têm direitos. **Uso pessoal: ok.** Distribuição na loja: precisa licença
  **ou** repertório de domínio público + modelo "usuário importa o próprio caderno".
  Gate da Fase 6, não das anteriores. Letras já ficam de fora (como hoje).
- **Notação no nativo** — Flutter não tem VexFlow; render via CustomPainter (mais
  controle, mais trabalho) ou lib de terceiros.

---

## 8. Próximos passos imediatos

1. **Fechar o framework** — Flutter (recomendado) vs React Native (se web junto).
2. **Fase 0 — Fundação de dados** (independe do framework, dá p/ começar já):
   reorganizar o conteúdo atual no modelo `piece` + `instrument` (trompete_bb) +
   `cell` + `curriculum`, extraindo a digitação para dados.
3. Scaffold do app nativo e port das telas de banco/jornada.
4. Fase 1 (metrônomo + rotina) como primeiro valor tocável.
