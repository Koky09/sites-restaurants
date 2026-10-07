"""Превращает готовый сайт sites/<key>/ в сайт-приложение (PWA), как у автомоек в tver-demo.

    python tools/make_app.py lado          # один сайт
    python tools/make_app.py               # все сайты

Что делает для каждого сайта:
- иконки рисует tools/icons.py: у каждого заведения свой рисунок, шрифт и цвета (дизайн — в icons.DESIGN)
  -> icon-192.png, icon-512.png, icon-maskable-512.png, apple-touch-icon.png, favicon.png;
- manifest.webmanifest (имя, цвета, иконки, start_url) и sw.js (работа без сети);
- в <head> — manifest, apple-touch-icon, иконку вкладки, мета для iPhone; перед </body> — ../../app.js
  (кнопка «Установить», кабинет владельца #admin). Нужен уже подключённый book.js (tools/add_booking.py).
Повторный запуск обновляет всё, не дублируя."""
import hashlib
import json
import re
import sys
from pathlib import Path

import icons

ROOT = Path(__file__).resolve().parent.parent
SITES = ROOT / "sites"
HEAD_MARK = re.compile(r"<!--app-->.*?<!--/app-->\n?", re.S)
BODY_MARK = re.compile(r'<script src="\.\./\.\./app\.js" defer></script>\n?')


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


def build(key):
    d = SITES / key
    page = d / "index.html"
    html = page.read_text(encoding="utf-8")
    m = re.search(r"window\.RBOOK=(\{.*?\});</script>", html)
    if not m:
        sys.exit(f"{key}: нет window.RBOOK — сначала python tools/add_booking.py {key}")
    rb = json.loads(m.group(1))
    name = rb["name"]
    if key not in icons.DESIGN:
        sys.exit(f"{key}: нет дизайна иконки — добавьте его в tools/icons.py (DESIGN)")
    bg = icons.DESIGN[key]["bg"]
    short = name if len(name) <= 12 else name.split()[0][:12]
    manifest = {"name": name, "short_name": short, "lang": "ru", "start_url": "./", "scope": "./", "display": "standalone",
                "background_color": bg, "theme_color": bg,
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
            f'<meta name="theme-color" content="{bg}">\n'
            f'<link rel="icon" type="image/png" href="favicon.png">\n'
            f'<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
            f'<meta name="apple-mobile-web-app-capable" content="yes">\n'
            f'<meta name="mobile-web-app-capable" content="yes">\n'
            f'<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
            f'<meta name="apple-mobile-web-app-title" content="{short}"><!--/app-->\n')
    html = html.replace("</head>", head + "</head>", 1)
    html = html.replace("</body>", '<script src="../../app.js" defer></script>\n</body>', 1)
    page.write_text(html, encoding="utf-8")
    art = json.dumps(icons.DESIGN[key], sort_keys=True) + icons.MOTIFS.get(icons.DESIGN[key]["motif"], "")  # новая иконка -> новый кэш
    ver = hashlib.md5((html + art + (ROOT / "app.js").read_text(encoding="utf-8") + (ROOT / "book.js").read_text(encoding="utf-8")).encode()).hexdigest()[:10]
    (d / "sw.js").write_text(SW.replace("__V__", f"{key}-{ver}"), encoding="utf-8")
    print(f"  {key:<30} {name[:24]:<24} {icons.DESIGN[key]['layout']}/{icons.DESIGN[key]['motif']}")


def main():
    keys = sys.argv[1:] or sorted(p.name for p in SITES.iterdir() if (p / "index.html").exists())
    for k in keys:
        build(k)
    icons.render(keys, lambda k: SITES / k)
    print("Готово:", len(keys))


if __name__ == "__main__":
    main()
