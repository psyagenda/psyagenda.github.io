// Kullanım: node shot.mjs <html-yolu> <çıktı.png> [genişlik] [yükseklik|full]
import { chromium } from 'playwright';
const [,, file, out, w = '1440', h = '1200'] = process.argv;
const browser = await chromium.launch();
const isMobile = Number(w) < 700;
const ctx = await browser.newContext({ viewport: { width: Number(w), height: h === 'full' ? 900 : Number(h) }, deviceScaleFactor: 1, isMobile, hasTouch: isMobile });
const page = await ctx.newPage();
await page.emulateMedia({ reducedMotion: 'reduce' }); // son hâli çek, geçiş ortasını değil
await page.goto('file://' + file, { waitUntil: 'load' });
// kaydırmayla açılan .rise öğelerini göstermek için sayfayı sonuna kadar kaydır
await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); });
await page.waitForTimeout(700);
await page.screenshot({ path: out, fullPage: h === 'full' });
await browser.close();
console.log('yazıldı', out);
