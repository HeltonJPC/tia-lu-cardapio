# Cardápio Tia Lu — contexto do projeto

Cliente: **Pizzaria & Lanchonete Tia Lu** — Rua Quinze de Agosto, 1844, Morro Santana, Ouro Preto/MG.
WhatsApp da pizzaria: (31) 99783-9091 · Instagram: @pizzarialanchonetetialu.
Fechou negócio em out/2026 (R$ 490). Eles vão comprar o domínio (sugestão: pizzariatialu.com.br no Registro.br; tialu.com.br já é de outra pessoa).

## Estrutura (v2, 28/10/2026)
- `site/index.html` — cardápio do cliente, um arquivo só (HTML + CSS + JS), sem build. Lê `/api/menu`; se a API não existir, cai no `menu.json`.
- `site/admin/index.html` — painel da pizzaria (senha única). Edita tudo e salva com PUT em `/api/menu`.
- `functions/api/menu.js` — Cloudflare Pages Function. GET: KV `menu` ou `site/menu.json`. POST: confere a senha. PUT: valida, grava `updated`, faz backup diário (`backup-AAAA-MM-DD`, 30 dias).
  Bindings: KV `MENU` + secret `ADMIN_PASSWORD`. Sem wrangler.toml de propósito (com ele o painel da Cloudflare trava as configurações).
- `site/menu.json` — cardápio inicial, tirado do cardápio novo deles (`Desktop\Tia Lu\Cardapio-Delivery-Tia-Lu-v2.pdf`), **todos os preços em null** ("Consultar") até eles preencherem pelo painel.
- `scripts/dev.mjs` — servidor local que roda a Function de verdade com KV em `.dev-kv.json`. `node scripts/dev.mjs` → :8788, senha `teste`.
- `scripts/limpa_logo.py` — tira o xadrez "falso" pintado no JPEG da logo (`fotos/originais/logo.jpeg` → `site/img/logo.webp`, fundo branco).
- `site/img/pizza.webp` — pizza do PDF (extraída com a máscara de transparência).

## Formato do menu.json
- `store`: `whats` (55+DDD+número), `force` (`''` automático | `aberta` | `fechada`), `hours[0..6]` (Dom..Sáb, `["18:00","01:00"]` ou null; passa da meia-noite), `notice`, `delivery` {`mode`: combinar|fixa|bairro, `fee`, `areas`:[{n,p}]}.
- `sections[]`: {id, title, kind?:'pizza', sizes? , groups[]}. Grupo de pizza: `prices[]` por tamanho + `extra` (acréscimo, só aparece se tiver valor). Grupo comum: itens com `p`. Grupo com `cols` (refrigerantes): `p` é array; `null` = Consultar, `false` = não vende.
- Item: id, name, desc?, opts? (cliente escolhe uma), off? (esgotado).
- Meio a meio: vale o preço da categoria mais cara (regra assumida, confirmar com o cliente). `half[]` na seção de pizza diz em quais tamanhos é permitido (Pequena não tem, pedido do Helton 28/10); liga/desliga no painel.
- Pedido no navegador do cliente (`tialu-cart3`) guarda só a escolha de cada item (`sp`); nome e preço são recalculados do cardápio atual (`build`/`reprice`). Item que sumiu/esgotou sai do pedido com aviso.
- Com a página aberta, o cardápio confere `/api/menu` a cada 60 s (e ao voltar para a aba) e redesenha se `updated` mudou.
- **Fotos das pizzas**: `site/fotos.json` (`{"id-do-sabor": "img/pizzas/x.webp"}`), miniaturas 160 px em `site/img/pizzas/`. Vêm pelo GitHub, NÃO pelo painel (o cardápio salvo no KV não tem foto). Sabor sem foto mostra ícone de pizza em traço. Para foto nova: tratar, salvar em img/pizzas/<id>.webp, registrar no fotos.json (ids reais: GET /api/menu). Hoje são as 3 fotos do v1 (provisórias).

## Visual
Segue o impresso v2: fundo branco, verde #1e5b2e, vermelho #b8231b, cinza #55524c. Fontes Bricolage Grotesque (títulos) + DM Sans (texto). Tema claro único, de propósito.

## Legado
- `mesa/` — cardápio de mesa do tema escuro antigo (v1). O `build_mesa.py` recortava as funções de desenho do site antigo, que não existem mais no v2: **não funciona mais**. Eles agora têm o impresso próprio (PDF v2).
- `fotos/tratadas/` e `site/img/{torresmo,portuguesa,calabresa}.webp` — fotos do v1, hoje sem uso no site.

## No ar
- https://tia-lu-cardapio.pages.dev (Cloudflare Pages, conta do Helton) ligado a github.com/heltonjpc/tia-lu-cardapio; KV `tialu-menu` → binding `MENU`; secret `ADMIN_PASSWORD`. Push em main = deploy.
- O KV já tem cardápio salvo pelo painel: mudar `site/menu.json` NÃO afeta mais o site (só vale como reserva se a API falhar).

## Pendências
- Preços: a Tia Lu preenche pelo painel (o PDF v2 veio com R$ 00,00).
- Taxa de entrega: Morro Santana e Morro São Sebastião = R$ 3; qualquer outro bairro = R$ 4. Sugestão (aguardando ok): modo "Por bairro" com 3 linhas (os dois Morros + "Outro bairro"), sem texto livre.
- Horário de funcionamento: eles preenchem pelo painel.
- Domínio (já comprado): trocar nameservers no Registro.br para a Cloudflare e adicionar em Custom domains.
- Confirmar regra do meio a meio e se acréscimo de pizza tem preço único.
