/* Sambrass Tutor — segmentador de notas p/ transcrição (gravação → notas), sem dependências.
 *
 * Entrada: quadros {t, hz, rms} vindos do detector (pitch-detector.js) sobre áudio MONOFÔNICO
 * (trompete solo, gravado com metrônomo). Saída: notas {t, dur, midi} e, quantizadas no grid
 * do metrônomo, eventos {cell, durCells, midi} — célula = 1/12 de tempo (semicolcheia = 3,
 * colcheia de quiáltera = 4: cobre binário e tercina exatos).
 *
 * Decisões (honestas):
 *  - Nota nova = buraco não-vozeado (língua) OU salto de altura sustentado OU re-ataque por RMS.
 *  - Afinação global da gravação (lábio/bomba) é estimada (mediana) e removida antes do snap.
 *  - Notas repetidas em legato puro (sem língua nem dip) NÃO são separáveis — limite conhecido.
 *
 * API: NoteSegmenter.framesToNotes(frames, opts) / NoteSegmenter.quantizeNotes(notes, opts)
 */
(function (global) {
  'use strict';

  function median(a) {
    if (!a.length) return 0;
    var s = a.slice().sort(function (x, y) { return x - y; });
    var m = s.length >> 1;
    return s.length % 2 ? s[m] : 0.5 * (s[m - 1] + s[m]);
  }
  function hzToMidiFloat(hz) { return 69 + 12 * Math.log(hz / 440) / Math.LN2; }

  // mediana deslizante (janela ímpar) só sobre trechos vozeados; null permanece null
  function medfilt(track, win) {
    var half = win >> 1, out = track.slice();
    for (var i = 0; i < track.length; i++) {
      if (track[i] == null) continue;
      var v = [];
      for (var k = -half; k <= half; k++) {
        var x = track[i + k];
        if (x != null) v.push(x);
      }
      out[i] = median(v);
    }
    return out;
  }

  function framesToNotes(frames, opts) {
    opts = opts || {};
    var hopSec = opts.hopSec || (256 / 44100);
    var minNoteSec = opts.minNoteSec != null ? opts.minNoteSec : 0.05;
    var maxGapSec = opts.maxGapSec != null ? opts.maxGapSec : 0.035;  // silêncio real fecha a nota
                                                                      // (língua: re-ataque por RMS)
    var splitSemis = opts.splitSemis != null ? opts.splitSemis : 0.55;
    var dipRatio = opts.dipRatio != null ? opts.dipRatio : 0.45;      // queda de RMS = possível re-ataque
    var riseRatio = opts.riseRatio != null ? opts.riseRatio : 2.0;    // subida pós-queda = re-ataque

    var track = medfilt(frames.map(function (f) { return f.hz ? hzToMidiFloat(f.hz) : null; }), 5);

    var groups = [], cur = null, gapRun = 0, jumpRun = 0;
    function close(endIdx) {
      if (cur && cur.idx.length) groups.push(cur);
      cur = null; gapRun = 0; jumpRun = 0;
    }
    for (var i = 0; i < frames.length; i++) {
      var m = track[i];
      if (m == null) {
        if (cur && ++gapRun * hopSec > maxGapSec) close(i);
        continue;
      }
      gapRun = 0;
      if (!cur) { cur = { idx: [i], peak: frames[i].rms, dipped: false, minRms: frames[i].rms }; continue; }
      var med = median(cur.idx.slice(-9).map(function (k) { return track[k]; }));
      if (Math.abs(m - med) > splitSemis) {
        if (++jumpRun >= 3) {                       // salto sustentado: reabre 3 quadros atrás
          var moved = cur.idx.splice(cur.idx.length - (jumpRun - 1));
          close(i);
          cur = { idx: moved.concat([i]), peak: frames[i].rms, dipped: false, minRms: frames[i].rms };
          jumpRun = 0;
        }
        continue;
      }
      jumpRun = 0;
      var rms = frames[i].rms;
      if (cur.dipped && rms > cur.minRms * riseRatio) {  // re-ataque (nota repetida com dip)
        close(i);
        cur = { idx: [i], peak: rms, dipped: false, minRms: rms };
        continue;
      }
      if (rms < cur.peak * dipRatio) { cur.dipped = true; cur.minRms = Math.min(cur.minRms, rms); }
      else if (!cur.dipped) cur.peak = Math.max(cur.peak, rms);
      cur.idx.push(i);
    }
    close(frames.length);

    var notes = groups.map(function (g) {
      var ms = g.idx.map(function (k) { return track[k]; });
      return {
        t: frames[g.idx[0]].t,
        dur: frames[g.idx[g.idx.length - 1]].t - frames[g.idx[0]].t + hopSec,
        midiFloat: median(ms), nFrames: g.idx.length
      };
    }).filter(function (n) { return n.dur >= minNoteSec; });

    // afinação global da gravação: mediana dos desvios → remove antes de arredondar
    var offset = median(notes.map(function (n) { return n.midiFloat - Math.round(n.midiFloat); }));
    notes.forEach(function (n) { n.midi = Math.round(n.midiFloat - offset); });
    return { notes: notes, tuningOffsetSemis: offset };
  }

  // notas (segundos) → eventos no grid do metrônomo. t0 = início musical da gravação (o app
  // controla a contagem/click, então t0 é conhecido); o desvio fino (latência) é estimado.
  function quantizeNotes(notes, opts) {
    var bpm = opts.bpm, t0 = opts.t0 || 0;
    var cellsPerBeat = opts.cellsPerBeat || 12;
    var restMinCells = opts.restMinCells != null ? opts.restMinCells : 2;
    var cell = 60 / bpm / cellsPerBeat;
    var shift = median(notes.map(function (n) {
      var x = (n.t - t0) / cell; return (x - Math.round(x)) * cell;
    }));
    var evs = notes.map(function (n) {
      return { cell: Math.max(0, Math.round((n.t - t0 - shift) / cell)), durV: n.dur, midi: n.midi };
    });
    for (var i = 0; i < evs.length; i++) {
      var durC = Math.max(1, Math.round(evs[i].durV / cell));
      var next = evs[i + 1];
      if (next) {
        var gapC = next.cell - (evs[i].cell + durC);
        evs[i].durCells = (gapC < restMinCells) ? Math.max(1, next.cell - evs[i].cell) : durC;
      } else evs[i].durCells = durC;
      delete evs[i].durV;
    }
    return { events: evs, shiftSec: shift };
  }

  var api = { framesToNotes: framesToNotes, quantizeNotes: quantizeNotes, median: median };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  global.NoteSegmenter = api;
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
