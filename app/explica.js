// explica.js — "como esse desenho é feito?": um modal reusável que mostra que os
// gráficos do app (Lego, contorno, selo) NÃO são decorativos — saem das notas da peça.
// Uso: carregue <script src="./explica.js"></script> e chame window.explicaDesenho()
// (ex.: ao clicar no selo do hero, ou num botão ⓘ).
(function (root) {
  'use strict';
  var built = false;
  function build() {
    if (built) return; built = true;
    var css =
      '.explica-back{position:fixed;inset:0;background:rgba(28,20,14,.55);backdrop-filter:blur(3px);' +
      'display:flex;align-items:center;justify-content:center;z-index:1000;padding:18px;animation:explica-fade .18s ease}' +
      '.explica-back[hidden]{display:none}' +
      '@keyframes explica-fade{from{opacity:0}to{opacity:1}}' +
      '.explica-card{position:relative;width:100%;max-width:430px;max-height:90vh;overflow:auto;background:#fffdf8;color:#221d18;' +
      'border:1px solid #e7e0d2;border-radius:16px;padding:22px 20px 18px;box-shadow:0 20px 60px rgba(20,15,10,.4);' +
      'font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;animation:explica-rise .22s cubic-bezier(.2,.8,.2,1)}' +
      '@keyframes explica-rise{from{transform:translateY(12px);opacity:0}to{transform:none;opacity:1}}' +
      '.explica-card h3{font-family:"Iowan Old Style",Palatino,Georgia,serif;font-weight:600;font-size:20px;margin:0 0 4px}' +
      '.explica-card p{margin:6px 0;color:#5b5446}' +
      '.explica-x{position:absolute;top:10px;right:10px;width:38px;height:38px;border:none;background:none;font-size:18px;color:#857a68;cursor:pointer;border-radius:10px}' +
      '.explica-x:active{background:#f1ece1}' +
      '.explica-svg{display:block;width:100%;height:auto;margin:12px 0;background:#f7f4ee;border:1px solid #e7e0d2;border-radius:12px}' +
      '.explica-list{list-style:none;margin:8px 0 0;padding:0}' +
      '.explica-list li{position:relative;padding:7px 0 7px 26px;border-top:1px solid #efe9dc;font-size:14px}' +
      '.explica-list li::before{content:"";position:absolute;left:0;top:12px;width:14px;height:14px;border-radius:4px;background:var(--dot,#8a2331)}' +
      '.explica-list b{color:#221d18}' +
      '.explica-foot{font-size:12.5px;color:#857a68;margin-top:12px}';
    var s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);

    // exemplo anotado: uma peça com contorno (altura) + colar (ritmo), colorida (tom)
    var svg =
      '<svg class="explica-svg" viewBox="0 0 300 150" role="img" aria-label="exemplo anotado de um Lego">' +
      '<rect x="20" y="20" width="200" height="110" rx="10" fill="hsl(210,58%,95%)" stroke="hsl(210,70%,46%)" stroke-width="1.5"/>' +
      '<rect x="36" y="14" width="15" height="9" rx="4" fill="hsl(210,70%,46%)"/><rect x="58" y="14" width="15" height="9" rx="4" fill="hsl(210,70%,46%)"/><rect x="80" y="14" width="15" height="9" rx="4" fill="hsl(210,70%,46%)"/>' +
      '<polyline points="36,70 70,44 104,58 138,36 172,66 196,50" fill="none" stroke="hsl(210,70%,46%)" stroke-width="2.5" stroke-linejoin="round"/>' +
      '<circle cx="36" cy="70" r="3" fill="hsl(210,70%,46%)"/><circle cx="70" cy="44" r="3" fill="hsl(210,70%,46%)"/><circle cx="104" cy="58" r="3" fill="hsl(210,70%,46%)"/><circle cx="138" cy="36" r="3" fill="hsl(210,70%,46%)"/><circle cx="172" cy="66" r="3" fill="hsl(210,70%,46%)"/><circle cx="196" cy="50" r="3" fill="hsl(210,70%,46%)"/>' +
      '<rect x="36" y="98" width="28" height="9" rx="3" fill="hsl(210,70%,46%)" opacity=".6"/><rect x="68" y="98" width="14" height="9" rx="3" fill="hsl(210,70%,46%)" opacity=".6"/><rect x="86" y="98" width="40" height="9" rx="3" fill="hsl(210,70%,46%)" opacity=".6"/><rect x="130" y="98" width="20" height="9" rx="3" fill="hsl(210,70%,46%)" opacity=".6"/><rect x="154" y="98" width="42" height="9" rx="3" fill="hsl(210,70%,46%)" opacity=".6"/>' +
      '<text x="232" y="40" font-size="11" fill="#5b5446">↑ altura</text>' +
      '<text x="232" y="54" font-size="9" fill="#857a68">(as notas)</text>' +
      '<text x="232" y="105" font-size="11" fill="#5b5446">ritmo</text>' +
      '<text x="232" y="118" font-size="9" fill="#857a68">(durações)</text>' +
      '<text x="22" y="146" font-size="10" fill="#857a68">cor = o tom (ciclo de quintas)</text>' +
      '</svg>';

    var d = document.createElement('div'); d.className = 'explica-back'; d.id = 'explica-back'; d.hidden = true;
    d.innerHTML = '<div class="explica-card" role="dialog" aria-modal="true" aria-label="como o desenho é feito">' +
      '<button class="explica-x" aria-label="fechar">✕</button>' +
      '<h3>Como esse desenho é feito</h3>' +
      '<p>Nada é decorativo — tudo sai das <b>notas da peça</b>, lidas automaticamente:</p>' + svg +
      '<ul class="explica-list">' +
      '<li style="--dot:hsl(210,70%,46%)"><b>A cor</b> é o <b>tom</b> da peça, pela posição no <b>ciclo de quintas</b> — tons vizinhos ganham cores vizinhas (quente = maior, frio = menor).</li>' +
      '<li style="--dot:#2f7d5b"><b>A linha</b> que sobe e desce é a <b>altura das notas</b> do trecho: o desenho da melodia no tempo.</li>' +
      '<li style="--dot:#8a2331"><b>As barrinhas</b> embaixo são a <b>duração</b> de cada nota — a célula rítmica (o colar).</li>' +
      '</ul>' +
      '<p class="explica-foot">Cada trecho que se repete na música vira uma peça de Lego. Toque uma peça pra <b>ouvir</b> aquele trecho.</p>' +
      '</div>';
    document.body.appendChild(d);
    d.addEventListener('click', function (e) { if (e.target === d || e.target.closest('.explica-x')) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }
  function open() { build(); var d = document.getElementById('explica-back'); if (d) d.hidden = false; }
  function close() { var d = document.getElementById('explica-back'); if (d) d.hidden = true; }
  root.explicaDesenho = open;
})(typeof window !== 'undefined' ? window : this);
