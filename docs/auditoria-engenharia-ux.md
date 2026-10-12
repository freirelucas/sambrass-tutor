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

## ✅ Resolvido na rodada de melhorias (2026-10-12)

Os achados 5 a 10 foram endereçados. **Um deles mudou de solução no meio do caminho** e vale
registrar por quê — está logo abaixo, no 5.

## 🟠 Achados estruturais

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

**✅ Resolvido — mas não como estava sugerido aqui.** A promoção para `ui.css` foi *tentada*
e **revertida**: mover as 15 regras compartilhadas mudou 12 das 22 telas, e no `estudo.html`
chegou a introduzir **overflow horizontal** (390 px → 1047 px de largura no celular). O motivo
é estrutural e vale guardar: **preencher a lacuna necessariamente muda as páginas que viviam
sem aquele estilo.** Não existe unificação "de graça" aqui — ou se aceita o redesenho das
telas, ou não se unifica.

Como a decisão foi *não mexer na aparência*, o objetivo real (que o bug de agosto não se
repita) foi entregue por outro caminho, sem mover um pixel: **`tools/check_css.py`**, que roda
no CI e falha quando uma página usa classe que nenhuma folha carregada por ela define. Junta
os `<link>`, o `<style>` interno **e o CSS que os scripts da página injetam em runtime**
(`config.js` e `explica.js` criam `<style>` na marra — sem isso o checador acusaria 12
falso-positivos). As 5 classes que legitimamente não têm regra — ganchos de JS e marcadores —
estão **declaradas com motivo**, e a declaração se autolimpa: se a classe sumir do código, o
checador falha pedindo pra tirar a linha.

Conferido por teste negativo: fazer `revisar.html` usar `.acao` (classe que só existe no
`style.css`, que ela não carrega) deixa o CI vermelho — que é exatamente o bug de agosto.

A duplicação do `.card` em 4 lugares **continua de pé**, por escolha. Ela agora é visível e
inofensiva: nenhuma página pode acabar sem estilo sem o CI reclamar.

### 7. Quatro páginas sem nenhum teste

| página | linhas de JS embutido | specs |
|---|---:|---:|
| `blocos.html` | 356 | **0** |
| `respira.html` | 123 | **0** |
| `revisar.html` | 98 | **0** |
| `afinar.html` | 59 | **0** |

São 636 linhas de lógica sem rede.

**✅ Resolvido:** quatro *smoke tests*, um por página — carrega, zero exceção, o conteúdo que
vem de dado popula, e o controle principal responde. O do `blocos.html` cobre de quebra um
**caminho preguiçoso** que nada exercitava: os 16 Legos das cumbias vêm na carga, mas os 110
dos sambas só existem depois de clicar "▸ mostrar os Legos dos sambas".

Todos conferidos por **teste negativo** — e isso pegou um erro meu: a primeira versão da spec
do `blocos` usava um seletor com `OR` (`#legos-samb .lego, #legos-cumb .lego`), então matar um
dos dois lados ainda passava. Só a tentativa de quebrar de propósito revelou que o teste não
testava nada.

### 8. Offline incompleto

`afinar.html`, `blocos.html`, `respira.html` e `revisar.html` estão **fora do SHELL** do
service worker. Como ele é network-first com cache de primeira visita, elas funcionam offline
**só depois de visitadas uma vez**. Instalar a PWA e abrir "Respira" sem rede falha. **✅ Resolvido:** `afinar.html`, `blocos.html` e `revisar.html` entraram no SHELL (cache `v23`)
e passam a abrir offline sem visita prévia. O **Respira ficou fora de propósito**: a página é
pequena, mas depende de 10 `.mp4` (~25 MB) impossíveis de pré-cachear — abrir offline sem os
play-alongs seria pior que não abrir.

Como a própria página não carrega offline, o aviso foi para **onde o link está**: o cartão do
Respira na aba *Aquecer* mostra, só quando não há conexão, que aquela tela precisa de internet.
Reage nos dois sentidos (conferido ligando e desligando a rede com a tela aberta).

---

## 🟡 Menor

9. **✅ 13,8 MB de zip, destrastreado.** `sambrass_course (1).zip` saiu do versionamento
   (`git rm --cached` + `.gitignore`) — o conteúdo já vive em `content/`. Some de qualquer
   clone novo; o histórico segue carregando os bytes, o que é reversível e não reescreve
   `main`. O `.gitignore` registra como recuperar: `git show <commit>:'sambrass_course (1).zip'`.
10. **✅ `docs/auditoria.md` sincronizado** com o snapshot fresco: 126 peças, 13 conferidas
    (10,3%), 126 blocos. E foi corrigida uma afirmação errada no cabeçalho dele: dizia ser
    "gerada por `auditoria.py`", mas o script só escreve o JSON — **o texto é mantido à mão**,
    então re-rodar não atualizava a página. Agora o cabeçalho diz isso.
    As menções a "15 cumbias" em `plano-ux-unificacao.md` e `ux-simulacao.md` **ficam como
    estão**: são documentos de planejamento descrevendo o estado da época, não placar vivo —
    reescrevê-los falsearia o histórico.
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
