// montariff.js — o JOGO "monte o riff": as notas do riff viram blocos de Lego EMBARALHADOS,
// cada um na cor da sua nota (Chromatone) e na ALTURA da sua nota. Você encaixa na ordem certa
// → reconstrói o CONTORNO do riff e ouve ele montado. Ver os Legos vira JOGAR com os Legos.
// Uso: montaRiff(el, { midis, nameOf, playNote, playSeq })
//   playNote(midi)  → som curto ao encaixar cada bloco
//   playSeq(midis)  → toca o riff montado (na vitória e no "ouvir o modelo")
(function (root) {
  'use strict';
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function col(m) { return root.chroma ? root.chroma.css(m, { s: 72, l: 46 }) : '#8a8a8a'; }

  function montaRiff(el, opt) {
    if (!el) return null;
    opt = opt || {};
    var midis = (opt.midis || []).slice(0, 8);               // limita p/ jogabilidade
    if (midis.length < 2) { el.innerHTML = ''; return null; }
    var nameOf = opt.nameOf || function () { return ''; };
    var playNote = opt.playNote || function () {};
    var playSeq = opt.playSeq || function () {};
    var lo = Math.min.apply(null, midis), hi = Math.max.apply(null, midis), rg = Math.max(1, hi - lo);
    var hPct = function (m) { return (26 + (m - lo) / rg * 56).toFixed(0); };   // 26..82% — deixa a base livre p/ o nome
    var next = 0;

    function stud(m) { return '<span class="mr-stud" style="bottom:' + hPct(m) + '%"></span>'; }
    function render() {
      next = 0; el.classList.remove('mr-win');
      var bag = shuffle(midis.map(function (m, i) { return { m: m, i: i }; }));
      var slots = midis.map(function (m, i) { return '<div class="mr-slot" data-slot="' + i + '"></div>'; }).join('');
      var pieces = bag.map(function (o) {
        return '<button class="mr-piece" data-midi="' + o.m + '" style="--c:' + col(o.m) + '" aria-label="nota ' + nameOf(o.m) + '">' +
          stud(o.m) + '<span class="mr-nm">' + nameOf(o.m) + '</span></button>';
      }).join('');
      el.innerHTML = '<div class="mr-slots">' + slots + '</div>' +
        '<div class="mr-bag">' + pieces + '</div>' +
        '<div class="mr-foot"><button class="mr-btn prim" data-act="hear">🔊 ouvir o modelo</button>' +
        '<button class="mr-btn" data-act="shuffle">🔀 de novo</button>' +
        '<span class="mr-msg" aria-live="polite">encaixe na ordem do riff</span></div>';
    }
    function win() {
      var msg = el.querySelector('.mr-msg'); if (msg) msg.textContent = '✓ montou o riff! 🎉';
      el.classList.add('mr-win'); playSeq(midis);
    }
    el.addEventListener('click', function (e) {
      var act = e.target.closest('[data-act]');
      if (act) { if (act.getAttribute('data-act') === 'shuffle') render(); else playSeq(midis); return; }
      var pc = e.target.closest('.mr-piece'); if (!pc || pc.disabled) return;
      var m = +pc.getAttribute('data-midi');
      if (m === midis[next]) {                                // encaixou
        var slot = el.querySelector('.mr-slot[data-slot="' + next + '"]');
        if (slot) { slot.className = 'mr-slot on'; slot.style.setProperty('--c', col(m)); slot.innerHTML = stud(m); }
        pc.disabled = true; pc.classList.add('used'); playNote(m); next++;
        var msg = el.querySelector('.mr-msg'); if (msg) msg.textContent = next + '/' + midis.length;
        if (next >= midis.length) win();
      } else {                                                // errou
        pc.classList.remove('shake'); void pc.offsetWidth; pc.classList.add('shake');
        var m2 = el.querySelector('.mr-msg'); if (m2) m2.textContent = 'essa não — ouça o modelo 🔊';
      }
    });
    render();
    return { reset: render };
  }
  root.montaRiff = montaRiff;
  if (typeof module !== 'undefined' && module.exports) module.exports = montaRiff;
})(typeof window !== 'undefined' ? window : this);
