# Plano de 5 — "O Lego da Cumbia": consistência visual + funcional

## O arco (vasculhando nossas conversas)

Construímos uma **análise rica e data-driven** das cumbias:
- **`blocos.py` → `blocos.json`**: por peça — **cor** (tônica+modo via Krumhansl-Schmuckler, posição no **ciclo de quintas**), **forma** (contorno, intervalos, salto, **arpejo**, classe), **groove** (onsets/meter — o **colar rítmico**), **riff** (midis/durs) e **células** detectadas.
- **`blocos.html`**: 4 geometrias (Cor=ciclo de quintas · Contorno=cordilheira · Groove=colar euclidiano · Parede de Lego) + Selos + Telar aperiódico.
- **`grafismo.js`**: o **selo** por bloco (matiz=tom · anel/ticks=groove · roseta=contorno).
- Pesquisa de fundo: ciclo de quintas, ritmo euclidiano, Penrose/Fibonacci (Telar), e a lição do Kené/Mapuche (representar com honestidade, não decorar).

## Onde se perdeu (o diagnóstico)

1. **Virou ícone, não função.** O selo é uma **imagem estática** no canto do estudo. A análise *gerou* a imagem, mas a imagem não *faz* nada — não toca, não decompõe, não anima, não conversa com as células da prática.
2. **Inconsistência de tema.** O app é claro (`#7a1f1f`), o `blocos.html` é **escuro** (`#0e0d0c`), o Respira é paper. Três línguas visuais.
3. **Siloed.** As geometrias vivem numa ferramenta à parte (linkada só agora), longe da prática.
4. **Falta o Lego de verdade.** Não existe um **bloco por cumbia** que mostre os **3 trechos que se repetem**, cada um com sua **célula rítmica** e seu **arpejo**.

## A visão

Um **Lego por cumbia**: dentro dela, os **3 trechos que se repetem** viram **peças encaixáveis**; cada peça carrega seu **colar rítmico** (a célula) e seu **arpejo/contorno**; a **cor** vem do ciclo de quintas. **Animado** (pulsa no tempo, a peça atual acende) e **concatenado com a prática** (as peças = as células do "coração"). Uma **linguagem só**, da trilha à prática à exploração.

---

## O plano (5 passos, cada um entregável e encaixando no próximo)

### 1 · Linguagem única (o "kit de Lego" + tema)
Definir o vocabulário visual **uma vez**: cor = matiz do ciclo de quintas · célula = **colar/polígono** (euclidiano) · arpejo/contorno = a **forma** da peça. Re-tematizar o `blocos.html` para o **tema claro do app** (hoje é escuro) e extrair os tokens num `lego-kit` (cores, traços) compartilhado por app/estudo/blocos.
**Entrega:** `blocos.html` no tema do app + tokens do kit. *Fecha a inconsistência (#2).*

### 2 · Decompor a cumbia nos 3 trechos que se repetem
Estender `phrases.py`/`blocos.py` para separar os **3 trechos** da cumbia (pela **forma A/B/C** ou riff+variações), cada um com: células rítmicas, onsets (colar), contorno (midis) e arpejo.
**Entrega:** campo `legos:[{parte, celulas, onsets, contorno, arpejo}]` por cumbia no `blocos.json`. *Cria a matéria do Lego (#4).*

### 3 · O Lego funcional (componente, não ícone)
Evoluir o `grafismo.js` para um componente `lego(cumbia)`: renderiza os **3 trechos como peças encaixáveis**; cada peça mostra o colar rítmico + o arpejo; **clicável → toca aquele trecho**. Substitui o selo estático.
**Entrega:** `lego.js` reusável. *Mata a "iconografia" (#1).*

### 4 · Animação sincronizada com a prática
No estudo, o Lego **anima junto com o playback** (TimingCallbacks do abcjs): o colar pulsa no tempo, a peça do trecho atual acende, o contorno desenha. As peças **são** as células do passo "coração".
**Entrega:** o Lego sincronizado nos passos Coração/Frase do estudo. *"Concatenado com as células" (a visão).*

### 5 · Integração na jornada (o arremate)
O **mesmo Lego** em toda parte: **mini no nó da trilha** (no lugar do selo), **completo no estudo** (coração = as peças), e o `blocos.html` vira "**explorar todos os Legos**" na mesma língua. Uma identidade só.
**Entrega:** selo→Lego em trilha/estudo/exploração; consistência visual fechada. *O arremate.*

---

## Sequência sugerida
1 (tema) → 2 (dados dos 3 trechos) → 3 (componente) → 4 (animação na prática) → 5 (espalhar).
Cada passo é testável e shippável sozinho; o app nunca quebra entre eles.
