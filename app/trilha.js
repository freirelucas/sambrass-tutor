'use strict';
/* Trilha — o "caminho sugerido" estilo Duolingo (rota "O Caminho do Sambrass").
 * Ordena as 110 pela heurística de complexidade (data/percurso.json, campo .lote 1–6),
 * SEM bloqueio (SDT: cadeado mina autonomia). Bandeira "SUGERIDA" na próxima não-dominada.
 * Usa de app.js: DB, tela, LCOR, isDone, prepDone, streakCount, countDone, nivelOf, NIVEL.
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
  let h = `<div class="hud">
      <div><b>O Caminho do Sambrass</b><div class="meta">trilha de 110 sambas</div></div>
      <div class="hudpills"><span class="pill">📅 ${nd} ${nd === 1 ? 'dia' : 'dias'}</span><span class="pill">🎺 ${countDone()}/${ms.length}</span></div>
    </div>
    <p class="trilha-intro">A ordem é um <b>caminho sugerido</b>, do mais confortável ao mais exigente. Toque o que quiser — a trilha é sua.</p>
    <div class="prepnode" onclick="openPrep()"><div class="pic">${prepDone() ? '✓' : '🌬️'}</div>
      <div><b>Aquecimento</b><div class="meta">12 exercícios · faça sempre antes</div></div></div>
    <div class="path">`;
  let last = 0;
  ms.forEach((m, i) => {
    if (m.lote !== last) {
      last = m.lote; const L = (DB.lotes || [])[m.lote - 1] || {};
      h += `<div class="lotehead" style="--ll:${LCOR[m.lote]}"><span class="band">Lote ${m.lote}</span>
        <div class="desc">tom de ${L.tom || '?'} · ${L.feat || ''} <button class="tecbtn" onclick="openTecnica(${m.lote})">técnica do lote ›</button></div></div>`;
    }
    const done = isDone(m.num), here = i === uni, nv = nivelOf(m.num);
    const side = (i % 6 < 3) ? 'rgt' : 'lft';
    const z = ['z0', 'z1', 'z2', 'z3', 'z2', 'z1'][i % 6];
    h += `<div class="node ${z} ${side}${here ? ' here' : ''}" style="--ll:${LCOR[m.lote]}">
      ${here ? '<div class="flag">SUGERIDA</div>' : ''}
      <button class="inner${done ? ' done' : ''}" onclick="openMusic(${m.num})" aria-label="${m.titulo}"><span class="ic">${done ? '✓' : '🎺'}</span></button>
      <div class="nlabel"><b>${m.titulo}</b><div class="meta">${String(m.num).padStart(3, '0')} · ${m.tom}${nv ? ` · <span class="niv niv-${nv}">${NIVEL[nv]}</span>` : ''}</div></div>
    </div>`;
  });
  tela.innerHTML = h + '</div>';
}
window.telaTrilha = telaTrilha;
