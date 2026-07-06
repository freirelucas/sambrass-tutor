# Plano de 5h — "Manter a pauta, enriquecer os canais de representação"

## O que a pesquisa diz (e como muda o desenho)

- **Múltiplas Representações Externas (Ainsworth, DeFT):** representações múltiplas *complementam*
  (cada uma carrega algo), *restringem* (uma ancora a leitura da outra) e *constroem* entendimento
  mais profundo. **MAS** o risco é o **split-attention**: se as representações ficam soltas, o aluno
  gasta carga cognitiva **relacionando-as** em vez de aprender. → **Canal novo só vale se for
  INTEGRADO** (sincronizado no tempo + **uma língua visual só**).
- **Notação colorida / Figurenotes:** cor por classe de altura ajuda iniciantes e revela acordes;
  **porém** a pesquisa (Rogers 1991 e réplicas) mostra que quem aprende **só** na cor **lê pior a
  pauta preta** (decora a cor, não a nota). → **Cor é andaime FADEÁVEL**, complemento da pauta,
  nunca substituto. A pauta continua sendo a verdade.
- **Soundslice / Music Animation Machine ("living sheet music"):** o padrão-ouro é **notação
  sincronizada** com o áudio/rolagem, playhead suave, vista horizontal contínua, mute/solo por
  parte. É a MER "bem integrada": **um só olhar alinhado no tempo**.
- **Viabilidade (abcjs):** com `add_classes:true` (o estudo já usa) cada nota vira `.abcjs-note` no
  SVG — dá pra **colorir notehead por classe de altura** e mover marcadores pós-render. Confirmado.

**Princípio do plano:** a **pauta é a verdade** (os pedagogos e o erudito têm razão). Enriquecemos
com canais **coordenados**, **na mesma língua de cor** (ciclo de quintas, igual ao Lego),
**sincronizados no tempo**, e **desligáveis** (andaime que some) — pra somar sem virar ruído.

## Os 5 blocos (≈1h cada, cada um shippável e testado 9/9)

### 1 · Noteheads coloridos por tom — a ponte pauta ↔ Lego 🎨 (1h)
Colorir cada notehead da partitura do estudo pela **classe de altura**, com **o mesmo matiz do
ciclo de quintas** que já colore o Lego. `add_classes:true` + pós-render em `.abcjs-note`. Toggle
**"🎨 cor nas notas"** (padrão da peça, mas **desligável** — respeita a pesquisa do decorar-cor).
*Efeito:* a pauta e o Lego passam a falar **uma cor só** (Figurenotes + MER integrada).

### 2 · O canal do contorno DENTRO da pauta 📈 (1h)
No passo Frase, abaixo da partitura, uma **fita de contorno** (a linha de altura da melodia) que o
**cursor percorre junto** com a notação — o gesto do Lego trazido pra perto da pauta, **alinhado no
tempo** (mata o split-attention: os dois canais num olhar só).

### 3 · O "Espelho" v1 — sua altura ao vivo sobre o modelo 🪞 (1,5h)
O mic já detecta sua altura; desenhar **a SUA linha** sobre a fita de contorno (item 2) **em tempo
real**, contra a linha-modelo — o canal do *som que você produz* vira **imagem**. Acende verde quando
encaixa. (A "aposta grande" do painel, em 1ª versão enxuta.)

### 4 · Uma língua só (legenda) + andaime fadeável 🔤 (1h)
Uma legenda curta amarrando os canais — **cor = tom · pauta = altura exata · contorno = gesto ·
colar = ritmo** — e um **mestre "modo limpo"** que desliga os canais extras (volta à pauta pura),
pro andaime sumir quando o aluno cresce. Documentar a base de pesquisa em `docs/`.

### 5 · Reserva/《polish》 (0,5h)
Rolagem/vista contínua estilo Soundslice **se** sobrar tempo; senão, folga pra testes/screenshots.

## Sequência & verificação
1 → 2 → 3 → 4 (→5). Cada bloco: build, **9/9** do suite + `pitch-core`, screenshot, commit, push,
`curl` no ar. A **pauta nunca sai** — só ganha companhia coordenada e desligável.

## Fontes da pesquisa
- Ainsworth, *DeFT: A conceptual framework for learning with multiple representations* (ScienceDirect).
- *The Multiple Representations Principle in Multimedia Learning* (Cambridge Handbook).
- *Colored music notation* (Wikipedia) · **Figurenotes** (figurenotes.org) · Ashley Danyew, *Teaching
  music literacy using color*.
- **Soundslice** — *Create living sheet music* / features / auto-scroll.
- **abcjs** — RenderAbc `add_classes`, *Classes*, issue #49 (colorir noteheads); projeto `abcjs-colored`.
