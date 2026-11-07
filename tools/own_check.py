# -*- coding: utf-8 -*-
"""Проверка индивидуальных сайтов (папка own/): телефон и компьютер, бронь, кабинет, битые фото, прокрутка вбок, ошибки.
    python tools/own_check.py [key ...]   -> снимки в raw/own/_check/<key>-*.jpg, в конце ИТОГ"""
import functools, http.server, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OWN, OUT = ROOT / "own", ROOT / "raw" / "own" / "_check"
OUT.mkdir(parents=True, exist_ok=True)
PORT = 8792


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(Q, directory=str(OWN)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()


def scroll_all(page):
    h = page.evaluate("document.documentElement.scrollHeight")
    for y in range(0, h, 500):
        page.evaluate("y=>scrollTo({top:y,behavior:'instant'})", y)
        page.wait_for_timeout(90)
    page.evaluate("scrollTo({top:0,behavior:'instant'})")
    page.wait_for_timeout(200)


def check(br, key):
    bad, url = [], f"http://127.0.0.1:{PORT}/{key}/"
    for name, vp, mobile in (("m", {"width": 390, "height": 800}, True), ("d", {"width": 1366, "height": 800}, False)):
        ctx = br.new_context(viewport=vp, device_scale_factor=1, is_mobile=mobile, has_touch=mobile, locale="ru-RU")
        page = ctx.new_page()
        page.on("pageerror", lambda e: bad.append(f"{name}: ошибка JS {e}"))
        page.on("console", lambda m: bad.append(f"{name}: console {m.text[:120]}") if m.type == "error" and "fonts.g" not in m.text else None)
        page.on("response", lambda r: bad.append(f"{name}: {r.status} {r.url[-50:]}") if r.status >= 400 and "127.0.0.1" in r.url else None)
        page.goto(url, wait_until="load")
        page.wait_for_timeout(2300)
        page.screenshot(path=OUT / f"{key}-{name}1.jpg", type="jpeg", quality=70)
        scroll_all(page)
        ow = page.evaluate("document.documentElement.scrollWidth - innerWidth")
        if ow > 1:
            who = page.evaluate("[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.closest('.cur')).slice(0,3).map(e=>e.tagName+'.'+e.className).join(', ')")
            bad.append(f"{name}: прокрутка вбок {ow}px: {who}")
        broken = page.evaluate("[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src'))")
        if broken:
            bad.append(f"{name}: битые фото {broken}")
        small = page.evaluate("[...document.querySelectorAll('a,button')].filter(e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height<30&&!e.closest('footer')&&!e.closest('nav')).length")
        page.screenshot(path=OUT / f"{key}-{name}full.jpg", type="jpeg", quality=55, full_page=True)
        if mobile:   # бронь на телефоне
            page.locator("[data-book]").first.click()
            page.wait_for_selector(".bk-o.on")
            page.wait_for_timeout(350)
            page.screenshot(path=OUT / f"{key}-book.jpg", type="jpeg", quality=70)
            page.locator(".bk [data-day]").nth(1).click()
            page.locator(".bk [data-g='4']").click()
            page.locator(".bk .tb:not([disabled])").first.click()
            page.locator(".bk input[name=n]").fill("Анна")
            page.locator(".bk input[name=p]").fill("+7 916 123-45-67")
            page.locator(".bk .go").click()
            page.wait_for_selector(".bk .done")
            if not page.locator("#own-tg").count():
                bad.append("нет уведомления")
            page.wait_for_timeout(800)
            page.screenshot(path=OUT / f"{key}-done.jpg", type="jpeg", quality=70)
            page.locator('.bk [data-a="admin"]').click()
            page.wait_for_selector("#own-admin")
            page.wait_for_timeout(400)
            if not page.locator(".ad-bk.fresh").count():
                bad.append("в кабинете нет новой брони")
            page.screenshot(path=OUT / f"{key}-admin.jpg", type="jpeg", quality=70)
            page.locator(".ad-i .y").first.click()
            if page.evaluate("document.getElementById('own-admin').scrollWidth - innerWidth") > 1:
                bad.append("кабинет шире экрана")
        ctx.close()
    return bad


def main():
    serve()
    keys = sys.argv[1:] or sorted(p.name for p in OWN.iterdir() if (p / "index.html").exists())
    total = 0
    with sync_playwright() as p:
        br = p.chromium.launch()
        for k in keys:
            try:
                bad = check(br, k)
            except Exception as e:
                bad = [f"сбой: {str(e)[:300]}"]
            total += len(bad)
            print(k, "OK" if not bad else "ПРОБЛЕМЫ:")
            for b in bad:
                print("   ", b)
        br.close()
    print("ИТОГ:", "всё работает" if not total else f"проблем {total}")


if __name__ == "__main__":
    main()
