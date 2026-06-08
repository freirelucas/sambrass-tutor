/* Teste de sanidade do núcleo DSP (sem navegador): autocorrelate() sobre senoides geradas.
 * Roda em Node: node tests/pitch-core.test.js
 */
const { autocorrelate, hzToMidi } = require('../app/vendor/pitch-detector.js');

const SR = 44100, N = 2048;
const midiToHz = (m) => 440 * Math.pow(2, (m - 69) / 12);

function tone(freq, harmonics = [1], noise = 0) {
  const buf = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    let s = 0;
    for (let h = 0; h < harmonics.length; h++) s += harmonics[h] * Math.sin(2 * Math.PI * freq * (h + 1) * i / SR);
    buf[i] = s + (noise ? (Math.random() * 2 - 1) * noise : 0);
  }
  let peak = 0;
  for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(buf[i]));
  if (peak > 0) for (let i = 0; i < N; i++) buf[i] *= 0.6 / peak;
  return buf;
}

let fails = 0;
const check = (name, cond) => { console.log((cond ? 'ok  ' : 'FAIL') + ' ' + name); if (!cond) fails++; };

// 1) varredura faixa do trompete (MIDI 55..82), tom com harmônicos
let swept = 0, hit = 0;
for (let m = 55; m <= 82; m++) {
  const hz = autocorrelate(tone(midiToHz(m), [1, 0.5, 0.3]), SR, {});
  const midi = hz ? Math.round(hzToMidi(hz)) : null;
  swept++; if (midi === m) hit++;
  if (midi !== m) console.log(`   miss MIDI ${m} -> ${midi} (${hz ? hz.toFixed(1) : 'null'} Hz)`);
}
check(`varredura 55..82: ${hit}/${swept} corretos`, hit === swept);

// 2) precisão de afinação melhor que ~15 cents em A4 (440)
{
  const hz = autocorrelate(tone(440, [1, 0.5, 0.25]), SR, {});
  const cents = hz ? Math.abs((hzToMidi(hz) - 69) * 100) : 999;
  check(`A4=440 dentro de 15 cents (${cents.toFixed(1)})`, cents < 15);
}

// 3) silêncio -> null
check('silêncio -> null', autocorrelate(new Float32Array(N), SR, {}) === null);

// 4) ruído branco -> null (gate de clareza)
{
  const noise = new Float32Array(N);
  for (let i = 0; i < N; i++) noise[i] = (Math.random() * 2 - 1) * 0.5;
  check('ruído branco -> null', autocorrelate(noise, SR, {}) === null);
}

// 5) 2º harmônico MAIS forte que a fundamental não vira oitava
{
  const hz = autocorrelate(tone(midiToHz(60), [0.5, 1.0, 0.3]), SR, {});
  const midi = hz ? Math.round(hzToMidi(hz)) : null;
  check(`robusto a oitava: MIDI 60 com 2º harm. dominante -> ${midi}`, midi === 60);
}

console.log(fails ? `\n${fails} FALHARAM` : '\nTODOS PASSARAM');
process.exit(fails ? 1 : 0);
