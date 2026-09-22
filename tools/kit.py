# -*- coding: utf-8 -*-
"""
Конструктор сайтов заведений: варианты блоков + палитры + шрифты (все шрифты с кириллицей).
Каждый сайт = spec (tools/specs.py) + данные карточки (data/<slug>.json) -> sites/<key>/index.html
"""
import html as H, re
from build import BASE_CSS, JS, head as build_head, digits

E = H.escape

FONTS = {  # ключ: (заголовки, текст, google-запрос, transform, weight, letter-spacing, style)
    "playfair": ("'Playfair Display',serif", "Onest,sans-serif", "family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Onest:wght@400;500;700", "none", 700, "-.01em", "normal"),
    "lora": ("Lora,serif", "Nunito,sans-serif", "family=Lora:ital,wght@0,500;0,700;1,500&family=Nunito:wght@400;600;800", "none", 700, "0", "normal"),
    "montserrat": ("Montserrat,sans-serif", "Montserrat,sans-serif", "family=Montserrat:wght@400;500;600;800", "lowercase", 800, "-.03em", "normal"),
    "unbounded": ("Unbounded,sans-serif", "Onest,sans-serif", "family=Unbounded:wght@500;800&family=Onest:wght@400;500;700", "uppercase", 800, "-.01em", "normal"),
    "russo": ("'Russo One',sans-serif", "Mulish,sans-serif", "family=Russo+One&family=Mulish:wght@400;600;800", "uppercase", 400, "0", "normal"),
    "prata": ("Prata,serif", "Commissioner,sans-serif", "family=Prata&family=Commissioner:wght@400;500;700", "none", 400, "0", "normal"),
    "oldstd": ("'Old Standard TT',serif", "'Golos Text',sans-serif", "family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&family=Golos+Text:wght@400;500;600", "none", 700, "0", "normal"),
    "yeseva": ("'Yeseva One',serif", "'Source Sans 3',sans-serif", "family=Yeseva+One&family=Source+Sans+3:wght@400;500;600;700", "none", 400, "0", "normal"),
    "bitter": ("Bitter,serif", "'PT Sans',sans-serif", "family=Bitter:ital,wght@0,600;0,800;1,400&family=PT+Sans:wght@400;700", "none", 800, "0", "normal"),
    "rubik": ("'Rubik Mono One',sans-serif", "Rubik,sans-serif", "family=Rubik:wght@400;500;700&family=Rubik+Mono+One", "uppercase", 400, "0", "normal"),
    "amatic": ("'Amatic SC',cursive", "Raleway,sans-serif", "family=Amatic+SC:wght@400;700&family=Raleway:wght@400;500;700", "uppercase", 700, ".03em", "normal"),
    "cormorant": ("Cormorant,serif", "Jost,sans-serif", "family=Cormorant:ital,wght@0,400;0,600;1,400&family=Jost:wght@300;400;600", "none", 600, "0", "normal"),
    "notoserif": ("'Noto Serif',serif", "'Noto Sans',sans-serif", "family=Noto+Serif:ital,wght@0,300;0,400;0,600;1,300&family=Noto+Sans:wght@400;500;600", "none", 300, "0", "normal"),
    "ruslan": ("'Ruslan Display',serif", "'Roboto Condensed',sans-serif", "family=Ruslan+Display&family=Roboto+Condensed:wght@400;700", "uppercase", 400, ".02em", "normal"),
    "oswald": ("Oswald,sans-serif", "Manrope,sans-serif", "family=Oswald:wght@400;500;700&family=Manrope:wght@400;600;800", "uppercase", 700, ".02em", "normal"),
    "ptserif": ("'PT Serif',serif", "'PT Sans',sans-serif", "family=PT+Serif:ital,wght@0,400;0,700;1,400&family=PT+Sans:wght@400;700", "none", 700, "0", "normal"),
    "comfortaa": ("Comfortaa,sans-serif", "Nunito,sans-serif", "family=Comfortaa:wght@500;700&family=Nunito:wght@400;600;800", "none", 700, "0", "normal"),
    "philosopher": ("Philosopher,serif", "Ubuntu,sans-serif", "family=Philosopher:ital,wght@0,400;0,700;1,400&family=Ubuntu:wght@400;500;700", "none", 700, "0", "normal"),
    "tenor": ("'Tenor Sans',sans-serif", "Raleway,sans-serif", "family=Tenor+Sans&family=Raleway:wght@400;500;700", "uppercase", 400, ".08em", "normal"),
    "merri": ("Merriweather,serif", "'Merriweather Sans',sans-serif", "family=Merriweather:ital,wght@0,400;0,700;1,400&family=Merriweather+Sans:wght@400;600;700", "none", 700, "0", "normal"),
    "exo": ("'Exo 2',sans-serif", "'Exo 2',sans-serif", "family=Exo+2:wght@400;600;800", "uppercase", 800, ".02em", "normal"),
    "alegreya": ("Alegreya,serif", "'Alegreya Sans',sans-serif", "family=Alegreya:ital,wght@0,500;0,800;1,500&family=Alegreya+Sans:wght@400;500;700", "none", 800, "0", "normal"),
    "caveat": ("Caveat,cursive", "Nunito,sans-serif", "family=Caveat:wght@500;700&family=Nunito:wght@400;600;800", "none", 700, "0", "normal"),
    "marck": ("'Marck Script',cursive", "Ubuntu,sans-serif", "family=Marck+Script&family=Ubuntu:wght@400;500;700", "none", 400, "0", "normal"),
    "spectral": ("Spectral,serif", "Inter,sans-serif", "family=Spectral:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600", "none", 700, "-.01em", "normal"),
    "manrope": ("Manrope,sans-serif", "Manrope,sans-serif", "family=Manrope:wght@400;500;700;800", "none", 800, "-.03em", "normal"),
}

# ключи палитры: bg surf ink dim acc acc_ink acc2 dark dark_ink line
PAL = {
    "cream_tomato": dict(bg="#f7f1e5", surf="#fffaf0", ink="#231a14", dim="#6d6156", acc="#c8321f", acc_ink="#ffffff", acc2="#e9a93a", dark="#26170f", dark_ink="#f7f1e5", line="#23191426"),
    "ink_gold": dict(bg="#0f0e0d", surf="#1a1816", ink="#f1e8d6", dim="#b0a58f", acc="#c9a253", acc_ink="#1a1408", acc2="#8a2b2b", dark="#080706", dark_ink="#f1e8d6", line="#f1e8d62b"),
    "forest_brass": dict(bg="#f4efe3", surf="#fbf7ec", ink="#14261c", dim="#57645b", acc="#1f4a35", acc_ink="#f4efe3", acc2="#b88a3b", dark="#10231a", dark_ink="#f4efe3", line="#14261c26"),
    "wine_blush": dict(bg="#fbeaee", surf="#fff5f7", ink="#2b0f18", dim="#6f4a55", acc="#7b1e3a", acc_ink="#fdeef2", acc2="#c9956a", dark="#4a0f22", dark_ink="#fdeef2", line="#2b0f1826"),
    "navy_coral": dict(bg="#f3f5fa", surf="#ffffff", ink="#12203b", dim="#54607a", acc="#d4402f", acc_ink="#ffffff", acc2="#f4b942", dark="#0e1a33", dark_ink="#eef2fb", line="#12203b26"),
    "night_neon": dict(bg="#120a22", surf="#1c1032", ink="#f2ecff", dim="#aa9bcb", acc="#ff4fa3", acc_ink="#1a0b2e", acc2="#38e0ff", dark="#0a0515", dark_ink="#f2ecff", line="#f2ecff26"),
    "sand_olive": dict(bg="#f2ecdc", surf="#faf6ea", ink="#2a2a1a", dim="#66664f", acc="#5d6b2f", acc_ink="#ffffff", acc2="#c98a2b", dark="#232a14", dark_ink="#f2ecdc", line="#2a2a1a26"),
    "charcoal_orange": dict(bg="#161514", surf="#22201e", ink="#f4efe8", dim="#b7aea3", acc="#ff7a1a", acc_ink="#1a0f05", acc2="#ffc247", dark="#0d0c0b", dark_ink="#f4efe8", line="#f4efe829"),
    "white_black": dict(bg="#ffffff", surf="#f5f5f2", ink="#111111", dim="#5e5e5a", acc="#111111", acc_ink="#ffffff", acc2="#e6c229", dark="#111111", dark_ink="#ffffff", line="#11111126"),
    "teal_peach": dict(bg="#eef7f5", surf="#ffffff", ink="#0f2f2c", dim="#4f6e69", acc="#0f7b70", acc_ink="#ffffff", acc2="#ff9f7a", dark="#0b3a36", dark_ink="#eef7f5", line="#0f2f2c26"),
    "burgundy_cream": dict(bg="#f6ede0", surf="#fdf8ef", ink="#2a1512", dim="#6f544d", acc="#8c1c2b", acc_ink="#fff6ee", acc2="#d0a24a", dark="#3d0f18", dark_ink="#f6ede0", line="#2a151226"),
    "mustard_blue": dict(bg="#fff8e1", surf="#ffffff", ink="#1b2a4a", dim="#56607a", acc="#2e5aac", acc_ink="#ffffff", acc2="#f2b01e", dark="#1b2a4a", dark_ink="#fff8e1", line="#1b2a4a26"),
    "slate_mint": dict(bg="#eef1f1", surf="#ffffff", ink="#1d2a2c", dim="#55666a", acc="#227a68", acc_ink="#ffffff", acc2="#e8b34a", dark="#17282b", dark_ink="#eef1f1", line="#1d2a2c26"),
    "terracotta_sage": dict(bg="#f6ece2", surf="#fcf5ec", ink="#3a231a", dim="#7a5a4c", acc="#b4532a", acc_ink="#ffffff", acc2="#7d8f69", dark="#3a231a", dark_ink="#f6ece2", line="#3a231a26"),
    "rose_gold": dict(bg="#fdf1ee", surf="#fff8f6", ink="#3a2320", dim="#8a625c", acc="#b0574b", acc_ink="#ffffff", acc2="#b08d57", dark="#4b2b28", dark_ink="#fdf1ee", line="#3a232026"),
    "steel_red": dict(bg="#eceef1", surf="#ffffff", ink="#161a22", dim="#565d6b", acc="#d02c2c", acc_ink="#ffffff", acc2="#2f3a4f", dark="#161a22", dark_ink="#eceef1", line="#161a2226"),
    "purple_lime": dict(bg="#f4f0fb", surf="#ffffff", ink="#1f1240", dim="#5f5580", acc="#5b2fd0", acc_ink="#ffffff", acc2="#c6f432", dark="#1f1240", dark_ink="#f4f0fb", line="#1f124026"),
    "brown_cream": dict(bg="#f3e9dc", surf="#faf3e8", ink="#33210f", dim="#78614a", acc="#7a4a1e", acc_ink="#fff7ea", acc2="#d9a441", dark="#2a1a0c", dark_ink="#f3e9dc", line="#33210f26"),
    "ocean": dict(bg="#e9f4f8", surf="#ffffff", ink="#0b2c3d", dim="#4b6a78", acc="#0d6e8f", acc_ink="#ffffff", acc2="#f2a541", dark="#0b2c3d", dark_ink="#e9f4f8", line="#0b2c3d26"),
    "black_red": dict(bg="#0c0c0c", surf="#181818", ink="#f5f0ea", dim="#b3aca4", acc="#d8232a", acc_ink="#ffffff", acc2="#f0c14b", dark="#050505", dark_ink="#f5f0ea", line="#f5f0ea29"),
    "green_pop": dict(bg="#f6fbe9", surf="#ffffff", ink="#132314", dim="#4c5f4d", acc="#2f7f27", acc_ink="#ffffff", acc2="#ff7a59", dark="#132314", dark_ink="#f6fbe9", line="#13231426"),
    "lavender": dict(bg="#f3eefa", surf="#fbf8ff", ink="#2a2140", dim="#6b6088", acc="#7b56c8", acc_ink="#ffffff", acc2="#f0a6c0", dark="#2a2140", dark_ink="#f3eefa", line="#2a214026"),
    "denim": dict(bg="#eef2f7", surf="#ffffff", ink="#172236", dim="#566277", acc="#2b5fa8", acc_ink="#ffffff", acc2="#f0b429", dark="#172236", dark_ink="#eef2f7", line="#17223626"),
    "emerald_gold": dict(bg="#0e1f1a", surf="#15302a", ink="#eee6cf", dim="#a9b8a9", acc="#d4af5a", acc_ink="#10231d", acc2="#3fb58c", dark="#08140f", dark_ink="#eee6cf", line="#eee6cf29"),
}


def lum(h):
    h = h.lstrip("#")[:6]
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def check_palette(name, p):
    w = []
    for a, b, lim in (("ink", "bg", 7), ("ink", "surf", 7), ("dim", "bg", 4.5), ("acc_ink", "acc", 4.5), ("dark_ink", "dark", 7), ("acc", "bg", 3.2), ("acc", "surf", 3.2)):
        c = contrast(p[a], p[b])
        if c < lim:
            w.append(f"{name}: {a}/{b} {c:.1f}<{lim}")
    return w


# ---------------------------------------------------------------- CSS
def css_root(p, f, ui):
    hf, bf, _, t, w, ls, st = FONTS[f]
    acc_d = max((p["acc"], p["acc2"], p["dark_ink"]), key=lambda c: contrast(c, p["dark"]) if contrast(c, p["dark"]) >= 4.5 or c == p["dark_ink"] else 0)
    qf = "var(--bf)" if f in ("rubik", "russo", "ruslan", "amatic", "oswald", "exo", "tenor", "unbounded", "caveat", "marck") else "var(--hf)"
    br = {"pill": "999px", "sq": "0", "soft": "10px", "hard": "6px"}[ui["btn"]]
    bs = {"pill": "none", "sq": "none", "soft": "none", "hard": f"4px 4px 0 var(--ink)"}[ui["btn"]]
    sh = {"none": "none", "soft": "0 14px 36px #0000001f", "hard": "6px 6px 0 var(--ink)"}[ui["sh"]]
    return (f":root{{--bg:{p['bg']};--surf:{p['surf']};--ink:{p['ink']};--dim:{p['dim']};--acc:{p['acc']};--acc-ink:{p['acc_ink']};"
            f"--acc2:{p['acc2']};--dark:{p['dark']};--dark-ink:{p['dark_ink']};--line:{p['line']};--r:{ui['r']}px;--bw:{ui['bw']}px;"
            f"--sh:{sh};--br:{br};--bsh:{bs};--hf:{hf};--bf:{bf};--hw:{w};--ht:{t};--hls:{ls};--focus:{p['acc']};--nav-bg:{p['dark']};"
            f"--nav-fg:{p['dark_ink']};--acc-d:{acc_d};--qf:{qf};--hh:68px}}")


CORE = """
body{font:400 17px/1.65 var(--bf);background:var(--bg);color:var(--ink)}
h1,h2,h3{font-family:var(--hf);font-weight:var(--hw);text-transform:var(--ht);letter-spacing:var(--hls);line-height:1.08}
a{color:inherit}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
section{padding:92px 0}
h2{font-size:clamp(30px,4.8vw,58px);margin-bottom:14px}
.lead{max-width:620px;color:var(--dim);margin-bottom:38px;font-size:18px}
.eyebrow{font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:var(--acc);font-weight:700;margin-bottom:12px}
.btn{display:inline-block;background:var(--acc);color:var(--acc-ink);font:700 15px var(--bf);letter-spacing:.02em;padding:15px 30px;border:var(--bw) solid var(--acc);border-radius:var(--br);box-shadow:var(--bsh);text-decoration:none;cursor:pointer;transition:transform .15s,background .15s,color .15s}
.btn:hover{transform:translateY(-2px)}
.btn.o{background:transparent;color:inherit;border-color:currentColor}
.btn.d{background:var(--ink);border-color:var(--ink);color:var(--bg)}
address{font-style:normal}
dl{display:grid;grid-template-columns:104px 1fr;gap:12px 14px;margin:22px 0 26px}
dt{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--acc);font-weight:700;padding-top:4px}
.chips{display:flex;flex-wrap:wrap;gap:8px;list-style:none}
.chips li{border:1.5px solid var(--line);background:var(--surf);border-radius:999px;padding:5px 14px;font-size:14px;font-weight:600}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;list-style:none}
.stats li{background:var(--surf);border:var(--bw) solid var(--line);border-radius:var(--r);padding:22px;box-shadow:var(--sh)}
.stats b{display:block;font:var(--hw) clamp(22px,2.6vw,34px)/1.1 var(--hf);text-transform:none;color:var(--acc);white-space:nowrap}
.stats span{font-size:14px;color:var(--dim)}
footer.end{background:var(--dark);color:var(--dark-ink);opacity:.9;padding:26px 0;font-size:14px}
footer.end .wrap{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.fab{display:none}
.bf{display:grid;grid-template-columns:1fr 1fr;gap:14px;background:var(--surf);color:var(--ink);border:var(--bw) solid var(--ink);border-radius:var(--r);padding:28px;box-shadow:var(--sh)}
.bf label{display:grid;gap:6px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--dim)}
.bf input,.bf select{padding:12px 14px;border:1.5px solid var(--ink);border-radius:calc(var(--r)/2);background:#fff;color:#111;min-height:48px;font-weight:500}
.bf .full{grid-column:1/-1}
.bf .btn{background:var(--acc);border-color:var(--acc)}
.callcard{background:var(--surf);border:var(--bw) solid var(--ink);border-radius:var(--r);padding:32px;box-shadow:var(--sh);display:grid;gap:14px;align-content:center}
.callcard .tel{font:var(--hw) clamp(26px,3.6vw,42px)/1.1 var(--hf);text-transform:none;text-decoration:none;color:var(--acc)}
.mnone{border:var(--bw) solid currentColor;border-radius:var(--r);padding:34px;max-width:720px}
.dark{background:var(--dark);color:var(--dark-ink)}
.dark .lead{color:var(--dark-ink);opacity:.75}
.dark .eyebrow{color:var(--acc-d)}
"""

V = {}  # CSS вариантов

V["h_bar"] = """
header{position:sticky;top:0;z-index:50;background:var(--surf);border-bottom:var(--bw) solid var(--ink)}
header .wrap{display:flex;align-items:center;justify-content:space-between;height:var(--hh);gap:16px}
.brand{font:var(--hw) 22px var(--hf);text-transform:var(--ht);letter-spacing:var(--hls);text-decoration:none}
.brand img{height:42px;width:auto;mix-blend-mode:multiply}
.js-nav{display:flex;gap:26px;font-size:14px;font-weight:600}
.js-nav a{text-decoration:none;opacity:.85}.js-nav a:hover{opacity:1;color:var(--acc)}
"""
V["h_center"] = """
header{position:sticky;top:0;z-index:50;background:var(--surf);border-bottom:var(--bw) solid var(--ink)}
header .wrap{display:flex;flex-direction:column;align-items:center;gap:4px;padding-top:10px;padding-bottom:10px;position:relative}
.brand{font:var(--hw) 28px var(--hf);text-transform:var(--ht);letter-spacing:var(--hls);text-decoration:none;text-align:center}
.js-nav{display:flex;gap:30px;font-size:12px;font-weight:700;letter-spacing:.2em;text-transform:uppercase}
.js-nav a{text-decoration:none}.js-nav a:hover{color:var(--acc)}
.burger{position:absolute;right:14px;top:10px}
header .btn{display:none}
:root{--hh:96px}
@media(max-width:860px){:root{--hh:64px}header .wrap{flex-direction:row;justify-content:space-between}.brand{font-size:22px}.burger{position:static}}
"""
V["h_overlay"] = """
header{position:absolute;top:0;left:0;right:0;z-index:50;color:#fff}
header .wrap{display:flex;align-items:center;justify-content:space-between;height:var(--hh);gap:16px}
.brand{font:var(--hw) 22px var(--hf);text-transform:var(--ht);letter-spacing:var(--hls);text-decoration:none;text-shadow:0 1px 12px #0008}
.js-nav{display:flex;gap:26px;font-size:14px;font-weight:600;text-shadow:0 1px 10px #0008}
.js-nav a{text-decoration:none}.js-nav a:hover{text-decoration:underline;text-underline-offset:6px}
header .btn{padding:11px 22px}
@media(max-width:860px){header{background:var(--dark)}}
"""

V["hero_full"] = """
.hero{position:relative;min-height:calc(100svh - 0px);display:flex;align-items:flex-end;color:#fff;background:linear-gradient(0deg,#000000d9 8%,#0000004d 55%,#00000066 100%),url(img/hero.webp) center/cover}
.hero .wrap{padding-top:130px;padding-bottom:72px;width:100%}
.hero h1{font-size:clamp(36px,6.6vw,96px);max-width:900px;margin:10px 0 16px;overflow-wrap:break-word}
.hero p{font-size:20px;max-width:560px;opacity:.95}
.hero .k{font-size:13px;letter-spacing:.3em;text-transform:uppercase;color:#ffffffd6;font-weight:700}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
.hero .btn.o{color:#fff}
.badge{display:inline-block;margin-top:22px;border:1.5px solid #ffffff88;border-radius:999px;padding:6px 16px;font-size:14px;font-weight:600}
"""
V["hero_split"] = """
.hero{padding:46px 0 64px}
.hero .wrap{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:center}
.hero h1{font-size:clamp(40px,6.4vw,88px);margin:12px 0 18px}
.hero p{font-size:19px;max-width:480px;color:var(--dim)}
.hero .k{font-size:12px;letter-spacing:.3em;text-transform:uppercase;color:var(--acc);font-weight:700}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
.hero .ph{position:relative}
.hero .ph img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--r);border:var(--bw) solid var(--ink);box-shadow:var(--sh)}
.badge{position:absolute;left:14px;bottom:14px;background:var(--surf);color:var(--ink);border:var(--bw) solid var(--ink);border-radius:999px;padding:7px 16px;font-size:14px;font-weight:700}
@media(max-width:860px){.hero .wrap{grid-template-columns:1fr}.hero .ph img{aspect-ratio:4/3}}
"""
V["hero_arch"] = """
.hero{background:var(--dark);color:var(--dark-ink);padding:96px 0 80px;position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;right:-140px;top:-140px;width:460px;height:460px;border-radius:50%;background:var(--acc);opacity:.18}
.hero .wrap{display:grid;grid-template-columns:1.1fr .9fr;gap:44px;align-items:center;position:relative;z-index:1}
.hero h1{font-size:clamp(40px,6.6vw,92px);margin:12px 0 18px}
.hero p{font-size:19px;max-width:480px;opacity:.9}
.hero .k{font-size:12px;letter-spacing:.3em;text-transform:uppercase;color:var(--acc-d);font-weight:700}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
.arch{aspect-ratio:3/4;border-radius:999px 999px calc(var(--r) + 10px) calc(var(--r) + 10px);object-fit:cover;width:100%;border:8px solid var(--bg);box-shadow:0 24px 60px #0007}
.badge{display:inline-block;margin-top:22px;border:1.5px solid currentColor;border-radius:999px;padding:6px 16px;font-size:14px;font-weight:600;opacity:.9}
@media(max-width:860px){.hero .wrap{grid-template-columns:1fr}.arch{max-width:340px;margin:0 auto}}
"""
V["hero_center"] = """
.hero{position:relative;min-height:calc(100svh);display:grid;place-items:center;text-align:center;color:#fff;background:linear-gradient(#000000a6,#000000cc),url(img/hero.webp) center/cover}
.hero::before{content:"";position:absolute;inset:26px;border:1.5px solid #ffffff66;pointer-events:none}
.hero .wrap{padding-top:120px;padding-bottom:90px}
.hero h1{font-size:clamp(34px,6.2vw,92px);margin:14px auto 18px;max-width:1000px;overflow-wrap:break-word}
.hero p{font-size:20px;max-width:560px;margin:0 auto;opacity:.95}
.hero .k{font-size:13px;letter-spacing:.34em;text-transform:uppercase;color:#ffffffd6;font-weight:700}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px;justify-content:center}
.hero .btn.o{color:#fff}
.badge{display:inline-block;margin-top:24px;font-size:14px;letter-spacing:.14em;text-transform:uppercase;opacity:.85}
"""
V["hero_poster"] = """
.hero{display:grid;grid-template-columns:1.1fr .9fr;min-height:calc(100svh - var(--hh));max-height:900px;overflow:hidden}
.hero .txt{background:var(--acc);color:var(--acc-ink);padding:8vh 6vw;display:flex;flex-direction:column;justify-content:center;gap:22px}
.hero h1{font-size:clamp(42px,7.4vw,104px)}
.hero p{font-size:19px;max-width:460px;opacity:.92}
.hero .k{font-size:12px;letter-spacing:.3em;text-transform:uppercase;font-weight:700;opacity:.85}
.cta{display:flex;flex-wrap:wrap;gap:12px}
.hero .btn{background:var(--acc-ink);color:var(--acc);border-color:var(--acc-ink)}
.hero .btn.o{background:transparent;color:var(--acc-ink)}
.hero .ph{display:grid;grid-template-rows:minmax(0,1.4fr) minmax(0,1fr);overflow:hidden;min-height:0}
.hero .ph img{width:100%;height:100%;object-fit:cover;min-height:0}
.badge{display:inline-block;border:1.5px solid currentColor;border-radius:999px;padding:6px 16px;font-size:14px;font-weight:700;align-self:flex-start}
@media(max-width:860px){.hero{grid-template-columns:1fr;min-height:0;max-height:none}.hero .ph{grid-template-rows:none;grid-template-columns:1fr 1fr;height:220px;order:-1}}
"""
V["hero_collage"] = """
.hero{padding:56px 0 84px;overflow:hidden}
.hero .wrap{display:grid;grid-template-columns:1fr 1.1fr;gap:40px;align-items:center}
.hero h1{font-size:clamp(42px,7vw,96px);margin:12px 0 18px}
.hero p{font-size:19px;max-width:460px;color:var(--dim)}
.hero .k{font-size:12px;letter-spacing:.3em;text-transform:uppercase;color:var(--acc);font-weight:700}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
.collage{position:relative;height:520px}
.collage img{position:absolute;object-fit:cover;background:#fff;padding:9px 9px 30px;box-shadow:0 14px 34px #0004;border-radius:2px}
.collage img:nth-child(1){width:52%;height:66%;left:0;top:6%;transform:rotate(-5deg)}
.collage img:nth-child(2){width:48%;height:58%;right:0;top:0;transform:rotate(4deg)}
.collage img:nth-child(3){width:46%;height:46%;left:26%;bottom:0;transform:rotate(-1.5deg);z-index:2}
.badge{position:absolute;right:4%;bottom:6%;z-index:3;background:var(--acc);color:var(--acc-ink);width:112px;height:112px;border-radius:50%;display:grid;place-content:center;text-align:center;font-weight:800;font-size:13px;line-height:1.2;transform:rotate(9deg)}
.badge b{font:var(--hw) 30px/1 var(--hf);text-transform:none;display:block}
@media(max-width:860px){.hero .wrap{grid-template-columns:1fr}.collage{height:400px}}
"""

V["ticker"] = """
.ticker{background:var(--acc);color:var(--acc-ink);overflow:hidden;white-space:nowrap;font:var(--hw) 22px var(--hf);text-transform:uppercase;letter-spacing:.06em;padding:11px 0;border-block:var(--bw) solid var(--ink)}
.ticker div{display:inline-block;animation:tk 34s linear infinite}
@keyframes tk{to{transform:translateX(-50%)}}
"""
V["awning"] = """
.awning{height:14px;background:repeating-linear-gradient(90deg,var(--acc) 0 28px,var(--surf) 28px 56px)}
"""

V["about_facts"] = ""
V["about_photo"] = """
.two{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}
.two img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--r);border:var(--bw) solid var(--ink);box-shadow:var(--sh)}
.two .chips{margin:20px 0 26px}
@media(max-width:860px){.two{grid-template-columns:1fr;gap:30px}}
"""
V["about_cols"] = """
.acols{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:var(--bw) solid var(--ink)}
.acols div{padding:26px 26px 26px 0;border-bottom:1px solid var(--line)}
.acols div+div{padding-left:26px;border-left:1px solid var(--line)}
.acols h3{font-size:22px;margin-bottom:8px;color:var(--acc)}
.acols p{color:var(--dim);font-size:16px}
.center{text-align:center}.center .lead{margin-left:auto;margin-right:auto}
@media(max-width:860px){.acols{grid-template-columns:1fr}.acols div+div{padding-left:0;border-left:0}}
"""

V["menu_cols"] = """
.mcols{display:grid;grid-template-columns:1fr 1fr;gap:0 64px}
.grp{margin-bottom:38px}
.grp h3{font-size:26px;color:var(--acc);padding-bottom:8px;border-bottom:var(--bw) solid var(--ink);margin-bottom:4px}
.dark .grp h3{border-color:var(--acc-d);color:var(--acc-d)}
.grp li{list-style:none;display:flex;gap:10px;align-items:baseline;padding:9px 0}
.grp li i{flex:1;border-bottom:1.5px dotted currentColor;opacity:.35;transform:translateY(-4px)}
.grp li b{white-space:nowrap}
@media(max-width:860px){.mcols{grid-template-columns:1fr}}
"""
V["menu_cards"] = """
.mcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}
.mcard{background:var(--surf);color:var(--ink);border:var(--bw) solid var(--ink);border-radius:var(--r);padding:26px;box-shadow:var(--sh)}
.mcard h3{font-size:24px;color:var(--acc);margin-bottom:8px}
.mcard li{list-style:none;display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1.5px dashed var(--line);font-size:16px}
.mcard li b{white-space:nowrap;color:var(--acc)}
"""
V["menu_tabs"] = """
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px}
.tabs button{font:700 14px var(--bf);letter-spacing:.08em;text-transform:uppercase;background:transparent;color:inherit;border:1.5px solid currentColor;padding:10px 20px;border-radius:var(--br);cursor:pointer;opacity:.75}
.tabs button[aria-selected=true]{background:var(--acc);border-color:var(--acc);color:var(--acc-ink);opacity:1}
.pane{display:none;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:0 50px;list-style:none}
.pane.on{display:grid}
.pane li{display:flex;justify-content:space-between;gap:14px;padding:13px 0;border-bottom:1px solid var(--line);font-weight:500}
.dark .pane li{border-color:#ffffff2e}
.pane li b{color:var(--acc);white-space:nowrap}.dark .pane li b{color:var(--acc-d)}
"""
V["menu_board"] = """
.board{background:var(--surf);color:var(--ink);border:10px solid var(--acc);border-radius:calc(var(--r)/2);padding:34px;box-shadow:var(--sh)}
.board .bgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:0 40px}
.board h3{font-size:24px;color:var(--acc);margin:14px 0 6px;border-bottom:2px solid var(--ink);padding-bottom:6px}
.board li{list-style:none;display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1.5px dotted var(--line)}
.board li b{white-space:nowrap}
"""
V["menu_tags"] = """
.tagsg{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:26px}
.tagc{background:var(--surf);color:var(--ink);border-radius:6px 6px var(--r) var(--r);padding:38px 24px 22px;position:relative;box-shadow:0 8px 0 #0004}
.tagc::before{content:"";position:absolute;top:13px;left:50%;width:16px;height:16px;border-radius:50%;background:var(--ink);transform:translateX(-50%)}
.tagc h3{font-size:22px;color:var(--acc);text-align:center;margin:4px 0 10px}
.tagc li{list-style:none;display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:2px dotted var(--line);font-weight:600}
.tagc li b{white-space:nowrap;color:var(--acc)}
"""
V["menu_none"] = """
.mnone{border:var(--bw) solid currentColor;border-radius:var(--r);padding:34px;max-width:720px}
"""

V["gal_mosaic"] = """
.gal{display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:230px;gap:12px;list-style:none}
.gal li{overflow:hidden;border-radius:var(--r);border:var(--bw) solid var(--ink)}
.gal img{width:100%;height:100%;object-fit:cover;transition:transform .5s}
.gal li:hover img{transform:scale(1.05)}
.gal li:nth-child(1){grid-column:span 2;grid-row:span 2}
.gal li:nth-child(6){grid-column:span 4}
@media(max-width:860px){.gal{grid-template-columns:1fr 1fr;grid-auto-rows:150px}.gal li:nth-child(1){grid-column:span 2;grid-row:span 1}.gal li:nth-child(6){grid-column:span 2}}
"""
V["gal_strip"] = """
.gal{display:flex;gap:14px;overflow-x:auto;padding:4px 22px 26px;scroll-snap-type:x mandatory;list-style:none;margin:0 -22px}
.gal li{flex:0 0 min(320px,72vw);scroll-snap-align:start}
.gal img{width:100%;height:420px;object-fit:cover;border-radius:var(--r);border:var(--bw) solid var(--ink)}
.gal li:nth-child(even) img{height:340px;margin-top:80px}
@media(max-width:860px){.gal li:nth-child(even) img{margin-top:0;height:420px}}
"""
V["gal_masonry"] = """
.gal{columns:3 240px;column-gap:14px;list-style:none}
.gal li{break-inside:avoid;margin-bottom:14px;overflow:hidden;border-radius:var(--r);border:var(--bw) solid var(--ink)}
.gal img{width:100%;height:auto}
"""
V["gal_polaroid"] = """
.gal{display:grid;grid-template-columns:repeat(3,1fr);gap:30px 22px;list-style:none;padding:10px}
.gal li{background:#fff;padding:10px 10px 34px;box-shadow:0 12px 28px #0003;transform:rotate(var(--rot,-2deg))}
.gal li:nth-child(2n){--rot:2.5deg}.gal li:nth-child(3n){--rot:-1deg}
.gal img{width:100%;aspect-ratio:1;object-fit:cover}
@media(max-width:860px){.gal{grid-template-columns:1fr 1fr}}
"""
V["gal_grid3"] = """
.gal{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;list-style:none}
.gal li{overflow:hidden;border-radius:var(--r);position:relative;aspect-ratio:4/3;border:var(--bw) solid var(--ink)}
.gal img{width:100%;height:100%;object-fit:cover;transition:transform .5s}
.gal li:hover img{transform:scale(1.06)}
@media(max-width:860px){.gal{grid-template-columns:1fr 1fr}}
"""

V["rev_cards"] = """
.rev{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px}
.rev figure{background:var(--surf);border:var(--bw) solid var(--ink);border-radius:var(--r);padding:28px;box-shadow:var(--sh);color:var(--ink)}
.rev blockquote{font-size:18px;line-height:1.55}
.rev figcaption{margin-top:14px;font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:var(--acc)}
"""
V["rev_big"] = """
.rev{display:grid;gap:0;max-width:860px}
.rev figure{padding:30px 0;border-bottom:1px solid currentColor}
.rev blockquote{font:500 clamp(21px,2.8vw,32px)/1.35 var(--qf);text-transform:none;letter-spacing:0}
.rev figcaption{margin-top:12px;font-size:13px;letter-spacing:.18em;text-transform:uppercase;font-weight:700;color:var(--acc)}
.dark .rev figcaption{color:var(--acc-d)}
"""
V["rev_cols"] = """
.rev{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:36px}
.rev figure{border-top:var(--bw) solid var(--acc);padding-top:22px}
.rev blockquote{font-size:18px;line-height:1.6}
.rev blockquote::before{content:"«";color:var(--acc);font:var(--hw) 40px/0 var(--hf);margin-right:4px}
.rev figcaption{margin-top:14px;font-size:12px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;color:var(--dim)}
@media(max-width:860px){.rev{grid-template-columns:1fr}}
"""

V["book_split"] = """
.bgrid{display:grid;grid-template-columns:1fr 1fr;gap:52px;align-items:start}
@media(max-width:860px){.bgrid{grid-template-columns:1fr}.bf{grid-template-columns:1fr}}
"""
V["book_center"] = """
.bcenter{max-width:820px;margin:0 auto;text-align:center}
.bcenter .bf{text-align:left;margin-top:30px}
.bcenter dl{text-align:left;max-width:520px;margin:26px auto}
.bcenter .callcard{text-align:center;justify-items:center}
@media(max-width:860px){.bf{grid-template-columns:1fr}}
"""
V["book_band"] = """
.bandg{display:grid;grid-template-columns:.9fr 1.1fr;gap:0;border:var(--bw) solid var(--ink);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh)}
.bandg .info{background:var(--acc);color:var(--acc-ink);padding:44px}
.bandg .info dt{color:var(--acc-ink);opacity:.8}
.bandg .info .btn{background:var(--acc-ink);color:var(--acc);border-color:var(--acc-ink)}
.bandg .info .btn.o{background:transparent;color:var(--acc-ink)}
.bandg .bf,.bandg .callcard{border:0;border-radius:0;box-shadow:none}
@media(max-width:860px){.bandg{grid-template-columns:1fr}.bf{grid-template-columns:1fr}.bandg .info{padding:30px}}
"""

RUDAY = {"пн": "Monday", "вт": "Tuesday", "ср": "Wednesday", "чт": "Thursday", "пт": "Friday", "сб": "Saturday", "вс": "Sunday"}
ORDER = list(RUDAY)


def parse_hours(txt):
    """'пн-чт 15:00–00:00; пт,сб 15:00–02:00' / 'ежедневно, 10:00–23:00' -> [(days, open, close)]"""
    out = []
    if not txt:
        return [(list(RUDAY.values()), "10:00", "22:00")]
    for part in txt.split(";"):
        part = part.strip()
        m = re.search(r"(\d{1,2}:\d{2})[–-](\d{1,2}:\d{2})", part)
        if "круглосуточно" in part:
            o, c = "00:00", "23:59"
        elif m:
            o, c = m.group(1).zfill(5), m.group(2).zfill(5)
        else:
            continue
        head = part.lower()
        days = []
        if head.startswith("ежедневно") or "круглосуточно" in head and not re.match(r"^[а-я]{2}", head):
            days = list(RUDAY)
        else:
            for a, b in re.findall(r"\b(пн|вт|ср|чт|пт|сб|вс)\s*-\s*(пн|вт|ср|чт|пт|сб|вс)\b", head):
                i, j = ORDER.index(a), ORDER.index(b)
                days += ORDER[i:j + 1] if i <= j else ORDER[i:] + ORDER[:j + 1]
            days += [d for d in re.findall(r"\b(пн|вт|ср|чт|пт|сб|вс)\b", head.split(m.group(1))[0] if m else head) if d not in days]
        out.append(([RUDAY[d] for d in dict.fromkeys(days)] or list(RUDAY.values()), o, c))
    return out or [(list(RUDAY.values()), "10:00", "22:00")]


def hours_rows(txt):
    if not txt:
        return [("Ежедневно", "по звонку")]
    rows = []
    for part in txt.split(";"):
        part = part.strip()
        m = re.search(r"(\d{1,2}:\d{2}[–-]\d{1,2}:\d{2})", part)
        if "круглосуточно" in part:
            rows.append((part.split(",")[0].capitalize() if not part.startswith("круглосуточно") else "Ежедневно", "круглосуточно"))
        elif m:
            d = part[:m.start()].strip(" ,")
            rows.append((d.capitalize().replace("Пн-", "Пн–").replace("-", "–") or "Ежедневно", m.group(1).replace("-", "–")))
    return rows or [("Ежедневно", txt)]


def rub(n):
    n = int(n)
    return f"{n:,}".replace(",", " ") + " ₽"


def clean(s):
    s = re.sub(r"\\+", "", s)
    return E(re.sub(r"\s+", " ", s.replace("u0026", "&")).strip())


# ---------------------------------------------------------------- блоки
def hdr(s, D):
    nav = "".join(f'<a href="#{i}">{E(t)}</a>' for i, t in s["nav"])
    logo = f'<img {{{{IMG:logo}}}} alt="{E(s["name"])}">' if s.get("logo_in_header") else E(s["brand"])
    return (f'<header><div class="wrap"><a class="brand" href="#top" aria-label="{E(s["name"])} — на главную">{logo}</a>'
            f'<button class="burger" type="button" aria-expanded="false" aria-controls="nav" aria-label="Меню"><span></span></button>'
            f'<nav class="js-nav" id="nav" aria-label="Основная навигация">{nav}</nav>'
            f'<a class="btn" style="padding:11px 22px" href="#book">Забронировать</a></div></header>')


def hero(s, D):
    v = s["hero"]
    cta = '<div class="cta"><a class="btn" href="#book">Забронировать столик</a><a class="btn o" href="#menu">Меню</a></div>'
    badge_txt = f'★ {D["rating_s"]} · {D["rc"]} оценок на Яндекс Картах'
    k = f'<span class="k">{E(s["kicker"])}</span>'
    h1 = f'<h1>{E(s["h1"])}</h1>'
    lead = f'<p>{E(s["lead"])}</p>'
    if v == "hero_full" or v == "hero_center":
        return f'<div class="hero" id="top"><div class="wrap">{k}{h1}{lead}{cta}<div class="badge">{badge_txt}</div></div></div>'
    if v == "hero_split":
        return (f'<div class="hero" id="top"><div class="wrap"><div>{k}{h1}{lead}{cta}</div>'
                f'<div class="ph"><img {{{{IMGE:hero}}}} alt="{E(s["hero_alt"])}"><div class="badge">{badge_txt}</div></div></div></div>')
    if v == "hero_arch":
        return (f'<div class="hero" id="top"><div class="wrap"><div>{k}{h1}{lead}{cta}<div class="badge">{badge_txt}</div></div>'
                f'<img class="arch" {{{{IMGE:hero}}}} alt="{E(s["hero_alt"])}"></div></div>')
    if v == "hero_poster":
        return (f'<div class="hero" id="top"><div class="txt">{k}{h1}{lead}{cta}<div class="badge">{badge_txt}</div></div>'
                f'<div class="ph"><img {{{{IMGE:hero}}}} alt="{E(s["hero_alt"])}"><img {{{{IMG:g1}}}} alt=""></div></div>')
    if v == "hero_collage":
        return (f'<div class="hero" id="top"><div class="wrap"><div>{k}{h1}{lead}{cta}</div>'
                f'<div class="collage"><img {{{{IMGE:hero}}}} alt="{E(s["hero_alt"])}"><img {{{{IMG:g1}}}} alt=""><img {{{{IMG:g2}}}} alt="">'
                f'<div class="badge"><span><b>{D["rating_s"]}</b>{D["rc"]} оценок</span></div></div></div></div>')
    raise KeyError(v)


def stats(D):
    hrs = hours_rows(D.get("hours"))
    first = hrs[0][1] if hrs else ""
    items = [(D["rating_s"], f'рейтинг, {D["rc"]} оценок')]
    if D.get("check"):
        items.append((D["check"].replace("от ", "от ").replace(" ₽", " ₽"), "средний счёт"))
    items.append((first.replace("–", "–"), "часы работы"))
    tables = [f.split(": ")[1] for f in D["feats"] if f.startswith("количество столов")]
    if tables:
        items.append((tables[0].replace("до ", "до "), "столов в зале"))
    return items[:4]


def about(s, D):
    v = s["about"]
    st = "".join(f"<li><b>{E(a)}</b><span>{E(b)}</span></li>" for a, b in stats(D))
    chips = "".join(f"<li>{E(c)}</li>" for c in s["chips"])
    if v == "about_facts":
        return (f'<section id="about" aria-labelledby="h-about"><div class="wrap"><div class="eyebrow">О заведении</div><h2 id="h-about">{E(s["about_h"])}</h2>'
                f'<p class="lead">{E(s["about_p"])}</p><ul class="stats">{st}</ul><ul class="chips" style="margin-top:22px">{chips}</ul></div></section>')
    if v == "about_photo":
        return (f'<section id="about" aria-labelledby="h-about"><div class="wrap two"><img {{{{IMG:g7}}}} alt="{E(s["about_alt"])}"><div>'
                f'<div class="eyebrow">О заведении</div><h2 id="h-about">{E(s["about_h"])}</h2><p class="lead" style="margin-bottom:0">{E(s["about_p"])}</p>'
                f'<ul class="chips">{chips}</ul><ul class="stats" style="grid-template-columns:1fr 1fr">{st}</ul></div></div></section>')
    if v == "about_cols":
        cols = "".join(f'<div><h3>{E(a)}</h3><p>{E(b)}</p></div>' for a, b in s["cols"])
        return (f'<section id="about" aria-labelledby="h-about"><div class="wrap center"><div class="eyebrow">О заведении</div><h2 id="h-about">{E(s["about_h"])}</h2>'
                f'<p class="lead">{E(s["about_p"])}</p><div class="acols" style="text-align:left">{cols}</div>'
                f'<ul class="stats" style="margin-top:34px">{st}</ul></div></section>')
    raise KeyError(v)


def menu_groups(s, D):
    groups = []
    want = s.get("menu_cats")
    skip = re.compile(r"соус|гарнир|мероприят|^чай|кофе|газир|специальн", re.I)
    for c in D.get("menu", []):
        if want is not None and not any(w.lower() in c["cat"].lower() for w in want):
            continue
        if want is None and skip.search(c["cat"]):
            continue
        items = [(a, b) for a, b in c["items"] if a and b and int(b) > 0]
        name = c["cat"].strip()
        if re.match(r"без категории", name, re.I):
            name = "Избранное"
        name = name.capitalize() if name.isupper() else name
        if items:
            groups.append((name, items[: s.get("menu_n", 6)]))
    return groups[: s.get("menu_groups", 6)]


def menu(s, D):
    v = s["menu"]
    dark = ' dark' if s.get("menu_dark") else ''
    g = menu_groups(s, D)
    head_ = (f'<div class="eyebrow">Меню</div><h2 id="h-menu">{E(s["menu_h"])}</h2>'
             f'<p class="lead">Избранное из карточки. Цены с Яндекс Карт, точные позиции уточняйте у администратора.</p>')
    if not g:
        feats = "".join(f"<li>{E(f.split(': ')[0].capitalize())}</li>" for f in D["feats"] if f.endswith(": true"))[:1200]
        return (f'<section class="{dark.strip()}" id="menu" aria-labelledby="h-menu"><div class="wrap"><div class="eyebrow">Меню</div><h2 id="h-menu">{E(s["menu_h"])}</h2>'
                f'<div class="mnone"><p>Меню и цены сообщают при бронировании. Средний счёт: {E(D.get("check") or "уточняйте")}.</p>'
                f'<ul class="chips" style="margin-top:16px">{feats}</ul></div></div></section>')
    if v == "menu_cols":
        body = "".join(f'<div class="grp"><h3>{clean(c)}</h3><ul>{"".join(f"<li><span>{clean(a)}</span><i></i><b>{rub(b)}</b></li>" for a, b in it)}</ul></div>' for c, it in g)
        return f'<section class="{dark.strip()}" id="menu" aria-labelledby="h-menu"><div class="wrap">{head_}<div class="mcols">{body}</div></div></section>'
    if v == "menu_cards":
        body = "".join(f'<div class="mcard"><h3>{clean(c)}</h3><ul>{"".join(f"<li><span>{clean(a)}</span><b>{rub(b)}</b></li>" for a, b in it)}</ul></div>' for c, it in g)
        return f'<section class="{dark.strip()}" id="menu" aria-labelledby="h-menu"><div class="wrap">{head_}<div class="mcards">{body}</div></div></section>'
    if v == "menu_tabs":
        tabs = "".join(f'<button type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="p{i}" id="t{i}">{clean(c)}</button>' for i, (c, _) in enumerate(g))
        panes = "".join(f'<ul class="pane{" on" if i == 0 else ""}" role="tabpanel" id="p{i}" aria-labelledby="t{i}">{"".join(f"<li><span>{clean(a)}</span><b>{rub(b)}</b></li>" for a, b in it)}</ul>' for i, (c, it) in enumerate(g))
        return f'<section class="{dark.strip()}" id="menu" aria-labelledby="h-menu"><div class="wrap">{head_}<div class="tabs" role="tablist">{tabs}</div>{panes}</div></section>'
    if v == "menu_board":
        body = "".join(f'<div><h3>{clean(c)}</h3><ul>{"".join(f"<li><span>{clean(a)}</span><b>{rub(b)}</b></li>" for a, b in it)}</ul></div>' for c, it in g)
        return f'<section class="{dark.strip()}" id="menu" aria-labelledby="h-menu"><div class="wrap">{head_}<div class="board"><div class="bgrid">{body}</div></div></div></section>'
    if v == "menu_tags":
        body = "".join(f'<div class="tagc"><h3>{clean(c)}</h3><ul>{"".join(f"<li><span>{clean(a)}</span><b>{rub(b)}</b></li>" for a, b in it)}</ul></div>' for c, it in g)
        return f'<section class="{dark.strip()}" id="menu" aria-labelledby="h-menu"><div class="wrap">{head_}<div class="tagsg">{body}</div></div></section>'
    raise KeyError(v)


def gallery(s, D):
    alts = s["gal_alts"]
    li = "".join(f'<li><img {{{{IMG:g{i + 1}}}}} alt="{E(alts[i])}"></li>' for i in range(6))
    return (f'<section id="gallery" aria-labelledby="h-gal"><div class="wrap"><div class="eyebrow">Фото</div><h2 id="h-gal">{E(s["gal_h"])}</h2>'
            f'<ul class="gal">{li}</ul></div></section>')


def reviews(s, D):
    rv = s["reviews"]
    body = "".join(f'<figure><blockquote>{E(t)}</blockquote><figcaption>{E(a)} · Яндекс Карты</figcaption></figure>' for a, t in rv)
    dark = " dark" if s.get("rev_dark") else ""
    return (f'<section id="reviews" class="{dark.strip()}" aria-labelledby="h-rev"><div class="wrap"><div class="eyebrow">Отзывы</div><h2 id="h-rev">{E(s["rev_h"])}</h2>'
            f'<div class="rev">{body}</div></div></section>')


def phone_is_mobile(ph):
    d = digits(ph)
    return len(d) == 11 and d[1] == "9"


def book(s, D):
    v = s["book"]
    rows = "".join(f"<dt>{E(a)}</dt><dd>{E(b)}</dd>" for a, b in hours_rows(D.get("hours"))[:4])
    tel = "+" + digits(D["phone"])
    info = (f'<dl><dt>Адрес</dt><dd><address>Москва, {{{{ADDR}}}}</address></dd>{rows}<dt>Телефон</dt><dd><a href="tel:{{{{TEL}}}}">{{{{PHONE}}}}</a></dd></dl>'
            f'<div class="cta" style="margin-top:0"><a class="btn d" href="tel:{{{{TEL}}}}">Позвонить</a><a class="btn o" href="{{{{MAP}}}}" target="_blank" rel="noopener">Как добраться</a></div>')
    wa = phone_is_mobile(D["phone"])
    if wa:
        form = ('<form class="bf" {{FORMATTR}}><label class="full">Имя<input name="n" required autocomplete="given-name"></label>'
                '<label>Дата<input name="d" type="date" required></label><label>Время<input name="t" type="time" value="19:00" required></label>'
                '<label class="full">Гостей<select name="g"><option>2</option><option>3</option><option>4</option><option>5</option><option>6</option><option>8</option><option>10</option></select></label>'
                '<button class="btn full" type="submit">Отправить в WhatsApp</button><div class="form-msg" role="status" aria-live="polite"></div></form>')
    else:
        form = ('<div class="callcard"><h3>Бронь по телефону</h3><p>Позвоните, и администратор подберёт время и стол.</p>'
                '<a class="tel" href="tel:{{TEL}}">{{PHONE}}</a><a class="btn" href="tel:{{TEL}}">Позвонить</a></div>')
    dark = " dark" if s.get("book_dark") else ""
    hd = f'<div class="eyebrow">Бронь</div><h2 id="h-book">{E(s["book_h"])}</h2><p class="lead" style="margin-bottom:0">{E(s["book_p"])}</p>'
    if v == "book_split":
        return f'<section id="book" class="{dark.strip()}" aria-labelledby="h-book"><div class="wrap bgrid"><div>{hd}{info}</div>{form}</div></section>'
    if v == "book_center":
        return f'<section id="book" class="{dark.strip()}" aria-labelledby="h-book"><div class="wrap bcenter">{hd}{form}<div style="margin-top:34px">{info}</div></div></section>'
    if v == "book_band":
        return (f'<section id="book" aria-labelledby="h-book"><div class="wrap"><div class="bandg"><div class="info"><div class="eyebrow" style="color:inherit;opacity:.8">Бронь</div>'
                f'<h2 id="h-book">{E(s["book_h"])}</h2><p style="margin-bottom:0">{E(s["book_p"])}</p>{info}</div>{form}</div></div></section>')
    raise KeyError(v)


TABS_JS = """
(function(){var t=document.querySelectorAll('.tabs [role=tab]'),p=document.querySelectorAll('.pane');
t.forEach(function(b,i){b.addEventListener('click',function(){t.forEach(function(x){x.setAttribute('aria-selected','false')});p.forEach(function(x){x.classList.remove('on')});b.setAttribute('aria-selected','true');p[i].classList.add('on')})})})();
"""


def render(s, D):
    p, f = PAL[s["pal"]], s["font"]
    used = [s["header"], s["hero"], s["about"], s["menu"], s["gal"], s["rev"], s["book"]] + s.get("decor", [])
    css = css_root(p, f, s["ui"]) + CORE + "".join(V[k] for k in used)
    for k in s.get("extra_css", []):
        css += k
    decor_top = '<div class="awning" aria-hidden="true"></div>' if "awning" in s.get("decor", []) else ""
    tick = ""
    if "ticker" in s.get("decor", []):
        txt = " ✦ ".join(x.upper() for x in s["ticker"]) + " ✦ "
        tick = f'<div class="ticker" aria-hidden="true"><div>{txt}{txt}</div></div>'
    order = s.get("order", ["about", "menu", "gallery", "reviews", "book"])
    parts = {"about": about(s, D), "menu": menu(s, D), "gallery": gallery(s, D), "reviews": reviews(s, D), "book": book(s, D)}
    body = "".join(parts[o] for o in order)
    if s.get("alt_bg", True):  # чередование фона секций без .dark
        pass
    hdr_html = hdr(s, D)
    main = f'<main id="main">{hero(s, D)}{tick}{body}</main>'
    js = JS + (TABS_JS if s["menu"] == "menu_tabs" else "")
    fab = "Забронировать столик" if phone_is_mobile(D["phone"]) else "Позвонить и забронировать"
    fab_href = "#book" if phone_is_mobile(D["phone"]) else "tel:{{TEL}}"
    page = (f'<!--TITLE: {s["title"]}-->\n<!doctype html>\n<html lang="ru">\n<head>\n{{{{HEAD}}}}\n<style>\n{{{{BASECSS}}}}\n{css}\n'
            f'@media(max-width:860px){{.fab{{display:block;position:fixed;left:12px;right:12px;bottom:12px;z-index:70;text-align:center;box-shadow:0 10px 26px #0007}}body{{padding-bottom:78px}}section{{padding:64px 0}}.stats{{grid-template-columns:1fr 1fr}}dl{{grid-template-columns:96px 1fr}}}}\n'
            f'</style>\n</head>\n<body>\n<a class="skip" href="#main">Перейти к содержимому</a>\n{decor_top}{hdr_html}\n{main}\n'
            f'<footer class="end"><div class="wrap"><span>© 2026 {{{{NAME}}}}</span><span>Москва, {{{{ADDR}}}}</span></div></footer>\n'
            f'<a class="btn fab" href="{fab_href}">{fab}</a>\n<script>{{{{JS}}}}{TABS_JS if s["menu"] == "menu_tabs" else ""}</script>\n</body>\n</html>\n')
    return page
