// proll.js — o "rolo de alturas" (pitch-roll) do Chromatone: tempo × altura, cada nota um
// bloco colorido pela SUA cor (chroma.js). Respeita os SILÊNCIOS (pausa = vão, sem bloco).
// O cursor sincroniza com a pauta (o mesmo evento que acende a nota acende o bloco).
// Uso: const pr = pitchRoll(el, {notes:[{midi,ms,durMs,startChar}], totalMs}, {h});
//      pr.highlight(pr.idxOf(ev.startChar));  pr.clear();
(function (root) {
  'use strict';
  function build(el, data, opt) {
    if (!el) return null;
    var notes = (data && data.notes) || [], total = (data && data.totalMs) || 0;
    if (!notes.length || total <= 0) { el.innerHTML = ''; return null; }
    opt = opt || {};
    var W = 1000, H = 200, pad = 10, top = 22, bot = H - 16;         // viewBox; escala p/ a largura via CSS
    var midis = notes.map(function (n) { return n.midi; });
    var lo = Math.min.apply(null, midis), hi = Math.max.apply(null, midis), rg = Math.max(1, hi - lo);
    var yOf = function (m) { return bot - (m - lo) / rg * (bot - top); };   // agudo em cima
    var xOf = function (ms) { return pad + ms / total * (W - 2 * pad); };
    var rects = '', map = {};
    for (var i = 0; i < notes.length; i++) {
      var n = notes[i], x = xOf(n.ms), w = Math.max(5, xOf(n.ms + n.durMs) - x - 1.5), y = yOf(n.midi);
      var col = root.chroma ? root.chroma.css(n.midi, { s: 72, l: 47 }) : '#8a8a8a';
      rects += '<rect class="pr-note" data-i="' + i + '" x="' + x.toFixed(1) + '" y="' + (y - 8).toFixed(1) +
               '" width="' + w.toFixed(1) + '" height="16" rx="6" fill="' + col + '"/>';
      if (n.startChar != null) map[n.startChar] = i;
    }
    el.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" class="proll-svg" role="img" ' +
      'aria-label="rolo de alturas colorido — a melodia no tempo, cada nota na sua cor">' +
      '<line class="pr-cursor" x1="0" y1="6" x2="0" y2="' + (H - 6) + '"/>' + rects + '</svg>';
    var cursor = el.querySelector('.pr-cursor');
    var cxOf = function (i) { var n = notes[i]; return xOf(n.ms + n.durMs / 2); };
    function clearOn() { var on = el.querySelectorAll('.pr-note.on'); for (var k = 0; k < on.length; k++) on[k].classList.remove('on'); }
    return {
      idxOf: function (sc) { return map[sc] == null ? null : map[sc]; },
      highlight: function (i) {
        clearOn();
        if (i == null) { if (cursor) cursor.classList.remove('on'); return; }
        var t = el.querySelector('.pr-note[data-i="' + i + '"]'); if (t) t.classList.add('on');
        if (cursor) { var cx = cxOf(i).toFixed(1); cursor.setAttribute('x1', cx); cursor.setAttribute('x2', cx); cursor.classList.add('on'); }
      },
      clear: function () { clearOn(); if (cursor) cursor.classList.remove('on'); }
    };
  }
  root.pitchRoll = build;
  if (typeof module !== 'undefined' && module.exports) module.exports = build;
})(typeof window !== 'undefined' ? window : this);
