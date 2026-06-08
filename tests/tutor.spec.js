/* Testes de navegador do tutor de escuta (Playwright).
 *   - detector: microfone SINTÉTICO (oscilador → MediaStreamDestination, sem permissão real)
 *     varrendo notas da faixa do trompete; assert do MIDI detectado.
 *   - página de estudo: carrega, mostra o badge de nível e os controles do tutor, sem erro.
 * Requer um browser: `npx playwright install chromium`. Rodar: `npx playwright test`.
 */
const { test, expect } = require('@playwright/test');
const path = require('path');

test('detector recupera o tom de um microfone sintético (oscilador → MediaStream)', async ({ page }) => {
  await page.goto('/');                                   // estabelece a origem http
  await page.setContent('<!doctype html><meta charset="utf-8"><title>detector</title>');
  await page.addScriptTag({ path: path.resolve(__dirname, '../app/vendor/pitch-detector.js') });

  const results = await page.evaluate(async () => {
    const midiToHz = (m) => 440 * Math.pow(2, (m - 69) / 12);
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    if (ac.state === 'suspended') await ac.resume();
    const dest = ac.createMediaStreamDestination();
    const osc = ac.createOscillator();
    osc.type = 'sawtooth';                                // rico em harmônicos, como o metal
    osc.connect(dest); osc.start();
    const det = new PitchDetector(ac, dest.stream, { minHz: 120, maxHz: 1300 });
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const out = [];
    for (const m of [55, 60, 62, 67, 72, 79]) {
      osc.frequency.value = midiToHz(m);
      await sleep(220);
      let got = null;
      for (let k = 0; k < 10 && got == null; k++) { got = det.detect(); if (!got) await sleep(30); }
      out.push({ target: m, detected: got ? got.midi : null });
    }
    det.close(); osc.stop(); await ac.close();
    return out;
  });

  console.log('varredura do detector:', JSON.stringify(results));
  const hits = results.filter((r) => r.detected === r.target).length;
  expect(hits, 'maioria das notas detectada corretamente').toBeGreaterThanOrEqual(results.length - 1);
});

test('página de estudo carrega com badge de nível e controles do tutor', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('/estudo.html?id=sb-011');
  await expect(page.locator('#badges')).toContainText('nível', { timeout: 10000 });
  for (const id of ['#tmic', '#tprat', '#tloop', '#tramp', '#tuner', '#needle']) {
    await expect(page.locator(id)).toHaveCount(1);
  }
  expect(errors, 'sem exceções não tratadas na página').toEqual([]);
});

test('ligar microfone e praticar: tuner ativa e o cursor silencioso avança', async ({ page, context }) => {
  await context.grantPermissions(['microphone']);
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('/estudo.html?id=sb-011');
  await expect(page.locator('#badges')).toContainText('nível');

  await page.click('#tmic');                                  // mic (fake device) → tuner ativo
  await expect(page.locator('#tuner')).toHaveClass(/ativo/);

  await page.click('#tprat');                                 // praticar → TimingCallbacks + clave
  await expect(page.locator('#tprat')).toContainText('parar');
  await expect(page.locator('.abcjs-highlight').first()).toBeVisible({ timeout: 5000 });

  await page.click('#tprat');                                 // parar
  await expect(page.locator('#tprat')).toContainText('praticar');
  expect(errors, 'sem exceções nos fluxos de mic/prática').toEqual([]);
});
