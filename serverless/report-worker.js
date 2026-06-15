// Cloudflare Worker — recebe um relato do beta (sem login) e cria uma issue no repo.
// Deploy: ver serverless/README.md. Segredo necessário: GITHUB_TOKEN (PAT fine-grained, Issues:write).
const REPO = 'freirelucas/sambrass-tutor';
const ALLOW_ORIGIN = 'https://freirelucas.github.io';   // ajuste p/ a origem do seu GitHub Pages
const LABEL = 'beta';

export default {
  async fetch(req, env) {
    const cors = {
      'Access-Control-Allow-Origin': ALLOW_ORIGIN,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (req.method !== 'POST') return json({ error: 'use POST' }, 405, cors);

    let d;
    try { d = await req.json(); } catch { return json({ error: 'json inválido' }, 400, cors); }
    if (d.website) return json({ ok: true }, 200, cors);          // honeypot: bot preencheu → finge sucesso
    const msg = (d.message || '').toString().trim();
    if (msg.length < 3) return json({ error: 'mensagem vazia' }, 400, cors);
    if (msg.length > 4000) return json({ error: 'mensagem longa demais' }, 400, cors);

    const piece = (d.piece || '').toString().slice(0, 60);
    const screen = (d.screen || '').toString().slice(0, 24);
    const contact = (d.contact || '').toString().slice(0, 140);
    const ua = (d.ua || '').toString().slice(0, 300);
    const title = `[beta] ${piece ? piece + ': ' : ''}${msg.slice(0, 60)}`.replace(/\s+/g, ' ').slice(0, 120);
    const body = [
      piece ? `**Peça:** ${piece}` : '',
      screen ? `**Tela:** ${screen}` : '',
      '', '**Relato:**', msg, '',
      contact ? `**Contato:** ${contact}` : '',
      '---', `_via app (sem login) · ${ua}_`,
    ].filter(x => x !== '').join('\n');

    const headers = {
      'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github+json',
      'User-Agent': 'sambrass-report-worker',
      'Content-Type': 'application/json',
    };
    // garante o label (ignora se já existe), depois cria a issue; se falhar com label, tenta sem.
    await fetch(`https://api.github.com/repos/${REPO}/labels`, {
      method: 'POST', headers, body: JSON.stringify({ name: LABEL, color: 'd4a017', description: 'feedback do beta' }),
    }).catch(() => {});
    let r = await fetch(`https://api.github.com/repos/${REPO}/issues`, {
      method: 'POST', headers, body: JSON.stringify({ title, body, labels: [LABEL] }),
    });
    if (!r.ok) r = await fetch(`https://api.github.com/repos/${REPO}/issues`, {
      method: 'POST', headers, body: JSON.stringify({ title, body }),
    });
    if (!r.ok) return json({ error: 'falha ao criar issue', status: r.status }, 502, cors);
    const issue = await r.json();
    return json({ ok: true, url: issue.html_url, number: issue.number }, 200, cors);
  },
};

function json(obj, status, cors) {
  return new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json', ...cors } });
}
