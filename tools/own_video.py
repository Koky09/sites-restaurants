# -*- coding: utf-8 -*-
"""Видео для рассылки: сайт ресторана, бронь гостя, уведомление в Telegram и кабинет владельца. Без звука, около 30 с.
    python tools/own_video.py [key ...]   -> own/v/<key>.mp4
Запись идёт с локальной копии сайта (папка own/), настоящие заявки не создаются."""
import base64, functools, http.server, shutil, subprocess, sys, threading, time
from pathlib import Path
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OWN, OUT = ROOT / "own", ROOT / "own" / "v"
PORT, W, H = 8793, 390, 760
CSS = """
.fab{display:none!important}
#vc{position:fixed;left:12px;right:12px;bottom:14px;z-index:2147483647;background:rgba(17,17,20,.93);color:#fff;font:600 17px/1.3 -apple-system,"Segoe UI",Roboto,sans-serif;
 padding:12px 15px;border-radius:14px;box-shadow:0 8px 24px rgba(0,0,0,.35);display:flex;gap:10px;align-items:center;pointer-events:none;transition:opacity .3s}
#vc b{flex:none;background:#fff;color:#111;border-radius:50%;width:26px;height:26px;display:grid;place-items:center;font-size:14px}
#vt{position:fixed;width:26px;height:26px;border-radius:50%;background:rgba(255,255,255,.6);border:2px solid rgba(0,0,0,.45);z-index:2147483646;pointer-events:none;transform:translate(-50%,-50%);left:50%;top:60%;transition:left .4s,top .4s}
"""


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def cap(p, n, t):
    p.evaluate("""([n,t])=>{let c=document.getElementById('vc');if(!c){c=document.createElement('div');c.id='vc';document.body.appendChild(c)}
      c.innerHTML=(n?'<b>'+n+'</b>':'')+'<span>'+t+'</span>'}""", [n, t])


def tap(p, loc):
    loc.scroll_into_view_if_needed()
    b = loc.bounding_box()
    p.evaluate("""([x,y])=>{let c=document.getElementById('vt');if(!c){c=document.createElement('div');c.id='vt';document.body.appendChild(c)}c.style.left=x+'px';c.style.top=y+'px'}""",
               [b["x"] + b["width"] / 2, b["y"] + b["height"] / 2])
    p.wait_for_timeout(480)
    loc.click()


def glide(p, ms):
    """плавно проматывает страницу до конца за ms (останавливается перед финальным экраном)"""
    p.evaluate("""ms=>new Promise(res=>{const a=scrollY,b=document.documentElement.scrollHeight-innerHeight,t0=performance.now();
      (function f(t){const k=Math.min(1,(t-t0)/ms),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;scrollTo({top:a+(b-a)*e,behavior:'instant'});k<1?requestAnimationFrame(f):res()})(t0)})""", ms)


def record(br, key):
    tmp = OUT / f"_{key}"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    ctx = br.new_context(viewport={"width": W, "height": H}, device_scale_factor=2, locale="ru-RU")
    p = ctx.new_page()
    # запись через CDP: встроенная запись Playwright не умеет снимать вёрстку телефона в двойной чёткости
    cdp = ctx.new_cdp_session(p)
    frames = []

    def on_frame(ev):
        f = tmp / f"{len(frames):05d}.jpg"
        f.write_bytes(base64.b64decode(ev["data"]))
        frames.append((f, ev["metadata"]["timestamp"]))
        try:
            cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception:
            pass   # последний кадр может прийти, когда страница уже закрыта

    cdp.on("Page.screencastFrame", on_frame)
    p.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent=%r;document.head.appendChild(s);document.documentElement.style.scrollBehavior='auto'})" % CSS)
    cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 88, "maxWidth": W * 2, "maxHeight": H * 2, "everyNthFrame": 1})
    p.goto(f"http://127.0.0.1:{PORT}/{key}/", wait_until="load")
    name = p.evaluate("OWN.name")
    p.wait_for_timeout(500)
    cap(p, 1, f"Сайт для «{name}» — с вашими фото")
    p.wait_for_timeout(3000)
    cap(p, 2, "Меню, зал, отзывы гостей")
    glide(p, 9000)
    p.wait_for_timeout(500)
    cap(p, 3, "Гость бронирует стол сам, без звонка")
    btn = p.locator("[data-book]:not(.fab)").last
    tap(p, btn)
    p.wait_for_selector(".bk-o.on")
    p.wait_for_timeout(800)
    tap(p, p.locator(".bk [data-day]").nth(1))
    p.wait_for_timeout(450)
    tap(p, p.locator(".bk [data-g='4']"))
    p.wait_for_timeout(350)
    cap(p, 3, "Занятые столы закрыты сами")
    free = p.locator(".bk .tb:not([disabled])")
    tap(p, free.nth(min(2, free.count() - 1)))
    p.wait_for_timeout(700)
    n = p.locator(".bk input[name=n]")
    n.scroll_into_view_if_needed()
    n.click(); n.type("Анна", delay=90)
    t = p.locator(".bk input[name=p]")
    t.click(); t.type("+7 916 123-45-67", delay=38)
    p.wait_for_timeout(250)
    tap(p, p.locator(".bk .go"))
    p.wait_for_selector(".bk .done")
    cap(p, 4, "Бронь сразу приходит вам в Telegram")
    p.wait_for_timeout(3400)
    cap(p, 5, "Все брони видно в одном кабинете")
    tap(p, p.locator('.bk [data-a="admin"]'))
    p.wait_for_selector("#own-admin")
    p.wait_for_timeout(2600)
    fresh = p.locator(".ad-i .y").first
    if fresh.count():
        cap(p, 5, "Подтверждаете бронь одним нажатием")
        fresh.scroll_into_view_if_needed()
        p.wait_for_timeout(900)
        tap(p, fresh)
        p.wait_for_timeout(1000)
    cap(p, None, "Легко следить за столами и гостями")
    p.wait_for_timeout(2300)
    cdp.send("Page.stopScreencast")
    ctx.close()
    # кадры приходят неравномерно: длительность каждого берём из его времени
    lst = tmp / "list.txt"
    with open(lst, "w", encoding="utf-8") as fh:
        for i, (f, ts) in enumerate(frames):
            dur = (frames[i + 1][1] - ts) if i + 1 < len(frames) else 0.5
            fh.write(f"file '{f.name}'\nduration {max(dur, 0.001):.4f}\n")
        fh.write(f"file '{frames[-1][0].name}'\n")
    mp4 = OUT / f"{key}.mp4"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", "1.6", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", "scale=720:-2,fps=30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "25", "-movflags", "+faststart", "-an", str(mp4)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return mp4


def main():
    OUT.mkdir(exist_ok=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(Q, directory=str(OWN)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    keys = sys.argv[1:] or sorted(d.name for d in OWN.iterdir() if (d / "index.html").exists())
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for k in keys:
            t = time.time()
            try:
                f = record(br, k)
                print(f"{k:10} {f.stat().st_size // 1024} КБ  запись {time.time() - t:.0f} с", flush=True)
            except Exception as e:
                print(f"{k:10} ОШИБКА {str(e)[:300]}", flush=True)
        br.close()


if __name__ == "__main__":
    main()
