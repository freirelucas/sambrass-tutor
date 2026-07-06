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
    var semiPx = (bot - top) / rg;                                    // pixels (viewBox) por semitom
    var yOf = function (m) { return bot - (m - lo) / rg * (bot - top); };   // agudo em cima
    var xOf = function (ms) { return pad + ms / total * (W - 2 * pad); };
    var rects = '', map = {}, ys = [];
    for (var i = 0; i < notes.length; i++) {
      var n = notes[i], x = xOf(n.ms), w = Math.max(5, xOf(n.ms + n.durMs) - x - 1.5), y = yOf(n.midi);
      var col = root.chroma ? root.chroma.css(n.midi, { s: 72, l: 47 }) : '#8a8a8a';
      rects += '<rect class="pr-note" data-i="' + i + '" x="' + x.toFixed(1) + '" y="' + (y - 8).toFixed(1) +
               '" width="' + w.toFixed(1) + '" height="16" rx="6" fill="' + col + '"/>';
      ys.push(y);
      if (n.startChar != null) map[n.startChar] = i;
    }
    el.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" class="proll-svg" role="img" ' +
      'aria-label="rolo de alturas colorido — a melodia no tempo, cada nota na sua cor">' +
      '<line class="pr-cursor" x1="0" y1="6" x2="0" y2="' + (H - 6) + '"/>' + rects +
      '<circle class="pr-you" r="15" cx="0" cy="0"/></svg>';                    // o "Espelho": sua altura ao vivo
    var cursor = el.querySelector('.pr-cursor'), you = el.querySelector('.pr-you');
    var cxOf = function (i) { var n = notes[i]; return xOf(n.ms + n.durMs / 2); };
    var curIdx = null, curX = 0;
    function clearOn() { var on = el.querySelectorAll('.pr-note.on'); for (var k = 0; k < on.length; k++) on[k].classList.remove('on'); }
    return {
      idxOf: function (sc) { return map[sc] == null ? null : map[sc]; },
      highlight: function (i) {
        clearOn();
        if (i == null) { curIdx = null; if (cursor) cursor.classList.remove('on'); return; }
        curIdx = i; curX = cxOf(i);
        var t = el.querySelector('.pr-note[data-i="' + i + '"]'); if (t) t.classList.add('on');
        if (cursor) { var cx = curX.toFixed(1); cursor.setAttribute('x1', cx); cursor.setAttribute('x2', cx); cursor.classList.add('on'); }
      },
      // Espelho: dev = seu desvio (em semitons, dobrado à oitava) da nota-alvo; matched = encaixou.
      // Ancorado no bloco atual → quando você acerta, o ponto pousa em cima do bloco e acende verde.
      mirror: function (dev, matched) {
        if (!you) return;
        if (curIdx == null) { you.classList.remove('on'); return; }
        var cy = Math.max(6, Math.min(H - 6, ys[curIdx] - dev * semiPx));
        you.setAttribute('cx', curX.toFixed(1)); you.setAttribute('cy', cy.toFixed(1));
        you.classList.add('on'); you.classList.toggle('lock', !!matched);
      },
      mirrorOff: function () { if (you) you.classList.remove('on'); },
      clear: function () { clearOn(); curIdx = null; if (cursor) cursor.classList.remove('on'); if (you) you.classList.remove('on'); }
    };
  }
  root.pitchRoll = build;
  if (typeof module !== 'undefined' && module.exports) module.exports = build;
})(typeof window !== 'undefined' ? window : this);
