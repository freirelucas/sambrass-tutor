# Diagrama da estrutura — `estrutura.html`

Mapa interativo de como o repositório se encaixa: o que roda no CI, o que chega no celular, e
onde fica a fronteira entre os dois. Abra `estrutura.html` em qualquer navegador — é um arquivo
só, sem dependência, com tema claro/escuro, zoom e links para o código-fonte de cada caixa.

## De onde vem

Gerado com **[Archify](https://github.com/tt-a1i/archify)** (MIT, © tt-a1i), que valida o
diagrama em quatro portões antes de entregar: schema, delivery, checagem estrita de proveniência
e um gate de navegador real. O HTML embute o visualizador do Archify — daí os ~800 KB.

`estrutura.candidate.json` é a **fonte** do diagrama: caixas, setas, evidências de código e
layout. É ele que se edita, não o HTML.

## Regenerar

```bash
# fixa o commit atual como evidência (o Archify confere os caminhos citados)
node <caminho-do-archify>/bin/archify.mjs finalize architecture \
  docs/arquitetura/estrutura.candidate.json docs/arquitetura/estrutura.html \
  --repo-root . --quality showcase --json
```

Se o gate de navegador reclamar que não achou Chrome, aponte `ARCHIFY_CHROME` para um Chromium.

## Honestidade sobre o que ele mostra

- Cada caixa carrega **evidência de linha real** (`app/app.js:19`, `tools/check_contrato.py:80`…),
  presa ao commit `1de3381`. Se o código andar muito, as linhas envelhecem — regenere.
- A interface do visualizador está **em inglês**: o pt-BR não tem catálogo embutido no Archify.
  Foram traduzidas as 21 mensagens que nomeiam a semântica *deste* diagrama (legenda, tipos de
  caixa); as outras 465 caem para o inglês.
- O diagrama é um **mapa de módulos**, não a jornada do usuário: mostra como o repo se organiza,
  não a sequência de telas que o trompetista percorre.
