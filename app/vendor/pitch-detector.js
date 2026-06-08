/* Sambrass Tutor — detector de tom monofônico (trompete), sem dependências.
 *
 * Autocorrelação normalizada (NSDF) com interpolação parabólica + gate de RMS e de clareza.
 * Faixa ~120–1300 Hz (trompete escrito Fá#3..Dó6 e folga). Pensado pra rodar a 60fps em
 * celular antigo: energia por prefix-sum (O(1)/lag), busca de lag limitada, zero alocação por
 * frame na via ao vivo (a PitchDetector reusa os buffers).
 *
 * API:
 *   PitchDSP.autocorrelate(float32, sampleRate, opts, scratch?) -> hz | null   (núcleo puro, testável)
 *   new PitchDetector(audioContext, mediaStream, opts).detect() -> {hz,midi,cents} | null
 */
(function (global) {
  'use strict';

  function autocorrelate(buf, sr, opts, scratchPS, scratchNSDF) {
    opts = opts || {};
    var minHz = opts.minHz || 120;
    var maxHz = opts.maxHz || 1300;
    var clarityThreshold = opts.clarityThreshold != null ? opts.clarityThreshold : 0.90;
    var rmsFloor = opts.rmsFloor != null ? opts.rmsFloor : 0.01;
    var peakRatio = opts.peakRatio != null ? opts.peakRatio : 0.90;  // MPM: 1º pico ≥ ratio·max
    var n = buf.length, i;

    // 1) gate de RMS — rejeita silêncio/ruído baixo antes do laço caro
    var sumsq = 0.0;
    for (i = 0; i < n; i++) { var v = buf[i]; sumsq += v * v; }
    if (Math.sqrt(sumsq / n) < rmsFloor) return null;

    // 2) prefix-sum dos quadrados → energia das janelas por lag em O(1)
    var ps = (scratchPS && scratchPS.length >= n + 1) ? scratchPS : new Float64Array(n + 1);
    ps[0] = 0.0;
    for (i = 0; i < n; i++) ps[i + 1] = ps[i] + buf[i] * buf[i];

    var minLag = Math.max(2, Math.floor(sr / maxHz));
    var maxLag = Math.min(n - 1, Math.ceil(sr / minHz));
    if (maxLag <= minLag) return null;

    // nsdf(lag) ∈ [-1,1] = 2·Σ x[i]x[i+lag] / (Σ x[i]² + Σ x[i+lag]²), i em [0, n-lag)
    function nsdf(lag) {
      var m = n - lag, ac = 0.0, k;
      for (k = 0; k < m; k++) ac += buf[k] * buf[k + lag];
      var e = ps[m] + (ps[n] - ps[lag]);
      return e > 0 ? (2 * ac) / e : 0;
    }

    // 3) NSDF em toda a faixa de lag; guarda valores e acha o máximo global
    var arr = (scratchNSDF && scratchNSDF.length > maxLag) ? scratchNSDF : new Float64Array(maxLag + 2);
    var gmax = 0;
    for (var lag = minLag; lag <= maxLag; lag++) {
      var val = nsdf(lag);
      arr[lag] = val;
      if (val > gmax) gmax = val;
    }
    if (gmax < clarityThreshold) return null;

    // 4) McLeod: escolhe o PRIMEIRO máximo local ≥ peakRatio·gmax — o período verdadeiro é
    // o pico de menor lag (maior freq); pegar o máximo global cairia na sub-oitava (2× período).
    var thr = peakRatio * gmax, bestLag = -1;
    for (var L = minLag + 1; L < maxLag; L++) {
      if (arr[L] >= thr && arr[L] >= arr[L - 1] && arr[L] >= arr[L + 1]) { bestLag = L; break; }
    }
    if (bestLag < 0) return null;

    // 5) interpolação parabólica nos vizinhos (lag sub-amostra → precisão de cents)
    var y0 = arr[bestLag - 1], y1 = arr[bestLag], y2 = arr[bestLag + 1];
    var denom = y0 - 2 * y1 + y2;
    var shift = denom !== 0 ? 0.5 * (y0 - y2) / denom : 0;
    var hz = sr / (bestLag + shift);
    if (hz < minHz || hz > maxHz) return null;
    return hz;
  }

  function hzToMidi(hz) { return 69 + 12 * Math.log(hz / 440) / Math.LN2; }

  function PitchDetector(audioContext, mediaStream, opts) {
    opts = opts || {};
    this.ac = audioContext;
    this.opts = {
      minHz: opts.minHz || 120,
      maxHz: opts.maxHz || 1300,
      clarityThreshold: opts.clarityThreshold != null ? opts.clarityThreshold : 0.90,
      rmsFloor: opts.rmsFloor != null ? opts.rmsFloor : 0.01
    };
    this.source = audioContext.createMediaStreamSource(mediaStream);
    this.analyser = audioContext.createAnalyser();
    this.analyser.fftSize = opts.fftSize || 2048;
    this.source.connect(this.analyser);   // tap de leitura — NUNCA liga em ac.destination
    this.stream = mediaStream;
    this.buf = new Float32Array(this.analyser.fftSize);
    this.scratchPS = new Float64Array(this.analyser.fftSize + 1);
    this.scratchNSDF = new Float64Array(this.analyser.fftSize + 1);
  }
  PitchDetector.prototype.detect = function () {
    this.analyser.getFloatTimeDomainData(this.buf);
    var hz = autocorrelate(this.buf, this.ac.sampleRate, this.opts, this.scratchPS, this.scratchNSDF);
    if (hz == null) return null;
    var midi = hzToMidi(hz), r = Math.round(midi);
    return { hz: hz, midi: r, cents: Math.round((midi - r) * 100) };
  };
  PitchDetector.prototype.stop = function () { try { this.source.disconnect(); } catch (e) {} };
  PitchDetector.prototype.close = function () {
    this.stop();
    if (this.stream) this.stream.getTracks().forEach(function (t) { try { t.stop(); } catch (e) {} });
  };

  var api = { PitchDetector: PitchDetector, autocorrelate: autocorrelate, hzToMidi: hzToMidi };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  global.PitchDSP = api;
  global.PitchDetector = PitchDetector;
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this));
