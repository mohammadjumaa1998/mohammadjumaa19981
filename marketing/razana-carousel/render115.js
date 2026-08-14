const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DIR = __dirname;
const OUT = path.join(DIR, 'out115');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--force-color-profile=srgb'] });
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1350 },
    deviceScaleFactor: 2,
  });
  await page.goto('file://' + path.join(DIR, 'case115.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1200);

  // report any overflow so layout problems are visible
  const diag = await page.evaluate(() => {
    return [...document.querySelectorAll('.slide')].map(s => {
      const wrap = s.querySelector('.d-wrap, .e-wrap');
      return {
        id: s.id,
        h: s.getBoundingClientRect().height,
        contentH: wrap ? wrap.scrollHeight : null,
        overflow: wrap ? wrap.scrollHeight - wrap.clientHeight : null,
      };
    });
  });
  console.log('LAYOUT DIAGNOSTICS:');
  diag.forEach(d => console.log(`  ${d.id}: slide=${d.h} contentH=${d.contentH} overflow=${d.overflow}`));

  const ids = ['s1', 's2', 's3', 's4', 's5', 's6', 's7'];
  for (let i = 0; i < ids.length; i++) {
    const el = await page.$('#' + ids[i]);
    const n = String(i + 1).padStart(2, '0');
    await el.screenshot({ path: path.join(OUT, `case115-${n}.png`) });
    console.log('rendered', `case115-${n}.png`);
  }

  await browser.close();
})();
