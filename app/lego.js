// lego.js — o "bloco de Lego" FUNCIONAL de uma peça: os trechos que se repetem,
// cada peça com seu CONTORNO (arpejo/forma das notas) + COLAR RÍTMICO (a célula),
// colorida pelo TOM (ciclo de quintas) e CLICÁVEL → toca aquele trecho e ANIMA no tempo.
// Precisa de lego.css (a FORMA) e, p/ tocar, do abcjs (vendor).
// API:
//   el.innerHTML = lego(record)                  → as peças encaixáveis
//   legoAbc(midis, durs, meter, bpm)             → ABC tocável de um trecho
//   legoMini(record, {w,h})                      → glifo pequeno (nó da trilha)
//   legoColors(record)                           → {col, pale, hue, maj}
//   legoPlay(scopeEl, record, i, {audioContext}) → toca o trecho i e acende contorno+colar no tempo
(function (root) {
  'use strict';
  var COF = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5], CP = {};
  COF.forEach(function (p, i) { CP[p] = i; });
  var PC = { C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, Gb: 6,
             G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11 };
  function hue(t) { var p = PC[t]; return (CP[p] == null ? 0 : CP[p]) * 30; }
  var NAMES = ['C', '^C', 'D', '^D', 'E', 'F', '^F', 'G', '^G', 'A', '^A', 'B'];
  function midiAbc(m) {
    var pc = ((m % 12) + 12) % 12, oct = Math.floor(m / 12) - 1, t = NAMES[pc], o;
    if (oct >= 5) { t = t.toLowerCase(); for (o = 5; o < oct; o++) t += "'"; }
    else { for (o = oct; o < 4; o++) t += ','; }
    return t;
  }
  function legoAbc(midis, durs, meter, bpm) {
    bpm = bpm || 96; var n = '';
    for (var i = 0; i < midis.length; i++) {
      var mult = Math.max(1, Math.round((durs[i] || 1) * 4));
      n += midiAbc(midis[i]) + (mult > 1 ? mult : '');
    }
    return 'X:1\nM:' + (Math.round(meter) === 2 ? '2/4' : '4/4') + '\nL:1/16\nQ:1/4=' + bpm + '\nK:C\n' + n + '|]';
  }

  function colors(d) {
    var h = hue(d && d.cor && d.cor.tonica), maj = !d || !d.cor || d.cor.modo === 'maior';
    return { hue: h, maj: maj,
      col: 'hsl(' + h + ',' + (maj ? 70 : 55) + '%,' + (maj ? 46 : 42) + '%)',
      pale: 'hsl(' + h + ',' + (maj ? 58 : 46) + '%,95%)' };
  }

  // o CONTORNO (arpejo/forma): a linha das alturas; cada nota é um nó .lp-dot[data-i]
  function contour(midis, col) {
    if (!midis || midis.length < 2) return '';
    var W = 190, H = 40, lo = Math.min.apply(null, midis), hi = Math.max.apply(null, midis),
        rg = Math.max(1, hi - lo), pts = [], dots = '', i, x, y;
    for (i = 0; i < midis.length; i++) {
      x = 8 + i * (W - 16) / (midis.length - 1); y = H - 5 - (midis[i] - lo) / rg * (H - 12);
      pts.push(x.toFixed(1) + ',' + y.toFixed(1));
      dots += '<circle class="lp-dot" data-i="' + i + '" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="2.4" fill="' + col + '"/>';
    }
    return '<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + col + '" stroke-width="2.5" stroke-linejoin="round"/>' + dots;
  }
  // o COLAR RÍTMICO (a célula): cada nota = um segmento proporcional à duração; .lp-seg[data-i]
  function rhythm(durs, col) {
    if (!durs || !durs.length) return '';
    var W = 190, y = 50, tot = durs.reduce(function (a, b) { return a + (b || 0); }, 0) || 1, x = 8, segs = '', i, w;
    for (i = 0; i < durs.length; i++) {
      w = (durs[i] / tot) * (W - 16);
      segs += '<rect class="lp-seg" data-i="' + i + '" x="' + x.toFixed(1) + '" y="' + y + '" width="' + Math.max(2.5, w - 2).toFixed(1) + '" height="9" rx="2.5" fill="' + col + '" opacity="0.55"/>';
      x += w;
    }
    return segs;
  }

  root.legoAbc = legoAbc;
  root.legoColors = colors;

  root.lego = function (d) {
    if (!d || !d.legos || !d.legos.length) return '<p class="lego-empty">sem trechos extraídos.</p>';
    var c = colors(d);
    var html = '<div class="lego" style="--lc:' + c.col + ';--lcbg:' + c.pale + '">';
    d.legos.forEach(function (lg, i) {
      html += '<button class="lego-pc" data-lego="' + i + '" aria-label="tocar trecho ' + (i + 1) + '">' +
        '<span class="lego-studs"><i></i><i></i><i></i></span>' +
        '<span class="lego-n">trecho ' + (i + 1) + '<small>×' + lg.x + ' · ' + lg.midis.length + ' notas</small></span>' +
        '<svg viewBox="0 0 190 62" class="lego-svg" preserveAspectRatio="none">' + contour(lg.midis, c.col) + rhythm(lg.durs, c.col) + '</svg>' +
        '<span class="lego-play">▶</span></button>';
    });
    return html + '</div>';
  };

  // glifo pequeno (o "selo" do nó da trilha / hero do estudo): o contorno do 1º trecho
  // na cor do tom; opt.rhythm acrescenta o colar (p/ um selo mais cheio, ex.: o hero).
  root.legoMini = function (d, opt) {
    opt = opt || {}; var lg = d && d.legos && d.legos[0]; if (!lg || !lg.midis || lg.midis.length < 2) return '';
    var c = colors(d), W = opt.w || 38, H = opt.h || 26, withR = !!opt.rhythm, m = lg.midis,
        pad = 3, cTop = pad, cBot = (withR ? H * 0.62 : H - pad),       // banda do contorno
        lo = Math.min.apply(null, m), hi = Math.max.apply(null, m), rg = Math.max(1, hi - lo), pts = [], i, x, y;
    for (i = 0; i < m.length; i++) {
      x = pad + i * (W - 2 * pad) / (m.length - 1); y = cBot - (m[i] - lo) / rg * (cBot - cTop);
      pts.push(x.toFixed(1) + ',' + y.toFixed(1));
    }
    var g = '<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + c.col + '" stroke-width="2" stroke-linejoin="round"/>';
    if (withR) {
      var durs = lg.durs || [], tot = durs.reduce(function (a, b) { return a + (b || 0); }, 0) || 1, xx = pad, yy = H - pad - 4, seg = '', w;
      for (i = 0; i < durs.length; i++) { w = (durs[i] / tot) * (W - 2 * pad);
        seg += '<rect x="' + xx.toFixed(1) + '" y="' + yy + '" width="' + Math.max(1.5, w - 1.5).toFixed(1) + '" height="4" rx="1.5" fill="' + c.col + '" opacity="0.7"/>'; xx += w; }
      g += seg;
    }
    return '<span class="lego-mini" aria-hidden="true"><svg width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '">' + g + '</svg></span>';
  };

  // ---- tocar + animar um trecho (L4): contorno/colar acendem no tempo ----
  function lit(scope, sel, i) {
    if (!scope) return;
    scope.querySelectorAll(sel + '.lit').forEach(function (e) { e.classList.remove('lit'); });
    if (i != null) { var t = scope.querySelector(sel + '[data-i="' + i + '"]'); if (t) t.classList.add('lit'); }
  }
  var _live = null;   // { synth, timer, scope } do trecho que está tocando agora
  function clearLive() {
    if (!_live) return;
    try { _live.synth.stop(); } catch (e) {}
    try { _live.timer.stop(); } catch (e) {}
    lit(_live.scope, '.lp-dot', null); lit(_live.scope, '.lp-seg', null);
    _live = null;
  }
  root.legoStop = clearLive;
  // scopeEl = a PEÇA clicada (.lego-pc), p/ acender só o contorno/colar dela
  root.legoPlay = function (scopeEl, d, idx, opts) {
    opts = opts || {};
    var lg = d && d.legos && d.legos[idx]; if (!lg) return Promise.resolve(null);
    if (!root.ABCJS || !root.ABCJS.synth || !root.ABCJS.synth.supportsAudio()) return Promise.resolve(null);
    var AC = opts.audioContext; if (!AC) { try { AC = new (root.AudioContext || root.webkitAudioContext)(); } catch (e) { return Promise.resolve(null); } }
    var bpm = opts.bpm || 96, abc = legoAbc(lg.midis, lg.durs, d.meter, bpm);
    var sc = document.getElementById('lego-scratch');
    if (!sc) { sc = document.createElement('div'); sc.id = 'lego-scratch'; sc.style.display = 'none'; document.body.appendChild(sc); }
    var visual; try { visual = root.ABCJS.renderAbc('lego-scratch', abc)[0]; } catch (e) { return Promise.resolve(null); }
    // abcjs não numera as notas → conta pela ORDEM dos eventos p/ acender o nó/segmento certo
    var k = -1;
    var timer = new root.ABCJS.TimingCallbacks(visual, { qpm: bpm,
      eventCallback: function (ev) {
        if (!ev) { lit(scopeEl, '.lp-dot', null); lit(scopeEl, '.lp-seg', null); return; }
        k++; lit(scopeEl, '.lp-dot', k); lit(scopeEl, '.lp-seg', k);
      } });
    var synth = new root.ABCJS.synth.CreateSynth();
    return synth.init({ audioContext: AC, visualObj: visual, options: { soundFontUrl: opts.soundFontUrl || './vendor/soundfont/', program: 56 } })
      .then(function () { return synth.prime(); })
      .then(function () {
        clearLive();                       // para o trecho anterior (synth + timer + acesos)
        _live = { synth: synth, timer: timer, scope: scopeEl };
        k = -1; synth.start(); timer.start();
        return { stop: clearLive };
      })
      .catch(function () { return null; });
  };

  if (typeof module !== 'undefined' && module.exports)
    module.exports = { lego: root.lego, legoAbc: root.legoAbc, legoColors: root.legoColors, legoMini: root.legoMini };
})(typeof window !== 'undefined' ? window : this);
