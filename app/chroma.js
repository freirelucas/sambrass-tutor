// chroma.js — a ÚNICA fonte de cor do app: o padrão Chromatone (chromatone.center).
// 12 notas → 12 matizes, ordem CROMÁTICA, A ancorado no VERMELHO (hue 0), +30°/semitom
// subindo. Confirmado no instrumento "Circle" do Chromatone: hsl(((pc+3) mod 12)*30,100%,40%).
// (Física: dobrando A=440Hz até a luz visível, A cai no vermelho, C no verde, E no azul.)
// Em melodia de uma voz, matiz cromática = ordem de altura → a cor REFORÇA o contorno.
// pc: C=0. Fonte/decisão: docs/plano-canais.md.
(function (root) {
  'use strict';
  var PC = { C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, Gb: 6,
             G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11 };
  function hue(pc) { pc = ((Math.round(pc) % 12) + 12) % 12; return ((pc + 3) % 12) * 30; }
  function tonicHue(name) { var pc = PC[name]; return hue(pc == null ? 9 : pc); }   // A (vermelho) se desconhecido
  // css(pc, {s,l,a}) — a MATIZ é o padrão Chromatone; S/L ficam afináveis p/ legibilidade no papel.
  function css(pc, o) { o = o || {};
    var s = o.s == null ? 72 : o.s, l = o.l == null ? 44 : o.l, a = o.a == null ? 1 : o.a;
    return 'hsla(' + hue(pc) + ',' + s + '%,' + l + '%,' + a + ')'; }
  root.chroma = { hue: hue, tonicHue: tonicHue, css: css, PC: PC };
  root.chromaHue = hue;                                            // atalho
  if (typeof module !== 'undefined' && module.exports) module.exports = root.chroma;
})(typeof window !== 'undefined' ? window : this);
