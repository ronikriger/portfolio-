// Renders resume.pdf, og.jpg (link preview), apple-touch-icon.png and favicon-32.png into public/.
//   node tools/render.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const root = path.resolve(__dirname, '..');
  const pub = path.join(root, 'public');
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy });

  // Résumé
  let page = await browser.newPage();
  await page.goto('file://' + path.join(root, 'tools/resume.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(pub, 'resume.pdf'), format: 'Letter', printBackground: true, preferCSSPageSize: true });
  await page.close();

  // Link preview: the real hero at 1200x630, light theme, arcs fully drawn
  let ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1, colorScheme: 'light', reducedMotion: 'reduce' });
  page = await ctx.newPage();
  await page.goto('file://' + path.join(pub, 'index.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.addStyleTag({ content: '.site-header{display:none}.hero{padding-block:56px 40px!important}.globe-fig .stops,.globe-hint,.langs{display:none}.globe-box{max-width:520px}' });
  await page.waitForTimeout(900);
  await page.screenshot({ path: path.join(pub, 'og.jpg'), type: 'jpeg', quality: 88, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  await ctx.close();

  // Home-screen icon
  ctx = await browser.newContext({ viewport: { width: 180, height: 180 }, deviceScaleFactor: 1 });
  page = await ctx.newPage();
  const svg = fs.readFileSync(path.join(pub, 'favicon.svg'), 'utf8').replace('rx="14"', 'rx="0"');
  await page.setContent(`<style>html,body{margin:0}svg{width:180px;height:180px;display:block}</style>${svg}`);
  await page.screenshot({ path: path.join(pub, 'apple-touch-icon.png'), clip: { x: 0, y: 0, width: 180, height: 180 } });
  await ctx.close();
  ctx = await browser.newContext({ viewport: { width: 32, height: 32 }, deviceScaleFactor: 1 });
  page = await ctx.newPage();
  await page.setContent(`<style>html,body{margin:0;background:transparent}svg{width:32px;height:32px;display:block}</style>${fs.readFileSync(path.join(pub, 'favicon.svg'), 'utf8')}`);
  await page.screenshot({ path: path.join(pub, 'favicon-32.png'), omitBackground: true, clip: { x: 0, y: 0, width: 32, height: 32 } });
  await browser.close();
  console.log('rendered resume.pdf, og.jpg, apple-touch-icon.png, favicon-32.png');
})().catch(e => { console.error(e); process.exit(1); });
