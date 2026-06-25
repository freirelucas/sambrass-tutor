// grafismo.js — selo generativo de um bloco/frase, derivado SÓ dos dados.
// Cada elemento mapeia uma medida (princípio: focado nos dados, nada decorativo):
//   matiz        = tônica (posição no círculo de quintas)
//   claro/escuro = modo (maior/menor)
//   anel pontilhado = confiança baixa do modo (pede ouvido)
//   ticks no anel = groove (ataques nas 1ªs barras, no relógio de tempos)
//   roseta interna = contorno do riff (raio = altura da nota, ângulo = ordem)
//   nós na roseta = notas do riff
// Uso: el.innerHTML = grafismo({midis,onsets,meter,tonica,modo,conf}, 96)
(function (root) {
  'use strict';
  var COF = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5];          // círculo de quintas
  var COFPOS = {}; COF.forEach(function (pc, i) { COFPOS[pc] = i; });
  var PC = { C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, Gb: 6,
             G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11 };
  function hueOf(tonica) { var pc = PC[tonica]; return (COFPOS[pc] == null ? 0 : COFPOS[pc]) * 30; }
  function pol(cx, cy, r, deg) { var a = (deg - 90) * Math.PI / 180; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }

  function grafismo(d, size) {
    size = size || 96;
    d = d || {};
    var midis = (d.midis || []).filter(function (x) { return typeof x === 'number' && isFinite(x); });
    var onsets = d.onsets || [], meter = d.meter || 4;
    var maj = d.modo === 'maior', minr = d.modo === 'menor';
    var low = (d.conf == null ? 1 : d.conf) < 0.06;
    var H = hueOf(d.tonica);
    var bg = 'hsl(' + H + ',' + (maj ? 55 : 45) + '%,' + (maj ? 22 : 15) + '%)';
    var line = 'hsl(' + H + ',78%,' + (maj ? 64 : 56) + '%)';
    var fill = 'hsl(' + H + ',70%,' + (maj ? 56 : 48) + '%)';
    var faint = 'hsl(' + H + ',40%,' + (maj ? 42 : 34) + '%)';
    var unknown = (d.modo !== 'maior' && d.modo !== 'menor');

    var p = '<rect x="2" y="2" width="96" height="96" rx="14" fill="' + (unknown ? '#222018' : bg) +
            '" stroke="' + faint + '" stroke-width="1.5"/>';
    // anel de groove
    p += '<circle cx="50" cy="50" r="44" fill="none" stroke="' + faint + '" stroke-width="1"' +
         (low ? ' stroke-dasharray="3 3"' : '') + '/>';
    for (var i = 0; i < onsets.length; i++) {
      var q = pol(50, 50, 44, 360 * (onsets[i] / (meter || 4)));
      p += '<circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="2.4" fill="' + line + '"/>';
    }
    // roseta do contorno
    if (midis.length >= 2) {
      var lo = Math.min.apply(null, midis), hi = Math.max.apply(null, midis), rg = Math.max(1, hi - lo);
      var pts = [], nodes = '';
      for (var k = 0; k < midis.length; k++) {
        var r = 18 + (midis[k] - lo) / rg * 22;
        var pt = pol(50, 50, r, 360 * k / midis.length);
        pts.push(pt[0].toFixed(1) + ',' + pt[1].toFixed(1));
        nodes += '<circle cx="' + pt[0].toFixed(1) + '" cy="' + pt[1].toFixed(1) + '" r="1.6" fill="' + line + '"/>';
      }
      p += '<polygon points="' + pts.join(' ') + '" fill="' + fill + '" fill-opacity="0.26" stroke="' +
           line + '" stroke-width="2" stroke-linejoin="round"/>' + nodes;
    }
    p += '<circle cx="50" cy="50" r="2" fill="' + line + '"/>';
    return '<svg viewBox="0 0 100 100" width="' + size + '" height="' + size + '" class="grafismo" ' +
           'role="img" aria-label="grafismo do bloco">' + p + '</svg>';
  }

  root.grafismo = grafismo;
  if (typeof module !== 'undefined' && module.exports) module.exports = grafismo;
})(typeof window !== 'undefined' ? window : this);
