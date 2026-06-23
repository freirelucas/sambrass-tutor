'use strict';
/* Progresso — painel factual (rota "O Caminho do Sambrass"): reflexão honesta, não placar.
 * 100% derivado do localStorage (logs {num:[{d,n}]}, days) + DB.percurso. Sem XP, sem cadeado.
 * A boa ideia veio do export single-file; aqui descansa sobre os dados vivos do app.
 * Usa de app.js: DB, tela, store, isDone, countDone, streakCount, LCOR.
 */
function telaProg() {
  const ms = DB.percurso || [];
  const logs = store.get('logs', {});
  let sessoes = 0, somaNiv = 0;
  const byDay = {};                                    // 'YYYY-MM-DD' -> nº de sessões
  Object.values(logs).forEach(arr => (arr || []).forEach(x => {
    sessoes++; somaNiv += x.n; byDay[x.d] = (byDay[x.d] || 0) + 1;
  }));
  const dom = countDone(), tot = ms.length || 110, streak = streakCount();
  const diasTot = (store.get('days', []) || []).length;
  const nivelMedio = sessoes ? (somaNiv / sessoes) : 0;

  // sparkline dos últimos 14 dias (sessões/dia)
  const dias = [];
  for (let i = 13; i >= 0; i--) { const d = new Date(); d.setDate(d.getDate() - i); dias.push(d.toISOString().slice(0, 10)); }
  const maxDay = Math.max(1, ...dias.map(d => byDay[d] || 0));
  const spark = dias.map(d => {
    const v = byDay[d] || 0, hp = v ? Math.max(8, Math.round(100 * v / maxDay)) : 0;
    return `<div class="spk" title="${d}: ${v} sessão(ões)"><i style="height:${hp}%"></i></div>`;
  }).join('');

  // progresso por lote (dominadas / total)
  const lotes = [1, 2, 3, 4, 5, 6].map(L => {
    const inl = ms.filter(m => m.lote === L), fei = inl.filter(m => isDone(m.num)).length;
    const pct = inl.length ? Math.round(100 * fei / inl.length) : 0;
    return `<div class="lrow"><span class="lname" style="--ll:${LCOR[L]}">Lote ${L}</span>
      <div class="lbar"><i style="width:${pct}%;background:${LCOR[L]}"></i></div>
      <span class="lval">${fei}/${inl.length}</span></div>`;
  }).join('');

  // ranking por compositor (por dominadas) — variar compositor = mais sotaques do samba
  const byComp = {};
  ms.forEach(m => { const c = m.compositor || '—'; (byComp[c] = byComp[c] || { d: 0, t: 0 }); byComp[c].t++; if (isDone(m.num)) byComp[c].d++; });
  const rank = Object.entries(byComp).filter(([, v]) => v.d > 0).sort((a, b) => b[1].d - a[1].d || b[1].t - a[1].t).slice(0, 8);
  const rankHtml = rank.length
    ? rank.map(([c, v]) => `<div class="crow"><span class="cname">${c}</span>
        <span class="cbar"><i style="width:${Math.round(100 * v.d / v.t)}%"></i></span><span class="cval">${v.d}/${v.t}</span></div>`).join('')
    : '<p class="meta">Domine peças (nível 4+ no diário) para ver seus compositores aqui.</p>';

  tela.innerHTML = `
    <div class="hud">
      <div><b>Seu progresso</b><div class="meta">reflexão honesta — não é placar</div></div>
      <div class="hudpills"><span class="pill">🎺 ${dom}/${tot}</span><span class="pill">📅 ${streak} ${streak === 1 ? 'dia' : 'dias'} seguidos</span></div>
    </div>
    <div class="pgrid">
      <div class="pcard"><div class="pnum">${dom}</div><div class="plab">dominadas</div></div>
      <div class="pcard"><div class="pnum">${sessoes}</div><div class="plab">sessões</div></div>
      <div class="pcard"><div class="pnum">${diasTot}</div><div class="plab">dias praticados</div></div>
      <div class="pcard"><div class="pnum">${nivelMedio ? nivelMedio.toFixed(1) : '—'}</div><div class="plab">nível médio</div></div>
    </div>
    <div class="card"><h3>Últimos 14 dias</h3><div class="spark">${spark}</div>
      <p class="meta">Cada barra = sessões concluídas no diário. Constância &gt; intensidade.</p></div>
    <div class="card"><h3>Progresso por lote</h3>${lotes}</div>
    <div class="card"><h3>Seus compositores</h3>${rankHtml}
      <p class="why" style="margin-top:10px">💡 Dominar (nível 4+) espalha o estudo pelo caderno inteiro — variar compositor treina mais sotaques rítmicos do samba.</p></div>`;
}
window.telaProg = telaProg;
