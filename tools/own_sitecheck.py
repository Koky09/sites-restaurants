# -*- coding: utf-8 -*-
"""Ручная сверка: у ресторанов (data/own/<key>.json) проверить домены-кандидаты из rest2-verified (checked):
открыть, посмотреть заголовок и есть ли на странице телефон ресторана или улица из адреса.
    python tools/own_sitecheck.py key1 key2 ...
"""
import json, re, sys, urllib.request, ssl
sys.stdout.reconfigure(encoding='utf-8')
V = json.load(open('D:/AI/tver-demo/tools/newclient/rest2-verified.json', encoding='utf-8'))
DIR = re.compile(r'restoran\.cafe|taplink|tabler|greatlist|wheretoeat|restoranoved|doставка|dostavka|eda-dost|доставкав|citybutlers|ayle\.ru|ovvy|topfoodcity|lunch-park|gdefood|eatout|restdom|so-svoim|kto72|nashaspravka|qr-cafe|топ-ресторан|trip-sochi|foodeon|vse-restorani|navse360|suvor|github\.io|clients\.site')
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(r, timeout=15, context=ctx) as x:
        return x.read(400000).decode('utf-8', 'ignore')
for k in sys.argv[1:]:
    d = json.load(open(f'data/own/{k}.json', encoding='utf-8'))
    g = d.get('gis') or {}
    v = V.get(str(g.get('id'))) or V.get(str(d.get('oid'))) or {}
    ph = [re.sub(r'\D', '', p)[-7:] for p in ([d.get('phone') or ''] + (g.get('contacts') or {}).get('phone', []))]
    st = [w for w in re.split(r'[,\s]+', d['addr']) if len(w) > 5 and w.lower() not in ('улица', 'проспект', 'республика', 'область', 'краснодарский')]
    for dom in v.get('checked', []):
        if DIR.search(dom):
            continue
        try:
            h = get('https://' + dom.encode('idna').decode())
            txt = re.sub(r'\D', '', h)
            t = re.search(r'<title[^>]*>(.*?)</title>', h, re.S)
            print(k, dom, 'тел' if any(p and p in txt for p in ph) else '-', [s for s in st if s.lower() in h.lower()][:3], '|', (t.group(1).strip()[:70] if t else ''))
        except Exception as e:
            print(k, dom, 'НЕ ОТКРЫЛСЯ', str(e)[:60])
