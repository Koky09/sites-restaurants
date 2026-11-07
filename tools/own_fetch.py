# -*- coding: utf-8 -*-
"""Данные и фото для индивидуальных сайтов (папка own/) с карточки Яндекс Карт.
    python tools/own_fetch.py key=имя-в-поиске ...   -> data/own/<key>.json, raw/own/<key>/NN.jpg, raw/own/_sheets/<key>.jpg
Источник карточек: tver-demo/tools/newclient/rest-found.json. Папки data/ и raw/ в git не идут."""
import io, json, os, re, sys, time, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import discover
from PIL import Image, ImageDraw

FOUND = json.loads((ROOT.parent / "tver-demo/tools/newclient/rest-found.json").read_text(encoding="utf-8"))
DATA, RAW = ROOT / "data" / "own", ROOT / "raw" / "own"
N = 36


def photos(key, ids):
    d = RAW / key
    d.mkdir(parents=True, exist_ok=True)
    k = 0
    for iid in ids[:N]:
        try:
            raw = urllib.request.urlopen(urllib.request.Request(f"https://avatars.mds.yandex.net/get-altay/{iid}/XXL",
                                                                headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
            im = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception:
            continue
        if min(im.size) < 500:
            continue
        im.thumbnail((1800, 1800))
        k += 1
        im.save(d / f"{k:02d}.jpg", quality=86)
        time.sleep(0.1)
    return k


def sheet(key):
    fs = sorted((RAW / key).glob("*.jpg"))
    W, Hh, cols = 190, 150, 9
    sh = Image.new("RGB", (W * cols, Hh * ((len(fs) + cols - 1) // cols)), "white")
    for j, f in enumerate(fs):
        im = Image.open(f)
        im.thumbnail((W - 4, Hh - 4))
        x, y = (j % cols) * W, (j // cols) * Hh
        sh.paste(im, (x, y))
        ImageDraw.Draw(sh).rectangle((x, y, x + 22, y + 14), fill="black")
        ImageDraw.Draw(sh).text((x + 3, y + 1), f.stem, fill="yellow")
    (RAW / "_sheets").mkdir(exist_ok=True)
    sh.save(RAW / "_sheets" / f"{key}.jpg", quality=72)


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    for a in sys.argv[1:]:
        key, nm = a.split("=", 1)
        x = next(f for f in FOUND if f["name"].lower().startswith(nm.lower()))
        m = re.search(r"/org/([a-z0-9_]+)/(\d+)", x["ya_url"])
        d = discover.full(m[1], m[2])
        (ROOT / "data" / f"{m[1]}.json").unlink(missing_ok=True)
        d.update(key=key, gis=x, name=x["name"])
        (DATA / f"{key}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        n = photos(key, d["img_ids"])
        sheet(key)
        print(f'{key:12} фото {n:2} меню {sum(len(c["items"]) for c in d["menu"]):3} отзывов {len(d["reviews"])} сайт={d["has_site"]} чек={d["check"]} | {d["hours"]} | {x["name"]}', flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
