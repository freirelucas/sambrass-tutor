# Curso interativo — como este app funciona por dentro

Cinco módulos que ensinam o repositório a quem não lê código: o caminho de um toque na tela,
o elenco de arquivos, a fronteira entre o que roda no CI e o que roda no celular, o acoplamento
por nome de arquivo, e um mapa de sintoma → causa para quando quebra.

Tem animação de fluxo, conversa em grupo entre os componentes, blocos de código lado a lado com
a tradução em português, 12 perguntas e glossário por cima de cada termo técnico.

## ⚠️ Faltam dois arquivos aqui — e isso é de propósito

`styles.css` e `main.js` vêm do gerador
**[codebase-to-course](https://github.com/zarazhangrui/codebase-to-course)**, que **não publica
arquivo de licença**. Sem licença, o padrão é "todos os direitos reservados": copiar 1.693 linhas
dele para dentro de um repositório público é redistribuição sem permissão expressa.

Então eles ficam fora do versionamento (veja o `.gitignore`). O que está aqui é **autoral**: os
cinco módulos, que falam do seu código.

## Para montar e abrir

```bash
cd docs/curso
git clone --depth 1 https://github.com/zarazhangrui/codebase-to-course /tmp/c2c
cp /tmp/c2c/references/styles.css /tmp/c2c/references/main.js .
bash build.sh          # concatena _base + modules/*.html + _footer → index.html
open index.html        # (ou xdg-open / start)
```

Se quiser os dois arquivos versionados junto, é decisão sua — basta tirar as duas linhas do
`.gitignore`. A rigor, o uso documentado do gerador é exatamente copiá-los para a saída.

## Mexer no conteúdo

Cada módulo é um arquivo solto em `modules/`, contendo só o `<section class="module">`. Edite,
rode `bash build.sh` de novo e pronto — nada de build complicado.

Três localizações foram feitas à mão no `main.js` (fora do versionamento, refaça se recopiar):
`Exactly!` → `Isso!`, `Not quite.` → `Quase.`, `messages` → `mensagens`, `Step` → `Passo`.

## O que foi verificado

Renderizado em Chromium a 1440px e 390px: zero erro de console, zero overflow horizontal, e os
elementos interativos foram **acionados de verdade** — a animação de fluxo avança e acende o ator,
o chat revela mensagem por mensagem, o quiz marca certa/errada e abre a explicação, e o tooltip
de glossário aparece no hover.
