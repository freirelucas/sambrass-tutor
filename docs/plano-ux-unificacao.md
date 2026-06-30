# Plano — Unificação da UX + melhorias (banho de loja, parte 2)

## Estado atual (o que já foi unificado)
- **Tema:** todas as telas principais no **papel claro** (#f7f4ee / marca #8a2331 / verde
  #2f7d5b): index/trilha/banco, **estudo** (era escuro), **blocos**, **afinar**, **respira**.
- **Voltar:** "‹ voltar" no topo-esquerdo em todas.
- **Stories → acordeão** (instrução colapsada). **Lego** unificado. **Explainer** ("como é feito?").
- **Aquecimento = Cichowicz** (nó da trilha + aba Aquecer).

## O que ainda destoa / pode melhorar
1. **`revisar.html` ainda é escuro** (último outlier de tema — é ferramenta de revisão).
2. **Tokens e componentes duplicados** por página (cada HTML tem seu `:root` e suas classes
   `.card`/`.toggle`/`.badge`). Mesmos valores hoje, mas **vão divergir de novo** sem um
   sistema compartilhado.
3. **estudo muito longo / denso:** ~12 toggles na fileira de controles; o passo Praticar é
   comprido. Falta **foco no primário** (tocar/praticar/ouvir) e esconder o avançado.
4. **Tipografia** levemente inconsistente (serif de título vs sans de UI entre páginas).
5. **blocos vista Legos** é uma rolagem longa (15 cumbias × peças).

## Eixos (ordenados por impacto × risco)

### A · `ui.css` — um sistema só (tokens + componentes)
Extrair **um** arquivo `app/ui.css` com os **tokens canônicos** (papel, tinta, marca, verde,
linha, sombra, raio, fontes) + **componentes base** reusáveis: `.ui-back` (voltar padrão),
`.acc` (acordeão), e tokens que as páginas já usam. Linkar em **todas** as páginas. Baixo risco
(os valores já batem): trava o sistema e mata a divergência futura. *Entrega: ui.css + links.*

### B · estudo — densidade e foco na função 🔴
Agrupar os controles: **primário sempre visível** (▶ Tocar com o tutor · ▶ praticar · 🎤 ouvir ·
andamento), e o **avançado colapsado** atrás de um "⚙ mais opções" (em concerto · 8ª abaixo ·
peça inteira · loop · rampa · esperar · com a banda + volume). Menos rolagem, mais "ligado à
função". Mantém todos os controles no DOM (testes verdes). *Entrega: controles em disclosure.*

### C · `revisar.html` → claro
Re-tematizar a última tela escura pro papel do app (mesmos tokens). *Entrega: revisar no claro.*

### D · Polimento de consistência
Header/voltar idênticos, badges/cards/botões alinhados ao `ui.css`, tipografia (um par
serif+sans), alvos de toque ≥44px (Samsung). *Entrega: micro-ajustes por página.*

## Sequência
A (sistema) → B (estudo, o mais sentido) → C (revisar) → D (polimento). Cada um testado
(9/9 verde), com screenshot, commitado e empurrado pro main. Aviso só no fim.

## Fora de escopo desta rodada
Refatorar a fidelidade dos sambas (dados), fechar os 3 rascunhos de cumbia (precisa do áudio),
e reescrever a IA da exploração (blocos) — ficam para depois.
