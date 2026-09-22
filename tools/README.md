# Инструменты сборки сайтов

Нужны Python 3 и Pillow (`pip install pillow`).

## Набор 3 (пять сайтов вручную)
    python tools/build.py [key]       # шаблоны tools/src/<key>.html

## Набор 4 (35 сайтов на конструкторе)
    python tools/discover.py search    # пул карточек из выдачи Яндекс Карт -> data/pool.json
    python tools/discover.py search2   # расширенный поиск по станциям метро
    python tools/discover.py check     # оставить карточки без сайта -> data/cands.json
    python tools/discover.py fetch slug/id ...   # полные данные карточки -> data/<slug>.json
    python tools/make.py rawphotos slug ...      # фото карточки -> raw/<slug>/  (в архив не входят)
    python tools/make.py sheet slug ...          # контактные листы для отбора кадров
    python tools/make.py build [key ...]         # сборка sites/<key>/

* `specs.py` арт-дирекция и тексты каждого сайта (палитра, шрифты, варианты блоков, кадры).
* `reviews.py` отзывы, отобранные вручную.
* `kit.py` конструктор: 3 шапки, 6 главных экранов, 3 блока «о заведении», 5 вариантов меню, 5 галерей, 3 блока отзывов, 3 блока брони, 24 палитры, 26 шрифтов с кириллицей. Контраст палитр проверяется при сборке.
* `build.py` общий `<head>` (SEO, Open Graph, schema.org), базовый CSS (доступность, мобильное меню), оптимизация фото в WebP, JS формы брони.

## Перед боевым запуском
1. В `build.py` укажите `DOMAIN`, поставьте `DEMO_NOINDEX = False`.
2. Замените демо-фото фото владельца.
3. Проверьте меню, цены и часы у заведения.
4. Форма брони открывает WhatsApp. Для приёма заявок на сайте нужен бэкенд или Telegram-бот.
