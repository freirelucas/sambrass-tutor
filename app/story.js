'use strict';
/* Stories por música (rota "O Caminho do Sambrass"): capa → perfil → plano → desafios → diário;
 * + Aquecimento e Técnica do lote. Engine de slides própria, sem dependência.
 * Lazy-load: data/{pedagogia,aquecimento,tecnica}.json (SVGs pré-assados; injetados como SVG puro).
 * SÍNTESE das duas rotas: todo desafio leva ao TUTOR DE ESCUTA real (estudo.html?id=).
 * Usa de app.js: DB, store, RATELBL, markDay. De trilha.js: telaTrilha (atualiza ✓ ao fechar).
 */
let S = { slides: [], i: 0, music: null, rate: 0, checks: {} };
const dots6 = v => { let h = '<span class="dots">'; for (let i = 1; i <= 6; i++) h += `<i class="${i <= v ? 'f' : ''}"></i>`; return h + '</span>'; };
const fetchJSON = f => fetch('./data/' + f).then(r => r.json()).catch(() => null);
async function loadPedagogia() { if (!DB.pedagogia) DB.pedagogia = (await fetchJSON('pedagogia.json')) || {}; }
async function loadAquec() { if (!DB.aquec) DB.aquec = (await fetchJSON('aquecimento.json')) || []; }
async function loadTecnica() { if (!DB.tecnica) DB.tecnica = (await fetchJSON('tecnica.json')) || []; }

function storyEl() {
  let s = document.getElementById('story');
  if (!s) {
    s = document.createElement('div'); s.id = 'story'; s.className = 'story'; s.hidden = true;
    s.innerHTML = `<div class="storytop"><button class="sclose" onclick="closeStory()" aria-label="fechar">✕</button><div id="sbars" class="sbars"></div></div>
      <div id="storyCtx" class="storyctx"></div><div id="slideHost" class="slideHost"></div><div id="snav" class="snav"></div>`;
    document.body.appendChild(s);
  }
  return s;
}
function showStory(ctx) {
  const s = storyEl(); document.getElementById('storyCtx').textContent = ctx;
  s.hidden = false; s.classList.add('on'); renderSlide(); window.scrollTo(0, 0);
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
  showStory('Aquecimento');
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

function tutorPeca(num) { location.href = './estudo.html?id=sb-' + String(num).padStart(3, '0'); }
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

function renderSlide() {
  renderBars();
  const s = S.slides[S.i]; let h = '';
  if (s.type === 'capa') { const m = s.m;
    h = `<div class="slide"><div class="kicker">Lote ${m.lote} · tom de ${m.tom}</div>
      <h2>${m.titulo}</h2><div class="by">${m.compositor}</div>
      ${capaNotas(m)}
      <div class="cplx">
        <div class="cchip"><span class="lab">Agudo</span>${dots6(m.agudo)}<span class="v">máx <b>${m.pico_nome || '?'}</b></span></div>
        <div class="cchip"><span class="lab">Veloc.</span>${dots6(m.vel)}<span class="v">${m.vel}/6</span></div>
        <div class="cchip"><span class="lab">Fôlego</span>${dots6(m.folego)}<span class="v">${m.folego}/6</span></div></div>
      <p class="big">Forma ${m.forma || '?'}. Deslize: o perfil, o plano de ataque e os desafios.</p>${micBtn(m.num)}</div>`;
  } else if (s.type === 'perfil') { const m = s.m, pf = m.perfil || {};
    const blk = (lab, v, txt) => `<div class="pf"><div class="ph"><span class="lab">${lab}</span>${dots6(v)}</div><p>${txt || ''}</p></div>`;
    h = `<div class="slide"><div class="kicker">Perfil</div><h2>Onde mora o esforço</h2>
      ${blk('Agudo', m.agudo, pf.agudo)}${blk('Velocidade', m.vel, pf.vel)}${blk('Fôlego', m.folego, pf.folego)}</div>`;
  } else if (s.type === 'plano') { const p = s.m.plano || {};
    h = `<div class="slide"><div class="kicker">Plano de ataque</div><h2>Como estudar esta peça</h2>
      <p class="big">O foco é <b>${p.foco || ''}</b>.</p><p>${p.leitura || ''}</p><p style="margin-top:10px">${p.estrategia || ''}</p></div>`;
  } else if (s.type === 'chal') { const d = s.d, on = S.checks[s.k];
    h = `<div class="slide"><div class="kicker">Desafio ${s.k + 1} de ${(S.music.desafios || []).length}</div>
      <div class="dchal"><div class="step">faça agora</div><h3>${d.t}</h3><p>${d.d}</p>
        ${d.svg ? `<div class="scorebox">${d.svg}</div>` : ''}
        <div class="chk" onclick="toggleChk(${s.k})"><span class="box ${on ? 'on' : ''}">${on ? '✓' : ''}</span>${on ? 'feito!' : 'marque quando fizer'}</div></div>
      ${d.w ? `<p class="why">💡 <b>Por quê:</b> ${d.w}</p>` : ''}${micBtn(S.music.num)}</div>`;
  } else if (s.type === 'diario') { const m = s.m;
    h = `<div class="slide"><div class="kicker">Diário</div><h2>Como foi hoje?</h2>
      <p>Registre para você — é o que mostra a evolução real entre as sessões.</p>
      <div class="rate" id="rate">${[1, 2, 3, 4, 5].map(n => `<button onclick="setRate(${n})">${n}</button>`).join('')}</div>
      <div class="ratelbl" id="ratelbl">toque um número</div>
      <p class="why" style="margin-top:18px">💡 Nível 4+ marca a peça como dominada na trilha. Voltar a ela em dias seguintes (repetição espaçada) é o que fixa.</p>${micBtn(m.num)}</div>`;
  } else if (s.type === 'prepIntro') {
    h = `<div class="slide"><div class="kicker">Capítulo 0</div><h2>Aquecimento</h2>
      <p class="big">Antes de tocar qualquer samba, prepare o corpo: <b>ar → bocal → som → flexibilidade → registro → articulação → dinâmica</b>.</p>
      <p>São 12 passos curtos. Faça com calma, som tranquilo.</p></div>`;
  } else if (s.type === 'prepEx') { const p = s.p;
    h = `<div class="slide"><div class="kicker">Aquecimento ${s.k + 1} de 12</div><h3>${p.nome}</h3>
      <p>${p.dica || ''}</p>${p.svg ? `<div class="scorebox">${p.svg}</div>` : ''}</div>`;
  } else if (s.type === 'prepFin') {
    h = `<div class="slide"><div class="kicker">Pronto</div><h2>Corpo aquecido 🌬️ ✓</h2><p class="big">Agora escolha um samba na trilha e toque.</p></div>`;
  } else if (s.type === 'tecIntro') { const t = s.t;
    h = `<div class="slide"><div class="kicker">Técnica do Lote ${t.lote}</div><h2>tom de ${t.tom}</h2>
      <p class="big">Foco do lote: <b>${t.feat}</b>.</p><p>Exercícios curtos por eixo — som, flexibilidade, articulação, dinâmica.</p></div>`;
  } else if (s.type === 'tecEx') { const ex = s.ex;
    h = `<div class="slide"><div class="kicker">${s.eixo}</div><h3>${ex.nome}</h3>
      <p>${ex.dica || ''}</p>${ex.svg ? `<div class="scorebox">${ex.svg}</div>` : ''}</div>`;
  } else if (s.type === 'tecFim') { const a = s.alvo;
    h = `<div class="slide"><div class="kicker">Aplicar na música</div><h2>A técnica vira samba</h2>
      <p class="big">Leve o que você treinou para uma peça do Lote ${s.lote}.</p>
      <button class="acao micbtn" onclick="openMusic(${a.num})">▶ abrir ${a.titulo}</button>
      <p class="why" style="margin-top:12px">💡 São ${s.n} peças neste lote — todas trabalham este mesmo foco técnico.</p></div>`;
  }
  document.getElementById('slideHost').innerHTML = h;
  const last = S.i === S.slides.length - 1;
  document.getElementById('snav').innerHTML =
    `<button class="sprev" onclick="prevSlide()"${S.i === 0 ? ' disabled' : ''}>‹ voltar</button>
     <button class="snext" onclick="${last ? 'finishStory()' : 'nextSlide()'}">${last ? (S.music ? 'concluir' : 'fechar') : 'continuar ›'}</button>`;
}
function renderBars() {
  let h = '';
  for (let i = 0; i < S.slides.length; i++) h += `<div class="sbar${i <= S.i ? ' done' : ''}"><i style="width:${i <= S.i ? 100 : 0}%"></i></div>`;
  document.getElementById('sbars').innerHTML = h;
}
function nextSlide() { if (S.i < S.slides.length - 1) { S.i++; renderSlide(); } }
function prevSlide() { if (S.i > 0) { S.i--; renderSlide(); } }
function setRate(n) {
  S.rate = n; document.querySelectorAll('#rate button').forEach((b, i) => b.classList.toggle('sel', i + 1 === n));
  document.getElementById('ratelbl').textContent = RATELBL[n];
}
function toggleChk(k) { S.checks[k] = !S.checks[k]; renderSlide(); }
function finishStory() {
  if (S.music) {
    if (!S.rate) { const l = document.getElementById('ratelbl'); if (l) l.textContent = 'escolha de 1 a 5 para concluir'; return; }
    const logs = store.get('logs', {}), num = S.music.num;
    (logs[num] = logs[num] || []).push({ d: new Date().toISOString().slice(0, 10), n: S.rate });
    store.set('logs', logs); markDay();
  } else if (!S.tec) { store.set('prepdone', true); markDay(); }
  closeStory();
}
