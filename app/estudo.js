/* Sambrass Tutor — página de estudo. Cursor + digitação ao vivo, e o TUTOR DE ESCUTA:
 * microfone → feedback play-along (verde/vermelho + agulha de cents), loop de trecho e
 * rampa de andamento. Sem dependências além do abcjs (vendor) e do pitch-detector (vendor).
 *
 * Modos:
 *  - OUVIR  (SynthController): toca o trompete pelos alto-falantes (como antes).
 *  - PRATICAR (TimingCallbacks): cursor silencioso + clave de groove; o aluno toca a melodia
 *    e o microfone gradua a nota atual. Silencioso de propósito — evita o mic ouvir o app.
 */
const ID = new URLSearchParams(location.search).get('id') || 'sb-011';
const JBASE = new URLSearchParams(location.search).get('jornada') === 'cumbias' ? 'cumbias/' : '';   // jornada → base dos dados
// células reais da peça → "o coração" = a mais saliente presente (não mais fixo C2/C1/C5)
const CUMBIA = JBASE === 'cumbias/';
const HEARTPRI = CUMBIA ? ['C6', 'C4', 'C3', 'C1', 'C2', 'C5', 'C7'] : ['C2', 'C6', 'C5', 'C4', 'C3', 'C7', 'C1'];
const HEARTH2 = CUMBIA
  ? { C6: 'O contratempo que balança a cumbia', C4: 'A semicolcheia que enfeita o riff', C3: 'A colcheia pontuada — o trote', C1: 'As colcheias da güira — a base', C2: 'A síncope que puxa o riff', C5: 'A tercina contra a divisão', C7: 'A anacruse: entrar antes do tempo' }
  : { C2: 'A síncope que move o samba', C6: 'O contratempo que dá o gingado', C5: 'A tercina contra a divisão binária', C4: 'A semicolcheia e o tu-ku', C3: 'A colcheia pontuada — o galope', C7: 'A anacruse: entrar antes do tempo', C1: 'As colcheias em grupo' };
const $ = s => document.querySelector(s);
const NOMES = ['Dó', 'Dó♯', 'Ré', 'Ré♯', 'Mi', 'Fá', 'Fá♯', 'Sol', 'Sol♯', 'Lá', 'Lá♯', 'Si'];
const SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const VALV = {'F#3':'123','G3':'13','G#3':'23','A3':'12','A#3':'1','B3':'2','C4':'0','C#4':'123','D4':'13','D#4':'23','E4':'12','F4':'1','F#4':'2','G4':'0','G#4':'23','A4':'12','A#4':'1','B4':'2','C5':'0','C#5':'12','D5':'1','D#5':'2','E5':'0','F5':'1','F#5':'2','G5':'0','G#5':'23','A5':'12','A#5':'1','B5':'2','C6':'0'};
function fingerOf(midi){ return VALV[SHARP[((midi % 12) + 12) % 12] + (Math.floor(midi / 12) - 1)]; }

// tolerâncias do tutor
const CENTS_TOL = 50, HOLD_MS = 120, WRONG_MS = 200;

let AC = null, MELODIA = null, SYNTH = null, BPM = 92, TR = 0, VISUAL = null;
// tutor de escuta
let MIC = null, DET = null, RAF = 0, MICON = false, EXP = null, OCTAVE_EXACT = false;
// grading: oitava exata só na melodia conferida; nos tiers provisórios (dedos/rascunho a
// oitava do OMR não é confiável) avalia pela CLASSE DE ALTURA, evitando falsos vermelhos.
function samePitch(a, b) { return OCTAVE_EXACT ? a === b : ((((a - b) % 12) + 12) % 12) === 0; }
let TIMER = null, PRACTON = false;
let ESPERAR = false, WAITING = false;   // "esperar por mim": cursor só avança quando o mic confirma a nota
let SLICE = null, LOOPON = false, LO_A = 1, LO_B = 1, MCOUNT = 1;
let RAMPON = false, RTARGET = 120;

function audioUnlock(){ try{ if(!AC){ AC = new (window.AudioContext||window.webkitAudioContext)(); ABCJS.synth.registerAudioContext(AC); } if(AC.state==='suspended') AC.resume(); }catch(e){} }
['pointerdown','touchend','click'].forEach(ev => document.addEventListener(ev, audioUnlock, {capture:true}));

async function j(f){ try{ return await (await fetch('./data/'+JBASE+f)).json(); }catch{ return null; } }

(async function(){
  const [pieces, cells, abc, escada, abcFull, quality, BLK] = await Promise.all([j('pieces.json'), j('cells.json'), j('abc.json'), j('escada.json'),
    JBASE === 'cumbias/' ? j('abc_full.json') : Promise.resolve(null),   // peça inteira só existe nas cumbias
    j('quality.json'),
    fetch('./data/blocos.json').then(r=>r.ok?r.json():null).catch(()=>null)]);   // índice de blocos (selo/grafismo)
  const WR = {C:'D',G:'A',D:'E',A:'B',F:'G',Bb:'C',Eb:'F',Ab:'Bb',E:'F#',Db:'Eb'};
  const NIVEL = {book1:'Book 1', book2:'Book 2', arban:'Arban', riff:'Riff & groove', sincopa:'Síncope', fogo:'Agudo & velocidade'};
  const p = (pieces?.pieces||[]).find(x => x.id===ID);
  const esc = (escada?.pieces||[]).find(x => x.id===ID);
  if(p){ $('#titulo').textContent = p.titulo; $('#byline').textContent = p.compositor;
    const bNivel = esc ? `<span class="badge nivel-${esc.nivel_minimo}">nível <b>${NIVEL[esc.nivel_minimo]||esc.nivel_minimo}</b>${esc.requisito_orfao_book1?.length?` · destrava: ${esc.requisito_orfao_book1.join(', ')}`:''}</span>` : '';
    $('#badges').innerHTML = `<span class="badge">tom <b>${WR[p.key_concert]||p.key_concert} maior</b></span><span class="badge">compasso <b>${p.compasso}</b></span><span class="badge">forma <b>${(p.forma||[]).join('/')}</b></span><span class="badge">células <b>${(p.celulas||[]).join(' ')}</b></span>${bNivel}`;
    if(window.grafismo && BLK?.pecas?.[ID]){ const b = BLK.pecas[ID];
      $('#selo').innerHTML = grafismo({midis:b.riff&&b.riff.midis, onsets:b.onsets, meter:b.meter, tonica:b.cor.tonica, modo:b.cor.modo, conf:b.cor.conf}, 84); }
    if(CUMBIA && esc){ const cb = {riff:1, sincopa:2, fogo:3}[esc.nivel_minimo];   // ponte reversa: aquece com o bloco do Cichowicz que prepara este lote
      if(cb) $('#badges').insertAdjacentHTML('beforeend', ` <a class="badge warm" href="./respira.html" title="Flow do Cichowicz que prepara este lote">🫁 aqueça: Bloco ${cb}</a>`); } }
  const cm = {}; (cells?.celulas_ritmicas||[]).forEach(c => cm[c.id]=c);
  const presentes = (p?.celulas||[]).filter(id => cm[id] && abc?.['cell-'+id]);
  const ordenadas = HEARTPRI.filter(id => presentes.includes(id)).concat(presentes.filter(id => !HEARTPRI.includes(id)));
  const CEL = (ordenadas.length ? ordenadas : ['C1']).slice(0,4);
  const HEART = CEL[0];
  { const h2 = $('#celH2'); if(h2) h2.textContent = HEARTH2[HEART] || 'As células desta peça'; }
  $('#celulas').innerHTML = CEL.map((id,i) => `<div class="pane cel ${id===HEART?'heart':''}" style="animation-delay:${i*.08}s">
    <button class="play" data-abc="cell-${id}" aria-label="tocar ${id}">▶</button>
    <div><h3>${id} · ${cm[id]?.nome||''}${id===HEART?' — o coração':''}</h3><div class="d">${cm[id]?.descricao||''}</div><div class="mini" id="mini-${id}"></div></div></div>`).join('');
  CEL.forEach(id => { if(abc?.['cell-'+id]) try{ ABCJS.renderAbc('mini-'+id, abc['cell-'+id].replace(/\nT:[^\n]*/,'').replace(/\nQ:[^\n]*/,''), {staffwidth:235,scale:1.35,paddingtop:2,paddingbottom:2,paddingleft:0,paddingright:0}); }catch{} });
  document.querySelectorAll('.play').forEach(b => b.onclick = () => playOnce(abc?.[b.dataset.abc]));
  { const formaTxt = (p?.forma||[]).join('/'), longa = (p?.forma||[]).length>=3, hn = cm[HEART]?.nome||HEART;
    const passosArr = [
      `<b>Aqueça</b> e toque a célula ${HEART} (${hn}) — ▶ acima — batendo o pé no tempo.`,
      `Leia a melodia <b>devagar</b> (baixe o BPM), olhando as válvulas, sem parar nos erros.`,
      longa ? `Estude <b>uma seção por vez</b> (forma ${formaTxt}); junte duas só quando cada uma sair de cor.`
            : `Isole o <b>compasso difícil</b> em loop 🔁 e suba o beat aos poucos.`,
      `Toque a frase inteira <b>de cór</b>, no andamento de roda.`];
    const ol = $('#passos'); if(ol) ol.innerHTML = passosArr.map(t => `<li><span class="chk">✓</span><span class="txt">${t}</span></li>`).join(''); }

  const TEMA = abc?.[ID] || null;
  const FULL = (abcFull && abcFull[ID]) || null;        // peça inteira (só nas cumbias OMR)
  const TEM_DOIS = !!(FULL && TEMA && FULL !== TEMA);    // há tema + peça inteira distintos?
  MELODIA = TEMA;                                        // pratica/avalia o TEMA por padrão
  const RASC = {
    conferida: 'Melodia <span class="ok">conferida ✓</span> · digitação de trompete.',
    dedos: 'Melodia <span class="ok">tom pelos dedos ✓</span> — a classe de altura veio da <b>digitação impressa</b>; oitava e ritmo do OMR (provisórios). As células acima são exatas.',
    rascunho: 'Melodia: rascunho de leitura automática (OMR), em revisão. As células acima são exatas.'
  };
  // tier do TEMA praticado: lê o quality.json padrão (cumbias não têm _quality embutido no abc.json)
  const tier = (quality && quality[ID]) || abc?._quality?.[ID] || (abc?._verified?.includes?.(ID) ? 'conferida' : 'rascunho');
  OCTAVE_EXACT = (tier === 'conferida');
  const RASC_TEMA = (RASC[tier] || RASC.rascunho) + (OCTAVE_EXACT ? '' : ' <span class="ok">O tutor avalia pela classe de altura (tolerante à oitava).</span>');
  $('#rasc').innerHTML = RASC_TEMA;
  { const rep = $('#reportar');
    if(rep) rep.onclick = e => { e.preventDefault(); if(window.reportarBeta) reportarBeta({ piece: `${ID}${p?' '+p.titulo:''}`, screen: 'estudo' }); }; }
  if(MELODIA){ setMel(); MCOUNT = Math.max(1, measures(MELODIA).length); LO_A = 1; LO_B = MCOUNT; }
  else { $('#paper').innerHTML = '<p class="nota-rasc">melodia indisponível.</p>'; }

  $('#menos').onclick = () => { BPM = Math.max(50, BPM-2); $('#bpm').textContent = BPM; PRACTON ? restartTimer() : setMel(); };
  $('#mais').onclick  = () => { BPM = Math.min(180, BPM+2); $('#bpm').textContent = BPM; PRACTON ? restartTimer() : setMel(); };
  $('#tconcert').onclick = e => { const c = e.currentTarget.classList.toggle('on'); TR = c?-2:0; e.currentTarget.textContent = c?'ouvir escrito (Bb)':'ouvir em concerto'; setMel(); if(PRACTON) restartTimer(); };
  // "os dois": pratica o TEMA; este botão toca/mostra a PEÇA INTEIRA (só quando há uma distinta)
  { const tFull = $('#tfull');
    if(tFull && !TEM_DOIS){ tFull.style.display = 'none'; }
    else if(tFull){ tFull.onclick = e => {
      const on = e.currentTarget.classList.toggle('on');
      MELODIA = on ? FULL : TEMA;
      e.currentTarget.textContent = on ? '↩ voltar ao tema' : '▶ tocar a peça inteira';
      if(PRACTON) stopPractice();                                  // avaliação é só no tema
      if(LOOPON){ LOOPON = false; $('#tloop')?.classList.remove('on'); SLICE = null; $('#loopchip').textContent = ''; }
      MCOUNT = Math.max(1, measures(MELODIA).length); LO_A = 1; LO_B = MCOUNT; syncLoopUI();
      $('#rasc').innerHTML = on ? 'Peça inteira: leitura automática (OMR), em revisão — o <b>tema</b> acima é o que você pratica/avalia.' : RASC_TEMA;
      setMel();
    }; } }

  // --- tutor de escuta ---
  $('#tmic').onclick = () => MICON ? disableMic() : enableMic();
  $('#tprat').onclick = () => PRACTON ? stopPractice() : startPractice();
  $('#tgo').onclick = async () => {   // um clique: admite o microfone + começa a praticar
    if(PRACTON){ stopPractice(); return; }
    audioUnlock();
    if(!MICON){ try{ await enableMic(); }catch{} }
    startPractice();
  };
  $('#tloop').onclick = e => { LOOPON = e.currentTarget.classList.toggle('on'); applyLoop(); };
  $('#laMinus').onclick = () => { LO_A = Math.max(1, Math.min(LO_A-1, LO_B)); syncLoopUI(); if(LOOPON) applyLoop(); };
  $('#laPlus').onclick  = () => { LO_A = Math.min(LO_B, LO_A+1); syncLoopUI(); if(LOOPON) applyLoop(); };
  $('#lbMinus').onclick = () => { LO_B = Math.max(LO_A, LO_B-1); syncLoopUI(); if(LOOPON) applyLoop(); };
  $('#lbPlus').onclick  = () => { LO_B = Math.min(MCOUNT, LO_B+1); syncLoopUI(); if(LOOPON) applyLoop(); };
  $('#tramp').onclick = e => { RAMPON = e.currentTarget.classList.toggle('on'); };
  $('#raMinus').onclick = () => { RTARGET = Math.max(60, RTARGET-4); $('#rampVal').textContent = RTARGET; };
  $('#raPlus').onclick  = () => { RTARGET = Math.min(180, RTARGET+4); $('#rampVal').textContent = RTARGET; };
  $('#tesp').onclick = e => { ESPERAR = e.currentTarget.classList.toggle('on'); if(!ESPERAR && WAITING){ WAITING = false; if(TIMER) try{ TIMER.start(); }catch{} } };
  syncLoopUI(); $('#rampVal').textContent = RTARGET;

  const passos = $('#passos'); const done = JSON.parse(localStorage.getItem('passos-'+ID)||'[]');
  [...passos.children].forEach((li,i) => { if(done.includes(i)) li.classList.add('done');
    li.onclick = () => { li.classList.toggle('done'); const d = [...passos.children].map((x,k) => x.classList.contains('done')?k:-1).filter(k => k>=0); localStorage.setItem('passos-'+ID, JSON.stringify(d)); }; });
})();

async function playOnce(abc){
  if(!abc || !window.ABCJS?.synth?.supportsAudio()) return; audioUnlock();
  try{ let sc = document.getElementById('scratch'); if(!sc){ sc = document.createElement('div'); sc.id = 'scratch'; sc.style.display = 'none'; document.body.appendChild(sc); }
    const v = ABCJS.renderAbc('scratch', abc)[0]; const s = new ABCJS.synth.CreateSynth();
    await s.init({audioContext:AC, visualObj:v, options:{soundFontUrl:'./vendor/soundfont/', program:56}}); await s.prime(); s.start();
  }catch(e){}
}

function setValves(f){ for(const i of '123'){ document.getElementById('v'+i).classList.toggle('press', f && f.includes(i)); } }
function clrHi(){ document.querySelectorAll('.abcjs-highlight').forEach(el => el.classList.remove('abcjs-highlight')); }
function clrGrade(){ document.querySelectorAll('.abcjs-good,.abcjs-bad').forEach(el => el.classList.remove('abcjs-good','abcjs-bad')); }

// mostra a nota atual (highlight + nome + válvulas); grade=true arma a comparação do mic
function showNote(ev, grade){
  clrHi();
  (ev.elements||[]).forEach(s => s.forEach(el => el.classList.add('abcjs-highlight')));
  const mp = ev.midiPitches && ev.midiPitches[0];
  if(mp){ const w = Math.round(mp.pitch) - TR; const f = fingerOf(w);
    $('#notaAtual').textContent = NOMES[((w % 12) + 12) % 12];
    $('#dedoAtual').textContent = (f === '0' ? 'solto (0)' : 'dedo ' + f) || '—'; setValves(f);
    if(grade){ EXP = {midi: w - 2, els: ev.elements || [], matchedMs: 0, wrongMs: 0, lastTs: performance.now(), painted: null}; }
  }
}
function cursor(){ // modo OUVIR (SynthController) — sem graduar (evita o mic julgar o próprio app)
  return { onStart(){ EXP = null; },
    onFinished(){ clrHi(); clrGrade(); setValves(''); $('#notaAtual').textContent = '·'; $('#dedoAtual').textContent = 'fim'; },
    onEvent(ev){ if(!ev) return; showNote(ev, false); } };
}

function setMel(){
  if(!MELODIA) return; audioUnlock();
  const raw = (LOOPON && SLICE) ? SLICE : MELODIA;
  const abc = raw.replace(/Q:1\/4=\d+/, 'Q:1/4=' + BPM).replace(/\nT:[^\n]*/, '');
  if(SYNTH){ try{ SYNTH.pause(); }catch{} }
  const pw = Math.max(280, (($('#paper').clientWidth) || 340) - 26);
  try{ VISUAL = ABCJS.renderAbc('paper', abc, {add_classes:true, staffwidth:pw, visualTranspose:TR, scale:1, wrap:{preferredMeasuresPerLine:4, minSpacing:1, maxSpacing:1.8, lastLineLimit:true}})[0]; }catch{ return; }
  if(!window.ABCJS?.synth?.supportsAudio()){ $('#audio').innerHTML = '<p class="nota-rasc">áudio não suportado.</p>'; return; }
  try{ SYNTH = new ABCJS.synth.SynthController();
    SYNTH.load('#audio', cursor(), {displayPlay:true, displayProgress:true, displayLoop:true, displayRestart:true});
    SYNTH.setTune(VISUAL, false, {program:56, soundFontUrl:'./vendor/soundfont/'}).catch(() => {});
  }catch(e){}
}

/* ---------------- loop de trecho (fatia o ABC por compasso) ---------------- */
function tuneParts(melodia){
  const lines = melodia.replace(/\nT:[^\n]*/, '').split('\n');
  const ki = lines.findIndex(l => /^K:/.test(l));
  if(ki < 0) return {header: '', body: melodia};
  const header = lines.slice(0, ki + 1).join('\n');
  const body = lines.slice(ki + 1).filter(l => l && !l.startsWith('%')).join(' ');
  return {header, body};
}
function measures(melodia){
  return tuneParts(melodia).body.split('|').map(s => s.trim()).filter(s => s.length);
}
function sliceABC(melodia, a, b){
  const {header} = tuneParts(melodia); const ms = measures(melodia);
  a = Math.max(0, Math.min(a, ms.length - 1)); b = Math.max(a, Math.min(b, ms.length - 1));
  return header + '\n' + ms.slice(a, b + 1).join(' | ') + ' |]';
}
function applyLoop(){
  SLICE = LOOPON ? sliceABC(MELODIA, LO_A - 1, LO_B - 1) : null;
  $('#loopchip').textContent = LOOPON ? `compassos ${LO_A}–${LO_B}` : '';
  setMel();
  if(PRACTON) restartTimer();
}
function syncLoopUI(){ $('#laVal').textContent = LO_A; $('#lbVal').textContent = LO_B; if(LOOPON) $('#loopchip').textContent = `compassos ${LO_A}–${LO_B}`; }

/* ---------------- praticar (cursor silencioso + clave + mic) ---------------- */
function beatsPerBar(){ const m = MELODIA && MELODIA.match(/M:\s*(\d+)/); return m ? +m[1] : 2; }
function clave(accent){
  if(!AC) return;
  const t = AC.currentTime, o = AC.createOscillator(), g = AC.createGain();
  o.type = 'square'; o.frequency.value = accent ? 2100 : 1500;
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(accent ? 0.4 : 0.22, t + 0.001);
  g.gain.exponentialRampToValueAtTime(0.0001, t + 0.05);
  o.connect(g).connect(AC.destination); o.start(t); o.stop(t + 0.06);
}
function newTimer(){
  const bpb = beatsPerBar();
  return new ABCJS.TimingCallbacks(VISUAL, {
    qpm: BPM,
    eventCallback: practiceEvent,
    beatCallback: (b) => { clave((b % bpb) === 0); }
  });
}
function startPractice(){
  if(!VISUAL) return; audioUnlock();
  if(SYNTH){ try{ SYNTH.pause(); }catch{} }
  TIMER = newTimer(); TIMER.start(); PRACTON = true;
  $('#tprat').classList.add('on'); $('#tprat').textContent = '⏸ parar';
  const g = $('#tgo'); if(g){ g.classList.add('on'); g.textContent = '⏸ parar'; }
}
function stopPractice(){
  if(TIMER){ try{ TIMER.stop(); }catch{} TIMER = null; }
  PRACTON = false; WAITING = false; EXP = null; clrHi(); clrGrade(); setValves('');
  $('#notaAtual').textContent = '·'; $('#dedoAtual').textContent = 'pronto';
  $('#tprat').classList.remove('on'); $('#tprat').textContent = '▶ praticar';
  const g = $('#tgo'); if(g){ g.classList.remove('on'); g.textContent = '▶ Tocar com o tutor'; }
}
function restartTimer(){ if(!PRACTON) return; if(TIMER){ try{ TIMER.stop(); }catch{} } TIMER = newTimer(); TIMER.start(); }
function practiceEvent(ev){
  if(!ev){ // fim do trecho → loopa (sobe o andamento se a rampa estiver ligada)
    clrHi(); EXP = null;
    if(PRACTON){
      if(RAMPON && BPM < RTARGET){ BPM = Math.min(RTARGET, BPM + 2); $('#bpm').textContent = BPM; }
      restartTimer();
    }
    return;
  }
  showNote(ev, MICON);   // gradua só se o mic estiver ligado
  if(ESPERAR && MICON && TIMER){ try{ TIMER.pause(); }catch{} WAITING = true; }   // espera você acertar
}

/* ---------------- microfone + agulha de afinação ---------------- */
async function enableMic(){
  audioUnlock();
  try{
    MIC = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false, noiseSuppression:false, autoGainControl:false}});
    DET = new PitchDetector(AC, MIC, {minHz:120, maxHz:1300});
    MICON = true;
    $('#tmic').classList.add('on'); $('#tmic').textContent = '🎤 ouvindo';
    $('#tuner').classList.add('ativo');
    RAF = requestAnimationFrame(micLoop);
  }catch(e){
    MICON = false;
    $('#tuner').classList.add('ativo');
    $('#micnota').innerHTML = 'sem acesso ao microfone — toque <b>🎤 ouvir meu som</b> de novo e <b>permita</b>; ou siga sem avaliar (clave + cursor funcionam).';
    $('#tmic').classList.remove('on'); $('#tmic').textContent = '🎤 ouvir meu som';
  }
}
function disableMic(){
  MICON = false; cancelAnimationFrame(RAF);
  if(DET){ try{ DET.close(); }catch{} DET = null; } MIC = null;
  $('#tmic').classList.remove('on'); $('#tmic').textContent = '🎤 ouvir meu som';
  $('#tuner').classList.remove('ativo'); $('#micnota').textContent = 'você: —'; clrGrade();
}
function paint(els, cls){ (els||[]).forEach(s => s.forEach(el => { el.classList.remove('abcjs-good','abcjs-bad'); el.classList.add('abcjs-' + cls); })); }
function updateNeedle(pp){
  const nd = $('#needle'), rd = $('#micnota');
  if(!nd) return;
  if(pp){
    nd.style.left = Math.max(0, Math.min(100, 50 + pp.cents)) + '%';
    nd.style.opacity = 1;
    rd.textContent = `você: ${NOMES[((pp.midi % 12) + 12) % 12]} ${pp.cents >= 0 ? '+' : ''}${pp.cents}¢`;
    nd.classList.toggle('intune', Math.abs(pp.cents) <= CENTS_TOL && EXP && samePitch(pp.midi, EXP.midi));
  }else{
    nd.style.opacity = .25; rd.textContent = 'você: —'; nd.classList.remove('intune');
  }
}
function micLoop(){
  if(!MICON) return;
  const now = performance.now();
  let pp = null; try{ pp = DET ? DET.detect() : null; }catch(e){}
  updateNeedle(pp);
  if(EXP){
    const dt = now - (EXP.lastTs || now); EXP.lastTs = now;
    if(pp && samePitch(pp.midi, EXP.midi) && Math.abs(pp.cents) <= CENTS_TOL){
      EXP.matchedMs += dt;
      if(EXP.matchedMs >= HOLD_MS && EXP.painted !== 'good'){ paint(EXP.els, 'good'); EXP.painted = 'good';
        if(WAITING){ WAITING = false; if(TIMER) try{ TIMER.start(); }catch{} } }   // acertou → avança o cursor
    }else if(pp){
      EXP.wrongMs += dt;
      if(EXP.wrongMs >= WRONG_MS && !EXP.painted){ paint(EXP.els, 'bad'); EXP.painted = 'bad'; }
    }
  }
  RAF = requestAnimationFrame(micLoop);
}
