"""Gera o PDF do cardápio de mesa (A4, frente e verso).
Uso:  python mesa/build_mesa.py      (rodar da raiz do projeto)
Requer: pip install playwright && playwright install chromium
Fontes: Lora e Poppins instaladas no sistema (Google Fonts). O logo "Tia Lu" e os títulos
"Pizzas"/"Porções" já são imagens (wordmark.png, pizzas.png, porcoes.png)."""
import os, pathlib
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent
site = (root/'site'/'index.html').read_text(encoding='utf-8')
eng = site[site.index('function hash('):site.index('/* ---------- Estado')]   # desenho das panelinhas/pizzas
html = (root/'mesa'/'mesa.html').read_text(encoding='utf-8').replace('/*ENGINE*/', eng)
build = root/'mesa'/'_build.html'; build.write_text(html, encoding='utf-8')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto(build.as_uri()); pg.wait_for_timeout(800)
    pg.pdf(path=str(root/'mesa'/'cardapio-mesa-tia-lu.pdf'), format='A4', print_background=True,
           margin={'top':'0','bottom':'0','left':'0','right':'0'})
    b.close()
build.unlink()
print('PDF gerado em mesa/cardapio-mesa-tia-lu.pdf')
