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
const CENTS_TOL = 50, HOLD_MS = 120, WRONG_MS = 200, POCKET_TOL = 70;   // ±70ms = "no tempo"

let AC = null, MELODIA = null, SYNTH = null, BPM = 92, TR = 0, OCT = 0, VISUAL = null;
let COLORON = localStorage.getItem('chroma-off') !== '1';   // canais de cor Chromatone (noteheads + rolo) — andaime fadeável
let PROLL = null;                                           // API do rolo de alturas (pitch-roll) atual
let RODA = null;                                            // API da roda de ritmo (groove circular)
// posição [0,1) no ciclo do groove, do relógio da BANDA (ou null se a banda está parada)
function groovePhase(){
  if(!window.Groove || !Groove.on) return null;
  const c = Groove.clock(); if(!c.playing || !c.stepDur) return null;
  let cs = c.step - (c.nextT - c.now) / c.stepDur;          // passo contínuo (16 por ciclo)
  cs = ((cs % 16) + 16) % 16;
  return cs / 16;
}
// tutor de escuta
let MIC = null, DET = null, RAF = 0, MICON = false, EXP = null, OCTAVE_EXACT = false;
// grading: oitava exata só na melodia conferida; nos tiers provisórios (dedos/rascunho a
// oitava do OMR não é confiável) avalia pela CLASSE DE ALTURA, evitando falsos vermelhos.
function samePitch(a, b) { return OCTAVE_EXACT ? a === b : ((((a - b) % 12) + 12) % 12) === 0; }
let TIMER = null, PRACTON = false, SCORE = { ok: 0, tot: 0 };
let TIMINGS = [], POCKET = { ok: 0, tot: 0 };   // grade rítmica: onsets vs cursor; baseline = mediana (tira a latência)
let ESPERAR = false, WAITING = false;   // "esperar por mim": cursor só avança quando o mic confirma a nota
let SLICE = null, LOOPON = false, LO_A = 1, LO_B = 1, MCOUNT = 1;
let RAMPON = false, RTARGET = 120;

function audioUnlock(){ try{ if(!AC){ AC = new (window.AudioContext||window.webkitAudioContext)(); ABCJS.synth.registerAudioContext(AC); } if(AC.state==='suspended') AC.resume(); }catch(e){} }
// nota curta (feedback do jogo "monte o riff")
function toneNote(midi){ if(!AC) return; const t=AC.currentTime, o=AC.createOscillator(), g=AC.createGain();
  o.type='triangle'; o.frequency.value=440*Math.pow(2,(midi-69)/12);
  g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(0.26,t+0.01); g.gain.exponentialRampToValueAtTime(0.0001,t+0.32);
  o.connect(g).connect(AC.destination); o.start(t); o.stop(t+0.36); }
['pointerdown','touchend','click'].forEach(ev => document.addEventListener(ev, audioUnlock, {capture:true}));

async function j(f){ try{ return await (await fetch('./data/'+JBASE+f)).json(); }catch{ return null; } }

(async function(){
  const [pieces, cells, abc, escada, abcFull, quality, BLK, pedag, percurso, barsWarn] = await Promise.all([j('pieces.json'), j('cells.json'), j('abc.json'), j('escada.json'),
    JBASE === 'cumbias/' ? j('abc_full.json') : Promise.resolve(null),   // peça inteira só existe nas cumbias
    j('quality.json'),
    fetch('./data/blocos.json').then(r=>r.ok?r.json():null).catch(()=>null),   // índice de blocos (selo/grafismo)
    j('pedagogia.json'),                                                 // desafios da peça → dicas no fluxo (P1③)
    j('percurso.json'),                                                  // pico/agudo p/ o badge de alcance
    j('bars_warn.json')]);                                               // compassos fora da métrica → aviso honesto
  const WR = {C:'D',G:'A',D:'E',A:'B',F:'G',Bb:'C',Eb:'F',Ab:'Bb',E:'F#',Db:'Eb'};
  const NIVEL = {book1:'Book 1', book2:'Book 2', arban:'Arban', riff:'Riff & groove', sincopa:'Síncope', fogo:'Agudo & velocidade'};
  const p = (pieces?.pieces||[]).find(x => x.id===ID);
  const esc = (escada?.pieces||[]).find(x => x.id===ID);
  if(p){ $('#titulo').textContent = p.titulo; $('#byline').textContent = p.compositor;
    const bNivel = esc ? `<span class="badge nivel-${esc.nivel_minimo}">nível <b>${NIVEL[esc.nivel_minimo]||esc.nivel_minimo}</b>${esc.requisito_orfao_book1?.length?` · destrava: ${esc.requisito_orfao_book1.join(', ')}`:''}</span>` : '';
    const perc = (percurso||[]).find(x => x.num === p.num) || {};   // alcance/registro: o que torna a cumbia difícil de verdade
    const bAlc = perc.agudo ? `<span class="badge alc${perc.agudo>=5?' hi':''}" title="${perc.agudo>=5?'registro alto — use 🎺 8ª abaixo se ainda não alcança':'registro confortável'}">🎺 agudo <b>${perc.agudo}/6</b>${perc.pico_nome?` · pico ${perc.pico_nome}`:''}</span>` : '';
    $('#badges').innerHTML = `<span class="badge">tom <b>${WR[p.key_concert]||p.key_concert} maior</b></span><span class="badge">compasso <b>${p.compasso}</b></span><span class="badge">forma <b>${(p.forma||[]).join('/')}</b></span><span class="badge">células <b>${(p.celulas||[]).join(' ')}</b></span>${bNivel}${bAlc}<button class="badge fav" id="tfav" type="button" aria-pressed="false">☆ repertório</button>`;
    { const tf = $('#tfav'); if(tf){                       // ⭐ Meu repertório — marca a peça pra voltar (visível no Progresso)
        const FAVS = () => { try { return JSON.parse(localStorage.getItem('favs')||'[]'); } catch { return []; } };
        const paint = v => { tf.textContent = v ? '★ no repertório' : '☆ repertório'; tf.classList.toggle('on', v); tf.setAttribute('aria-pressed', v?'true':'false'); };
        paint(FAVS().includes(ID));
        tf.onclick = () => { let a = FAVS(); const has = a.includes(ID); a = has ? a.filter(x => x !== ID) : a.concat(ID); localStorage.setItem('favs', JSON.stringify(a)); paint(!has); };
      } }
    if(BLK?.pecas?.[ID]){ const b = BLK.pecas[ID];          // selo do hero = o Lego (mesma língua); fallback grafismo
      if(window.legoMini && b.legos?.length) $('#selo').innerHTML = window.legoMini(b, {w:84, h:84, rhythm:true});
      else if(window.grafismo) $('#selo').innerHTML = grafismo({midis:b.riff&&b.riff.midis, onsets:b.onsets, meter:b.meter, tonica:b.cor.tonica, modo:b.cor.modo, conf:b.cor.conf}, 84);
      const se = $('#selo'); if(se){ se.style.cursor='pointer'; se.title='como esse desenho é feito?'; se.onclick=()=>window.explicaDesenho&&window.explicaDesenho(); } }
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
  // L4/L5: o Lego do CORAÇÃO — os trechos que se repetem, tocáveis e ANIMADOS (mesma língua da trilha/blocos)
  if (window.lego && BLK?.pecas?.[ID]?.legos?.length) {
    const rec = BLK.pecas[ID], lb = $('#legoblk');
    if (lb) {
      lb.innerHTML = '<div class="sec-h">os trechos que se repetem <button class="comofeito" type="button" id="legoexplica">ⓘ como é feito?</button></div>' +
        '<p class="lead">Cada peça é um trecho que <b>volta</b> na música: em cima o <b>contorno</b> (o desenho das notas), embaixo o <b>colar rítmico</b> (a célula). Toque uma peça — ela <b>acende no tempo</b>. São os mesmos Legos da trilha e da exploração.</p>' +
        window.lego(rec);
      const ex = $('#legoexplica'); if(ex) ex.onclick = () => window.explicaDesenho && window.explicaDesenho();
      lb.querySelectorAll('.lego-pc').forEach(pc => pc.onclick = () => {
        lb.querySelectorAll('.lego-pc.on').forEach(e => e.classList.remove('on'));
        pc.classList.add('on'); audioUnlock();
        if (window.legoPlay) window.legoPlay(pc, rec, +pc.dataset.lego, { audioContext: AC, bpm: BPM });
      });
    }
    // JOGO "monte o riff": encaixe os blocos do riff na ordem → reconstrói o contorno e ouve montado
    const mrEl = $('#montariff'), mrWrap = $('#montariff-wrap'), riff = rec.legos[0];
    if (window.montaRiff && mrEl && riff?.midis?.length >= 2) {
      window.montaRiff(mrEl, {
        midis: riff.midis,
        nameOf: m => NOMES[((m % 12) + 12) % 12],
        playNote: m => { audioUnlock(); toneNote(m); },
        playSeq: seq => { audioUnlock(); if (window.legoAbc) playOnce(window.legoAbc(seq, riff.durs || seq.map(() => 1), rec.meter, Math.min(BPM, 96))); }
      });
      if (mrWrap) mrWrap.hidden = false;
    }
  }
  { const formaTxt = (p?.forma||[]).join('/'), longa = (p?.forma||[]).length>=3, hn = cm[HEART]?.nome||HEART;
    const passosArr = [
      `<b>Aqueça</b> e toque a célula ${HEART} (${hn}) — ▶ acima — batendo o pé no tempo.`,
      `Leia a melodia <b>devagar</b> (baixe o BPM), olhando as válvulas, sem parar nos erros.`,
      longa ? `Estude <b>uma seção por vez</b> (forma ${formaTxt}); junte duas só quando cada uma sair de cor.`
            : `Isole o <b>compasso difícil</b> em loop 🔁 e suba o beat aos poucos.`,
      `Toque a frase inteira <b>de cór</b>, no andamento de roda.`];
    const ol = $('#passos'); if(ol) ol.innerHTML = passosArr.map(t => `<li><span class="chk">✓</span><span class="txt">${t}</span></li>`).join(''); }
  if(pedag && pedag[p?.num]?.desafios){ const dz = $('#desafios');                 // P1③: a pedagogia da Story, aqui no fluxo
    if(dz) dz.innerHTML = pedag[p.num].desafios.map(d => `<div class="desafio"><h3>${d.t}</h3>${d.d?`<p>${d.d}</p>`:''}${d.w?`<p class="por">${d.w}</p>`:''}${d.svg||''}</div>`).join(''); }
  { const dz = $('#desafios'); if(dz && p) dz.insertAdjacentHTML('beforeend', improvPanel(p.key_concert, BLK?.pecas?.[ID]?.cor?.modo)); }   // painel de improviso (escala + notas-alvo)

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
  const bw = barsWarn && barsWarn[ID];                                 // compassos que não fecham a métrica (silêncio/duração errada na transcrição)
  const RASC_TEMA = (bw && bw.length)
    ? `Melodia: <span class="ok">tom e notas conferidos</span>, mas <b style="color:var(--vinho2)">${bw.length} compasso${bw.length>1?'s':''} com ritmo/silêncio errado</b> (compasso${bw.length>1?'s':''} ${bw.join(', ')}) — em correção com a partitura. As células acima são exatas.`
    : (RASC[tier] || RASC.rascunho) + (OCTAVE_EXACT ? '' : ' <span class="ok">O tutor avalia pela classe de altura (tolerante à oitava).</span>');
  $('#rasc').innerHTML = RASC_TEMA;
  { const rep = $('#reportar');
    if(rep) rep.onclick = e => { e.preventDefault(); if(window.reportarBeta) reportarBeta({ piece: `${ID}${p?' '+p.titulo:''}`, screen: 'estudo' }); }; }
  if(MELODIA){ setMel(); MCOUNT = Math.max(1, measures(MELODIA).length); LO_A = 1; LO_B = MCOUNT; }
  else { $('#paper').innerHTML = '<p class="nota-rasc">melodia indisponível.</p>'; }

  const syncBand = () => { if(window.Groove && Groove.on) Groove.setBpm(BPM); };
  $('#menos').onclick = () => { BPM = Math.max(50, BPM-2); $('#bpm').textContent = BPM; syncBand(); PRACTON ? restartTimer() : setMel(); };
  $('#mais').onclick  = () => { BPM = Math.min(180, BPM+2); $('#bpm').textContent = BPM; syncBand(); PRACTON ? restartTimer() : setMel(); };
  $('#tconcert').onclick = e => { const c = e.currentTarget.classList.toggle('on'); TR = c?-2:0; e.currentTarget.textContent = c?'🎼 escrito (Sib)':'🎼 em concerto'; setMel(); if(PRACTON) restartTimer(); };
  $('#toct').onclick = e => { const c = e.currentTarget.classList.toggle('on'); OCT = c?-12:0; e.currentTarget.textContent = c?'🔼 voltar à 8ª':'🎺 8ª abaixo'; setMel(); if(PRACTON) restartTimer(); };   // registro grave: alcança o agudo / aquece
  { const tc = $('#tcor'); if(tc){ tc.classList.toggle('on', COLORON); tc.textContent = COLORON ? '🎨 cor: sim' : '🎨 cor: não';
      tc.onclick = () => { COLORON = !COLORON; localStorage.setItem('chroma-off', COLORON ? '0' : '1');
        tc.classList.toggle('on', COLORON); tc.textContent = COLORON ? '🎨 cor: sim' : '🎨 cor: não'; renderChannels(); }; } }   // andaime de cor fadeável (Figurenotes)
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
  { const bandRoot = window.Groove ? Groove.rootFromKey(p?.key_concert) : 41;   // acompanhamento no tom de CONCERTO
    const tb = $('#tband'), bv = $('#bandvol'), rodaEl = $('#roda');
    RODA = (window.RodaRitmo && rodaEl) ? window.RodaRitmo(rodaEl) : null;       // a roda de ritmo (aparece com a banda)
    let bvol = Math.max(0, Math.min(100, +(localStorage.getItem('bandvol') ?? 65)));
    if(bv){ bv.value = bvol;
      bv.oninput = () => { bvol = +bv.value; localStorage.setItem('bandvol', bvol); if(window.Groove) Groove.setVolume(bvol/100); }; }
    if(tb) tb.onclick = () => {
      if(!window.Groove) return;
      if(Groove.on){ Groove.stop(); tb.classList.remove('on'); tb.textContent = '🪘 com a banda';
        if(RODA){ RODA.stop(); RODA.clear(); } if(rodaEl) rodaEl.hidden = true; }
      else { audioUnlock(); Groove.start({audioContext: AC, bpm: BPM, root: bandRoot, volume: bvol/100}); tb.classList.add('on'); tb.textContent = '⏹ parar a banda';
        if(rodaEl) rodaEl.hidden = false; if(RODA) RODA.start(groovePhase); }   // a roda gira no tempo da banda
    }; }
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
  { const tm = $('#tmais'), mo = $('#maisopcoes');   // densidade: avançado colapsado, foco no primário
    if(tm && mo) tm.onclick = () => { const show = mo.hidden; mo.hidden = !show; tm.setAttribute('aria-expanded', show ? 'true' : 'false'); tm.textContent = show ? '⚙ menos opções' : '⚙ mais opções'; }; }
  syncLoopUI(); $('#rampVal').textContent = RTARGET;

  const passos = $('#passos'); const done = JSON.parse(localStorage.getItem('passos-'+ID)||'[]');
  [...passos.children].forEach((li,i) => { if(done.includes(i)) li.classList.add('done');
    li.onclick = () => { li.classList.toggle('done'); const d = [...passos.children].map((x,k) => x.classList.contains('done')?k:-1).filter(k => k>=0); localStorage.setItem('passos-'+ID, JSON.stringify(d)); }; });
})();

// painel "para improvisar": a escala de concerto + as notas do acorde, dos dados (tom+modo)
function improvPanel(keyConcert, modo){
  const PCs = {C:0,'C#':1,Db:1,D:2,'D#':3,Eb:3,E:4,F:5,'F#':6,Gb:6,G:7,'G#':8,Ab:8,A:9,'A#':10,Bb:10,B:11};
  const tpc = PCs[keyConcert]; if(tpc == null) return '';
  const flat = ['F','Bb','Eb','Ab','Db','Gb','Cb'].includes(keyConcert);
  const SH = ['Dó','Dó♯','Ré','Ré♯','Mi','Fá','Fá♯','Sol','Sol♯','Lá','Lá♯','Si'];
  const FL = ['Dó','Ré♭','Ré','Mi♭','Mi','Fá','Sol♭','Sol','Lá♭','Lá','Si♭','Si'];
  const nm = pc => (flat ? FL : SH)[((pc % 12) + 12) % 12];
  const menor = modo === 'menor';
  const steps = menor ? [0,2,3,5,7,8,10] : [0,2,4,5,7,9,11];
  // escala como PALETA (Chromatone): cada grau na cor da sua nota
  const cspan = pc => { const p = ((pc%12)+12)%12;
    const c = window.chroma ? window.chroma.css(p,{s:80,l:38}) : 'var(--tinta)';
    return `<span style="color:${c};font-weight:700">${nm(p)}</span>`; };
  const scale = steps.map(s => cspan((tpc + s) % 12));
  const triad = [0, menor ? 3 : 4, 7].map(s => cspan((tpc + s) % 12));
  return `<div class="desafio"><h3>🎷 Para improvisar</h3>
    <p>Tom <b>${nm(tpc)} ${menor ? 'menor' : 'maior'}</b> (concerto). Escala pra solar por cima do riff:</p>
    <p class="por" style="font-size:15px;color:var(--tinta);letter-spacing:.3px">${scale.join(' · ')}</p>
    <p class="por">Mire as <b>notas do acorde</b> (${triad.join(' ')}) nos tempos fortes e passe pelas outras como ligação. Na cumbia, frases curtas que <b>respondem</b> ao riff — deixe espaço.</p></div>`;
}

async function playOnce(abc){
  if(!abc || !window.ABCJS?.synth?.supportsAudio()) return; audioUnlock();
  try{ let sc = document.getElementById('scratch'); if(!sc){ sc = document.createElement('div'); sc.id = 'scratch'; sc.style.display = 'none'; document.body.appendChild(sc); }
    const v = ABCJS.renderAbc('scratch', abc)[0]; const s = new ABCJS.synth.CreateSynth();
    await s.init({audioContext:AC, visualObj:v, options:{soundFontUrl:'./vendor/soundfont/', program:56}}); await s.prime(); s.start();
  }catch(e){}
}

function setValves(f, col){ for(const i of '123'){ const v = document.getElementById('v'+i), on = !!(f && f.includes(i));
  v.classList.toggle('press', on);                                    // "mão cromática": o pistão pressionado ganha a cor da nota
  if(on && col){ v.classList.add('chroma'); v.style.setProperty('--nc', col); } else { v.classList.remove('chroma'); v.style.removeProperty('--nc'); } } }
function clrHi(){ document.querySelectorAll('.abcjs-highlight').forEach(el => el.classList.remove('abcjs-highlight')); if(PROLL) PROLL.clear(); }
function clrGrade(){ document.querySelectorAll('.abcjs-good,.abcjs-bad').forEach(el => el.classList.remove('abcjs-good','abcjs-bad')); }
function paintScore(){ const e = $('#micscore'); if(e) e.textContent = SCORE.tot ? `sessão: ✓ ${SCORE.ok}/${SCORE.tot}` : ''; }
// --- grade rítmica (pocket): o ataque do aluno vs o cursor, relativo ao próprio baseline ---
function median(a){ if(!a.length) return 0; const s = [...a].sort((x,y)=>x-y), m = s.length>>1; return s.length%2 ? s[m] : (s[m-1]+s[m])/2; }
function recordPocket(delta){
  TIMINGS.push(delta); if(TIMINGS.length > 40) TIMINGS.shift();
  const rel = delta - median(TIMINGS);                 // tira a latência sistêmica → mede a regularidade
  POCKET.tot++; if(Math.abs(rel) <= POCKET_TOL) POCKET.ok++;
  paintPocket(rel);
}
function paintPocket(rel){
  const m = $('#pkmark'), l = $('#pklbl'); if(!m) return;
  const cls = Math.abs(rel) <= POCKET_TOL ? 'ok' : (rel > 0 ? 'late' : 'early');
  m.className = 'pk-mark on ' + cls; m.style.left = Math.max(2, Math.min(98, 50 + rel/4)) + '%';
  if(l){ l.className = 'pk-lbl ' + cls;
    l.textContent = (Math.abs(rel) <= POCKET_TOL ? 'no tempo' : (rel > 0 ? `atrasado +${Math.round(rel)}ms` : `adiantado ${Math.round(-rel)}ms`))
      + ` · regularidade ${POCKET.tot ? Math.round(100*POCKET.ok/POCKET.tot) : 0}%`; }
}
function resetPocket(){ TIMINGS = []; POCKET = { ok: 0, tot: 0 };
  const m = $('#pkmark'), l = $('#pklbl'); if(m) m.className = 'pk-mark'; if(l){ l.className = 'pk-lbl'; l.textContent = 'pocket: toque pra medir'; } }
// persiste a sessão de prática (precisão de notas + regularidade) p/ o Progresso ver a evolução
function logPractice(){
  if((SCORE.tot||0) < 3 && (POCKET.tot||0) < 3) return;              // só sessões com substância
  try{
    const log = JSON.parse(localStorage.getItem('practicelog')||'[]');
    log.push({ d: new Date().toISOString().slice(0,10), id: ID,
      acc: SCORE.tot ? Math.round(100*SCORE.ok/SCORE.tot) : null,
      reg: POCKET.tot ? Math.round(100*POCKET.ok/POCKET.tot) : null, n: SCORE.tot||0 });
    while(log.length > 60) log.shift();
    localStorage.setItem('practicelog', JSON.stringify(log));
  }catch(e){}
}

// mostra a nota atual (highlight + nome + válvulas); grade=true arma a comparação do mic
function showNote(ev, grade){
  clrHi();
  (ev.elements||[]).forEach(s => s.forEach(el => el.classList.add('abcjs-highlight')));
  if(PROLL && ev) PROLL.highlight(PROLL.idxOf(ev.startChar));         // acende o bloco do rolo no mesmo tempo
  const mp = ev.midiPitches && ev.midiPitches[0];
  if(mp){ const w = Math.round(mp.pitch) - TR; const f = fingerOf(w);
    const col = (COLORON && window.chroma) ? window.chroma.css(w, {s:78, l:40}) : '';   // mão cromática
    const na = $('#notaAtual'); na.textContent = NOMES[((w % 12) + 12) % 12]; na.style.color = col;
    $('#dedoAtual').textContent = (f === '0' ? 'solto (0)' : 'dedo ' + f) || '—'; setValves(f, col);
    if(grade){ EXP = {midi: w - 2, els: ev.elements || [], matchedMs: 0, wrongMs: 0, lastTs: performance.now(), painted: null, cursorTs: performance.now(), onsetTs: null}; }
  }
}
function cursor(){ // modo OUVIR (SynthController) — sem graduar (evita o mic julgar o próprio app)
  return { onStart(){ EXP = null; },
    onFinished(){ clrHi(); clrGrade(); setValves(''); const na = $('#notaAtual'); na.textContent = '·'; na.style.color = ''; $('#dedoAtual').textContent = 'fim'; },
    onEvent(ev){ if(!ev) return; showNote(ev, false); } };
}

// lê a melodia renderizada do abcjs: cada nota com {midi (concerto), ms, durMs, startChar}.
// setUpAudio resolve armadura + acidentes; as pausas viram vãos (midiPitches vazio → puladas).
function melodyNotes(){
  const out = { notes: [], totalMs: 0 };
  try{ if(VISUAL){ if(VISUAL.setUpAudio) VISUAL.setUpAudio(); if(VISUAL.setTiming) VISUAL.setTiming(BPM);
    const nt = VISUAL.noteTimings || []; if(!nt.length) return out;
    out.totalMs = nt[nt.length-1].milliseconds || 0;
    for(let k=0;k<nt.length;k++){ const ev = nt[k]; if(ev.type !== 'event') continue;
      let nextMs = out.totalMs; for(let j=k+1;j<nt.length;j++){ if(nt[j].milliseconds != null){ nextMs = nt[j].milliseconds; break; } }
      if(ev.midiPitches && ev.midiPitches.length)
        out.notes.push({ midi: Math.round(ev.midiPitches[0].pitch) - TR, ms: ev.milliseconds || 0,
                         durMs: Math.max(1, nextMs - (ev.milliseconds || 0)), startChar: ev.startChar });
    }
  } }catch(e){}
  return out;
}
// desenha os canais de cor a partir da mesma fonte: (1) noteheads da pauta, (2) rolo de alturas.
// Andaime FADEÁVEL: o toggle 🎨 desliga tudo (volta à pauta preta). Cursor/acerto/erro (!important) vencem.
function renderChannels(){
  const data = melodyNotes();                                         // popula VISUAL.noteTimings (setUpAudio)
  const paper = document.getElementById('paper');
  if(paper){
    const heads = paper.querySelectorAll('.abcjs-notehead');
    heads.forEach(h => { h.style.fill = ''; });                       // reset
    if(COLORON && window.chroma && VISUAL){
      // 1) cada evento sonoro colore o SEU notehead (por referência de DOM → robusto a ligaduras)
      (VISUAL.noteTimings || []).forEach(ev => {
        if(ev.type !== 'event' || !ev.midiPitches || !ev.midiPitches.length) return;
        const col = window.chroma.css(Math.round(ev.midiPitches[0].pitch) - TR);
        (ev.elements || []).forEach(s => s.forEach(el => {
          if(!el) return;
          if(el.classList && el.classList.contains('abcjs-notehead')) el.style.fill = col;
          else if(el.querySelectorAll) el.querySelectorAll('.abcjs-notehead').forEach(h => { h.style.fill = col; });
        }));
      });
      // 2) nota LIGADA (sem evento próprio) herda a cor da anterior em ordem de leitura — mesma altura
      let last = '';
      heads.forEach(h => { if(h.style.fill) last = h.style.fill; else if(last) h.style.fill = last; });
    }
  }
  const proll = document.getElementById('proll');
  if(proll){ PROLL = (COLORON && window.pitchRoll) ? window.pitchRoll(proll, data, {}) : (proll.innerHTML = '', null); }
  const leg = document.getElementById('proll-leg'); if(leg) leg.hidden = !(COLORON && PROLL);   // a legenda segue os canais
}

function setMel(){
  if(!MELODIA) return; audioUnlock();
  const raw = (LOOPON && SLICE) ? SLICE : MELODIA;
  const abc = raw.replace(/Q:1\/4=\d+/, 'Q:1/4=' + BPM).replace(/\nT:[^\n]*/, '');
  if(SYNTH){ try{ SYNTH.pause(); }catch{} }
  const pw = Math.max(280, (($('#paper').clientWidth) || 340) - 26);
  try{ VISUAL = ABCJS.renderAbc('paper', abc, {add_classes:true, staffwidth:pw, visualTranspose:TR+OCT, scale:1, wrap:{preferredMeasuresPerLine:4, minSpacing:1, maxSpacing:1.8, lastLineLimit:true}})[0]; }catch{ return; }
  renderChannels();                                                   // canais de cor: noteheads + rolo de alturas
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
    beatCallback: (b) => { if(!(window.Groove && Groove.on)) clave((b % bpb) === 0); }   // a banda já dá o tempo
  });
}
function startPractice(){
  if(!VISUAL) return; audioUnlock();
  if(SYNTH){ try{ SYNTH.pause(); }catch{} }
  SCORE = { ok: 0, tot: 0 }; paintScore(); resetPocket(); TIMER = newTimer(); TIMER.start(); PRACTON = true;
  $('#tprat').classList.add('on'); $('#tprat').textContent = '⏸ parar';
  const g = $('#tgo'); if(g){ g.classList.add('on'); g.textContent = '⏸ parar'; }
}
function stopPractice(){
  if(TIMER){ try{ TIMER.stop(); }catch{} TIMER = null; }
  logPractice();                                                     // registra a sessão que acabou
  PRACTON = false; WAITING = false; EXP = null; clrHi(); clrGrade(); setValves('');
  { const na = $('#notaAtual'); na.textContent = '·'; na.style.color = ''; } $('#dedoAtual').textContent = 'pronto';
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
  $('#tuner').classList.remove('ativo'); $('#micnota').textContent = 'você: —'; clrGrade(); if(PROLL) PROLL.mirrorOff();
}
function paint(els, cls){ (els||[]).forEach(s => s.forEach(el => { el.classList.remove('abcjs-good','abcjs-bad'); el.classList.add('abcjs-' + cls); })); }
function updateNeedle(pp){
  const nd = $('#needle'), rd = $('#micnota');
  if(!nd) return;
  if(pp){
    nd.style.left = Math.max(0, Math.min(100, 50 + pp.cents)) + '%';
    nd.style.opacity = 1;
    rd.textContent = `você: ${NOMES[((pp.midi % 12) + 12) % 12]} ${pp.cents >= 0 ? '+' : ''}${pp.cents}¢`;
    rd.style.color = (COLORON && window.chroma) ? window.chroma.css(pp.midi, {s:80, l:38}) : '';   // sua nota, na cor dela
    nd.classList.toggle('intune', Math.abs(pp.cents) <= CENTS_TOL && EXP && samePitch(pp.midi, EXP.midi));
  }else{
    nd.style.opacity = .25; rd.textContent = 'você: —'; rd.style.color = ''; nd.classList.remove('intune');
  }
}
function micLoop(){
  if(!MICON) return;
  const now = performance.now();
  let pp = null; try{ pp = DET ? DET.detect() : null; }catch(e){}
  updateNeedle(pp);
  if(PROLL){                                                          // Espelho: sua altura ao vivo no rolo
    if(EXP && pp){
      let dev = ((((pp.midi - EXP.midi) % 12) + 12) % 12); if(dev > 6) dev -= 12;   // semitom, dobrado à oitava
      dev += (pp.cents || 0) / 100;
      PROLL.mirror(dev, samePitch(pp.midi, EXP.midi) && Math.abs(pp.cents) <= CENTS_TOL);
    }else PROLL.mirrorOff();
  }
  if(EXP){
    const dt = now - (EXP.lastTs || now); EXP.lastTs = now;
    if(pp && samePitch(pp.midi, EXP.midi) && Math.abs(pp.cents) <= CENTS_TOL){
      if(EXP.onsetTs == null && EXP.cursorTs != null){ EXP.onsetTs = now; recordPocket(now - EXP.cursorTs);   // 1º ataque certo → mede o tempo
        if(RODA && window.Groove && Groove.on) RODA.hit(); }                     // …e pousa o ponto na roda (trave no giro)
      EXP.matchedMs += dt;
      if(EXP.matchedMs >= HOLD_MS && EXP.painted !== 'good'){ paint(EXP.els, 'good'); EXP.painted = 'good'; SCORE.ok++; SCORE.tot++; paintScore();
        if(WAITING){ WAITING = false; if(TIMER) try{ TIMER.start(); }catch{} } }   // acertou → avança o cursor
    }else if(pp){
      EXP.wrongMs += dt;
      if(EXP.wrongMs >= WRONG_MS && !EXP.painted){ paint(EXP.els, 'bad'); EXP.painted = 'bad'; SCORE.tot++; paintScore(); }
    }
  }
  RAF = requestAnimationFrame(micLoop);
}
