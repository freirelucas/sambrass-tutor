'use strict';
/* Trilha — o "caminho sugerido" estilo Duolingo (rota "O Caminho do Sambrass").
 * Ordena pela ESCADA pedagógica (Book 1 → Book 2 → Arban) como eixo PRIMÁRIO e pela
 * heurística de complexidade DENTRO de cada nível (data/percurso.json: campos .nivel + .lote 1–6),
 * SEM bloqueio (SDT: cadeado mina autonomia). Bandeira "SUGERIDA" na próxima não-dominada.
 * Cada nível abre uma faixa (.nivelhead); os 6 lotes ficam aninhados nas faixas (.lotehead).
 * Usa de app.js: DB, tela, LCOR, isDone, prepDone, streakCount, countDone, NIVEL_FULL, NIVEL_DESC.
 * Abre Story/Aquecimento/Técnica (story.js): openMusic, openPrep, openTecnica.
 */
function suggestedIndex() {
  const ms = DB.percurso || [];
  for (let i = 0; i < ms.length; i++) if (!isDone(ms[i].num)) return i;
  return ms.length - 1;
}

function telaTrilha() {
  const ms = DB.percurso || [];
  if (!ms.length) { tela.innerHTML = '<p class="carregando">trilha indisponível.</p>'; return; }
  const uni = suggestedIndex(), nd = streakCount();
  const welcome = store.get('onboarded', false) ? '' : `<div class="welcome card">
    <h3>Bem-vindo ao Caminho do Sambrass 🎺</h3>
    <ol class="wsteps">
      <li><b>Toque o caderno inteiro</b> — 110 sambas, do mais fácil (Book 1) ao mais técnico. No seu ritmo: nada trava.</li>
      <li><b>O tutor ouve você.</b> Toque a peça e o microfone mostra se a nota saiu certa — no modo praticar o app fica em silêncio pra escutar só você (sem fone).</li>
      <li><b>Comece</b> pelo aquecimento e pela peça marcada <span class="flag-inline">SUGERIDA</span>.</li>
    </ol>
    <button class="acao" onclick="fecharWelcome()">entendi, bora tocar</button></div>`;
  let h = welcome + `<div class="hud">
      <div><b>O Caminho do Sambrass</b><div class="meta">trilha de 110 sambas</div></div>
      <div class="hudpills"><span class="pill">📅 ${nd} ${nd === 1 ? 'dia' : 'dias'}</span><span class="pill">🎺 ${countDone()}/${ms.length}</span></div>
    </div>
    <p class="trilha-intro">A ordem segue a <b>escada pedagógica</b>: primeiro o Book 1 (fundação), depois Book 2 e Arban — e, dentro de cada nível, do mais confortável ao mais exigente. Nada trava: toque o que quiser.</p>
    <div class="prepnode" onclick="openPrep()"><div class="pic">${prepDone() ? '✓' : '🌬️'}</div>
      <div><b>Aquecimento</b><div class="meta">12 exercícios · faça sempre antes</div></div></div>
    <div class="path">`;
  let lastNivel = null, lastLote = 0;
  ms.forEach((m, i) => {
    if (m.nivel && m.nivel !== lastNivel) {
      lastNivel = m.nivel;
      const tot = ms.filter(x => x.nivel === m.nivel).length;
      const fei = ms.filter(x => x.nivel === m.nivel && isDone(x.num)).length;
      h += `<div class="nivelhead niv-${m.nivel}">
        <div class="nivtop"><span class="nivband">${NIVEL_FULL[m.nivel] || m.nivel}</span><span class="nivcount">${fei}/${tot}</span></div>
        <p class="nivdesc">${NIVEL_DESC[m.nivel] || ''}</p></div>`;
    }
    if (m.lote !== lastLote) {
      lastLote = m.lote; const L = (DB.lotes || [])[m.lote - 1] || {};
      h += `<div class="lotehead" style="--ll:${LCOR[m.lote]}"><span class="band">Lote ${m.lote}</span>
        <div class="desc">tom de ${L.tom || '?'} · ${L.feat || ''} <button class="tecbtn" onclick="openTecnica(${m.lote})">técnica do lote ›</button></div></div>`;
    }
    const done = isDone(m.num), here = i === uni;
    const side = (i % 6 < 3) ? 'rgt' : 'lft';
    const z = ['z0', 'z1', 'z2', 'z3', 'z2', 'z1'][i % 6];
    h += `<div class="node ${z} ${side}${here ? ' here' : ''}" style="--ll:${LCOR[m.lote]}">
      ${here ? '<div class="flag">SUGERIDA</div>' : ''}
      <button class="inner${done ? ' done' : ''}" onclick="openMusic(${m.num})" aria-label="${m.titulo}"><span class="ic">${done ? '✓' : '🎺'}</span></button>
      <div class="nlabel"><b>${m.titulo}</b><div class="meta">${String(m.num).padStart(3, '0')} · ${m.tom}</div></div>
    </div>`;
  });
  tela.innerHTML = h + '</div>';
}
window.telaTrilha = telaTrilha;
window.fecharWelcome = () => { store.set('onboarded', true); telaTrilha(); };
