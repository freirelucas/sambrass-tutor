'use strict';
/* "Instrução colapsada" por música (rota "O Caminho do Sambrass"): capa · perfil · plano ·
 * desafios · diário — agora como ACORDEÃO rolável (seções colapsáveis), não mais slides swipe.
 * + Técnica do lote e as instruções de aquecimento (12 passos) usam o mesmo acordeão.
 * O aquecimento de verdade é o Cichowicz (respira.html). Lazy-load: data/{pedagogia,aquecimento,tecnica}.json.
 * Todo desafio leva ao TUTOR DE ESCUTA real (estudo.html?id=). Usa de app.js: DB, store, RATELBL, markDay.
 */
let S = { slides: [], i: 0, music: null, rate: 0, checks: {} };
const dots6 = v => { let h = '<span class="dots">'; for (let i = 1; i <= 6; i++) h += `<i class="${i <= v ? 'f' : ''}"></i>`; return h + '</span>'; };
const fetchJSON = f => fetch('./data/' + JCFG().base + f).then(r => r.json()).catch(() => null);
async function loadPedagogia() { if (!DB.pedagogia) DB.pedagogia = (await fetchJSON('pedagogia.json')) || {}; }
async function loadAquec() { if (!DB.aquec) DB.aquec = (await fetchJSON('aquecimento.json')) || []; }
async function loadTecnica() { if (!DB.tecnica) DB.tecnica = (await fetchJSON('tecnica.json')) || []; }

function storyEl() {
  let s = document.getElementById('story');
  if (!s) {
    s = document.createElement('div'); s.id = 'story'; s.className = 'story'; s.hidden = true;
    s.innerHTML = `<div class="storytop"><button class="sclose" onclick="closeStory()" aria-label="fechar">✕</button><div id="storyCtx" class="storyctx"></div></div>
      <div id="slideHost" class="slideHost"></div><div id="snav" class="snav"></div>`;
    document.body.appendChild(s);
  }
  return s;
}
function showStory(ctx) {
  const s = storyEl(); document.getElementById('storyCtx').textContent = ctx;
  s.hidden = false; s.classList.add('on'); renderAccordion(); window.scrollTo(0, 0);
}
function closeStory() {
  const s = document.getElementById('story'); if (s) { s.hidden = true; s.classList.remove('on'); }
  if (typeof telaTrilha === 'function' && $('.abas button.ativa')?.dataset.tela === 'trilha') telaTrilha();
}

async function openMusic(num) {
  await loadPedagogia();
  const m = Object.assign({}, DB.percByNum[num] || {}, (DB.pedagogia || {})[num] || {});  // nó + perfil/plano/desafios
  S = { slides: buildMusicSlides(m), i: 0, music: m, rate: 0, checks: {} };
  showStory(`Lote ${m.lote} · ${m.titulo}`);
}
function buildMusicSlides(m) {
  const sl = [{ type: 'capa', m }, { type: 'perfil', m }, { type: 'plano', m }];
  (m.desafios || []).forEach((d, k) => sl.push({ type: 'chal', m, d, k }));
  sl.push({ type: 'diario', m });
  return sl;
}
async function openPrep() {
  await loadAquec();
  const sl = [{ type: 'prepIntro' }];
  (DB.aquec || []).forEach((p, k) => sl.push({ type: 'prepEx', p, k }));
  sl.push({ type: 'prepFin' });
  S = { slides: sl, i: 0, music: null, rate: 0, checks: {} };
  showStory('Instruções de aquecimento');
}
async function openTecnica(lote) {
  await loadTecnica();
  const t = (DB.tecnica || [])[lote - 1]; if (!t) return;
  const sl = [{ type: 'tecIntro', t }];
  (t.eixos || []).forEach(e => (e.exercicios || []).forEach(ex => sl.push({ type: 'tecEx', eixo: e.eixo, ex })));
  const pcs = (DB.percurso || []).filter(x => x.lote === lote);
  const alvo = pcs.find(x => typeof isDone === 'function' && !isDone(x.num)) || pcs[0];
  if (alvo) sl.push({ type: 'tecFim', lote, alvo, n: pcs.length });
  S = { slides: sl, i: 0, music: null, rate: 0, checks: {}, tec: true };
  showStory(`Técnica · Lote ${lote} · tom de ${t.tom}`);
}

function tutorPeca(num) { location.href = './estudo.html?id=' + idOf(num) + (JORNADA !== 'sambrass' ? '&jornada=' + JORNADA : ''); }
const micBtn = num => `<button class="acao micbtn" onclick="tutorPeca(${num})">🎤 tocar no tutor (ele ouve você)</button>`;
// avisos da capa: tier da melodia (honestidade do grader) + empurrão suave de nível (não-bloqueante)
function capaNotas(m) {
  let h = '';
  const tier = (typeof qualOf === 'function') ? qualOf(m.num) : 'conferida';
  if (tier !== 'conferida') {
    const txt = tier === 'dedos' ? 'leitura provisória (tom pelos dedos · oitava e ritmo em revisão)' : 'leitura automática (OMR), em revisão';
    h += `<p class="capanote warn">⚠ Melodia: ${txt}. Confira a partitura — o tutor avalia pela classe de altura.</p>`;
  }
  const ms = DB.percurso || [], RANK = { book1: 0, book2: 1, arban: 2 };
  if (typeof suggestedIndex === 'function' && m.nivel) {
    const sug = ms[suggestedIndex()];
    if (sug && (RANK[m.nivel] || 0) > (RANK[sug.nivel] || 0)) {
      const lbl = (typeof NIVEL_FULL !== 'undefined' && NIVEL_FULL[m.nivel]) || m.nivel;
      h += `<p class="capanote soft">💡 Esta é <b>${lbl}</b> — o sugerido agora é mais abaixo na escada. Mas nada trava: se quiser encarar, vá.</p>`;
    }
  }
  return h;
}

// cada "slide" → uma seção de acordeão: {title, sub, body, open?}
function slidePart(s) {
  if (s.type === 'capa') { const m = s.m;
    return { open: true, title: m.titulo, sub: `Lote ${m.lote} · ${m.tom}`,
      body: `<div class="by">${m.compositor}</div>${capaNotas(m)}
      <div class="cplx">
        <div class="cchip"><span class="lab">Agudo</span>${dots6(m.agudo)}<span class="v">máx <b>${m.pico_nome || '?'}</b></span></div>
        <div class="cchip"><span class="lab">Veloc.</span>${dots6(m.vel)}<span class="v">${m.vel}/6</span></div>
        <div class="cchip"><span class="lab">Fôlego</span>${dots6(m.folego)}<span class="v">${m.folego}/6</span></div></div>
      <p class="big">Forma ${m.forma || '?'}.</p>${micBtn(m.num)}` };
  }
  if (s.type === 'perfil') { const m = s.m, pf = m.perfil || {};
    const blk = (lab, v, txt) => `<div class="pf"><div class="ph"><span class="lab">${lab}</span>${dots6(v)}</div><p>${txt || ''}</p></div>`;
    return { title: 'Onde mora o esforço', sub: 'perfil',
      body: `${blk('Agudo', m.agudo, pf.agudo)}${blk('Velocidade', m.vel, pf.vel)}${blk('Fôlego', m.folego, pf.folego)}` };
  }
  if (s.type === 'plano') { const p = s.m.plano || {};
    return { title: 'Como estudar esta peça', sub: 'plano',
      body: `<p class="big">O foco é <b>${p.foco || ''}</b>.</p><p>${p.leitura || ''}</p><p style="margin-top:10px">${p.estrategia || ''}</p>` };
  }
  if (s.type === 'chal') { const d = s.d, on = S.checks[s.k];
    return { title: d.t, sub: `desafio ${s.k + 1}`,
      body: `<div class="dchal"><div class="step">faça agora</div><p>${d.d}</p>
        ${d.svg ? `<div class="scorebox">${d.svg}</div>` : ''}
        <div class="chk" data-chk="${s.k}" onclick="toggleChk(${s.k})"><span class="box ${on ? 'on' : ''}">${on ? '✓' : ''}</span><span class="chktxt">${on ? 'feito!' : 'marque quando fizer'}</span></div></div>
      ${d.w ? `<p class="why">💡 <b>Por quê:</b> ${d.w}</p>` : ''}` };
  }
  if (s.type === 'diario') { const m = s.m;
    return { open: true, title: 'Como foi hoje?', sub: 'diário',
      body: `<p>Registre para você — é o que mostra a evolução real entre as sessões.</p>
      <div class="rate" id="rate">${[1, 2, 3, 4, 5].map(n => `<button onclick="setRate(${n})">${n}</button>`).join('')}</div>
      <div class="ratelbl" id="ratelbl">toque um número</div>
      <p class="why" style="margin-top:14px">💡 Nível 4+ marca a peça como dominada na trilha. Voltar a ela em dias seguintes (repetição espaçada) é o que fixa.</p>${micBtn(m.num)}` };
  }
  if (s.type === 'prepIntro') {
    return { open: true, title: 'Aquecimento — 12 passos', sub: 'instruções',
      body: `<p class="big">Antes de tocar, prepare o corpo: <b>ar → bocal → som → flexibilidade → registro → articulação → dinâmica</b>. Som tranquilo, sem pressa.</p>
      <p class="why">💡 O aquecimento de verdade é o <b>Cichowicz</b> (na aba Aquecer / no nó da trilha). Aqui é só a referência passo a passo.</p>` };
  }
  if (s.type === 'prepEx') { const p = s.p;
    return { title: p.nome, sub: `passo ${s.k + 1}`, body: `<p>${p.dica || ''}</p>${p.svg ? `<div class="scorebox">${p.svg}</div>` : ''}` };
  }
  if (s.type === 'prepFin') {
    return { title: 'Corpo aquecido 🌬️', sub: 'pronto', body: `<p class="big">Agora escolha um samba na trilha e toque.</p>` };
  }
  if (s.type === 'tecIntro') { const t = s.t;
    return { open: true, title: `Técnica — tom de ${t.tom}`, sub: `lote ${t.lote}`,
      body: `<p class="big">Foco do lote: <b>${t.feat}</b>.</p><p>Exercícios curtos por eixo — som, flexibilidade, articulação, dinâmica.</p>` };
  }
  if (s.type === 'tecEx') { const ex = s.ex;
    return { title: ex.nome, sub: s.eixo, body: `<p>${ex.dica || ''}</p>${ex.svg ? `<div class="scorebox">${ex.svg}</div>` : ''}` };
  }
  if (s.type === 'tecFim') { const a = s.alvo;
    return { title: 'A técnica vira samba', sub: 'aplicar',
      body: `<p class="big">Leve o que você treinou para uma peça do Lote ${s.lote}.</p>
      <button class="acao micbtn" onclick="openMusic(${a.num})">▶ abrir ${a.titulo}</button>
      <p class="why" style="margin-top:12px">💡 São ${s.n} peças neste lote — todas trabalham este mesmo foco técnico.</p>` };
  }
  return { title: '', body: '' };
}
function renderAccordion() {
  document.getElementById('slideHost').innerHTML = S.slides.map(s => {
    const part = slidePart(s);
    return `<div class="acc${part.open ? ' open' : ''}"><button class="acc-h" onclick="accToggle(this)">${part.title}${part.sub ? `<span class="acc-sub">${part.sub}</span>` : ''}<span class="acc-i">▸</span></button><div class="acc-b">${part.body}</div></div>`;
  }).join('');
  document.getElementById('snav').innerHTML =
    `<button class="snext" onclick="finishStory()">${S.music ? 'concluir' : 'fechar'}</button>`;
}
function accToggle(btn) { const it = btn.closest('.acc'); if (it) it.classList.toggle('open'); }
function setRate(n) {
  S.rate = n; document.querySelectorAll('#rate button').forEach((b, i) => b.classList.toggle('sel', i + 1 === n));
  const l = document.getElementById('ratelbl'); if (l) l.textContent = RATELBL[n];
}
function toggleChk(k) {
  S.checks[k] = !S.checks[k];
  const el = document.querySelector(`[data-chk="${k}"]`);
  if (el) { const box = el.querySelector('.box'), tx = el.querySelector('.chktxt');
    if (box) { box.classList.toggle('on', S.checks[k]); box.textContent = S.checks[k] ? '✓' : ''; }
    if (tx) tx.textContent = S.checks[k] ? 'feito!' : 'marque quando fizer'; }
}
function finishStory() {
  if (S.music) {
    if (!S.rate) { const l = document.getElementById('ratelbl'); if (l) l.textContent = 'no Diário, escolha de 1 a 5 para concluir'; return; }
    const logs = store.get('logs', {}), num = S.music.num;
    (logs[num] = logs[num] || []).push({ d: new Date().toISOString().slice(0, 10), n: S.rate });
    store.set('logs', logs); markDay();
    const t = treinoCount() + 1; store.set('treinos', t);   // conta o treino p/ repetição espaçada
    const lt = store.get('lastT', {}); lt[num] = t; store.set('lastT', lt);
  } else if (!S.tec) { store.set('prepdone', true); markDay(); }
  closeStory();
}
