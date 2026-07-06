// roda.js — a RODA DE RITMO da cumbia (o "rhythm wheel" do Chromatone, adaptado).
// O groove invisível (güira + baixo + naipe) vira um CÍRCULO que gira no tempo da banda.
// E vira JOGO: cada ataque seu pousa um ponto no anel — VERDE quando você trava na grade
// da güira (no giro), quente/frio quando adianta/atrasa. "Trave no giro."
// Uso: const r = RodaRitmo(el); r.start(phaseFn);  r.hit();  r.stop();  r.clear();
//   phaseFn() → posição [0,1) no ciclo de 16 passos (do relógio da banda), ou null.
(function (root) {
  'use strict';
  var STEPS = 16;
  var GUIRA = [0, 2, 4, 6, 8, 10, 12, 14], ACC = [2, 6, 10, 14],
      BASS = [0, 6, 8, 14], STAB = [4, 12], BEAT = [0, 4, 8, 12];
  var C = 100, R = 78;
  function ang(step) { return (-90 + step * (360 / STEPS)) * Math.PI / 180; }
  function pt(r, step) { var a = ang(step); return [C + r * Math.cos(a), C + r * Math.sin(a)]; }

  function build(el) {
    if (!el) return null;
    var marks = '<circle cx="100" cy="100" r="' + R + '" fill="none" stroke="#e7e0d2" stroke-width="10"/>';
    for (var s = 0; s < STEPS; s++) {
      var p = pt(R, s), isBeat = BEAT.indexOf(s) >= 0, isGui = GUIRA.indexOf(s) >= 0, acc = ACC.indexOf(s) >= 0;
      if (isBeat) marks += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="7" fill="#221d18"/>';
      else if (isGui) marks += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="' + (acc ? 4.2 : 3) + '" fill="#b8ab93"/>';
    }
    BASS.forEach(function (s) { var p = pt(R - 17, s); marks += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="4.6" fill="#a9762e"><title>baixo</title></circle>'; });
    STAB.forEach(function (s) { var p = pt(R - 17, s); marks += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="4.6" fill="#8a2331"><title>naipe</title></circle>'; });
    el.innerHTML = '<svg viewBox="0 0 200 200" class="roda-svg" role="img" aria-label="roda de ritmo da cumbia — a güira girando no tempo">' +
      marks + '<g class="roda-hits"></g>' +
      '<line class="roda-hand" x1="100" y1="100" x2="100" y2="' + (100 - R - 3) + '"/>' +
      '<circle class="roda-hub" cx="100" cy="100" r="6.5"/>' +
      '<text x="100" y="150" text-anchor="middle" font-size="12" fill="#857a68">trave no giro</text></svg>';
    var hand = el.querySelector('.roda-hand'), hub = el.querySelector('.roda-hub'), hits = el.querySelector('.roda-hits');
    var raf = 0, phaseFn = null, lastBeat = -1;
    function frame() {
      raf = requestAnimationFrame(frame);
      if (!phaseFn) return;
      var ph = phaseFn();
      if (ph == null) { hand.style.opacity = 0.15; return; }
      hand.style.opacity = 1;
      hand.setAttribute('transform', 'rotate(' + (ph * 360).toFixed(1) + ' 100 100)');
      var b = Math.floor(ph * 4) % 4;                        // 4 tempos no ciclo
      if (b !== lastBeat) { lastBeat = b; hub.classList.remove('beat'); void hub.getBBox; hub.classList.add('beat'); }
    }
    return {
      start: function (fn) { phaseFn = fn; if (!raf) raf = requestAnimationFrame(frame); },
      stop: function () { phaseFn = null; if (raf) { cancelAnimationFrame(raf); raf = 0; } hand.style.opacity = 0.15; },
      // pousa um ponto onde a mão está AGORA; verde se travou na grade da güira (passo par)
      hit: function () {
        if (!phaseFn) return; var ph = phaseFn(); if (ph == null) return;
        var cs = ph * STEPS, near = Math.round(cs / 2) * 2, off = cs - near;
        var cls = Math.abs(off) <= 0.45 ? 'ok' : (off > 0 ? 'late' : 'early');
        var col = cls === 'ok' ? '#2f7d5b' : (cls === 'late' ? '#b5642a' : '#2f6f9e');
        var p = pt(R, cs);
        hits.insertAdjacentHTML('beforeend',
          '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="6" fill="' + col + '" class="roda-hit ' + cls + '">' +
          '<animate attributeName="opacity" from="1" to="0" dur="1.8s" fill="freeze"/>' +
          '<animate attributeName="r" from="8" to="4" dur="1.8s" fill="freeze"/></circle>');
        while (hits.children.length > 10) hits.removeChild(hits.firstChild);
        return cls;
      },
      clear: function () { hits.innerHTML = ''; }
    };
  }
  root.RodaRitmo = build;
  if (typeof module !== 'undefined' && module.exports) module.exports = build;
})(typeof window !== 'undefined' ? window : this);
