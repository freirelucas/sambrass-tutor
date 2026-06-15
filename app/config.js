'use strict';
/* Config + util de relato do beta, compartilhado entre index.html e estudo.html.
 * Sem REPORT_ENDPOINT definido: o "enviar" abre o GitHub (com login) já preenchido.
 * Com REPORT_ENDPOINT (um Worker — ver serverless/): posta direto e cria a issue SEM login. */
window.REPORT_REPO = 'freirelucas/sambrass-tutor';
// OPÇÃO MAIS SIMPLES (sem servidor, sem login): cole a URL do seu Google Form / Tally.
// O botão "reportar" abre o form já pré-preenchido com a peça/tela. Ver docs/feedback-form.md.
window.REPORT_FORM_URL = '';
window.REPORT_FORM_FIELDS = {};   // Google Forms (opcional) p/ pré-preencher: { piece:'entry.123', screen:'entry.456' }
// alternativa: endpoint (Worker/Formsubmit) p/ o form in-app. Vazio = link do GitHub (com login).
window.REPORT_ENDPOINT = '';

function buildFormUrl(ctx) {
  const base = window.REPORT_FORM_URL, map = window.REPORT_FORM_FIELDS || {}, params = [];
  const add = (k, v) => { if (v) params.push(encodeURIComponent(k) + '=' + encodeURIComponent(v)); };
  add(map.piece || 'peca', ctx.piece || ''); add(map.screen || 'tela', ctx.screen || '');
  if (map.piece || map.screen) params.push('usp=pp_url');   // Google Forms prefill
  return params.length ? base + (base.includes('?') ? '&' : '?') + params.join('&') : base;
}
window.reportarBeta = function (ctx) {
  ctx = ctx || {};
  if (window.REPORT_FORM_URL) { window.open(buildFormUrl(ctx), '_blank', 'noopener'); return; }   // Google Forms / Tally
  const ghTitle = `[beta] ${ctx.piece ? ctx.piece + ': ' : ''}`;
  const ghBody = `**Peça:** ${ctx.piece || '—'}\n**Tela:** ${ctx.screen || '—'}\n\n**O que aconteceu?**\n\n**O que era esperado?**\n\n**Aparelho/navegador:** ${navigator.userAgent}`;
  const ghUrl = `https://github.com/${window.REPORT_REPO}/issues/new?labels=beta&title=${encodeURIComponent(ghTitle)}&body=${encodeURIComponent(ghBody)}`;

  if (!document.getElementById('rep-style')) {
    const s = document.createElement('style'); s.id = 'rep-style';
    s.textContent = `.rep-ov{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;padding:18px}
.rep-card{background:#fff;color:#1a1a1a;border-radius:14px;padding:18px;max-width:430px;width:100%;box-shadow:0 24px 64px rgba(0,0,0,.45);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.rep-card h3{margin:0 0 4px;font-size:17px}.rep-sub{margin:0 0 12px;font-size:12.5px;color:#777}
.rep-card textarea,.rep-card input{width:100%;border:1px solid #ddd;border-radius:9px;padding:10px 12px;font:inherit;font-size:15px;margin-bottom:9px}
.rep-card textarea{resize:vertical}.rep-hp{position:absolute!important;left:-9999px;width:1px;height:1px}
.rep-row{display:flex;gap:8px;justify-content:flex-end}
.rep-row button{min-height:46px;padding:0 18px;border-radius:11px;border:1px solid #ddd;background:#f2f2f2;font:inherit;font-weight:700;cursor:pointer}
.rep-send{background:#7a1f1f;border-color:#7a1f1f;color:#fff}
.rep-status{font-size:12.5px;color:#555;margin:9px 0 0;min-height:16px}
.rep-status a,.rep-gh{color:#7a1f1f}.rep-gh{display:inline-block;margin-top:10px;font-size:12px;text-decoration:none}`;
    document.head.appendChild(s);
  }

  const el = document.createElement('div'); el.className = 'rep-ov';
  el.innerHTML = `<div class="rep-card" role="dialog" aria-modal="true">
      <h3>Reportar erro / sugestão</h3>
      <p class="rep-sub">${ctx.piece ? 'Peça <b>' + ctx.piece + '</b> · ' : ''}vai direto pro repositório${window.REPORT_ENDPOINT ? ' — sem login' : ''}.</p>
      <textarea id="rep-msg" rows="4" placeholder="O que aconteceu? (ex.: o tutor marcou vermelho no compasso 5 mas eu acertei)"></textarea>
      <input id="rep-contact" placeholder="contato p/ resposta (opcional)">
      <input id="rep-website" class="rep-hp" tabindex="-1" autocomplete="off" aria-hidden="true" placeholder="não preencha">
      <div class="rep-row"><button class="rep-cancel" id="rep-cancel">cancelar</button><button class="rep-send" id="rep-send">enviar</button></div>
      <p class="rep-status" id="rep-status"></p>
      <a class="rep-gh" href="${ghUrl}" target="_blank" rel="noopener">ou abrir no GitHub (com login) ›</a>
    </div>`;
  document.body.appendChild(el);
  const close = () => el.remove();
  const $r = s => el.querySelector(s);
  el.addEventListener('click', e => { if (e.target === el) close(); });
  $r('#rep-cancel').onclick = close;
  $r('#rep-send').onclick = async () => {
    const msg = $r('#rep-msg').value.trim(), st = $r('#rep-status');
    if (msg.length < 3) { st.textContent = 'escreva o que aconteceu.'; return; }
    if (!window.REPORT_ENDPOINT) { window.open(ghUrl, '_blank', 'noopener'); close(); return; }
    st.textContent = 'enviando…'; $r('#rep-send').disabled = true;
    try {
      const r = await fetch(window.REPORT_ENDPOINT, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, piece: ctx.piece || '', screen: ctx.screen || '', contact: $r('#rep-contact').value.trim(), website: $r('#rep-website').value, ua: navigator.userAgent })
      });
      const j = await r.json().catch(() => ({}));
      if (r.ok && j.ok) { st.innerHTML = 'enviado ✓ obrigado!' + (j.url ? ` <a href="${j.url}" target="_blank" rel="noopener">ver</a>` : ''); setTimeout(close, 1800); }
      else { st.innerHTML = 'não consegui enviar — <a href="' + ghUrl + '" target="_blank" rel="noopener">abrir no GitHub</a>'; $r('#rep-send').disabled = false; }
    } catch (e) { st.innerHTML = 'sem rede — <a href="' + ghUrl + '" target="_blank" rel="noopener">abrir no GitHub</a>'; $r('#rep-send').disabled = false; }
  };
  $r('#rep-msg').focus();
};
