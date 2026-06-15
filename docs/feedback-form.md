# Feedback do beta sem login (Google Forms ou Tally)

O jeito mais simples: o botão **⚠ reportar** abre um formulário externo seu,
já **pré-preenchido** com a peça/tela. O tester não loga em nada; as respostas
caem numa **planilha** sua. Sem servidor, sem token.

## Opção A — Google Forms (recomendada)

1. Crie um form (forms.google.com) com os campos, por exemplo:
   - **Peça** (resposta curta)
   - **Tela** (resposta curta)
   - **O que aconteceu?** (parágrafo)
   - **O que era esperado?** (parágrafo)
   - **Contato** (opcional)
2. Em **Enviar → 🔗 (link)**, copie a URL (`https://docs.google.com/forms/d/e/XXXX/viewform`).
3. Cole em `app/config.js`:
   ```js
   window.REPORT_FORM_URL = 'https://docs.google.com/forms/d/e/XXXX/viewform';
   ```
4. **(Opcional) pré-preencher Peça/Tela**: no form, menu **⋮ → Receber link
   pré-preenchido**, preencha qualquer coisa nos campos Peça e Tela e clique
   *Obter link*. Na URL gerada aparecem `entry.NÚMERO=...` — copie os dois números:
   ```js
   window.REPORT_FORM_FIELDS = { piece: 'entry.1111111111', screen: 'entry.2222222222' };
   ```
5. Commit + push. Respostas: no form, aba **Respostas → Planilha**.

## Opção B — Tally (visual melhor, prefill por nome)

1. Crie o form (tally.so) e nomeie os campos com as **keys** `peca` e `tela`
   (Tally: *Field settings → key*).
2. Cole a URL pública em `window.REPORT_FORM_URL`. Deixe `REPORT_FORM_FIELDS = {}`
   — o app já manda `?peca=...&tela=...`, que o Tally usa para pré-preencher.
3. Respostas no painel do Tally (ou conecte a uma planilha).

## Como o app usa
`reportarBeta()` (em `app/config.js`) detecta `REPORT_FORM_URL` e abre o form com
os parâmetros de contexto. Sem essa URL, cai no fluxo do GitHub (com login). Nada
quebra enquanto você não configura.
