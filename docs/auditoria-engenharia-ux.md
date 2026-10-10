# Auditoria de engenharia e UX — 2026-10

Complementa [`auditoria.md`](auditoria.md), que audita a **qualidade dos dados**. Esta
olha o **código e a interface**: o que quebra, o que engana e o que vai quebrar.

**Método.** O app foi *renderizado* num navegador real (Chromium via Playwright), não lido:
8 páginas × 3 viewports (390×844, 768×1024, 1440×900), com console, requisições falhas,
overflow horizontal e alvos de toque medidos; mais um passe de interação dirigindo os
caminhos profundos (as 6 abas, trocar de jornada, metrônomo, Story, microfone no estudo,
as 4 vistas dos blocos, setor do Respira, afinador). Medições reproduzíveis — os números
abaixo saíram dessas rodadas, não de leitura de código.

## Placar

| Eixo | Resultado |
|---|---|
| Erros de JavaScript (8 páginas × 3 viewports) | **0** |
| Requisições falhas não previstas | **0** (os 6 404 são os declarados em `tools/check_contrato.py`) |
| Overflow horizontal | **0** em todas as páginas e viewports |
| `console.log`/`debugger` em produção | **0** |
| Integridade do shell do service worker | **28/28** arquivos existem |
| Alvos de toque abaixo do piso da casa | **6 classes** → corrigidas |
| Páginas sem nenhum teste | **4 de 6** ← maior lacuna |

Veredito: **a base é sólida e o acabamento é bom; o risco está na estrutura do CSS e na
cobertura de teste**, não na correção do que já roda.

---

## 🔴 Corrigido nesta auditoria

### 1. O ▶ das células do Aquecer era um botão sem estilo (34×21 px)

`app.js` emitia `<button class="prog">`, mas `style.css` estiliza `.prog button` — um
**descendente**. A regra nunca se aplicava: o botão ficava sem borda, sem fundo e com
21 px de altura. `superchops.js` já usava a estrutura certa (`<div class="prog"><button>`),
o que mostra que era desvio de um call site, não decisão.

**Mesma família do bug de agosto** (CSS do bloco 🎙 em `style.css`, que `estudo.html` não
carrega). O markup foi alinhado ao CSS. Agora: **40×40 px**, com borda e fundo.

### 2. Dois botões de texto com alvo de toque minúsculo

| controle | antes | depois | onde |
|---|---:|---:|---|
| `.tecbtn` "técnica do lote ›" | **16 px** (×6) | **47 px** efetivos | trilha |
| `.reportar-top` "⚠ reportar" | **25 px** | **44 px** efetivos | cabeçalho, todas as telas |

Crescer a caixa empurraria o cabeçalho e o cabeçalho de lote. A área de toque foi ampliada
com `::after` posicionado, preservando o desenho. Conferido que **não rouba clique dos
vizinhos** (`.planobtn`, `.nlabel`, `.node .inner` seguem recebendo o próprio toque).

> Nota de medição: `getBoundingClientRect()` **não enxerga** a área de `::after`. A
> verificação usa `elementFromPoint` sondando para cima e para baixo. E `html{scroll-behavior:smooth}`
> falseia qualquer medida logo após um `scrollIntoView` — é preciso rolar com `behavior:'instant'`.

### 3. Dois controles 1–2 px abaixo do piso da casa

`.planobtn` (36 px, ×110) e `.nlabel` (37 px, ×110) subiram para **40 px**. O piso de 38 px
tinha sido estabelecido no teste de usabilidade de agosto; estes dois ficaram de fora.

### 4. Virou teste

`tests/tutor.spec.js` ganhou **2 specs** que medem a altura **efetiva** de toque de todo
controle visível na home, nas duas jornadas, a 390 px, e falham abaixo de 38 px. Conferidos
por teste negativo: revertendo a correção do `.tecbtn`, a spec fica vermelha.

---

## 🟠 Achados estruturais (não corrigidos — exigem decisão)

### 5. `style.css` só é carregado pelo `index.html`

Das 6 páginas, **só a home carrega `style.css`**. As outras cinco carregam `ui.css` (o
sistema visual compartilhado) e resolvem o resto num `<style>` interno.

Consequência medida: **157 classes existem só em `style.css`** e são invisíveis fora da home.
Hoje **não há bug vivo** — cada página redefine localmente o que usa (conferido: zero classes
usadas sem estilo em lugar nenhum). Mas é exatamente o mecanismo que produziu o bug de agosto,
e ele continua armado: qualquer reaproveitamento futuro de uma classe da home em outra página
renderiza sem estilo, **em silêncio**.

### 6. 16 classes definidas em mais de um lugar — e divergindo

`.card` existe **4 vezes**, com valores diferentes:

| onde | fundo | raio | padding |
|---|---|---:|---:|
| `style.css` | `--card` | 14 px | 16 px |
| `blocos.html` | `--pane` | 12 px | 8 px |
| `afinar.html` | `--card` | 16 px | 18 px |
| `revisar.html` | `--pane` | 16 px | 16 px |

Também `.wrap` (5 lugares), `.prog` (3), `.hint` (3). O cabeçalho do `ui.css` diz ser "a
fonte canônica, uma só" — na prática o cartão do app tem quatro aparências. Os tokens
divergem pouco (`--sombra` .07 vs .08, `--card` `#fff` vs `#ffffff`); o `--warm` do Respira
é outra cor de propósito, tema próprio.

**Sugestão:** promover para `ui.css` o punhado que já é comum (`.card`, `.wrap`, `.prog`,
`.btnrow`, `.meta`, `.sec`) e apagar as cópias — é a continuação natural do trabalho de
unificação que `ui.css` começou, e fecha o 5 e o 6 de uma vez.

### 7. Quatro páginas sem nenhum teste

| página | linhas de JS embutido | specs |
|---|---:|---:|
| `blocos.html` | 356 | **0** |
| `respira.html` | 123 | **0** |
| `revisar.html` | 98 | **0** |
| `afinar.html` | 59 | **0** |

São 636 linhas de lógica sem rede. Esta auditoria dirigiu as quatro à mão e elas funcionam,
mas nada impede uma regressão silenciosa amanhã. O barato aqui é um *smoke test* por página:
carrega, sem erro de console, o controle principal responde.

### 8. Offline incompleto

`afinar.html`, `blocos.html`, `respira.html` e `revisar.html` estão **fora do SHELL** do
service worker. Como ele é network-first com cache de primeira visita, elas funcionam offline
**só depois de visitadas uma vez**. Instalar a PWA e abrir "Respira" sem rede falha. Decisão
defensável (o Respira depende de 10 `.mp4` que também não estão no cache), mas hoje é
implícita — vale escolher: entram no shell, ou o app avisa.

---

## 🟡 Menor

9. **13,8 MB de zip versionado.** `sambrass_course (1).zip` está rastreado — o `(1)` no nome
   denuncia download de navegador. Com o PDF de 23,5 MB, são **37 MB** num repo cujo código
   todo tem ~10 mil linhas. O `.gitignore` já exclui o material *extraído*; o zip escapou.
   Tirar do histórico é destrutivo — fica como decisão sua.
10. **`docs/auditoria.md` está defasado:** fala em "125 peças = 110 sambrass + 15 cumbias";
    hoje são 126 e 16. É gerado por `content/curadoria/auditoria.py` — basta re-rodar.
    Os mesmos números velhos aparecem em `plano-ux-unificacao.md` e `ux-simulacao.md`.
11. **Seletor de jornada a 38 px** — exatamente no piso, não abaixo. Fica como está.

---

## O que foi verificado e o que não foi

**Verificado em navegador:** as 6 páginas em 3 viewports; as 6 abas da home; troca de
jornada; metrônomo (iniciar/groove/parar); Story com acordeão; célula tocando no Aquecer;
filtro do banco; os 3 passos do estudo com microfone falso, praticar e loop; as 4 vistas
dos blocos; setor do Respira com cronômetro; afinador; revisar.

**Não verificado:** áudio real (o soundfont toca, mas ninguém escutou); as 10 gravações da
banda; render de partitura além de "desenhou sem erro"; iOS/Safari real — o teste é Chromium,
e `AudioContext` e `wakeLock` se comportam diferente lá.
