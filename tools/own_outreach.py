# -*- coding: utf-8 -*-
"""Страница рассылки для индивидуальных сайтов ресторанов: шаг 1 — видео и короткое сообщение, шаг 2 (ответили) — ссылка и условия.
    python tools/own_outreach.py   -> ../tver-demo/tools/outreach/out/rest-own-1.html (в git не идёт: там телефоны)
Шаблон и проверка страницы — из tver-demo/tools/outreach. Публиковать с capabilities {"db": {}}."""
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUTREACH = ROOT.parent / "tver-demo" / "tools" / "outreach"
sys.path.insert(0, str(OUTREACH))
from check import check_page

BASE = "https://koky09.github.io/sites-restaurants/own/"
# key, название, город, показать телефон, Telegram, что известно о контакте
REST = [
    ("sosedi", "Соседи", "Новосибирск", "+7 913 916-10-22", "https://t.me/+79139161022", "номер указан как Telegram в 2ГИС"),
    ("bereza", "Белая берёза", "Краснодар", "+7 938 523-52-35", "https://t.me/+79385235235", "номер указан как Telegram в 2ГИС и на Яндексе"),
    ("balerina", "Балерина и Бифштекс", "Краснодар", "+7 918 299-93-77", "https://t.me/+79182999377", "номер указан как Telegram в 2ГИС"),
    ("pera", "Pera", "Казань", "+7 939 746-94-60", "https://t.me/pera_kazan", "личный аккаунт @pera_kazan, проверен"),
    ("kipyatok", "КипятокЪ", "Самара", "+7 846 333-27-20", "https://t.me/+79270077072", "отдельный номер 7 927 007-70-72 указан как Telegram в 2ГИС"),
    ("hadson", "Hadson", "Самара", "+7 939 717-10-77", "https://t.me/+79397171077", "проверьте: чат по номеру (не откроется — Telegram нет)"),
    ("ataman", "Атаманская усадьба", "Ростов-на-Дону", "+7 928 270-30-19", "https://t.me/+79282703019", "проверьте: чат по номеру (не откроется — Telegram нет)"),
    ("sisi", "cafe Sisi", "Ростов-на-Дону", "+7 988 253-33-83", "https://t.me/+79882533383", "проверьте: чат по номеру (не откроется — Telegram нет)"),
    ("nonna", "Nonna Rosa", "Краснодар", "+7 918 129-81-29", "https://t.me/+79181298129", "проверьте: чат по номеру (не откроется — Telegram нет)"),
    ("gavar", "Гавар", "Новосибирск", "+7 923 775-72-01", "https://t.me/+79237757201", "проверьте: чат по номеру (не откроется — Telegram нет)"),
]


def first(name):
    return (f"Здравствуйте! Меня зовут Роман. Сделал для «{name}» сайт с вашими фото и онлайн-бронью стола, на видео 30 секунд, как он работает. "
            f"Гость сам выбирает стол, бронь сразу приходит вам в Telegram, а все брони видно в одном кабинете. Могу скинуть ссылку, посмотрите сами?")


def after(name, key):
    return (f"Спасибо, что ответили! Вот сайт, он сделан отдельно под «{name}», это не шаблон:\n{BASE}{key}/\n\n"
            f"Попробуйте забронировать стол сами, а потом нажмите внизу страницы «Кабинет владельца»: там видно все брони по столам и по времени. "
            f"Пока это демо, заявки никуда не уходят. Меню, цены и фото поставлю ваши.\n\n"
            f"Онлайн-запись у нас уже работает, например, у детейлинга ISDetailing в Москве. Стоимость 5 000 ₽ один раз, без абонентской платы, оплата после запуска, когда всё проверите.")


def remind(name):
    return f"Здравствуйте! Напомню про сайт с бронью для «{name}»: могу скинуть ссылку, посмотрите сами. Если неактуально, просто напишите, больше не побеспокою."


def main():
    items = []
    for i, (key, name, city, phone, tg, note) in enumerate(REST):
        d = re.sub(r"\D", "", phone)
        if not (ROOT / "own" / key / "index.html").exists() or not (ROOT / "own" / "v" / f"{key}.mp4").exists():
            sys.exit(f"ОШИБКА: нет сайта или видео {key}")
        items.append(dict(id=i, group=city, name=name, phone=phone, tg=tg, tgn=note, text=after(name, key), first=first(name), remind=remind(name), remind_old=remind(name),
                          wa=d if d[1] == "9" else "", pre=False, video=f"{BASE}v/{key}.mp4"))
    html = (OUTREACH / "outreach_template.html").read_text(encoding="utf-8")
    title = "рестораны, свои сайты"
    html = html.replace("<title>Рассылка владельцам</title>", f"<title>Рассылка: {title}</title>").replace("<h1>Рассылка владельцам</h1>", f"<h1>Рассылка: {title}</h1>")
    html = html.replace("localStorage.getItem(k)", "localStorage.getItem('restown1-' + k)").replace("localStorage.setItem(k,", "localStorage.setItem('restown1-' + k,")
    html = html.replace("/*PRESENT*/", "")
    html = html.replace('<span class="phone">${esc(it.phone)}</span></div>', '<span class="phone">${esc(it.phone)}</span></div>${it.tgn ? `<div class="phone">Telegram: ${esc(it.tgn)}</div>` : ""}')
    # порядок шагов этой рассылки: сначала видео, ссылка только после ответа
    a = "todo: it.first ? 'Шаг 1 — короткое сообщение без ссылки' : 'Сообщение',"
    b = "replied: 'Ответили — шаг 2: ссылка и видео', no: 'Отказались',"
    c = "todo: `${send}<label class=\"done\">"
    for s in (a, b, c):
        assert s in html, s
    html = html.replace(a, "todo: 'Шаг 1 — видео и это сообщение (ссылка только после ответа)',").replace(b, "replied: 'Ответили — шаг 2: ссылка на сайт', no: 'Отказались',")
    html = html.replace(c, "todo: `<a class=\"btn ok\" href=\"${esc(it.video)}\" target=\"_blank\" rel=\"noopener\">Видео ▶</a>${send}<label class=\"done\">")
    out = OUTREACH / "out" / "rest-own-1.html"
    out.write_text(html.replace("/*DATA*/[]", json.dumps(items, ensure_ascii=False)), encoding="utf-8")
    check_page(out, len(REST))
    print(out)


if __name__ == "__main__":
    main()
