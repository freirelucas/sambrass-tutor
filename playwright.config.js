// Config Playwright — serve o _site estático e roda os specs em chromium com áudio fake.
// Pré-requisito: `python3 app/build_site.py` (gera _site) e `npx playwright install chromium`.
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  timeout: 30000,
  fullyParallel: false,
  use: { baseURL: 'http://localhost:8099' },
  webServer: {
    command: 'python3 -m http.server 8099 --directory _site',
    url: 'http://localhost:8099/estudo.html',
    reuseExistingServer: true,
    timeout: 20000,
  },
  projects: [{
    name: 'chromium',
    use: {
      browserName: 'chromium',
      launchOptions: {
        args: [
          '--autoplay-policy=no-user-gesture-required',
          '--use-fake-device-for-media-stream',
          '--use-fake-ui-for-media-stream',
        ],
      },
    },
  }],
});
