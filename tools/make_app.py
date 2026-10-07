"""Превращает готовый сайт sites/<key>/ в сайт-приложение (PWA), как у автомоек в tver-demo.

    python tools/make_app.py lado          # один сайт
    python tools/make_app.py               # все сайты

Что делает для каждого сайта:
- рисует иконку в цветах сайта (--dark, --acc, --acc2, --bg): монограмма в кольце и знак по типу заведения
  (бар — бокал, кафе и пекарня — чашка, ресторан — вилка и нож) -> icon-192.png, icon-512.png,
  icon-maskable-512.png (с запасом под круглую маску Android), apple-touch-icon.png (180);
- manifest.webmanifest (имя, цвета, иконки, start_url) и sw.js (работа без сети);
- в <head> — manifest, apple-touch-icon, иконку вкладки, мета для iPhone; перед </body> — ../../app.js
  (кнопка «Установить», кабинет владельца #admin). Нужен уже подключённый book.js (tools/add_booking.py).
Повторный запуск обновляет всё, не дублируя."""
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITES = ROOT / "sites"
SERIF = ["georgiab.ttf", "timesbd.ttf", "DejaVuSerif-Bold.ttf"]
HEAD_MARK = re.compile(r"<!--app-->.*?<!--/app-->\n?", re.S)
BODY_MARK = re.compile(r'<script src="\.\./\.\./app\.js" defer></script>\n?')


def rgb(h):
    h = h.strip().lstrip("#")[:6]
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def serif(px):
    for name in SERIF:
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def palette(html):
    v = dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", html))
    dark = rgb(v.get("dark") or v.get("ink") or "#1a1a1a")
    acc = rgb(v.get("acc") or "#333333")
    gold = rgb(v.get("acc2") or v.get("acc") or "#c9a24a")
    light = rgb(v.get("dark-ink") or v.get("bg") or "#ffffff")
    if lum(dark) > 0.35:  # светлая тема: фон иконки — акцент
        dark, light = acc, rgb(v.get("acc-ink") or "#ffffff")
    if contrast(gold, dark) < 2.2:  # знак должен читаться на фоне
        gold = mix(light, gold, 0.35)
    return dict(dark=dark, acc=acc, gold=gold, light=light, bg=rgb(v.get("bg") or "#ffffff"))


def kind_of(html, catalog_kind):
    t = (catalog_kind + " " + (re.search(r"<title>([^<]+)", html) or [None, ""])[1]).lower()
    if re.search(r"ресторан|бистро|стейк|кухн|хинкал", t):
        return "dish"
    if re.search(r"бар\b|бар |паб|рюмочн|вин|коктейл|пив", t):
        return "glass"
    if re.search(r"кафе|кофе|пекар|bread|завтрак", t):
        return "cup"
    return "dish"


def initial(name):
    n = re.sub(r"^[\W_]+", "", name)
    return (n[:1] or "•").upper()


def draw_symbol(d, kind, cx, cy, s, color, w):
    """Знак шириной ~s по центру (cx, cy), линии толщиной w."""
    if kind == "glass":  # бокал
        top, bowl_h = cy - s * 0.55, s * 0.55
        d.polygon([(cx - s * 0.32, top), (cx + s * 0.32, top), (cx + s * 0.06, top + bowl_h), (cx - s * 0.06, top + bowl_h)], fill=color)
        d.line([(cx, top + bowl_h), (cx, cy + s * 0.38)], fill=color, width=w)
        d.line([(cx - s * 0.22, cy + s * 0.4), (cx + s * 0.22, cy + s * 0.4)], fill=color, width=w)
    elif kind == "cup":  # чашка с паром
        x0, x1, y0, y1 = cx - s * 0.34, cx + s * 0.22, cy - s * 0.12, cy + s * 0.38
        d.rounded_rectangle([x0, y0, x1, y1], radius=s * 0.1, fill=color)
        d.arc([x1 - s * 0.08, y0 + s * 0.06, x1 + s * 0.2, y0 + s * 0.3], -90, 90, fill=color, width=w)
        for dx in (-0.16, 0.0):
            x = cx + s * dx
            d.arc([x - s * 0.06, cy - s * 0.55, x + s * 0.06, cy - s * 0.35], 90, 270, fill=color, width=max(2, w // 2))
            d.arc([x - s * 0.06, cy - s * 0.35, x + s * 0.06, cy - s * 0.17], -90, 90, fill=color, width=max(2, w // 2))
    else:  # вилка и нож
        y0, y1 = cy - s * 0.55, cy + s * 0.5
        fx = cx - s * 0.22
        for dx in (-0.1, 0, 0.1):
            d.line([(fx + s * dx, y0), (fx + s * dx, y0 + s * 0.3)], fill=color, width=max(2, w * 2 // 3))
        d.rounded_rectangle([fx - s * 0.13, y0 + s * 0.26, fx + s * 0.13, y0 + s * 0.42], radius=s * 0.06, fill=color)
        d.line([(fx, y0 + s * 0.4), (fx, y1)], fill=color, width=w)
        kx = cx + s * 0.22
        d.polygon([(kx - s * 0.02, y0), (kx + s * 0.12, y0 + s * 0.12), (kx + s * 0.1, y0 + s * 0.5), (kx - s * 0.04, y0 + s * 0.5)], fill=color)
        d.line([(kx + s * 0.03, y0 + s * 0.5), (kx + s * 0.03, y1)], fill=color, width=w)


def make_icon(name, kind, pal, size, safe=1.0, rounded=False):
    S = 1024
    img = Image.new("RGB", (S, S), pal["dark"])
    # мягкий свет сверху: фон -> чуть светлее к центру
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse([S * 0.05, -S * 0.35, S * 0.95, S * 0.65], fill=90)
    img = Image.composite(Image.new("RGB", (S, S), mix(pal["dark"], pal["acc"], 0.9)), img, glow.filter(ImageFilter.GaussianBlur(S * 0.12)))
    d = ImageDraw.Draw(img)
    c, k = S / 2, safe  # k < 1 — всё внутри безопасной зоны маски
    R = S * 0.40 * k
    d.ellipse([c - R, c - R, c + R, c + R], outline=pal["gold"], width=round(S * 0.012))
    r2 = R - S * 0.03 * k
    d.ellipse([c - r2, c - r2, c + r2, c + r2], outline=mix(pal["gold"], pal["dark"], 0.55), width=round(S * 0.005))
    f = serif(round(S * 0.42 * k))
    letter = initial(name)
    box = d.textbbox((0, 0), letter, font=f)
    lw, lh = box[2] - box[0], box[3] - box[1]
    d.text((c - lw / 2 - box[0], c - S * 0.07 * k - lh / 2 - box[1]), letter, font=f, fill=pal["light"])
    # знак под буквой, между линиями
    sy = c + S * 0.235 * k
    d.line([(c - S * 0.21 * k, sy), (c - S * 0.09 * k, sy)], fill=pal["gold"], width=round(S * 0.006))
    d.line([(c + S * 0.09 * k, sy), (c + S * 0.21 * k, sy)], fill=pal["gold"], width=round(S * 0.006))
    draw_symbol(d, kind, c, sy, S * 0.13 * k, pal["gold"], max(3, round(S * 0.012 * k)))
    out = img.resize((size, size), Image.LANCZOS)
    if rounded:
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=size * 0.22, fill=255)
        bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        bg.paste(out, (0, 0), m)
        return bg
    return out


SW = """// Работа без сети: страница — сначала из сети, остальное — из кэша. Версия меняется при каждой сборке.
const V = '__V__';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', '../../book.js', '../../app.js'];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(V).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return; // сервер брони и шрифты — напрямую
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).then((res) => { caches.open(V).then((c) => c.put('index.html', res.clone())); return res; }).catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(r).then((hit) => hit || fetch(r).then((res) => { if (res.ok) { const cl = res.clone(); caches.open(V).then((c) => c.put(r, cl)); } return res; })));
});
"""


def catalog():
    rows = {}
    f = SITES / "CLIENTS.md"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\| ([a-z0-9_]+) \| ([^|]+) \| ([^|]+) \|", line)
            if m and m[1] != "Папка":
                rows[m[1]] = m[3].strip()
    return rows


def build(key, kinds):
    d = SITES / key
    page = d / "index.html"
    html = page.read_text(encoding="utf-8")
    m = re.search(r"window\.RBOOK=(\{.*?\});</script>", html)
    if not m:
        sys.exit(f"{key}: нет window.RBOOK — сначала python tools/add_booking.py {key}")
    rb = json.loads(m.group(1))
    name = rb["name"]
    pal = palette(html)
    kind = kind_of(html, kinds.get(key, ""))
    make_icon(name, kind, pal, 512).save(d / "icon-512.png", optimize=True)
    make_icon(name, kind, pal, 192).save(d / "icon-192.png", optimize=True)
    make_icon(name, kind, pal, 180).save(d / "apple-touch-icon.png", optimize=True)
    make_icon(name, kind, pal, 512, safe=0.8).save(d / "icon-maskable-512.png", optimize=True)
    make_icon(name, kind, pal, 64, rounded=True).save(d / "favicon.png", optimize=True)
    hexc = lambda c: "#%02x%02x%02x" % c
    short = name if len(name) <= 12 else name.split()[0][:12]
    manifest = {"name": name, "short_name": short, "lang": "ru", "start_url": "./", "scope": "./", "display": "standalone",
                "background_color": hexc(pal["dark"]), "theme_color": hexc(pal["dark"]),
                "description": (re.search(r'<meta name="description" content="([^"]*)"', html) or [None, ""])[1],
                "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
                          {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    (d / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    html = HEAD_MARK.sub("", html)
    html = BODY_MARK.sub("", html)
    html = re.sub(r'<link rel="icon" href="data:image/svg\+xml[^"]*">\n?', "", html)  # старая иконка вкладки
    html = re.sub(r'<meta name="theme-color" content="[^"]*">\n?', "", html)
    head = (f'<!--app--><link rel="manifest" href="manifest.webmanifest">\n'
            f'<meta name="theme-color" content="{hexc(pal["dark"])}">\n'
            f'<link rel="icon" type="image/png" href="favicon.png">\n'
            f'<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
            f'<meta name="apple-mobile-web-app-capable" content="yes">\n'
            f'<meta name="mobile-web-app-capable" content="yes">\n'
            f'<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
            f'<meta name="apple-mobile-web-app-title" content="{short}"><!--/app-->\n')
    html = html.replace("</head>", head + "</head>", 1)
    html = html.replace("</body>", '<script src="../../app.js" defer></script>\n</body>', 1)
    page.write_text(html, encoding="utf-8")
    ver = hashlib.md5((html + (ROOT / "app.js").read_text(encoding="utf-8") + (ROOT / "book.js").read_text(encoding="utf-8")).encode()).hexdigest()[:10]
    (d / "sw.js").write_text(SW.replace("__V__", f"{key}-{ver}"), encoding="utf-8")
    print(f"  {key:<30} {name[:24]:<24} знак: {kind}, фон {hexc(pal['dark'])}, золото {hexc(pal['gold'])}")


def main():
    kinds = catalog()
    keys = sys.argv[1:] or sorted(p.name for p in SITES.iterdir() if (p / "index.html").exists())
    for k in keys:
        build(k, kinds)
    print("Готово:", len(keys))


if __name__ == "__main__":
    main()
