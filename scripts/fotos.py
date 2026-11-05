# Fotos do cliente -> miniaturas 240 px do site (site/img/pizzas e site/img/porcoes) + site/fotos.json.
# Fundo (branco ou o xadrez "falso" pintado) = pixel claro e sem cor. Pizza: recorte redondo com transparência; porção: quadrado no fundo branco.
# Uso: python scripts/fotos.py "<pasta das fotos>"   (o mapa arquivo -> id fica em FOTOS abaixo)
import sys, json, pathlib, numpy as np, cv2
from PIL import Image

FOTOS = {  # arquivo do cliente: (id no cardápio, é pizza?)
 'Pizza portuguesa': ('portuguesa', 1), 'Pizza de Calabresa com Cebola': ('calabresa', 1), 'Pizza de Calabresa picante': ('calabresa-picante', 1),
 'Pizza de frango com catupiry': ('frango-catupiry', 1), 'Pizza de Lombinho': ('lombinho', 1), 'Pizza de brcolis': ('brocolis', 1),
 'Pizza bacon': ('bacon', 1), 'Pizza muarela': ('mucarela', 1), 'Pizza de palmito': ('palmito', 1), 'Pizza milho': ('milho', 1),
 'Pizza de torresmo': ('torresmo', 1), 'Pizzza a mineira': ('mineira', 1), 'Pizza de iscas de file': ('iscas-file', 1),
 'Pizza  PEITO DE PERU': ('peito-peru', 1), 'Pizza de Frango com Bacon': ('frango-bacon', 1),
 'Batatas fritas com queijo e bacon': ('batata-qb', 0), 'Torresmo': ('torresmo-p', 0), 'Nuggets': ('nuggets', 0),
 'Trio mineiro': ('trio', 0), 'file de grango com catupiry': ('frango-catupiry-p', 0), 'meio da asa': ('meio-asa', 0),
}
src, root, S = pathlib.Path(sys.argv[1]), pathlib.Path(__file__).resolve().parents[1] / 'site', 240
fotos = json.loads((root / 'fotos.json').read_text(encoding='utf-8'))
for nome, (fid, pizza) in FOTOS.items():
    im = cv2.imread(str(src / f'{nome}.png'), cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    obj = ~((hsv[..., 1] < 22) & (hsv[..., 2] > 165))
    obj = cv2.morphologyEx(obj.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj)
    x, y, w, h = st[1 + st[1:, cv2.CC_STAT_AREA].argmax(), :4]
    cx, cy, r = x + w / 2, y + h / 2, max(w, h) / 2 * (0.955 if pizza else 1.04)
    pad = int(r) + 4
    big = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    c = big[int(cy - r) + pad:int(cy + r) + pad, int(cx - r) + pad:int(cx + r) + pad]
    c = cv2.cvtColor(cv2.resize(c, (S, S), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    if pizza:
        yy, xx = np.mgrid[:S, :S]; d = np.hypot(xx - S / 2 + .5, yy - S / 2 + .5) / (S / 2)
        c = np.dstack([c, (np.clip((1 - d) / 0.02, 0, 1) * 255).astype(np.uint8)])
    pasta = 'pizzas' if pizza else 'porcoes'; (root / 'img' / pasta).mkdir(exist_ok=True)
    Image.fromarray(c).save(root / 'img' / pasta / f'{fid}.webp', quality=84, method=6)
    fotos[fid] = f'img/{pasta}/{fid}.webp'
(root / 'fotos.json').write_text(json.dumps(fotos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(len(FOTOS), 'fotos ->', len(fotos), 'no fotos.json')
