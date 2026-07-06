# Plano de 5h — "Manter a pauta, enriquecer os canais" (ancorado no Chromatone)

> Tarefa: *pesquisar a fundo a estrutura e conteúdo do [Chromatone](https://chromatone.center)
> para planejar* + *manter partitura, mas enriquecer canais de representação.*

## 1. O que é o Chromatone (estrutura + conteúdo)

**Chromatone** é um projeto **open-source** (github.com/chromatone, Vue.js) que se define como
uma *"linguagem musical visual"* — um jardim digital de teoria musical visual + uma coleção de
instrumentos visuais. A meta declarada é **estabelecer um padrão** que interligue **12 notas ↔ 12
cores**, aproveitando a visão como canal de aprendizado.

- **Theory** (13 trilhas): Color · Sound · Interplay/**Spectrum** · Rhythm · **Notes** · Intervals ·
  Chords · Scales · Harmony · Melody · Composition · Synthesis · Glossary.
- **Practice** (dezenas de instrumentos interativos): **Circle** (o disco de notas coloridas),
  Keyboard, Pitch, Chords, Scales, **Chroma**, **MIDI/Pitch-roll**, Synthesis, Sequencing, Jam,
  Visuals.
- **Shop** (material impresso/imprimível) · Tutorship · Projects.
- **Recomendações de notação do próprio Chromatone** (`theory/notes/color`): *colorir a pauta
  tradicional com 12 marcadores cromáticos*, usar **pitch-roll / MIDI-roll**, espectrogramas, e a
  **"mão cromática"** (dedo ↔ nota, canal cinestésico).

## 2. O mapa de cor EXATO (confirmado no instrumento "Circle" ao vivo)

O disco de notas do Chromatone pinta cada nota com `hsla(hue,100%,40%)` e coloca **A no topo**,
girando **cromaticamente** (+30°/semitom):

| nota | A | A# | B | C | C# | D | D# | E | F | F# | G | G# |
|------|---|----|---|---|----|---|----|---|---|----|---|----|
| hue  | 0 | 30 | 60 | 90 | 120 | 150 | 180 | 210 | 240 | 270 | 300 | 330 |
| hex* | `#cc0000` | `#cc6600` | `#cccc00` | `#66cc00` | `#00cc00` | `#00cc66` | `#00cccc` | `#0066cc` | `#0000cc` | `#6600cc` | `#cc00cc` | `#cc0066` |

\* base `hsl(h,100%,40%)`. **Fórmula:** `chromaHue(pc) = ((pc + 3) mod 12) · 30`  (pc: C=0)
— equivale a ancorar **A = 0° (vermelho)** e somar 30° por semitom subindo.

**Origem (por que A = vermelho):** dobrando A=440 Hz até a faixa da luz visível, A cai no
**vermelho-alaranjado**, C no **verde**, E no **azul** — daí o padrão físico. As pétalas do disco
ainda codificam as teclas pretas/brancas do piano (A#, C#, D#, F#, G# escuras).

## 3. A decisão de arquitetura: adotar a cor do Chromatone 🔑

Hoje o app colore por **ciclo de quintas** (`COF`, C=vermelho, semitons vizinhos com matizes bem
distantes). O Chromatone usa **ordem cromática** (semitons vizinhos = matizes vizinhos, A=vermelho).
São mapas **diferentes** para a mesma nota.

**Recomendação: adotar o mapa cromático do Chromatone** como **única fonte de cor** do app
(`chromaHue(pc)`), usada pelo Lego **e** pelas notas da pauta. Motivos:

1. **É o padrão que você escolheu** — alinha com um ecossistema aberto e crescente (mesma cor no
   nosso app e em qualquer ferramenta/impresso Chromatone).
2. **A cor passa a reforçar o contorno.** Como somos **melodia de uma voz só** (cumbia), matiz
   cromático = ordem de altura: subir a escala vira um arco-íris que **acompanha a subida da
   melodia**. O ciclo de quintas *brigava* com o contorno (nota vizinha, cor oposta). Isso é MER
   "restringindo" no bom sentido — dois canais dizendo a mesma altura.
3. **Troca de baixo risco:** é **uma função só** (`chromaHue`) trocando `COF`. Reversível.

*Ajuste fino:* mantemos a **matiz** (o padrão), mas podemos suavizar S/L no papel (ex.: `S≈70%
L≈45%`) para as bolinhas de nota não ficarem neon sobre `#f7f4ee`. Matiz = padrão; S/L =
apresentação. O ponto de ancoragem (A=vermelho) é **uma constante** — se você preferir C=vermelho,
troca-se um número.

## 4. O que a pesquisa pedagógica manda (não muda, reforça)

- **Múltiplas Representações (Ainsworth/DeFT):** representações múltiplas *complementam*,
  *restringem* e *constroem* — **mas** o risco é **split-attention**. → canal novo só vale
  **INTEGRADO**: sincronizado no tempo + **uma língua de cor só** (agora, a do Chromatone).
- **Figurenotes / notação colorida:** cor por classe de altura ajuda iniciantes, **mas** quem
  aprende *só* na cor lê pior a pauta preta. → cor é **andaime FADEÁVEL**; a **pauta continua sendo
  a verdade**.
- **Soundslice / Music Animation Machine:** padrão-ouro = **notação sincronizada**, playhead suave,
  vista contínua. O pitch-roll colorido do Chromatone é exatamente esse casamento som↔imagem.

## 5. Os 5 blocos (~1h cada, cada um shippável e testado 9/9)

### 1 · A cor Chromatone: uma língua de cor só (pauta ↔ Lego) 🎨 (1h)
Criar `chromaHue(pc)` (mapa cromático acima) como **fonte única** e (a) recolorir o **Lego** e (b)
colorir os **noteheads** da pauta do estudo com a mesma matiz (`add_classes:true` + pós-render em
`.abcjs-note`). Toggle **"🎨 cor"** (padrão ligado, **desligável** — respeita o "decorar-cor").
*Efeito:* pauta, Lego e todo o ecossistema Chromatone falam **uma cor só**, e a cor passa a
**reforçar o contorno**.

### 2 · O pitch-roll colorido — o canal-assinatura do Chromatone 📊 (1h)
No passo Frase, abaixo da pauta, um **pitch-roll** (tempo × altura, blocos coloridos por
`chromaHue`) que o **cursor percorre junto** com a notação. É o nosso "contorno" **elevado ao
pitch-roll do Chromatone** e colorido — canal que o Chromatone prova funcionar, **alinhado no tempo**
(mata o split-attention).

### 3 · O "Espelho" v1 — sua altura ao vivo no pitch-roll 🪞 (1,5h)
O mic já detecta sua altura; desenhar **a SUA linha/ponto** sobre o pitch-roll (bloco 2), em tempo
real, contra o modelo — colorida pela `chromaHue` da nota mais próxima, então **quando você acerta,
sua cor bate com a do bloco-alvo**. Acende verde no encaixe. (A "aposta grande", 1ª versão enxuta.)

### 4 · Legenda + "mão cromática" + modo limpo 🖐️ (1h)
Uma legenda curta amarrando os canais numa língua Chromatone só (**cor = tom · pauta = altura
exata · pitch-roll = gesto + tom · colar = ritmo**); um toque de **"mão cromática"** (mostrar a cor
da nota na dica de pistão/dedilhado — canal cinestésico que o Chromatone recomenda); e o mestre
**"modo limpo"** que desliga os canais extras (volta à pauta preta pura), pro andaime sumir quando o
aluno cresce. Documentar a base (Chromatone + MER) em `docs/`.

### 5 · Reserva / polish (0,5h)
Rolagem contínua estilo Soundslice **se** sobrar tempo; um link **"sobre as cores (padrão
Chromatone)"** creditando chromatone.center; senão, folga pra testes/screenshots.

## 6. Sequência & verificação
1 → 2 → 3 → 4 (→5). Cada bloco: build (`build_cumbia.py` + `build_site.py`), **9/9** do suite +
`pitch-core`, screenshot, commit, push, `curl` no ar. A **pauta nunca sai** — só ganha companhia
coordenada, na cor-padrão do Chromatone, e desligável.

## 7. Fontes
- **Chromatone** — chromatone.center: `/theory/notes/color`, `/theory/interplay/spectrum`,
  instrumento **Circle** (mapa `hsl(h,100%,40%)`, A=0°, +30°/semitom, confirmado no SVG ao vivo);
  código aberto em github.com/chromatone (Vue).
- Ainsworth, *DeFT: learning with multiple representations*. · *Multiple Representations Principle*
  (Cambridge Handbook of Multimedia Learning).
- *Colored music notation* (Wikipedia) · **Figurenotes** · Ashley Danyew, *Teaching music literacy
  using color*.
- **Soundslice** — *living sheet music* / auto-scroll · **Music Animation Machine**.
- **abcjs** — `add_classes`, colorir noteheads (`.abcjs-note`).
