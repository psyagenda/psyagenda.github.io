import { chromium } from 'playwright';
const P = process.env.HOME + '/Desktop/psyagenda.github.io/' + (process.argv[2] || '_preview') + '/';
const pages = ['index.html','index-en.html','privacy-tr.html','privacy-en.html','terms-tr.html','terms-en.html','faq-tr.html','faq-en.html','guide-tr.html','guide-en.html'];
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
await ctx.addInitScript(() => {});
let bad = 0;
for (const f of pages) {
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('JS: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  page.on('requestfailed', r => errs.push('istek: ' + r.url().split('/').pop()));
  await page.goto('file://' + P + f, { waitUntil: 'load' });
  await page.waitForTimeout(400);
  const toc = await page.$$eval('#toc-list a', a => a.length).catch(() => 0);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  console.log((errs.length || overflow ? 'HATA ' : 'ok   ') + f.padEnd(16) + ' toc=' + String(toc).padStart(2) + (overflow ? ' YATAY-TAŞMA' : '') + (errs.length ? '  ' + errs.join(' | ') : ''));
  if (errs.length || overflow) bad++;
  await page.close();
}
// EN anasayfa üst kısım
let page = await ctx.newPage(); await page.emulateMedia({ reducedMotion: 'reduce' });
await page.goto('file://' + P + 'index-en.html'); await page.waitForTimeout(300);
await page.screenshot({ path: 'en_home.png' });
// Rehber: ilk bölüm açık
await page.goto('file://' + P + 'guide-tr.html'); await page.waitForTimeout(300);
await page.$eval('.guide-section', d => d.open = true);
await page.waitForTimeout(200); await page.screenshot({ path: 'guide_open.png' });
// Gizlilik: ortaya kaydır, vurgu doğru mu
await page.goto('file://' + P + 'privacy-tr.html'); await page.waitForTimeout(300);
await page.evaluate(() => window.scrollTo(0, 2600)); await page.waitForTimeout(400);
const cur = await page.$eval('#toc-list a.current', a => a.textContent).catch(() => '(yok)');
console.log('kaydırma sonrası vurgulu bölüm:', cur);
await page.screenshot({ path: 'priv_mid.png' });
await browser.close();
console.log(bad ? `${bad} sayfada sorun` : 'tüm sayfalar temiz');
