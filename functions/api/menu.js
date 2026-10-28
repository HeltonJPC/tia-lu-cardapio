// /api/menu — GET devolve o cardápio (KV ou o padrão site/menu.json); POST confere a senha; PUT salva (precisa da senha).
// KV: binding MENU. Senha: variável secreta ADMIN_PASSWORD no painel da Cloudflare.
const JSON_H = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' };
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function authorized(request, env) {
  if (!env.ADMIN_PASSWORD) return false;
  const enc = new TextEncoder(), dig = s => crypto.subtle.digest('SHA-256', enc.encode(s));
  const [a, b] = (await Promise.all([dig(request.headers.get('authorization') || ''), dig('Bearer ' + env.ADMIN_PASSWORD)])).map(x => new Uint8Array(x));
  let d = 0; for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i];
  if (d) await sleep(800);                                            // freia tentativa de adivinhar senha
  return d === 0;
}

export async function onRequestGet({ request, env }) {
  const saved = await env.MENU.get('menu');
  const body = saved ?? await (await env.ASSETS.fetch(new URL('/menu.json', request.url))).text();
  return new Response(body, { headers: JSON_H });
}

export async function onRequestPost({ request, env }) {
  return (await authorized(request, env)) ? new Response('{"ok":true}', { headers: JSON_H }) : new Response('Senha incorreta', { status: 401 });
}

export async function onRequestPut({ request, env }) {
  if (!(await authorized(request, env))) return new Response('Senha incorreta', { status: 401 });
  const txt = await request.text();
  if (txt.length > 300000) return new Response('Cardápio grande demais', { status: 413 });
  let m; try { m = JSON.parse(txt); } catch { return new Response('JSON inválido', { status: 400 }); }
  if (!m || typeof m.store !== 'object' || !Array.isArray(m.sections)) return new Response('Cardápio inválido', { status: 400 });
  m.updated = Date.now();                                             // o site do cliente limpa pedidos montados com o cardápio antigo
  const old = await env.MENU.get('menu');
  if (old) await env.MENU.put('backup-' + new Date().toISOString().slice(0, 10), old, { expirationTtl: 60 * 60 * 24 * 30 }); // 1 cópia por dia, 30 dias
  await env.MENU.put('menu', JSON.stringify(m));
  return new Response('{"ok":true}', { headers: JSON_H });
}
