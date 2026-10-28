import sys, numpy as np, cv2
im = cv2.imread(sys.argv[1]); h, w = im.shape[:2]
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
s = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[...,1]
neu = s < 16
# área do chef: componente de pele/cabelo/botões (saturado) ampliado
sat = ((s > 40) & (g > 60)).astype(np.uint8)
sat[600:] = 0                                   # abaixo do chef só tem letra
ys, xs = np.where(sat); chef = np.zeros((h,w), bool)
y0 = max(0, ys.min()-150); x0 = max(0, xs.min()-110); x1 = min(w, xs.max()+40)
y0, x0, x1 = 255, 332, 606; chef[y0:600, x0:x1] = True
out = np.zeros((h,w), bool)
out |= ~chef & neu & (g > 150)                  # fora do chef: tudo neutro claro
m = cv2.blur(g,(9,9)); sd = np.sqrt(np.maximum(cv2.blur(g*g,(9,9))-m*m,0))
grey = ((np.abs(g-204) <= 8) & (s < 10)).astype(np.uint8)
blk = cv2.morphologyEx(grey, cv2.MORPH_OPEN, np.ones((9,9),np.uint8))
flat = cv2.morphologyEx(((sd < 2.2) & (s < 12) & (g > 190)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((7,7),np.uint8))
out |= chef & cv2.dilate(blk|flat, np.ones((5,5),np.uint8)).astype(bool) & neu & (g > 150)
out |= (g > 246) & (s < 10)
o = im.copy(); o[out] = 255
print('chef box', y0, x0, x1)
nz = np.where(o.min(axis=2) < 230); a,b,c,d = nz[0].min(),nz[0].max(),nz[1].min(),nz[1].max()
cv2.imwrite(sys.argv[2], o[max(0,a-12):b+12, max(0,c-12):d+12])
