# -*- coding: utf-8 -*-
"""
  python tools/make.py photos <key> ...    # скачать фото карточек в raw/<key>/ (по данным specs)
  python tools/make.py sheet <key> ...     # контактные листы для отбора кадров -> raw/sheets/
  python tools/make.py build [key ...]     # собрать сайты из specs.py + data/*.json
"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build, kit
from build import digits

ROOT = build.ROOT
KIND = {"i": "Интерьер", "f": "Блюда", "d": "Напитки", "e": "Вход", "b": "Барная стойка", "t": "Терраса", "s": "Сервировка"}
BAD = re.compile(r"ужасн|отвратит|развели|хамств|плох|не рекоменд|разочар|грязн|нахал|долго ждали|обман|не понравил|хуже|дорого|навязчив|испортил|тухл|холодн|не вкусн|невкусн|хамил|грубо|нелюбез", re.I)
GOOD = re.compile(r"вкусн|отличн|класс|рекоменд|уют|понравил|супер|прекрасн|замечательн|восторг|любим|лучш|шикарн|приятн|атмосфер", re.I)
EMO = re.compile("[\U0001F000-\U0001FAFF☀-➿️ ]")
CHIP_SKIP = re.compile(r"туалет|wc|зарядка|питьевая|пандус|инвалид|количество|цена|средний|время завтрака|скидка|можно с ноутбуком|оплата счета|забота|ограничен", re.I)


def load(slug):
    return json.load(open(os.path.join(ROOT, "data", slug + ".json"), encoding="utf-8"))


def parse_pick(p):
    m = re.match(r"(\d+)([a-z]?)", str(p))
    return int(m.group(1)), (m.group(2) or "i")


def pick_reviews(D, n=3, strict=True):
    out = []
    for r in D.get("reviews", []):
        t = EMO.sub("", r["t"]).strip()
        if BAD.search(t) or (strict and not GOOD.search(t)):
            continue
        sents = re.split(r"(?<=[.!?])\s+", t)
        txt = ""
        for s in sents:
            if len(txt) + len(s) > 260 and txt:
                break
            txt += (" " if txt else "") + s
        txt = txt.strip()
        if len(txt) < 50:
            continue
        if txt[-1] not in ".!?":
            txt = txt.rstrip(",;: —-") + "."
        out.append((r["a"], txt))
        if len(out) == n:
            break
    return out


def chips(D, n=6):
    out = []
    for f in D.get("feats", []):
        name, _, val = f.partition(": ")
        if val != "true" or CHIP_SKIP.search(name):
            continue
        c = name.strip().capitalize()
        if c not in out:
            out.append(c)
    return out[:n]


def price_sym(check):
    m = re.search(r"(\d[\d\s]*)", check or "")
    if not m:
        return "₽₽"
    n = int(m.group(1).replace(" ", "").replace("\xa0", ""))
    return "₽" if n < 700 else "₽₽" if n < 1500 else "₽₽₽" if n < 3000 else "₽₽₽₽"


def prep(s):
    D = load(s["slug"])
    D["rating_s"] = f'{D["rating"]:.1f}'.replace(".", ",")
    D["check"] = (D.get("check") or "").replace("\xa0", " ")
    if not D["check"]:
        m = [f.split(": ")[1] for f in D.get("feats", []) if f.startswith("средний счёт")]
        D["check"] = m[0].replace("\xa0", " ") if m else ""
    return D


def venue(s, D):
    street = re.sub(r"^Москва,\s*", "", D["addr"] or "").replace("улица ", "ул. ").replace("переулок", "пер.").replace("проспект", "просп.").replace("бульвар", "бул.").replace("набережная", "наб.").replace("шоссе", "ш.")
    p = kit.PAL[s["pal"]]
    typ = "BarOrPub" if s.get("bar") else "Restaurant"
    return dict(
        name=s["name"], type=typ, cuisine=s.get("cuisine", "Ресторан"), desc=s["meta"], street=street, phone=D["phone"],
        wa=kit.phone_is_mobile(D["phone"]), price=price_sym(D["check"]), hours=kit.parse_hours(D.get("hours")),
        slug=f'{D["slug"]}/{D["oid"]}', color=p["acc"], letter=s.get("letter", s["name"].strip("«»\"' ")[0].upper()),
        bg=p["acc"], fg=p["acc_ink"], fonts=kit.FONTS[s["font"]][2],
        pick=dict(hero=parse_pick(s["hero_photo"])[0], g=[parse_pick(x)[0] for x in s["gal"]] if False else [parse_pick(x)[0] for x in s["photos"]],
                  og=parse_pick(s["hero_photo"])[0], **({"logo": s["logo"]} if s.get("logo") else {})),
        trim_logo=s.get("trim_logo", False))


def build_one(s):
    key = s["key"]
    D = prep(s)
    s = dict(s)
    s.setdefault("brand", s["name"])
    s.setdefault("title", f'{s["name"]} — {s["kicker"]}')
    s.setdefault("meta", (f'{s["name"]}: {s["kicker"].lower()}. {s["lead"]}')[:158])
    s.setdefault("cuisine", ", ".join(D["cats"][:2]) or "Ресторан")
    s.setdefault("bar", bool(re.search(r"^(бар|паб|спортбар|рюмочная|винотека)", (D["cats"][0] if D["cats"] else "").lower())))
    s.setdefault("nav", [("about", "О месте"), ("menu", "Меню"), ("gallery", "Фото"), ("reviews", "Отзывы"), ("book", "Бронь")])
    s.setdefault("chips", chips(D))
    s.setdefault("menu_h", "Меню")
    s.setdefault("gal_h", "Фото")
    s.setdefault("rev_h", "Гости о нас")
    s.setdefault("book_h", "Забронировать столик")
    s.setdefault("book_p", "Отправьте заявку, мы подтвердим бронь. Компаниям и на выходные лучше бронировать заранее.")
    s.setdefault("hero_alt", f'{KIND[parse_pick(s["hero_photo"])[1]]} {s["name"]}')
    s.setdefault("about_alt", f'{KIND[parse_pick(s["photos"][6])[1]]} {s["name"]}')
    s["gal_alts"] = [f'{KIND[parse_pick(x)[1]]} {s["name"]}' for x in s["photos"][:6]]
    if "reviews" not in s:
        s["reviews"] = pick_reviews(D, 3)
        if len(s["reviews"]) < 2:
            s["reviews"] = pick_reviews(D, 3, strict=False)
    if not s["reviews"]:
        print(f"  ! {key}: нет отзывов, блок скрыт")
        s["order"] = [o for o in s.get("order", ["about", "menu", "gallery", "reviews", "book"]) if o != "reviews"]
        s["nav"] = [n for n in s["nav"] if n[0] != "reviews"]
    if s["about"] == "about_cols" and "cols" not in s:
        g = kit.menu_groups(s, D)
        cats = ", ".join(c.lower() for c, _ in g[:4])
        hrs = kit.hours_rows(D.get("hours"))
        s["cols"] = [("Кухня и бар", (cats.capitalize() + ".") if cats else f'{s["cuisine"]}.'),
                     ("Часы", "; ".join(f"{a}: {b}" for a, b in hrs[:3]) + "."),
                     ("Удобства", (", ".join(x.lower() for x in s["chips"][:4]).capitalize() + ".") if s["chips"] else "Уточняйте у администратора.")]
    v = venue(s, D)
    for w in kit.check_palette(s["pal"], kit.PAL[s["pal"]]):
        print("  ! контраст", w)
    tpl = kit.render(s, D)
    dims = build.process_images(key, v)
    out = build.render(key, v, tpl, dims)
    with open(os.path.join(ROOT, "sites", key, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    size = sum(os.path.getsize(os.path.join(ROOT, "sites", key, "img", x)) for x in os.listdir(os.path.join(ROOT, "sites", key, "img")))
    print(f"{key}: ok img {size // 1024} KB html {len(out) // 1024} KB reviews {len(s['reviews'])} menu {len(kit.menu_groups(s, D))}")


def photos(keys):
    from specs import SPECS
    for s in SPECS:
        if keys and s["key"] not in keys:
            continue
        D = load(s["slug"])
        d = os.path.join(ROOT, "raw", s["key"])
        os.makedirs(d, exist_ok=True)
        for i, iid in enumerate(D["img_ids"][:18], 1):
            fn = os.path.join(d, f"{i}.jpg")
            if os.path.exists(fn):
                continue
            try:
                urllib.request.urlretrieve(f"https://avatars.mds.yandex.net/get-altay/{iid}/XXL_height", fn)
            except Exception as e:
                print("fail", s["key"], i, e)
            time.sleep(0.15)
        print("photos", s["key"], len(os.listdir(d)))


def rawphotos(slugs, n=18):
    for slug in slugs:
        D = load(slug)
        d = os.path.join(ROOT, "raw", slug)
        os.makedirs(d, exist_ok=True)
        for i, iid in enumerate(D["img_ids"][:n], 1):
            fn = os.path.join(d, f"{i}.jpg")
            if os.path.exists(fn) and os.path.getsize(fn) > 1000:
                continue
            try:
                urllib.request.urlretrieve(f"https://avatars.mds.yandex.net/get-altay/{iid}/XXL_height", fn)
            except Exception as e:
                print("fail", slug, i, e)
            time.sleep(0.12)
        print("photos", slug, len(os.listdir(d)), flush=True)


def sheet(keys):
    from PIL import Image, ImageDraw
    os.makedirs(os.path.join(ROOT, "raw", "sheets"), exist_ok=True)
    for k in keys:
        d = os.path.join(ROOT, "raw", k)
        files = sorted((f for f in os.listdir(d) if f.endswith(".jpg")), key=lambda f: int(f[:-4]))
        W = H = 170
        cols = 9
        rows = (len(files) + cols - 1) // cols
        sh = Image.new("RGB", (W * cols, H * rows), "white")
        for j, f in enumerate(files):
            try:
                im = Image.open(os.path.join(d, f)).convert("RGB")
            except Exception:
                continue
            im.thumbnail((W, H))
            x, y = (j % cols) * W, (j // cols) * H
            sh.paste(im, (x, y))
            ImageDraw.Draw(sh).text((x + 4, y + 3), f[:-4], fill="red")
        sh.save(os.path.join(ROOT, "raw", "sheets", f"{k}.jpg"), quality=68)


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "rawphotos":
        rawphotos(args)
    elif cmd == "photos":
        photos(args)
    elif cmd == "sheet":
        sheet(args)
    elif cmd == "build":
        from specs import SPECS
        for s in SPECS:
            if args and s["key"] not in args:
                continue
            build_one(s)
