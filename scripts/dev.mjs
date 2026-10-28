// Servidor local que imita o Cloudflare Pages: serve site/ e roda functions/api/menu.js com um KV em arquivo.
// Uso (da raiz do projeto):  node scripts/dev.mjs   → http://localhost:8788  (senha do admin: teste, ou ADMIN_PASSWORD=...)
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(root, 'site'), kvFile = path.join(root, '.dev-kv.json');
const fn = await import(pathToFileURL(path.join(root, 'functions/api/menu.js')));
const TYPES = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.webp': 'image/webp', '.png': 'image/png', '.js': 'text/javascript', '.svg': 'image/svg+xml' };

const kvData = JSON.parse(await fs.readFile(kvFile, 'utf8').catch(() => '{}'));
const MENU = {
  get: async k => kvData[k] ?? null,
  put: async (k, v) => { kvData[k] = v; await fs.writeFile(kvFile, JSON.stringify(kvData)); }
};
async function file(p) {
  let f = path.join(site, decodeURIComponent(p));
  if (!f.startsWith(site)) return new Response('Proibido', { status: 403 });
  if ((await fs.stat(f).catch(() => null))?.isDirectory()) f = path.join(f, 'index.html');
  try { return new Response(await fs.readFile(f), { headers: { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' } }); }
  catch { return new Response('Não encontrado', { status: 404 }); }
}
const env = { MENU, ADMIN_PASSWORD: process.env.ADMIN_PASSWORD || 'teste', ASSETS: { fetch: u => file(new URL(u).pathname) } };

http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost:8788');
  const body = ['GET', 'HEAD'].includes(req.method) ? undefined : await new Promise(r => { const c = []; req.on('data', d => c.push(d)); req.on('end', () => r(Buffer.concat(c))); });
  const request = new Request(url, { method: req.method, headers: req.headers, body });
  let r;
  if (url.pathname === '/api/menu') {
    const h = fn['onRequest' + req.method[0] + req.method.slice(1).toLowerCase()];
    r = h ? await h({ request, env }) : new Response('Método não permitido', { status: 405 });
  } else r = await file(url.pathname);
  res.writeHead(r.status, Object.fromEntries(r.headers));
  res.end(Buffer.from(await r.arrayBuffer()));
}).listen(8788, () => console.log('http://localhost:8788  ·  admin: http://localhost:8788/admin/'));
