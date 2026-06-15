# Relato do beta sem login (Cloudflare Worker)

O app já reporta erros pelo **link do GitHub** (o tester confirma logado). Para um
envio **sem login** (1 toque), este Worker recebe o relato e cria a issue usando
um token guardado no servidor — o token **nunca** vai para o navegador.

## Por que precisa de um servidor?
Criar issue como você exige um token. Token no cliente = qualquer um o lê. Então
um endpoint mínimo (este Worker) guarda o segredo e cria a issue por você.

## Setup (~5 min)

1. **Token** — GitHub → Settings → Developer settings → **Fine-grained tokens** →
   *Generate new token*:
   - *Repository access*: só `freirelucas/sambrass-tutor`
   - *Permissions* → **Issues: Read and write** (só isso)
   - Copie o token.

2. **Deploy do Worker**
   ```bash
   npm i -g wrangler
   cd serverless
   wrangler login
   wrangler secret put GITHUB_TOKEN      # cole o token quando pedir
   # ajuste ALLOW_ORIGIN em report-worker.js para a sua origem do Pages
   wrangler deploy                        # imprime a URL https://sambrass-report.<conta>.workers.dev
   ```

3. **Ligar no app** — em `app/config.js`:
   ```js
   window.REPORT_ENDPOINT = 'https://sambrass-report.<conta>.workers.dev';
   ```
   Commit + push (o Pages publica). Pronto: o "enviar" do app passa a criar a
   issue direto, sem login.

> Sem o passo 3, o app continua funcionando — o "enviar" cai no link do GitHub.

## Segurança / abuso
- Token **mínimo** (só Issues, só este repo) e como **segredo** do Worker.
- `ALLOW_ORIGIN` restringe a origem (reduz uso casual; cabeçalho é falsificável
  fora do navegador — não é blindagem).
- **Honeypot** (campo `website`) descarta bots simples.
- Limites de tamanho no relato.
- Use o **Rate Limiting** grátis da Cloudflare (Security → WAF) na rota do Worker.
- Se spammarem: rotacione o token (revoga o antigo) ou pause o Worker.

## Alternativas
Mesma lógica (um `fetch` que chama a API do GitHub com o token em segredo) roda em
**Vercel** ou **Netlify Functions** — basta portar o handler. Para algo mais
robusto que um PAT (sem expiração, escopo por instalação), use um **GitHub App**.
