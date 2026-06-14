'use strict';
// Sambrass Tutor — PWA (vanilla). Lê ./data/*.json gerados de content/.

const DB = {};            // dados carregados
const $ = (s, e = document) => e.querySelector(s);
const tela = document.getElementById('tela');

async function carregar() {
  const get = async (f) => { try { return await (await fetch('./data/' + f)).json(); } catch { return null; } };
  [DB.pieces, DB.curriculo, DB.trilha, DB.cells, DB.rotina, DB.quality, DB.escada, DB.percurso, DB.lotes] = await Promise.all(
    ['pieces.json', 'curriculum.json', 'trilha.json', 'cells.json', 'rotina.json', 'quality.json', 'escada.json', 'percurso.json', 'lotes.json'].map(get));
  DB.byNum = {}; (DB.pieces?.pieces || []).forEach(p => DB.byNum[p.num] = p);
  DB.nivelByNum = {}; (DB.escada?.pieces || []).forEach(e => DB.nivelByNum[e.num] = e.nivel_minimo);
  DB.percByNum = {}; (DB.percurso || []).forEach(m => DB.percByNum[m.num] = m);
}

/* ---------- progresso (localStorage) ---------- */
const PROG = JSON.parse(localStorage.getItem('sambrass_prog') || '{}');
const setProg = (n, s) => { if (PROG[n] === s) delete PROG[n]; else PROG[n] = s; localStorage.setItem('sambrass_prog', JSON.stringify(PROG)); };

/* progresso SDT (autoavaliação 1–5, sem XP/cadeado) — rota "O Caminho do Sambrass".
   Fonte de verdade = sb2_logs {num:[{d,n}]}; dominada = melhor nível ≥ 4. */
const store = {
  get(k, d) { try { const v = JSON.parse(localStorage.getItem('sb2_' + k)); return v == null ? d : v; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('sb2_' + k, JSON.stringify(v)); } catch {} }
};
const RATELBL = ['', 'tive dificuldade na leitura', 'leio, mas paro/erro', 'toco seguido, lento', 'toco no andamento', 'toco de cor 🎉'];
const LCOR = ['', '#2e6b4f', '#5a7a1f', '#8a5a1f', '#a3431f', '#7a1f1f', '#3a3a3a'];   // cor por lote 1–6
const bestLevel = n => { const l = store.get('logs', {})[n]; return (!l || !l.length) ? 0 : Math.max(...l.map(x => x.n)); };
const isDone = n => bestLevel(n) >= 4;
const countDone = () => (DB.percurso || []).filter(m => isDone(m.num)).length;
const prepDone = () => store.get('prepdone', false);
const markDay = () => { const days = store.get('days', []); const t = new Date().toISOString().slice(0, 10); if (!days.includes(t)) { days.push(t); store.set('days', days); } };
const streakCount = () => { const days = store.get('days', []).slice().sort(); let s = 0, d = new Date(); for (; ;) { const k = d.toISOString().slice(0, 10); if (days.includes(k)) { s++; d.setDate(d.getDate() - 1); } else break; } return s; };
// migração única: 'dominada' do modelo antigo (sambrass_prog) vira um log nível 4
(function migrarProg() {
  if (store.get('migrado', false)) return;
  const logs = store.get('logs', {}), hoje = new Date().toISOString().slice(0, 10);
  Object.keys(PROG).forEach(n => { if (PROG[n] === 'dominada' && !(logs[n] || []).some(x => x.n >= 4)) (logs[n] = logs[n] || []).push({ d: hoje, n: 4 }); });
  store.set('logs', logs); store.set('migrado', true);
})();
const TOM = { C: 'Dó', G: 'Sol', D: 'Ré', A: 'Lá', E: 'Mi', 'F#': 'Fá#', F: 'Fá', Bb: 'Si♭', Eb: 'Mi♭', Ab: 'Lá♭', Db: 'Ré♭', B: 'Si' };
const WRIT = { C: 'D', G: 'A', D: 'E', A: 'B', E: 'F#', 'F#': 'G#', F: 'G', Bb: 'C', Eb: 'F', Ab: 'Bb', Db: 'Eb', B: 'C#' };
const tomEscrito = p => (WRIT[p.key_concert] || p.key_concert) + (p.modulates_to_concert ? '→' + (WRIT[p.modulates_to_concert] || '') : '');
// qualidade da melodia: rascunho (OMR) < dedos (fusão pela digitação) < conferida (à mão)
const QUAL = {
  conferida: { tag: '✓', cls: 'q-ok', txt: 'conferida à mão' },
  dedos: { tag: '♪', cls: 'q-mid', txt: 'tom pelos dedos · oitava/ritmo provisórios' },
  rascunho: { tag: '~', cls: 'q-raw', txt: 'leitura automática (OMR) · em revisão' }
};
const idOf = n => 'sb-' + String(n).padStart(3, '0');
const qualOf = n => (DB.quality && DB.quality[idOf(n)]) || 'rascunho';
// nível pedagógico (escada Book1/2/Arban)
const NIVEL = { book1: 'Book 1', book2: 'Book 2', arban: 'Arban' };
const nivelOf = n => (DB.nivelByNum && DB.nivelByNum[n]) || null;

/* ---------- telas ---------- */
// A home é a Trilha (telaTrilha em trilha.js) — o caminho sugerido estilo Duolingo.

function linhaPeca(n) {
  const p = DB.byNum[n]; if (!p) return '';
  const st = PROG[n] ? ` · ${PROG[n]}` : '';
  const q = QUAL[qualOf(n)];
  return `<li><div class="linha"><button class="playmini" onclick="event.stopPropagation();tocarPeca(${n})" aria-label="tocar">▶</button>
    <a class="peca" href="#" onclick="verPeca(${n});return false">
      <span class="num">${String(n).padStart(3, '0')}</span> ${p.titulo} <span class="qual ${q.cls}" title="melodia: ${q.txt}">${q.tag}</span>
      <span class="dif">${p.dificuldade || '?'}</span>
      <div class="meta">${p.compositor} · ${TOM[p.key_concert] || p.key_concert} · ${p.compasso}${st}${(() => { const nv = nivelOf(n); return nv ? ` · <span class="niv niv-${nv}">${NIVEL[nv]}</span>` : ''; })()}</div></a></div></li>`;
}

function telaBanco() {
  const ps = (DB.pieces?.pieces || []).slice().sort((a, b) => a.num - b.num);
  const inp = 'width:100%;min-height:44px;padding:8px 12px;border:1px solid var(--linha);border-radius:8px;font:inherit;margin-bottom:6px';
  const eff = (k, lab) => `<label class="efflab">${lab} até <select id="f_${k}" class="effsel">${[1, 2, 3, 4, 5, 6].map(i => `<option value="${i}"${i === 6 ? ' selected' : ''}>${i}</option>`).join('')}</select></label>`;
  tela.innerHTML = `<h2 class="sec">Banco — ${ps.length} peças</h2>
    <input id="busca" placeholder="buscar título ou compositor…" style="${inp}">
    <select id="fnivel" style="${inp}">
      <option value="">todos os níveis (escada pedagógica)</option>
      <option value="book1">Book 1 — fundação</option>
      <option value="book2">Book 2 — células/tons novos</option>
      <option value="arban">Arban — ornamento/resistência</option></select>
    <div class="effrow"><span class="meta">esforço:</span> ${eff('agudo', 'agudo')} ${eff('vel', 'veloc.')} ${eff('folego', 'fôlego')}</div>
    <ul class="lista" id="listapecas">${ps.map(p => linhaPeca(p.num)).join('')}</ul>`;
  const aplica = () => {
    const q = ($('#busca').value || '').toLowerCase(), nv = $('#fnivel').value;
    const fa = +$('#f_agudo').value, fv = +$('#f_vel').value, ff = +$('#f_folego').value;
    $('#listapecas').innerHTML = ps.filter(p => {
      const m = DB.percByNum[p.num] || {};
      return (p.titulo + ' ' + p.compositor).toLowerCase().includes(q) && (!nv || nivelOf(p.num) === nv)
        && (m.agudo || 0) <= fa && (m.vel || 0) <= fv && (m.folego || 0) <= ff;
    }).map(p => linhaPeca(p.num)).join('') || '<li class="meta" style="padding:12px">nenhuma peça nesse filtro.</li>';
  };
  $('#busca').oninput = aplica; $('#fnivel').onchange = aplica;
  ['agudo', 'vel', 'folego'].forEach(k => $('#f_' + k).onchange = aplica);
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
      <div class="btnrow" style="justify-content:flex-start;margin-top:12px"><a class="acao" href="./estudo.html?id=sb-${String(n).padStart(3, '0')}">▶ Estudar (partitura + áudio)</a></div>
      ${p.obs ? `<p class="meta" style="font-style:italic;margin-top:10px">${p.obs}</p>` : ''}
    </div>`;
  window.scrollTo(0, 0);
}

function telaVocab() {
  const c = DB.cells || {};
  const li = (arr, play) => (arr || []).map(x =>
    `<li>${play ? `<button class="prog" style="min-width:34px" onclick="tocarCell('${x.id}')">▶</button> ` : ''}<code>${x.id}</code> ${x.nome}${x.descricao ? ' — ' + x.descricao : ''}</li>`).join('');
  tela.innerHTML = `<div class="card" style="text-align:center"><button class="acao" style="width:100%" onclick="openPrep()">🌬️ Aquecimento — 12 exercícios${prepDone() ? ' ✓' : ''}</button>
      <p class="meta" style="margin-top:8px">Prepare o corpo antes de tocar: ar → bocal → som → registro → articulação.</p></div>
    <h2 class="sec">Vocabulário do caderno</h2>
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
// Áudio do celular: 1 AudioContext registrado no abcjs, retomado a cada toque (gesto).
let AC = null;
function audioUnlock() { try { if (!AC) { AC = new (window.AudioContext || window.webkitAudioContext)(); if (window.ABCJS?.synth?.registerAudioContext) ABCJS.synth.registerAudioContext(AC); } if (AC.state === 'suspended') AC.resume(); } catch (e) {} }
['pointerdown', 'touchend'].forEach(ev => document.addEventListener(ev, audioUnlock, { capture: true }));

async function abrirPlayer(id, titulo, prov, voltar) {
  pararMetro(); await loadAbc();
  const abc = (DB.abc || {})[id];
  PLAYER = abc ? { abc, transpose: 0, titulo, voltar: voltar || 'banco' } : null;
  document.querySelectorAll('.abas button').forEach(b => b.classList.remove('ativa'));
  if (!abc) { tela.innerHTML = `<button class="voltar" onclick="ir('${voltar || 'banco'}')">‹ voltar</button><p class="carregando">partitura não disponível.</p>`; return; }
  tela.innerHTML = `<button class="voltar" onclick="ir('${voltar || 'banco'}')">‹ voltar</button>
    <div class="card">
      <h3>${titulo}</h3>
      ${(() => { const t = (DB.quality && DB.quality[id]) || 'rascunho'; if (t === 'conferida') return ''; const m = QUAL[t]; return `<p class="meta">⚠ melodia provisória — ${m.txt}; as células são exatas</p>`; })()}
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
  let visual;
  try {
    visual = ABCJS.renderAbc('paper', PLAYER.abc, { add_classes: true, responsive: 'resize', visualTranspose: transpose })[0];
  } catch (e) { $('#paper').innerHTML = '<p class="meta">não consegui desenhar a partitura.</p>'; return; }
  if (!window.ABCJS || !ABCJS.synth || !ABCJS.synth.supportsAudio()) { $('#audio').innerHTML = '<p class="meta">áudio não suportado neste navegador.</p>'; return; }
  audioUnlock();
  try {
    SYNTH = new ABCJS.synth.SynthController();
    SYNTH.load('#audio', cursorCtl(), { displayPlay: true, displayProgress: true, displayWarp: true, displayLoop: true, displayRestart: true });
    SYNTH.setTune(visual, false, { program: 56, soundFontUrl: './vendor/soundfont/' })
      .catch(e => { const a = $('#audio'); if (a) a.insertAdjacentHTML('beforeend', `<p class="meta">não consegui carregar o som (${e}). Recarregue.</p>`); });
  } catch (e) { $('#audio').innerHTML = `<p class="meta">erro no player: ${e.message}</p>`; }
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
  ({ trilha: telaTrilha, banco: telaBanco, metronomo: metroTela, vocab: telaVocab }[t] || telaTrilha)();
  window.scrollTo(0, 0);
}
window.ir = ir; window.verPeca = verPeca; window.setProg = setProg;
document.querySelectorAll('.abas button').forEach(b => b.onclick = () => ir(b.dataset.tela));

if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(() => {});
carregar().then(() => ir('trilha')).catch(() => { tela.innerHTML = '<p class="carregando">erro ao carregar os dados.</p>'; });
