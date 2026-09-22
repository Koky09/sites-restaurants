# -*- coding: utf-8 -*-
"""
Поиск заведений без сайта в карточке Яндекс Карт и сбор их данных.

  python tools/discover.py search    # собрать пул карточек из выдачи -> data/pool.json
  python tools/discover.py check     # проверить карточки, оставить кандидатов -> data/cands.json
  python tools/discover.py fetch K.. # выгрузить полные данные выбранных (по slug/id) -> data/<slug>.json

Запросы идут с паузами (~0.6 c), объём небольшой. Используются только публичные страницы карточек.
"""
import html as H, json, os, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppData Chrome/126.0 Safari/537.36".replace("AppData", "AppleWebKit/537.36 (KHTML, like Gecko)"),
       "Accept-Language": "ru-RU,ru;q=0.9"}

# уже сделанные (slug) — не берём повторно
DONE = {"esterum", "zag_zag", "chago", "peys", "made_in_bali", "vino_i_khinkali", "intelligentsiya", "vyet_lotos", "uz_samsa_uz",
        "myaso_v_lavashe", "am_nyamych", "kofeynya_na_ostozhenke", "st_riders_coffee", "tszya_yan", "be_my_pizza_", "lafferia",
        "arma_kraft", "yeshchyo_vina", "ryby_net", "max_s_beef_for_money", "ekspromt", "jawsspot", "brums", "bonitto", "valya_bistro",
        "bebe_de_la_mer", "shokunin", "vova_z_bar", "teburasi", "nashe_vino", "nebesa", "filosofiya", "zarya", "yuniti", "harat_s_pub",
        "yeshchyo_parochku", "safo", "sokol", "severnaya_bashnya"}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=40) as r:
                return r.read().decode("utf8", "ignore")
        except Exception as e:
            time.sleep(1.5 * (i + 1))
    return ""


def search():
    kinds = ["ресторан", "бар", "винный бар", "коктейльный бар", "стейк-хаус", "гастробар", "паб", "пивной ресторан",
             "ресторан итальянской кухни", "ресторан грузинской кухни", "ресторан японской кухни", "ресторан китайской кухни",
             "ресторан корейской кухни", "ресторан узбекской кухни", "ресторан армянской кухни", "ресторан французской кухни",
             "ресторан испанской кухни", "ресторан мексиканской кухни", "ресторан индийской кухни", "ресторан русской кухни",
             "ресторан европейской кухни", "ресторан средиземноморской кухни", "рыбный ресторан", "мясной ресторан",
             "ресторан авторской кухни", "ресторан паназиатской кухни", "ресторан вьетнамской кухни", "ресторан тайской кухни",
             "ресторан с верандой", "ресторан с живой музыкой", "ресторан для банкетов", "семейный ресторан", "ресторан домашней кухни",
             "пиццерия", "суши-бар", "бистро", "ресторан кавказской кухни", "ресторан азербайджанской кухни", "ресторан белорусской кухни",
             "бар с бильярдом", "спорт-бар", "рюмочная", "джаз-бар", "рок-бар", "ресторан на крыше", "ресторан у воды"]
    areas = ["", " Арбат", " Тверская", " Таганка", " Китай-город", " Чистые пруды", " Сокольники", " Кутузовская", " Сокол",
             " Динамо", " Парк Культуры", " Проспект Мира", " Бауманская", " Марьино", " Тушино", " Юго-Запад"]
    jobs = []
    for k in kinds:
        for a in areas[:1]:
            for p in range(1, 9):
                jobs.append((k + a, p))
    for k in kinds[:8]:
        for a in areas[1:]:
            for p in range(1, 4):
                jobs.append((k + a, p))
    print(len(jobs), "страниц выдачи")
    pool = {}

    def one(j):
        q, p = j
        time.sleep(0.4)
        t = get(f"https://yandex.ru/maps/213/moscow/search/{urllib.parse.quote(q)}/?page={p}")
        return re.findall(r"/maps/org/([a-z0-9_]+)/(\d+)", t)

    with ThreadPoolExecutor(6) as ex:
        for n, res in enumerate(ex.map(one, jobs)):
            for slug, oid in res:
                pool[oid] = slug
            if n % 40 == 0:
                print(n, len(pool), flush=True)
    json.dump(pool, open(os.path.join(DATA, "pool.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("пул:", len(pool))


def search2():
    metro = ["Охотный ряд", "Лубянка", "Кузнецкий мост", "Пушкинская", "Чеховская", "Тверская", "Маяковская", "Белорусская", "Новослободская",
             "Менделеевская", "Комсомольская", "Красные ворота", "Чистые пруды", "Тургеневская", "Сухаревская", "Проспект Мира", "Рижская", "ВДНХ",
             "Курская", "Марксистская", "Таганская", "Пролетарская", "Кузнецкий", "Полянка", "Серпуховская", "Тульская", "Нагатинская", "Автозаводская",
             "Павелецкая", "Новокузнецкая", "Третьяковская", "Октябрьская", "Парк культуры", "Кропоткинская", "Библиотека имени Ленина", "Арбатская",
             "Смоленская", "Киевская", "Кутузовская", "Студенческая", "Фили", "Беговая", "Динамо", "Аэропорт", "Сокол", "Войковская", "Речной вокзал",
             "Алексеевская", "Бабушкинская", "Отрадное", "Бибирево", "Динамо", "Савёловская", "Дмитровская", "Тимирязевская", "Петровско-Разумовская",
             "Щукинская", "Сходненская", "Планерная", "Строгино", "Крылатское", "Молодёжная", "Юго-Западная", "Профсоюзная", "Новые Черёмушки", "Калужская",
             "Беляево", "Коньково", "Тёплый Стан", "Ясенево", "Чертановская", "Южная", "Пражская", "Царицыно", "Орехово", "Домодедовская", "Красногвардейская",
             "Марьино", "Братиславская", "Люблино", "Печатники", "Текстильщики", "Кузьминки", "Рязанский проспект", "Выхино", "Новогиреево", "Перово",
             "Шоссе Энтузиастов", "Авиамоторная", "Площадь Ильича", "Римская", "Бауманская", "Электрозаводская", "Семёновская", "Партизанская", "Измайлово",
             "Сокольники", "Преображенская площадь", "Черкизовская", "Речной", "Ленинский проспект", "Спортивная", "Воробьёвы горы", "Университет"]
    jobs = [(f"{k} {m}", p) for m in dict.fromkeys(metro) for k in ("ресторан", "бар") for p in (1, 2, 3)]
    print(len(jobs), "страниц выдачи")
    pool = json.load(open(os.path.join(DATA, "pool.json"), encoding="utf-8"))
    before = len(pool)

    def one(j):
        q, p = j
        time.sleep(0.4)
        t = get(f"https://yandex.ru/maps/213/moscow/search/{urllib.parse.quote(q)}/?page={p}")
        return re.findall(r"/maps/org/([a-z0-9_]+)/(\d+)", t)

    with ThreadPoolExecutor(6) as ex:
        for n, res in enumerate(ex.map(one, jobs)):
            for slug, oid in res:
                pool[oid] = slug
            if n % 60 == 0:
                print(n, len(pool), flush=True)
    json.dump(pool, open(os.path.join(DATA, "pool.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("пул:", before, "->", len(pool))


def parse(t):
    g = lambda r: (re.search(r, t) or [None, None])[1]
    urls = [u for u in re.findall(r'"urls":\[[^\]]*\]', t) if "yastatic" not in u]
    cats = [c for c in re.findall(r'"name":"([^"]*)"', (re.search(r'"categories":\[[^\]]{0,700}', t) or [""])[0])]
    return dict(
        title=H.unescape(g(r"<title>([^<]*)") or ""), has_site=any("http" in u for u in urls),
        rc=int(g(r'"ratingCount":(\d+)') or 0), rating=float(g(r'"ratingValue":([\d.]+)') or 0),
        phone=g(r'"phones":\[\{"number":"([^"]*)"'), addr=g(r'"fullAddress":"([^"]*)"'), hours=g(r'"workingTimeText":"([^"]*)"'),
        check=g(r'"priceRange":\{"lower":\d+,"text":"([^"]*)"'), cats=cats,
        book=bool(re.search(r"предварительная запись|онлайн-бронь", t)),
        nimg=len(set(re.findall(r"get-altay\\?/\d+\\?/([a-z0-9]+)", t))))


def check():
    pool = json.load(open(os.path.join(DATA, "pool.json"), encoding="utf-8"))
    from collections import Counter
    cnt = Counter(pool.values())
    todo = [(oid, s) for oid, s in pool.items() if s not in DONE and cnt[s] == 1]  # слуги, встречающиеся у нескольких id, считаем сетью
    prev = {}
    fp = os.path.join(DATA, "checked.json")
    if os.path.exists(fp):
        prev = json.load(open(fp, encoding="utf-8"))
    todo = [x for x in todo if x[0] not in prev]
    print("проверяем", len(todo), "из", len(pool), "(уже проверено", len(prev), ")")
    out = dict(prev)

    def one(x):
        oid, s = x
        time.sleep(0.5)
        t = get(f"https://yandex.ru/maps/org/{s}/{oid}/")
        if not t:
            return oid, None
        d = parse(t)
        d["slug"] = s
        return oid, d

    with ThreadPoolExecutor(6) as ex:
        for n, (oid, d) in enumerate(ex.map(one, todo)):
            if d:
                out[oid] = d
            if n % 50 == 0:
                print(n, flush=True)
    bad = re.compile(r"кальян|быстрое питание|столовая|магазин|кондитерск|пекарн|доставка", re.I)
    good = re.compile(r"ресторан|бар|паб|винотека|гастро", re.I)
    cands = {oid: d for oid, d in out.items()
             if not d["has_site"] and d["rc"] >= 90 and d["phone"] and d["nimg"] >= 25
             and any(good.search(c) for c in d["cats"]) and not any(bad.search(c) for c in d["cats"])}
    json.dump(out, open(os.path.join(DATA, "checked.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(cands, open(os.path.join(DATA, "cands.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("кандидатов:", len(cands))
    for oid, d in sorted(cands.items(), key=lambda kv: -kv[1]["rc"]):
        print(d["slug"], oid, d["rc"], d["rating"], d["check"], "|", d["title"][:50], "|", ", ".join(d["cats"][:3]))


def full(slug, oid):
    t = get(f"https://yandex.ru/maps/org/{slug}/{oid}/")
    m = get(f"https://yandex.ru/maps/org/{slug}/{oid}/menu/")
    d = parse(t)
    d["slug"], d["oid"] = slug, oid
    d["feats"] = list(dict.fromkeys(f"{n}: {v.strip(chr(34))}" for v, n in
                                     re.findall(r'\{"id":"[a-z_0-9]+","value":("?[^"{}]*"?),"name":"([^"]*)"', t)))[:24]
    rv = []
    for a, txt in re.findall(r'"reviewId":"[^"]*","businessId":"\d+","author":\{"name":"([^"]*)"[\s\S]*?\},"text":"((?:[^"\\]|\\.)*)"', t):
        txt = re.sub(r"\\u003cbr/\\u003e|\\\\n|\\n", " ", txt).replace('\\"', '"').replace("\\u2028", " ")
        if len(txt) > 50:
            rv.append({"a": H.unescape(a), "t": txt[:520]})
    d["reviews"] = rv[:6]
    menu = []
    for cat, body in re.findall(r'"categoryName":"([^"]*)","categoryItems":\[([\s\S]*?)\]\}', m):
        items = [(H.unescape(a), b) for a, b in re.findall(r'"title":"([^"]*)"(?:,"description":"[^"]*")?(?:,"photoLink":"[^"]*")?,"price":"(\d+)"', body)][:8]
        if items and cat.lower() != "popular":
            menu.append({"cat": H.unescape(cat), "items": items})
    d["menu"] = menu[:9]
    d["img_ids"] = list(dict.fromkeys(f"{a}/{b}" for a, b in re.findall(r"avatars\.mds\.yandex\.net\\?/get-altay\\?/(\d+)\\?/([a-z0-9]+)", t)))[:40]
    desc = re.findall(r'"description":"((?:[^"\\]|\\.){70,600})"', t)
    d["desc"] = desc[:2]
    json.dump(d, open(os.path.join(DATA, f"{slug}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        search()
    elif cmd == "search2":
        search2()
    elif cmd == "check":
        check()
    elif cmd == "fetch":
        for a in sys.argv[2:]:
            slug, oid = a.split("/")
            full(slug, oid)
            time.sleep(0.6)
            print("ok", slug)
