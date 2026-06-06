'use strict';
// Sambrass Tutor — PWA (vanilla). Lê ./data/*.json gerados de content/.

const DB = {};            // dados carregados
const $ = (s, e = document) => e.querySelector(s);
const tela = document.getElementById('tela');

async function carregar() {
  const get = async (f) => { try { return await (await fetch('./data/' + f)).json(); } catch { return null; } };
  [DB.pieces, DB.curriculo, DB.trilha, DB.cells, DB.rotina] = await Promise.all(
    ['pieces.json', 'curriculum.json', 'trilha.json', 'cells.json', 'rotina.json'].map(get));
  DB.byNum = {}; (DB.pieces?.pieces || []).forEach(p => DB.byNum[p.num] = p);
}

/* ---------- progresso (localStorage) ---------- */
const PROG = JSON.parse(localStorage.getItem('sambrass_prog') || '{}');
const setProg = (n, s) => { if (PROG[n] === s) delete PROG[n]; else PROG[n] = s; localStorage.setItem('sambrass_prog', JSON.stringify(PROG)); };
const TOM = { C: 'Dó', G: 'Sol', D: 'Ré', A: 'Lá', E: 'Mi', 'F#': 'Fá#', F: 'Fá', Bb: 'Si♭', Eb: 'Mi♭', Ab: 'Lá♭', Db: 'Ré♭', B: 'Si' };
const WRIT = { C: 'D', G: 'A', D: 'E', A: 'B', E: 'F#', 'F#': 'G#', F: 'G', Bb: 'C', Eb: 'F', Ab: 'Bb', Db: 'Eb', B: 'C#' };
const tomEscrito = p => (WRIT[p.key_concert] || p.key_concert) + (p.modulates_to_concert ? '→' + (WRIT[p.modulates_to_concert] || '') : '');

/* ---------- telas ---------- */
function telaHoje() {
  const mods = DB.curriculo?.modulos || [];
  const m = mods[Math.min(+(localStorage.getItem('sambrass_mod') || 0), mods.length - 1)] || null;
  let h = `<h2 class="sec">Treino de hoje</h2>`;
  if (m) {
    h += `<div class="card"><div class="meta">Módulo ${m.modulo}/${mods.length} · dificuldade ${m.faixa_dificuldade[0]}–${m.faixa_dificuldade[1]}</div>
      <h3>Habilidades novas</h3><div>${(m.habilidades_novas || []).map(s => `<span class="tag">${s}</span>`).join('') || '<span class="meta">consolidação</span>'}</div>
      <div style="margin-top:10px" class="prog"><b>Módulo:</b> ${mods.map((_, i) => `<button class="${i === m.modulo - 1 ? 'sel' : ''}" onclick="localStorage.setItem('sambrass_mod',${i});ir('hoje')">${i + 1}</button>`).join('')}</div></div>`;
    h += `<h2 class="sec">A rotina (90 min)</h2><ul class="lista rotina">` +
      (DB.rotina || []).map(b => `<li><span class="rmin">${b.min}min</span> <b>${b.bloco}</b> — ${b.conteudo}</li>`).join('') + `</ul>`;
    h += `<h2 class="sec">Em foco</h2><ul class="lista">` + (m.foco || []).map(f => linhaPeca(f.num)).join('') + `</ul>`;
    if (m.leitura_1avista?.length)
      h += `<h2 class="sec">Leitura à 1ª vista</h2><ul class="lista">` + m.leitura_1avista.map(f => linhaPeca(f.num)).join('') + `</ul>`;
  } else h += `<p class="carregando">currículo indisponível.</p>`;
  tela.innerHTML = h;
}

function linhaPeca(n) {
  const p = DB.byNum[n]; if (!p) return '';
  const st = PROG[n] ? ` · ${PROG[n]}` : '';
  return `<li><a class="peca" href="#" onclick="verPeca(${n});return false">
    <span class="num">${String(n).padStart(3, '0')}</span> ${p.titulo}
    <span class="dif">${p.dificuldade || '?'}</span>
    <div class="meta">${p.compositor} · ${TOM[p.key_concert] || p.key_concert} · ${p.compasso}${st}</div></a></li>`;
}

function telaBanco() {
  const ps = (DB.pieces?.pieces || []).slice().sort((a, b) => a.num - b.num);
  tela.innerHTML = `<h2 class="sec">Banco — ${ps.length} peças</h2>
    <input id="busca" placeholder="buscar título ou compositor…" style="width:100%;min-height:44px;padding:8px 12px;border:1px solid var(--linha);border-radius:8px;font:inherit;margin-bottom:6px">
    <ul class="lista" id="listapecas">${ps.map(p => linhaPeca(p.num)).join('')}</ul>`;
  $('#busca').oninput = e => {
    const q = e.target.value.toLowerCase();
    $('#listapecas').innerHTML = ps.filter(p => (p.titulo + ' ' + p.compositor).toLowerCase().includes(q)).map(p => linhaPeca(p.num)).join('');
  };
}

function verPeca(n) {
  const p = DB.byNum[n]; if (!p) return;
  const sts = ['a_ler', 'em_foco', 'dominada'];
  tela.innerHTML = `<button class="voltar" onclick="ir('banco')">‹ banco</button>
    <div class="card"><span class="dif">dif ${p.dificuldade || '?'}</span>
      <h3>${String(n).padStart(3, '0')} — ${p.titulo}</h3>
      <div class="meta">${p.compositor}</div>
      <div class="meta" style="margin:6px 0">Tom escrito <b>${tomEscrito(p)}</b> (concerto ${TOM[p.key_concert] || p.key_concert}) · ${p.compasso} · ${p.densidade} · forma ${(p.forma || []).join('/') || '?'}</div>
      <div>${(p.celulas || []).map(c => `<span class="tag">${c}</span>`).join('')} ${(p.requisitos || []).map(r => `<span class="tag">${r}</span>`).join('')}</div>
      <div class="prog" style="margin-top:10px"><b>Progresso:</b> ${sts.map(s => `<button class="${PROG[n] === s ? 'sel' : ''}" onclick="setProg(${n},'${s}');verPeca(${n})">${s.replace('_', ' ')}</button>`).join('')}</div>
      <div class="btnrow" style="justify-content:flex-start;margin-top:12px"><button class="acao" onclick="tocarPeca(${n})">▶ Tocar partitura</button></div>
      <img class="score" loading="lazy" src="./scores/sb-${String(n).padStart(3, '0')}.jpg" alt="partitura ${p.titulo}"
        onerror="this.style.display='none';this.insertAdjacentHTML('afterend','<p class=meta>partitura indisponível offline</p>')">
      ${p.obs ? `<p class="meta" style="font-style:italic;margin-top:8px">${p.obs}</p>` : ''}
    </div>`;
  window.scrollTo(0, 0);
}

function telaVocab() {
  const c = DB.cells || {};
  const li = (arr, play) => (arr || []).map(x =>
    `<li>${play ? `<button class="prog" style="min-width:34px" onclick="tocarCell('${x.id}')">▶</button> ` : ''}<code>${x.id}</code> ${x.nome}${x.descricao ? ' — ' + x.descricao : ''}</li>`).join('');
  tela.innerHTML = `<h2 class="sec">Vocabulário do caderno</h2>
    <p class="meta">Toque ▶ para ouvir e ver cada célula (timbre de trompete, com cursor).</p>
    <div class="card vocab"><h3>Células rítmicas</h3><ul class="lista">${li(c.celulas_ritmicas, true)}</ul></div>
    <div class="card vocab"><h3>Arpejos</h3><ul class="lista">${li(c.arpejos, false)}</ul></div>
    <p class="meta">Quase tudo é 2/4 em poucas células — dominá-las é ler o caderno à primeira vista.</p>`;
}

/* ---------- metrônomo (Web Audio) ---------- */
const M = { ctx: null, on: false, bpm: 100, alvo: 160, rampa: false, beats: 2, beat: 0, next: 0, bars: 0, timer: null };
function metroTela() {
  tela.innerHTML = `<h2 class="sec">Metrônomo</h2><div class="card metro">
    <div class="bpm"><span id="vbpm">${M.bpm}</span> <small>BPM</small></div>
    <input type="range" min="40" max="260" value="${M.bpm}" id="sbpm">
    <div class="beats" id="vbeats"></div>
    <div class="btnrow" style="margin:8px 0">
      <button class="toggle" id="tcomp">2/4</button>
      <button class="toggle ${M.rampa ? 'on' : ''}" id="trampa">rampa → <span id="valvo">${M.alvo}</span></button>
    </div>
    <input type="range" min="60" max="260" value="${M.alvo}" id="salvo" ${M.rampa ? '' : 'disabled'}>
    <div class="btnrow"><button class="acao ${M.on ? 'parar' : ''}" id="bgo">${M.on ? 'parar' : 'iniciar'}</button>
      <button class="toggle" id="btap">tap</button></div>
    <p class="meta" style="margin-top:10px">A rampa sobe 4 BPM a cada 4 compassos até o alvo — pratique a célula lenta e acelere.</p></div>`;
  desenhaBeats();
  $('#sbpm').oninput = e => { M.bpm = +e.target.value; $('#vbpm').textContent = M.bpm; };
  $('#salvo').oninput = e => { M.alvo = +e.target.value; $('#valvo').textContent = M.alvo; };
  $('#tcomp').onclick = e => { M.beats = M.beats === 2 ? 4 : (M.beats === 4 ? 3 : 2); e.target.textContent = M.beats + '/4'; desenhaBeats(); };
  $('#trampa').onclick = e => { M.rampa = !M.rampa; e.target.classList.toggle('on', M.rampa); $('#salvo').disabled = !M.rampa; };
  $('#bgo').onclick = toggleMetro;
  let taps = [];
  $('#btap').onclick = () => { const t = performance.now(); taps = taps.filter(x => t - x < 2000); taps.push(t); if (taps.length > 1) { const d = (taps[taps.length - 1] - taps[0]) / (taps.length - 1); M.bpm = Math.max(40, Math.min(260, Math.round(60000 / d))); $('#vbpm').textContent = M.bpm; $('#sbpm').value = M.bpm; } };
}
function desenhaBeats() { const v = $('#vbeats'); if (v) v.innerHTML = Array.from({ length: M.beats }, (_, i) => `<span class="beat" id="b${i}"></span>`).join(''); }
function toggleMetro() { M.on ? pararMetro() : iniciarMetro(); }
function iniciarMetro() {
  M.ctx = M.ctx || new (window.AudioContext || window.webkitAudioContext)();
  M.ctx.resume(); M.on = true; M.beat = 0; M.bars = 0; M.next = M.ctx.currentTime + 0.1;
  M.timer = setInterval(scheduler, 25);
  const b = $('#bgo'); if (b) { b.textContent = 'parar'; b.classList.add('parar'); }
}
function pararMetro() { M.on = false; clearInterval(M.timer); const b = $('#bgo'); if (b) { b.textContent = 'iniciar'; b.classList.remove('parar'); } }
function scheduler() {
  while (M.next < M.ctx.currentTime + 0.1) {
    click(M.next, M.beat === 0);
    flash(M.beat);
    M.next += 60 / M.bpm;
    M.beat = (M.beat + 1) % M.beats;
    if (M.beat === 0) { M.bars++; if (M.rampa && M.bars % 4 === 0 && M.bpm < M.alvo) { M.bpm = Math.min(M.alvo, M.bpm + 4); const v = $('#vbpm'); if (v) { v.textContent = M.bpm; $('#sbpm').value = M.bpm; } } }
  }
}
function click(t, acc) {
  const o = M.ctx.createOscillator(), g = M.ctx.createGain();
  o.frequency.value = acc ? 1500 : 900; g.gain.value = acc ? 0.5 : 0.3;
  o.connect(g); g.connect(M.ctx.destination);
  o.start(t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.04); o.stop(t + 0.05);
}
function flash(i) { const at = M.next - M.ctx.currentTime; setTimeout(() => { document.querySelectorAll('.beat').forEach((b, j) => b.classList.toggle('on', j === i)); }, Math.max(0, at * 1000)); }

/* ---------- player (abcjs: partitura + MIDI trompete + cursor) ---------- */
let SYNTH = null, PLAYER = null;  // PLAYER = {abc, transpose, titulo, voltar}
async function loadAbc() { if (!DB.abc) DB.abc = await fetch('./data/abc.json').then(r => r.json()).catch(() => ({})); }
function pararSynth() { if (SYNTH) { try { SYNTH.pause(); } catch {} SYNTH = null; } }

async function abrirPlayer(id, titulo, prov, voltar) {
  pararMetro(); await loadAbc();
  const abc = (DB.abc || {})[id];
  PLAYER = abc ? { abc, transpose: 0, titulo, voltar: voltar || 'banco' } : null;
  document.querySelectorAll('.abas button').forEach(b => b.classList.remove('ativa'));
  if (!abc) { tela.innerHTML = `<button class="voltar" onclick="ir('${voltar || 'banco'}')">‹ voltar</button><p class="carregando">partitura não disponível.</p>`; return; }
  tela.innerHTML = `<button class="voltar" onclick="ir('${voltar || 'banco'}')">‹ voltar</button>
    <div class="card">
      <h3>${titulo}</h3>
      ${prov ? '<p class="meta">⚠ transcrição automática (provisória) — as notas podem ter erros; o tom está conferido</p>' : ''}
      <div class="btnrow" style="justify-content:flex-start;margin:4px 0 10px">
        <button class="toggle" id="tconcert">ouvir em concerto</button>
      </div>
      <div id="paper" class="paper"></div>
      <div id="audio" class="audio"></div>
      <p class="meta" style="margin-top:8px">▶ toca com timbre de trompete · ↔ controla o andamento · o cursor segue as notas.</p>
    </div>`;
  $('#tconcert').onclick = e => { const c = e.target.classList.toggle('on'); e.target.textContent = c ? 'ouvir escrito (Bb)' : 'ouvir em concerto'; renderPlayer(c ? -2 : 0); };
  renderPlayer(0);
  window.scrollTo(0, 0);
}

function renderPlayer(transpose) {
  if (!PLAYER) return;
  pararSynth(); PLAYER.transpose = transpose;
  const visual = ABCJS.renderAbc('paper', PLAYER.abc, { add_classes: true, responsive: 'resize', visualTranspose: transpose })[0];
  if (!ABCJS.synth || !ABCJS.synth.supportsAudio()) { $('#audio').innerHTML = '<p class="meta">áudio não suportado neste navegador.</p>'; return; }
  SYNTH = new ABCJS.synth.SynthController();
  SYNTH.load('#audio', cursorCtl(), { displayPlay: true, displayProgress: true, displayWarp: true });
  SYNTH.setTune(visual, false, { program: 56 }).catch(() => {});
}
function cursorCtl() {
  const clear = () => document.querySelectorAll('.abcjs-highlight').forEach(el => el.classList.remove('abcjs-highlight'));
  return { onStart() {}, onFinished() { clear(); }, onEvent(ev) { if (!ev || ev.measureStart && ev.left === null) return; clear(); (ev.elements || []).forEach(s => s.forEach(el => el.classList.add('abcjs-highlight'))); } };
}
window.abrirPlayer = abrirPlayer;
window.tocarPeca = n => { const p = DB.byNum[n]; if (p) abrirPlayer('sb-' + String(n).padStart(3, '0'), String(n).padStart(3, '0') + ' — ' + p.titulo, true, 'banco'); };
window.tocarCell = cid => { const c = (DB.cells?.celulas_ritmicas || []).find(x => x.id === cid) || {}; abrirPlayer('cell-' + cid, 'Célula ' + cid + ' — ' + (c.nome || ''), false, 'vocab'); };

/* ---------- roteador ---------- */
function ir(t) {
  pararSynth();
  if (t !== 'metronomo' && M.on) pararMetro();
  document.querySelectorAll('.abas button').forEach(b => b.classList.toggle('ativa', b.dataset.tela === t));
  ({ hoje: telaHoje, banco: telaBanco, metronomo: metroTela, vocab: telaVocab }[t] || telaHoje)();
  window.scrollTo(0, 0);
}
window.ir = ir; window.verPeca = verPeca; window.setProg = setProg;
document.querySelectorAll('.abas button').forEach(b => b.onclick = () => ir(b.dataset.tela));

if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});
carregar().then(() => ir('hoje')).catch(() => { tela.innerHTML = '<p class="carregando">erro ao carregar os dados.</p>'; });
