# Cardápio Tia Lu

- `site/index.html` — cardápio do cliente (pedido pelo WhatsApp).
- `site/admin/` — painel da pizzaria: itens, preços, esgotado, horário, aviso, WhatsApp e taxa de entrega.
- `functions/api/menu.js` — API (Cloudflare Pages Function) que lê/grava o cardápio no KV.
- `site/menu.json` — cardápio inicial; vale até o primeiro "Salvar" no painel.

## Rodar no computador
    node scripts/dev.mjs
Cardápio em http://localhost:8788 · painel em http://localhost:8788/admin/ (senha: `teste`).
O que for salvo fica em `.dev-kv.json` (apague o arquivo para voltar ao `menu.json`).

## Publicar no Cloudflare Pages (gratuito)
Functions só funcionam com o projeto ligado ao Git (o "upload de arquivos" do painel não roda a API).

1. Suba esta pasta inteira para um repositório no GitHub (com `site/` e `functions/` na raiz).
2. Cloudflare → **Workers & Pages → Create → Pages → Connect to Git** → escolha o repositório.
   - Framework preset: **None** · Build command: *(vazio)* · Build output directory: **`site`**
3. Cloudflare → **Storage & Databases → KV → Create namespace** → nome `tialu-menu`.
4. No projeto do Pages → **Settings → Bindings → Add → KV namespace**: variável **`MENU`**, namespace `tialu-menu`.
5. **Settings → Variables and Secrets → Add** → tipo **Secret**, nome **`ADMIN_PASSWORD`**, valor = senha da pizzaria.
6. **Deployments → Retry deployment** (bindings e senha só valem a partir do próximo deploy).
7. Domínio: **Custom domains → Set up a domain** → `pizzariatialu.com.br` (o Registro.br aponta para os nameservers do Cloudflare).

Trocar a senha: repetir o passo 5 com o novo valor e fazer um novo deploy.
Cópia de segurança: a cada dia em que se salva, a versão anterior fica no KV como `backup-AAAA-MM-DD` por 30 dias.
