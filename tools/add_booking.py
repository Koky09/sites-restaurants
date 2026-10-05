"""Подключает онлайн-бронь стола (book.js) ко всем готовым сайтам sites/<key>/index.html.

    python tools/add_booking.py          # все сайты
    python tools/add_booking.py lado     # один

Данные берутся из самой страницы: название, телефон, часы работы (schema.org openingHoursSpecification,
иначе первые часы в блоке брони, иначе 12:00–23:00). Повторный запуск обновляет данные, не дублируя их.
Адрес сервера записи — из ../tver-demo/settings.json (тот же Google Apps Script)."""
import html as H
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITES = ROOT / "sites"
SETTINGS = ROOT.parent / "tver-demo" / "settings.json"
API = json.loads(SETTINGS.read_text(encoding="utf-8"))["apiUrl"]
DAYS = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
MARK = re.compile(r"<script>window\.RBOOK=.*?</script><script src=\"\.\./\.\./book\.js\" defer></script>\n?", re.S)


def mins(t):
    h, m = t.split(":")[:2]
    return int(h) * 60 + int(m)


def info(key, html):
    ld = {}
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("telephone"):
            ld = d
            break
    name = (re.search(r'data-name="([^"]+)"', html) or [None, None])[1] or ld.get("name") or re.search(r"<title>([^<|–—]+)", html).group(1).strip()
    phone = ld.get("telephone") or re.search(r'href="tel:([^"]+)"', html).group(1)
    shown = (re.search(r'<a[^>]+href="tel:[^"]+"[^>]*>([^<]*\d[^<]*)</a>', html) or [None, phone])[1]
    hours, src = {}, "schema"
    for spec in ld.get("openingHoursSpecification", []) or []:
        o, c = mins(spec["opens"]), mins(spec["closes"])
        c = 1440 if c == 0 else c
        for d in spec.get("dayOfWeek", []):
            hours[DAYS[d]] = [o, c]
    if not hours:
        book = html[html.find('id="book"'):]
        m = re.search(r"(\d{1,2}:\d{2})\s*[–-]\s*(\d{1,2}:\d{2})", book)
        src = "блок брони" if m else "по умолчанию"
        o, c = (mins(m.group(1)), mins(m.group(2))) if m else (12 * 60, 23 * 60)
        c = 1440 if c == 0 else c
        hours = {d: [o, c] for d in range(7)}
    tel = "+" + re.sub(r"\D", "", phone)
    shown = H.unescape(shown.strip())
    if re.fullmatch(r"\+?\d{11}", shown):  # +79773782708 -> +7 (977) 378-27-08
        d = re.sub(r"\D", "", shown)
        shown = f"+7 ({d[1:4]}) {d[4:7]}-{d[7:9]}-{d[9:]}"
    name = H.unescape(name)
    return {"slug": "r-" + key.replace("_", "-"), "name": name, "phone": shown.strip(), "tel": tel, "hours": hours, "api": API}, src


def main():
    keys = sys.argv[1:] or sorted(p.name for p in SITES.iterdir() if (p / "index.html").exists())
    for key in keys:
        f = SITES / key / "index.html"
        html = MARK.sub("", f.read_text(encoding="utf-8"))
        cfg, src = info(key, html)
        tag = f'<script>window.RBOOK={json.dumps(cfg, ensure_ascii=False)};</script><script src="../../book.js" defer></script>\n'
        assert "</body>" in html, key
        html = html.replace("</body>", tag + "</body>", 1)
        f.write_text(html, encoding="utf-8")
        days = sorted(cfg["hours"])
        print(f"  {key:<30} {cfg['name'][:26]:<26} {cfg['phone']:<20} часы: {src}, дней {len(days)}")
    print("Готово:", len(keys))


if __name__ == "__main__":
    main()
