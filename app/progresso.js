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

  // precisão & regularidade — do practicelog persistido pelo estudo (o grader ao vivo virando histórico)
  const plog = (() => { try { return JSON.parse(localStorage.getItem('practicelog') || '[]'); } catch { return []; } })();
  const titById = {}; ms.forEach(m => { if (typeof idOf === 'function') titById[idOf(m.num)] = m.titulo; });
  const nameOf = id => titById[id] || id;
  let gradeCard;
  if (!plog.length) {
    gradeCard = `<div class="card"><h3>Precisão &amp; regularidade</h3>
      <p class="meta">Pratique com o <b>microfone</b> ligado (no estudo → <b>praticar</b>) e o app mede sua <b>precisão de notas</b> e sua <b>regularidade rítmica</b> (pocket) — a evolução aparece aqui.</p></div>`;
  } else {
    const accs = plog.filter(x => x.acc != null).map(x => x.acc), regs = plog.filter(x => x.reg != null).map(x => x.reg);
    const avg = a => a.length ? Math.round(a.reduce((s, v) => s + v, 0) / a.length) : null;
    const mAcc = avg(accs), mReg = avg(regs), bReg = regs.length ? Math.max(...regs) : null;
    const rspark = plog.slice(-14).map(x => { const v = x.reg == null ? 0 : x.reg;
      return `<div class="spk" title="${x.d}: regularidade ${x.reg == null ? '—' : x.reg + '%'}"><i style="height:${v ? Math.max(8, v) : 0}%;background:var(--brand)"></i></div>`; }).join('');
    const ult = plog.slice(-6).reverse().map(x => `<div class="crow"><span class="cname">${nameOf(x.id)}</span>
      <span class="cval" style="min-width:auto;white-space:nowrap">${x.acc != null ? '✓ ' + x.acc + '%' : ''}${x.reg != null ? ' · ⏱ ' + x.reg + '%' : ''}</span></div>`).join('');
    gradeCard = `<div class="card"><h3>Precisão &amp; regularidade</h3>
      <div class="pgrid" style="grid-template-columns:repeat(3,1fr)">
        <div class="pcard"><div class="pnum">${mAcc != null ? mAcc + '%' : '—'}</div><div class="plab">precisão média</div></div>
        <div class="pcard"><div class="pnum">${mReg != null ? mReg + '%' : '—'}</div><div class="plab">regularidade média</div></div>
        <div class="pcard"><div class="pnum">${bReg != null ? bReg + '%' : '—'}</div><div class="plab">melhor regularidade</div></div>
      </div>
      <div class="spark" style="margin-top:8px">${rspark}</div>
      <p class="meta">Barras = regularidade rítmica (pocket) das últimas sessões. <b>Precisão</b> = notas certas; <b>regularidade</b> = tempo constante.</p>
      <h3 style="margin-top:14px">Últimas praticadas</h3>${ult}</div>`;
  }

  // ⭐ Meu repertório — peças marcadas no estudo (desta jornada), pra voltar fácil
  const favs = (() => { try { return JSON.parse(localStorage.getItem('favs') || '[]'); } catch { return []; } })();
  const myrep = (typeof idOf === 'function') ? ms.filter(m => favs.includes(idOf(m.num))) : [];
  const repCard = myrep.length ? `<div class="card"><h3>⭐ Meu repertório</h3>
    ${myrep.map(m => `<div class="crow"><a class="cname" style="color:inherit;text-decoration:none" href="./estudo.html?id=${idOf(m.num)}${JORNADA !== 'sambrass' ? '&jornada=' + JORNADA : ''}">${m.titulo}</a><span class="cval" style="min-width:auto">${m.tom || ''}${isDone(m.num) ? ' ✓' : ''}</span></div>`).join('')}
    <p class="meta" style="margin-top:8px">Marque peças com <b>☆ repertório</b> no estudo pra voltar fácil aqui.</p></div>` : '';

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
    ${repCard}
    <div class="card"><h3>Últimos 14 dias</h3><div class="spark">${spark}</div>
      <p class="meta">Cada barra = sessões concluídas no diário. Constância &gt; intensidade.</p></div>
    ${gradeCard}
    <div class="card"><h3>Progresso por lote</h3>${lotes}</div>
    <div class="card"><h3>Seus compositores</h3>${rankHtml}
      <p class="why" style="margin-top:10px">💡 Dominar (nível 4+) espalha o estudo pelo caderno inteiro — variar compositor treina mais sotaques rítmicos do samba.</p></div>`;
}
window.telaProg = telaProg;
