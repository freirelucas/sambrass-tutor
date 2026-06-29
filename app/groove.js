// groove.js — o ACOMPANHAMENTO de cumbia, sintetizado no Web Audio (sem samples, offline).
// Cumbia é música de conjunto: tocar o riff sozinho é o maior buraco do app. Aqui mora
// "tocar com a banda" — güira (raspador) + baixo (tônica/quinta, com o lilt) + naipe no
// contratempo (a "chunchaca"), em loop no TOM DE CONCERTO e no BPM da peça.
//
// Soa no tom de CONCERTO (= o que o trompete Bb realmente toca lendo o escrito), então
// encaixa com o aluno tocando por cima. API:
//   Groove.start({audioContext, bpm, root})   root = MIDI da tônica de concerto (grave)
//   Groove.setBpm(bpm) · Groove.setRoot(midi) · Groove.stop() · Groove.on (bool)
//   Groove.rootFromKey('F'|'Bb'|...)           nome do tom de concerto → MIDI grave
(function (root) {
  'use strict';
  var PC = { C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, Gb: 6,
             G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11 };
  var ctx = null, master = null, timer = null, noiseBuf = null,
      nextT = 0, step = 0, bpm = 96, rootMidi = 41, playing = false;
  var LOOKAHEAD = 0.12, TICK = 25;                         // scheduler "two clocks"
  function freq(m) { return 440 * Math.pow(2, (m - 69) / 12); }
  function s16() { return (60 / bpm) / 4; }                // segundos por semicolcheia

  function noise() {
    if (noiseBuf) return noiseBuf;
    var n = Math.floor(ctx.sampleRate * 0.4), b = ctx.createBuffer(1, n, ctx.sampleRate), d = b.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    noiseBuf = b; return b;
  }
  function guira(t, accent) {                              // o raspador: ruído filtrado, curto
    var src = ctx.createBufferSource(); src.buffer = noise();
    var bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = accent ? 6800 : 5200; bp.Q.value = 0.7;
    var g = ctx.createGain(), a = accent ? 0.15 : 0.085;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(a, t + 0.004);
    g.gain.exponentialRampToValueAtTime(0.0001, t + (accent ? 0.075 : 0.05));
    src.connect(bp).connect(g).connect(master); src.start(t); src.stop(t + 0.1);
  }
  function bass(t, midi) {
    var o = ctx.createOscillator(); o.type = 'triangle'; o.frequency.value = freq(midi);
    var lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 850;
    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.34, t + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.19);
    o.connect(lp).connect(g).connect(master); o.start(t); o.stop(t + 0.22);
  }
  function stab(t, midis) {                                // o naipe no contratempo (órgão/guitarra)
    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.11, t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.14);
    g.connect(master);
    midis.forEach(function (m) {
      var o = ctx.createOscillator(); o.type = 'sawtooth'; o.frequency.value = freq(m);
      var og = ctx.createGain(); og.gain.value = 0.45; o.connect(og).connect(g); o.start(t); o.stop(t + 0.16);
    });
  }
  // grade de 16 passos (semicolcheias) por compasso — o feel da cumbia
  function schedule(t, s) {
    if (s % 2 === 0) guira(t, s % 4 === 2);               // güira nas colcheias, acento no contratempo
    if (s === 0) bass(t, rootMidi);                       // baixo: tônica/quinta com o lilt
    else if (s === 6) bass(t, rootMidi + 7);
    else if (s === 8) bass(t, rootMidi);
    else if (s === 14) bass(t, rootMidi + 7);
    if (s === 4 || s === 12) stab(t, [rootMidi + 12, rootMidi + 19]);   // naipe nos tempos 2 e 4
  }
  function tick() {
    while (nextT < ctx.currentTime + LOOKAHEAD) {
      schedule(nextT, step);
      nextT += s16(); step = (step + 1) % 16;
    }
  }

  root.Groove = {
    start: function (o) {
      o = o || {};
      try {
        ctx = o.audioContext || ctx || new (root.AudioContext || root.webkitAudioContext)();
        if (ctx.state === 'suspended') ctx.resume();
      } catch (e) { return; }
      if (o.bpm) bpm = o.bpm;
      if (o.root != null) rootMidi = o.root;
      if (playing) return;
      if (!master) { master = ctx.createGain(); master.gain.value = 0.9; master.connect(ctx.destination); }
      playing = true; step = 0; nextT = ctx.currentTime + 0.08;
      timer = setInterval(tick, TICK);
    },
    stop: function () { playing = false; if (timer) { clearInterval(timer); timer = null; } },
    setBpm: function (b) { if (b) bpm = b; },
    setRoot: function (m) { if (m != null) rootMidi = m; },
    rootFromKey: function (key) {
      var pc = PC[(key || 'C').replace(/m$/, '')]; if (pc == null) pc = 0;
      return 36 + pc;                                      // tônica grave (C2..B2)
    },
    get on() { return playing; }
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.Groove;
})(typeof window !== 'undefined' ? window : this);
