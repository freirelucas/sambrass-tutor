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
  await expect(page.locator('#rasc')).toContainText('conferida');   // sb-011 = tier conferida
  for (const id of ['#tmic', '#tprat', '#tloop', '#tramp', '#tuner', '#needle']) {
    await expect(page.locator(id)).toHaveCount(1);
  }
  expect(errors, 'sem exceções não tratadas na página').toEqual([]);
});

test('rótulo de qualidade reflete o tier (melodia fundida pelos dedos)', async ({ page }) => {
  await page.goto('/estudo.html?id=sb-003');                        // sb-003 = tier dedos
  await expect(page.locator('#rasc')).toContainText('pelos dedos', { timeout: 10000 });
});

test('banco mostra o nível pedagógico e filtra por ele', async ({ page }) => {
  await page.goto('/index.html');
  await page.waitForFunction(() => document.querySelector('#tela') && document.querySelector('#tela').textContent.length > 40);
  await page.evaluate(() => ir('banco'));                           // ir() é global (onclick inline)
  await expect(page.locator('#fnivel')).toBeVisible();
  await expect(page.locator('#listapecas .niv').first()).toBeVisible();
  await page.selectOption('#fnivel', 'book1');                      // filtra Book 1
  const chips = await page.locator('#listapecas .niv').allInnerTexts();
  expect(chips.length, 'há peças Book 1').toBeGreaterThan(0);
  expect(chips.every((t) => t.includes('Book 1')), 'só Book 1 no filtro').toBeTruthy();
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

/* ---- rota "O Caminho do Sambrass": trilha + Stories + desafios (o melhor dos dois) ---- */
test('trilha é a home: 110 nós em 6 lotes, sem cadeado, com bandeira SUGERIDA', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('/index.html');
  await expect(page.locator('.path .node')).toHaveCount(110, { timeout: 10000 });
  await expect(page.locator('.lotehead')).toHaveCount(6);
  await expect(page.locator('.prepnode')).toBeVisible();                 // aquecimento
  await expect(page.locator('.node.here .flag')).toContainText('SUGERIDA');
  await expect(page.locator('.hud')).toContainText('/110');
  expect(errors, 'trilha sem exceções').toEqual([]);
});

test('Story por música: capa→perfil→plano→desafio com pauta→diário marca dominada', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('/index.html');
  await expect(page.locator('.path .node')).toHaveCount(110, { timeout: 10000 });

  await page.locator('.node .inner').first().click();                    // abre a Story (lazy pedagogia)
  await expect(page.locator('#story.on')).toBeVisible();
  await expect(page.locator('.slide h2')).toBeVisible();                 // capa: título

  let sawSvg = false;                                                    // avança até a pauta de um desafio
  for (let i = 0; i < 12; i++) {
    if (await page.locator('.scorebox svg').first().isVisible().catch(() => false)) { sawSvg = true; break; }
    await page.click('.snext');
  }
  expect(sawSvg, 'um desafio mostra a pauta (SVG pré-assado)').toBeTruthy();

  for (let i = 0; i < 8 && !(await page.locator('#rate').isVisible().catch(() => false)); i++) await page.click('.snext');
  await expect(page.locator('#rate')).toBeVisible();                     // diário
  await page.locator('#rate button').nth(3).click();                     // autoavaliação nível 4
  await page.click('.snext');                                            // concluir
  await expect(page.locator('#story.on')).toBeHidden();
  await expect(page.locator('.node .inner.done').first()).toBeVisible(); // virou dominada (✓)
  expect(errors, 'Story sem exceções').toEqual([]);
});

test('a síntese: o desafio leva ao tutor de escuta real (estudo.html)', async ({ page }) => {
  await page.goto('/index.html');
  await expect(page.locator('.path .node')).toHaveCount(110, { timeout: 10000 });
  await page.locator('.node .inner').first().click();
  await expect(page.locator('.micbtn').first()).toBeVisible();
  await page.locator('.micbtn').first().click();                         // 🎤 tocar no tutor
  await page.waitForURL(/estudo\.html\?id=sb-\d+/);
  await expect(page.locator('#badges')).toContainText('nível', { timeout: 10000 });
});
