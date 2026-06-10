/* Bench de transcrição (página): mini-parser do dialeto ABC do repo, sintetizador de
 * "performance" com os samples reais de trompete do app (soundfont) e detecção offline
 * com o pitch-detector de produção. Chamado pelo bench_sb011.mjs via page.evaluate().
 */
'use strict';

/* ---------- mini-parser do dialeto ABC do repo ----------
 * Cobre exatamente o que to_abc/notes_manual emitem: L:1/16, M:2/4, K:<letra>,
 * acidentes explícitos [_^=] (persistem no compasso), oitavas ,/', ligadura '-',
 * quiáltera '(3', barras | e |]. Célula = 1/12 de tempo (semicolcheia=3, tercina=4).
 */
function parseAbc(abc) {
  var fifthsMap = { 'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6, 'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6 };
  var SH = ['F', 'C', 'G', 'D', 'A', 'E', 'B'], FL = ['B', 'E', 'A', 'D', 'G', 'C', 'F'];
  var BASE = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  var bpm = 92, fifths = 0, meterCells = 24, unitCells = 3, body = [];

  abc.split('\n').forEach(function (ln) {
    var s = ln.trim();
    if (!s || s[0] === '%') return;
    var h = /^([A-Za-z]):(.*)$/.exec(s);
    if (h && h[1].length === 1) {
      var v = h[2].trim();
      if (h[1] === 'K') fifths = fifthsMap[v.split(/[\s]/)[0]] || 0;
      else if (h[1] === 'M') { var ab = v.split('/').map(Number); meterCells = Math.round(ab[0] * (4 / ab[1]) * 12); }
      else if (h[1] === 'L') { var lu = v.split('/').map(Number); unitCells = Math.round((lu[0] / lu[1]) * 4 * 12); }
      else if (h[1] === 'Q') { var q = /=\s*(\d+)/.exec(v); if (q) bpm = +q[1]; }
      return;
    }
    body.push(s);
  });

  function keyAcc(letter) {
    if (fifths > 0) return SH.indexOf(letter) < fifths ? 1 : 0;
    if (fifths < 0) return FL.indexOf(letter) < -fifths ? -1 : 0;
    return 0;
  }

  var events = [], cur = 0, barStart = 0, violations = [], measureAcc = {}, tup = 0, lastTied = null;
  var re = /(\|\]?)|(\(3)|z(\d*)|([_^=]?)([A-Ga-g])([,']*)(\d*)(-?)/g, m;
  var text = body.join(' ');
  while ((m = re.exec(text)) !== null) {
    if (m[1]) {                                        // barra: valida soma e zera acidentes
      if (cur > barStart && cur - barStart !== meterCells)
        violations.push('compasso em ' + barStart + ' soma ' + (cur - barStart) + ' células (esperado ' + meterCells + ')');
      barStart = cur; measureAcc = {};
      continue;
    }
    if (m[2]) { tup = 3; continue; }                    // (3 — três próximas figuras ×2/3
    var dur;
    if (m[0][0] === 'z') {                              // pausa
      dur = (m[3] ? +m[3] : 1) * unitCells;
      if (tup > 0) { dur = dur * 2 / 3; tup--; }
      cur += dur; lastTied = null;
      continue;
    }
    var accSym = m[4], letter = m[5].toUpperCase(), marks = m[6] || '';
    var midi = BASE[letter] + (m[5] === letter ? 60 : 72);
    for (var i = 0; i < marks.length; i++) midi += marks[i] === ',' ? -12 : 12;
    var accKey = letter + ':' + Math.floor(midi / 12);
    var alt;
    if (accSym === '^') alt = 1; else if (accSym === '_') alt = -1; else if (accSym === '=') alt = 0;
    if (alt !== undefined) measureAcc[accKey] = alt;
    else alt = (accKey in measureAcc) ? measureAcc[accKey] : keyAcc(letter);
    midi += alt;
    dur = (m[7] ? +m[7] : 1) * unitCells;
    if (tup > 0) { dur = dur * 2 / 3; tup--; }
    if (Math.abs(dur - Math.round(dur)) > 1e-6) violations.push('duração não-inteira em célula ' + cur);
    dur = Math.round(dur);
    if (lastTied && lastTied.midi === midi) lastTied.durCells += dur;   // ligadura: estende
    else { var ev = { cell: cur, durCells: dur, midi: midi }; events.push(ev); lastTied = null; if (m[8]) lastTied = ev; }
    if (lastTied && !m[8]) lastTied = null;
    if (m[8] && !lastTied) lastTied = events[events.length - 1];
    cur += dur;
  }
  return { bpm: bpm, fifths: fifths, events: events, totalCells: cur, violations: violations };
}

/* ---------- sintetizador: samples reais de trompete (soundfont do app) ---------- */
function mulberry(seed) {
  var a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0;
    var t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
var NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
function sampleName(midi) { return NAMES[midi % 12] + (Math.floor(midi / 12) - 1); }

async function sintetiza(events, p) {
  var SR = 44100, cell = 60 / p.bpm / 12, t0 = p.t0 || 0.15;
  var endCells = 0;
  events.forEach(function (e) { endCells = Math.max(endCells, e.cell + e.durCells); });
  var ctx = new OfflineAudioContext(1, Math.ceil((t0 + endCells * cell + 1.0) * SR), SR);
  var bufs = {}, names = events.map(function (e) { return sampleName(e.midi); });
  await Promise.all(Array.from(new Set(names)).map(async function (n) {
    var r = await fetch('/app/vendor/soundfont/trumpet-mp3/' + n + '.mp3');
    if (!r.ok) throw new Error('sample ' + n + ': HTTP ' + r.status);
    bufs[n] = await ctx.decodeAudioData(await r.arrayBuffer());
  }));
  var rng = mulberry(p.seed || 1), schedLog = [];
  events.forEach(function (e) {
    var t = Math.max(0, t0 + e.cell * cell + (rng() * 2 - 1) * (p.jitterMs || 0) / 1000);
    var dur = Math.max(0.06, e.durCells * cell - (p.gapMs || 28) / 1000);
    var src = ctx.createBufferSource();
    src.buffer = bufs[sampleName(e.midi)];
    schedLog.push({ cell: e.cell, name: sampleName(e.midi), t: +t.toFixed(3), dur: +dur.toFixed(3), bufLen: +src.buffer.duration.toFixed(2) });
    src.playbackRate.value = Math.pow(2, ((p.detuneCents || 0) + (rng() * 2 - 1) * 4) / 1200);
    var g = ctx.createGain();
    var vel = Math.pow(10, ((rng() * 2 - 1) * (p.velJitterDb || 2)) / 20) * 0.8;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(vel, t + 0.012);
    g.gain.setValueAtTime(vel, Math.max(t + 0.012, t + dur - 0.02));
    g.gain.linearRampToValueAtTime(0, t + dur);
    src.connect(g); g.connect(ctx.destination);
    src.start(t); src.stop(t + dur + 0.05);
  });
  var rendered = await ctx.startRendering();
  var out = rendered.getChannelData(0);
  if (p.snrDb != null) {
    // ruído RELATIVO ao sinal (SNR), não ao full-scale: os samples do soundfont são baixos,
    // e o que importa pra detecção é a razão sinal/ruído da gravação, não o nível absoluto.
    var sumsq = 0, nsum = 0;
    schedLog.forEach(function (l) {
      var a = Math.floor(l.t * SR), z = Math.min(out.length, Math.floor((l.t + l.dur) * SR));
      for (var i = a; i < z; i++) sumsq += out[i] * out[i];
      nsum += z - a;
    });
    var sigRms = Math.sqrt(sumsq / (nsum || 1));
    var noise = new Float32Array(out.length), y = 0, a1 = 0.39, nsq = 0;
    for (var i = 0; i < noise.length; i++) {            // branco → 1 polo passa-baixa (~3.5kHz)
      y += a1 * ((rng() * 2 - 1) - y); noise[i] = y; nsq += y * y;
    }
    var scale = (sigRms / Math.pow(10, p.snrDb / 20)) / Math.sqrt(nsq / noise.length);
    for (var i = 0; i < out.length; i++) out[i] += noise[i] * scale;
  }
  var peak = 0;                                          // normaliza (gravação com nível são)
  for (var i = 0; i < out.length; i++) peak = Math.max(peak, Math.abs(out[i]));
  if (peak > 0) for (var i = 0; i < out.length; i++) out[i] *= 0.7 / peak;
  out.schedLog = schedLog;
  return out;
}

/* ---------- detecção offline com o detector de produção ---------- */
// Offline pode ser mais permissivo que o ao vivo (clareza 0.80 vs 0.90): a mediana e o
// agrupamento do segmentador filtram falsos positivos que no tuner ao vivo seriam ruído.
function detecta(samples, SR) {
  var W = 2048, H = 256, buf = new Float32Array(W);
  var opts = { clarityThreshold: 0.80, rmsFloor: 0.005 };
  var ps = new Float64Array(W + 1), nsdf = new Float64Array(W + 1), frames = [];
  // RMS numa sub-janela CURTA central (12ms): o buraco de língua (~25ms) some na janela de
  // pitch (46ms), mas aparece nítido na curta — é ela que separa notas repetidas.
  var RW = 512, r0 = (W - RW) >> 1;
  for (var i = 0; i + W <= samples.length; i += H) {
    buf.set(samples.subarray(i, i + W));
    var rms = 0;
    for (var k = r0; k < r0 + RW; k++) rms += buf[k] * buf[k];
    var hz = PitchDSP.autocorrelate(buf, SR, opts, ps, nsdf);
    frames.push({ t: (i + W / 2) / SR, hz: hz, rms: Math.sqrt(rms / RW) });
  }
  return frames;
}

/* ---------- WAV 16-bit (pra ouvir a "performance" sintética) ---------- */
function wavB64(samples, SR) {
  var n = samples.length, buf = new ArrayBuffer(44 + n * 2), v = new DataView(buf);
  function str(off, s) { for (var i = 0; i < s.length; i++) v.setUint8(off + i, s.charCodeAt(i)); }
  str(0, 'RIFF'); v.setUint32(4, 36 + n * 2, true); str(8, 'WAVEfmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, SR, true); v.setUint32(28, SR * 2, true); v.setUint16(32, 2, true);
  v.setUint16(34, 16, true); str(36, 'data'); v.setUint32(40, n * 2, true);
  for (var i = 0; i < n; i++) {
    var s = Math.max(-1, Math.min(1, samples[i]));
    v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
  var bytes = new Uint8Array(buf), out = '';
  for (var off = 0; off < bytes.length; off += 0x8000)
    out += String.fromCharCode.apply(null, bytes.subarray(off, off + 0x8000));
  return btoa(out);
}

/* ---------- orquestra: gabarito + perfis ---------- */
async function runBench(cfg) {
  var SR = 44100;
  var gtAbc = await (await fetch('/content/notes_manual/sb-011.abc')).text();
  var omrAbc = await (await fetch('/tools/transcricao/sb-011-omr.abc')).text();
  var gt = parseAbc(gtAbc), omr = parseAbc(omrAbc);
  var out = { gt: gt, omr: omr, profiles: {} };
  for (var name in cfg.profiles) {
    var p = Object.assign({ bpm: gt.bpm }, cfg.profiles[name]);
    var samples = await sintetiza(gt.events, p);
    var frames = detecta(samples, SR);
    var seg = NoteSegmenter.framesToNotes(frames, { hopSec: 256 / SR });
    var q = NoteSegmenter.quantizeNotes(seg.notes, { bpm: gt.bpm, t0: p.t0 || 0.15 });
    out.profiles[name] = {
      events: q.events, nRaw: seg.notes.length,
      tuningOffsetCents: Math.round(seg.tuningOffsetSemis * 100),
      shiftMs: Math.round(q.shiftSec * 1000), wav: wavB64(samples, SR)
    };
    if (p.debug) {                                       // raio-x por nota do gabarito
      var cs = 60 / gt.bpm / 12, t0 = p.t0 || 0.15;
      out.profiles[name].diag = gt.events.map(function (e) {
        var a = t0 + e.cell * cs, b = a + e.durCells * cs;
        var fs = frames.filter(function (f) { return f.t >= a && f.t < b; });
        var v = fs.filter(function (f) { return f.hz; });
        return {
          cell: e.cell, midi: e.midi, frames: fs.length, voiced: v.length,
          rms: +(fs.reduce(function (s, f) { return s + f.rms; }, 0) / (fs.length || 1)).toFixed(4),
          hzMed: v.length ? +v[v.length >> 1].hz.toFixed(1) : null
        };
      });
    }
  }
  return out;
}
window.runBench = runBench;
window.parseAbc = parseAbc;
