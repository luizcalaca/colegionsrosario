"""Remove o fundo cinza do brasão preservando as bordas antisserrilhadas."""
import sys
from collections import deque
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGBA")
a = np.asarray(im).astype(np.float32)
rgb = a[..., :3]
H, W = rgb.shape[:2]

mx = rgb.max(axis=2)
mn = rgb.min(axis=2)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)   # 0 = cinza puro
chroma = mx - mn

# Candidato a fundo: pouco croma (cinza claro do fundo e da sombra projetada)
cand = chroma < 26

# Flood fill a partir das bordas: só o cinza CONECTADO à moldura é fundo,
# o que impede vazamento para reflexos acinzentados dentro do brasão.
bg = np.zeros((H, W), dtype=bool)
q = deque()
for x in range(W):
    for y in (0, H - 1):
        if cand[y, x] and not bg[y, x]:
            bg[y, x] = True; q.append((y, x))
for y in range(H):
    for x in (0, W - 1):
        if cand[y, x] and not bg[y, x]:
            bg[y, x] = True; q.append((y, x))

while q:
    y, x = q.popleft()
    for dy, dx in ((1,0), (-1,0), (0,1), (0,-1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W and cand[ny, nx] and not bg[ny, nx]:
            bg[ny, nx] = True
            q.append((ny, nx))

# Matte suave APENAS numa faixa de 2 px junto à silhueta: recupera o antialias
# original da borda sem preservar os resíduos da sombra projetada, que também
# têm croma residual mas ficam longe do brasão.
fg = ~bg
band = np.zeros_like(bg)
for dy in range(-2, 3):
    for dx in range(-2, 3):
        band |= np.roll(np.roll(fg, dy, axis=0), dx, axis=1)
band &= bg

soft = np.clip((chroma - 16.0) / 28.0, 0.0, 1.0)
alpha = np.where(bg, np.where(band, soft, 0.0), 1.0)

# Reduz a franja clara herdada do fundo nos pixels semitransparentes
edge = (alpha > 0.02) & (alpha < 0.98)
if edge.any():
    al = alpha[edge][:, None]
    rgb[edge] = np.clip((rgb[edge] - (1 - al) * 242.0) / np.maximum(al, 0.15), 0, 255)

# Descarta ilhas opacas minúsculas (ruído do render que sobrou na sombra),
# mantendo apenas o componente conectado do brasão.
solid = alpha > 0.5
seen = np.zeros_like(solid)
best = None
for sy in range(0, H, 4):
    for sx in range(0, W, 4):
        if not solid[sy, sx] or seen[sy, sx]:
            continue
        comp = []
        st = [(sy, sx)]
        seen[sy, sx] = True
        while st:
            y, x = st.pop()
            comp.append((y, x))
            for dy, dx in ((1,0), (-1,0), (0,1), (0,-1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and solid[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    st.append((ny, nx))
        if best is None or len(comp) > len(best):
            best = comp

keep = np.zeros_like(solid)
ys, xs = zip(*best)
keep[np.array(ys), np.array(xs)] = True
for dy in range(-3, 4):
    for dx in range(-3, 4):
        keep |= np.roll(np.roll(keep, dy, axis=0), dx, axis=1)
alpha = np.where(keep, alpha, 0.0)

out = np.dstack([rgb, alpha * 255.0]).astype(np.uint8)
img = Image.fromarray(out, "RGBA")
img = img.crop(img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
print("recortado para:", img.size)
img.save(dst)
