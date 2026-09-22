# -*- coding: utf-8 -*-
"""
Сборка демо-сайтов заведений (набор 3).

  python tools/build.py            # собрать все
  python tools/build.py shokunin   # собрать один

Что делает:
  * оптимизирует фото из raw/<key>/ -> sites/<key>/img/*.webp (макс. 1600px, с width/height против CLS);
  * подставляет общий <head> (SEO, Open Graph, favicon, schema.org), базовый CSS (a11y, reduced-motion, мобильное меню)
    и общий JS (меню, форма брони) в шаблоны src/<key>.html;
  * дизайн каждого сайта живёт в своём шаблоне и не зависит от остальных.

Перед выкладкой в бой: замените DOMAIN, уберите DEMO_NOINDEX, положите фото владельца вместо демо-фото.
"""
import html, json, os, re, sys
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = ""            # например "https://example.ru" — тогда появятся canonical и абсолютные og:image
DEMO_NOINDEX = True    # демо-сайты закрыты от индексации

D = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

VENUES = {
    "bebe": dict(
        name="Bébé de la mer", type="Restaurant", cuisine="Морепродукты, рыба",
        desc="Bébé de la mer: рыбный ресторан на Петровке. Устрицы, морепродукты, икра, завтраки до 16:00 и веранда. Бронь столиков.",
        street="ул. Петровка, 30/7", phone="+7 (985) 435-77-77", wa=True, price="₽₽₽₽",
        hours=[(D, "10:00", "23:00")], slug="bebe_de_la_mer/203614270812", color="#f4b400", letter="b", bg="#f4b400", fg="#111",
        fonts="family=Montserrat:wght@400;500;600;800",
        pick=dict(hero=1, logo=2, g=[3, 4, 5, 7, 9, 10, 12], og=1)),
    "shokunin": dict(
        name="Shokunin", type="Restaurant", cuisine="Японская",
        desc="Shokunin: японский ресторан и суши-бар во дворе на Покровском бульваре. Сашими, суши, маки, сакэ и авторские коктейли. Бронь столиков.",
        street="Покровский бул., 8, стр. 2А", phone="+7 (964) 513-51-05", wa=True, price="₽₽₽₽",
        hours=[(D, "14:00", "23:00")], slug="shokunin/6683237127", color="#d0202f", letter="S", bg="#d0202f", fg="#fff",
        fonts="family=Noto+Serif:ital,wght@0,300;0,400;0,600;1,300&family=Noto+Sans:wght@400;500;600",
        pick=dict(hero=7, logo=2, g=[3, 4, 5, 6, 9, 8, 10, 11, 12], og=7)),
    "vova": dict(
        name="Вова'з бар", type="BarOrPub", cuisine="Настойки, коктейли, закуски",
        desc="Вова'з бар на Маросейке: 8 и 16 настоек в сетах, коктейли, крафтовое пиво, диджеи и танцпол. По выходным до 04:00.",
        street="ул. Маросейка, 10/1с1", phone="+7 (916) 390-30-02", wa=True, price="₽₽",
        hours=[(D[:4], "17:00", "00:00"), (["Friday"], "17:00", "04:00"), (["Saturday"], "15:00", "04:00"), (["Sunday"], "15:00", "00:00")],
        slug="vova_z_bar/26289331238", color="#ff7a1a", letter="В", bg="#1a0b2e", fg="#ff7a1a",
        fonts="family=Unbounded:wght@400;600;800&family=Onest:wght@400;500;700",
        pick=dict(hero=4, logo=2, g=[3, 6, 7, 8, 10, 11, 12], og=4)),
    "teburasi": dict(
        name="Тебураси", type="BarOrPub", cuisine="Японская, рамен, гёдза",
        desc="Тебураси: японский бар в переулке у Страстного бульвара. Рамен, гёдза, сэндо, коктейли в банках, фонари и внутренний дворик.",
        street="Страстной бул., 7, стр. 3", phone="+7 (969) 125-40-00", wa=True, price="₽₽",
        hours=[(D[:4], "15:00", "00:00"), (["Friday"], "15:00", "02:00"), (["Saturday"], "14:00", "02:00"), (["Sunday"], "14:00", "00:00")],
        slug="teburasi/80137249291", color="#d8371f", letter="Т", bg="#d8371f", fg="#fff",
        fonts="family=Russo+One&family=Mulish:wght@400;600;800",
        pick=dict(hero=2, g=[1, 3, 5, 6, 7, 8, 9, 10, 11], og=2)),
    "nashe": dict(
        name="Наше Вино", type="BarOrPub", cuisine="Вино, сыры, деликатесы",
        desc="Наше Вино: винотека и бар на Профсоюзной. Отечественные вина бокалами и бутылками, дегустации, сыры и колбасы.",
        street="Профсоюзная ул., 98, корп. 1", phone="+7 (495) 123-47-10", wa=False, price="₽₽",
        hours=[(D, "10:00", "23:00")], slug="nashe_vino/192220045846", color="#6b1830", trim_logo=True, letter="Н", bg="#6b1830", fg="#f7d9e0",
        fonts="family=Prata&family=Commissioner:wght@400;500;700",
        pick=dict(hero=1, logo=2, g=[3, 4, 5, 7, 9, 11, 12], og=1)),
}

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
*{margin:0}
ul,ol{padding:0}
img{max-width:100%;height:auto;display:block}
button,input,select{font:inherit}
html{scroll-behavior:smooth;scroll-padding-top:72px;-webkit-text-size-adjust:100%}
.skip{position:absolute;left:12px;top:-60px;background:#fff;color:#000;padding:10px 16px;z-index:999;border-radius:6px;font:600 14px sans-serif;text-decoration:none}
.skip:focus{top:12px}
.vh{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
:focus-visible{outline:3px solid var(--focus,#f4b400);outline-offset:3px}
.burger{display:none;align-items:center;justify-content:center;width:44px;height:44px;background:none;border:0;color:inherit;cursor:pointer}
.burger span,.burger span::before,.burger span::after{display:block;width:24px;height:2px;background:currentColor;position:relative;transition:.2s}
.burger span::before,.burger span::after{content:"";position:absolute;left:0}
.burger span::before{top:-7px}.burger span::after{top:7px}
.burger[aria-expanded=true] span{background:transparent}
.burger[aria-expanded=true] span::before{top:0;transform:rotate(45deg)}
.burger[aria-expanded=true] span::after{top:0;transform:rotate(-45deg)}
@media(max-width:860px){
 .burger{display:inline-flex}
 .js-nav{display:none!important;position:fixed;left:0;right:0;top:var(--hh,60px);flex-direction:column;gap:0!important;padding:8px 20px 20px;background:var(--nav-bg,#111);color:var(--nav-fg,#fff);z-index:60;box-shadow:0 20px 40px #0008}
 .js-nav.open{display:flex!important}
 .js-nav a{padding:14px 0;border-bottom:1px solid #ffffff22;font-size:18px!important;text-align:left}
 header .wrap>.btn{display:none}
}
.form-msg{grid-column:1/-1;min-height:1.4em;font-size:14px}
@media(prefers-reduced-motion:reduce){
 html{scroll-behavior:auto}
 *,*::before,*::after{animation:none!important;transition:none!important}
}
"""

JS = r"""
(function(){
 var b=document.querySelector('.burger'),n=document.getElementById('nav');
 if(b&&n){
  b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)});
  n.addEventListener('click',function(e){if(e.target.tagName==='A'){n.classList.remove('open');b.setAttribute('aria-expanded','false')}});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){n.classList.remove('open');b.setAttribute('aria-expanded','false')}});
 }
 var f=document.getElementById('bf');
 if(!f)return;
 var d=f.querySelector('input[type=date]');
 if(d){var t=new Date();t.setMinutes(t.getMinutes()-t.getTimezoneOffset());d.min=t.toISOString().slice(0,10)}
 f.addEventListener('submit',function(e){
  e.preventDefault();
  var m=f.querySelector('.form-msg'),v=new FormData(f);
  var name=f.dataset.name,wa=f.dataset.wa,tel=f.dataset.tel;
  var txt='Здравствуйте! Хочу забронировать стол в «'+name+'»: '+v.get('d')+' в '+v.get('t')+', гостей: '+v.get('g')+'. Имя: '+v.get('n')+'.';
  if(wa){window.open('https://wa.me/'+wa+'?text='+encodeURIComponent(txt),'_blank','noopener');if(m)m.textContent='Открываем WhatsApp с готовым сообщением. Если не открылось, позвоните нам.'}
  else{if(m)m.textContent='Для брони позвоните: '+tel;location.href='tel:'+tel}
 });
})();
"""


def digits(s):
    return re.sub(r"\D", "", s)


def process_images(key, v):
    """Оптимизирует фото, возвращает {имя: (w, h)}."""
    src = os.path.join(ROOT, "raw", key)
    out = os.path.join(ROOT, "sites", key, "img")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    pick, dims = v["pick"], {}
    jobs = {"hero": pick["hero"], "og": pick.get("og", pick["hero"])}
    if "logo" in pick:
        jobs["logo"] = pick["logo"]
    for i, idx in enumerate(pick["g"], 1):
        jobs[f"g{i}"] = idx
    for name, idx in jobs.items():
        im = Image.open(os.path.join(src, f"{idx}.jpg")).convert("RGB")
        if name == "logo" and v.get("trim_logo"):
            diff = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255)))
            box = diff.point(lambda p: 255 if p > 18 else 0).getbbox()
            if box:
                pad = 14
                box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad))
                im = im.crop(box)
        limit = 1200 if name == "og" else 1600
        im.thumbnail((limit, limit), Image.LANCZOS)
        if name == "og":
            w, h = im.size
            tw, th = 1200, 630
            r = max(tw / w, th / h)
            im = im.resize((int(w * r), int(h * r)), Image.LANCZOS)
            l, t = (im.width - tw) // 2, (im.height - th) // 2
            im = im.crop((l, t, l + tw, t + th))
            im.save(os.path.join(out, "og.jpg"), quality=80, optimize=True, progressive=True)
            continue
        im.save(os.path.join(out, f"{name}.webp"), quality=78, method=6)
        dims[name] = im.size
    return dims


def head(key, v, title):
    esc = html.escape
    url = (DOMAIN + "/") if DOMAIN else ""
    og_img = (DOMAIN + "/img/og.jpg") if DOMAIN else "img/og.jpg"
    fav = ("data:image/svg+xml," + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='{bg}'/%3E%3Ctext x='32' y='45' font-size='38' font-family='Georgia,serif' font-weight='700' text-anchor='middle' fill='{fg}'%3E{l}%3C/text%3E%3C/svg%3E"
           .format(bg=v["bg"].replace("#", "%23"), fg=v["fg"].replace("#", "%23"), l=html.escape(v["letter"])))
    parts = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(v["desc"])}">',
        f'<meta name="theme-color" content="{v["color"]}">',
        f'<link rel="icon" href="{fav}">',
        '<meta property="og:type" content="restaurant.restaurant">',
        '<meta property="og:locale" content="ru_RU">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(v["desc"])}">',
        f'<meta property="og:image" content="{og_img}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if DOMAIN:
        parts.append(f'<link rel="canonical" href="{url}">')
        parts.append(f'<meta property="og:url" content="{url}">')
    if DEMO_NOINDEX:
        parts.append('<meta name="robots" content="noindex, nofollow">')
    parts += [
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link href="https://fonts.googleapis.com/css2?{v["fonts"]}&display=swap" rel="stylesheet">',
    ]
    # schema.org
    spec = [{"@type": "OpeningHoursSpecification", "dayOfWeek": days, "opens": o, "closes": c} for days, o, c in v["hours"]]
    ld = {
        "@context": "https://schema.org", "@type": v["type"], "name": v["name"],
        "description": v["desc"], "image": og_img, "telephone": "+" + digits(v["phone"]),
        "priceRange": v["price"], "servesCuisine": v["cuisine"],
        "address": {"@type": "PostalAddress", "streetAddress": v["street"], "addressLocality": "Москва", "addressCountry": "RU"},
        "openingHoursSpecification": spec,
        "acceptsReservations": True,
        "sameAs": ["https://yandex.ru/maps/org/" + v["slug"] + "/"],
    }
    parts.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>")
    return "\n".join(parts)


def render(key, v, tpl, dims):
    def img(m):
        eager, name = m.group(1) == "E", m.group(2)
        w, h = dims[name]
        extra = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
        return f'src="img/{name}.webp" width="{w}" height="{h}" {extra}'

    title = re.search(r"<!--TITLE:(.*?)-->", tpl).group(1).strip()
    tpl = re.sub(r"<!--TITLE:.*?-->\n?", "", tpl)
    out = tpl.replace("{{HEAD}}", head(key, v, title)).replace("{{BASECSS}}", BASE_CSS).replace("{{JS}}", JS)
    out = re.sub(r"\{\{IMG(E?):(\w+)\}\}", img, out)
    tel = "+" + digits(v["phone"])
    repl = {
        "{{NAME}}": html.escape(v["name"]), "{{PHONE}}": v["phone"], "{{TEL}}": tel,
        "{{MAP}}": "https://yandex.ru/maps/org/" + v["slug"] + "/", "{{ADDR}}": html.escape(v["street"]),
        "{{FORMATTR}}": f'id="bf" data-name="{html.escape(v["name"])}" data-wa="{digits(v["phone"]) if v["wa"] else ""}" data-tel="{tel}" novalidate',
    }
    for k, val in repl.items():
        out = out.replace(k, val)
    left = re.findall(r"\{\{[^}]+\}\}", out)
    if left:
        raise SystemExit(f"[{key}] неразрешённые плейсхолдеры: {left}")
    return out


def main():
    keys = sys.argv[1:] or list(VENUES)
    for key in keys:
        v = VENUES[key]
        dims = process_images(key, v)
        tpl = open(os.path.join(ROOT, "tools", "src", f"{key}.html"), encoding="utf-8").read()
        out = render(key, v, tpl, dims)
        with open(os.path.join(ROOT, "sites", key, "index.html"), "w", encoding="utf-8") as f:
            f.write(out)
        size = sum(os.path.getsize(os.path.join(ROOT, "sites", key, "img", x)) for x in os.listdir(os.path.join(ROOT, "sites", key, "img")))
        print(f"{key}: ok, картинки {size // 1024} КБ, html {len(out) // 1024} КБ")


if __name__ == "__main__":
    main()
