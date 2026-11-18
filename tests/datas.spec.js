/* Datas no fuso LOCAL, não em UTC — e a sequência que não zera antes da prática do dia.
 *   - toISOString() devolve a data de Greenwich: prática às 22h30 em Brasília caía no dia
 *     seguinte. timezoneId fixa o relógio do navegador em Brasília em qualquer máquina.
 *   - sequência: com 30 dias seguidos até ontem, às 10h de hoje ainda vale 30 (o dia de
 *     hoje está em aberto, não quebrado).
 */
const { test, expect } = require('@playwright/test');

test.use({ timezoneId: 'America/Sao_Paulo' });

test('o dia de prática é o local: 22h30 em Brasília é 18/11, não 19/11', async ({ page }) => {
  await page.clock.setFixedTime(new Date('2026-11-18T22:30:00-03:00'));
  await page.goto('/index.html');
  expect(await page.evaluate(() => diaLocal())).toBe('2026-11-18');

  await page.goto('/estudos.html');
  await page.evaluate(() => marcaDia());
  const dias = await page.evaluate(() => JSON.parse(localStorage.getItem('est_dias')));
  expect(dias, 'marcaDia grava o dia local').toEqual(['2026-11-18']);
});

test('sequência: 30 dias seguidos até ontem continuam valendo às 10h de hoje', async ({ page }) => {
  await page.clock.setFixedTime(new Date('2026-11-18T10:00:00-03:00'));
  await page.goto('/estudos.html');
  await page.evaluate(() => {
    const l = [];
    for (let i = 1; i <= 30; i++) { const d = new Date(); d.setDate(d.getDate() - i); l.push(diaLocal(d)); }
    localStorage.setItem('est_dias', JSON.stringify(l));
  });
  await page.reload();
  await expect(page.locator('.es-sub')).toContainText('30');
  await expect(page.locator('.es-sub'), 'não pode voltar a "primeiro dia"').not.toContainText('Primeiro dia');
});

test('sequência: quem ainda não praticou hoje e não praticou ontem recomeça do zero', async ({ page }) => {
  await page.clock.setFixedTime(new Date('2026-11-18T10:00:00-03:00'));
  await page.goto('/estudos.html');
  await page.evaluate(() => {
    const d = new Date(); d.setDate(d.getDate() - 2);            // só anteontem
    localStorage.setItem('est_dias', JSON.stringify([diaLocal(d)]));
  });
  await page.reload();
  await expect(page.locator('.es-sub')).toContainText('Primeiro dia');
});
