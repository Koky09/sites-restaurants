/* Бронь стола и кабинет владельца для индивидуальных сайтов ресторанов (папка own/).
   Настройки — window.OWN: {key, name, phone, tel, hours:{0..6:[открытие, закрытие] в минутах, 0 = вс}, zones:[...], tables}.
   Пока сайт демонстрационный, заявка никуда не уходит: она хранится в этом браузере и сразу видна в кабинете (#admin).
   Цвета берутся из переменных сайта: --b-bg --b-fg --b-acc --b-acc-ink --b-line --b-font --b-r. */
(function () {
  'use strict';
  var C = window.OWN; if (!C) return;
  var KEY = 'own-' + C.key + '-bookings', TABLES = C.tables || 12, ZONES = C.zones || ['Зал'], STEP = 30, DUR = 120;
  var WD = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'], MON = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var ymd = function (d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); };
  var hm = function (m) { return pad(Math.floor(m / 60)) + ':' + pad(m % 60); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var word = function (n) { var a = n % 10, b = n % 100; return a === 1 && b !== 11 ? 'гость' : a >= 2 && a <= 4 && (b < 12 || b > 14) ? 'гостя' : 'гостей'; };
  var dayName = function (d) {
    var t = new Date(), tm = new Date(); tm.setDate(t.getDate() + 1);
    return ymd(d) === ymd(t) ? 'Сегодня' : ymd(d) === ymd(tm) ? 'Завтра' : d.getDate() + ' ' + MON[d.getMonth()];
  };
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
  // псевдослучайно, но одинаково для одной и той же даты: занятые столы и примерные брони в кабинете
  function rnd(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return function () { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return (h >>> 0) / 4294967296; }; }

  function slots(d) {
    var h = C.hours[d.getDay()]; if (!h) return [];
    var close = h[1] <= h[0] ? 1440 : h[1], now = new Date(), min = ymd(d) === ymd(now) ? now.getHours() * 60 + now.getMinutes() + 45 : 0, out = [];
    for (var t = Math.ceil(h[0] / STEP) * STEP; t <= close - 90; t += STEP) if (t >= min) out.push(t);
    return out;
  }
  function days() { var o = [], d = new Date(); for (var i = 0; o.length < 14 && i < 21; i++) { var x = new Date(d.getFullYear(), d.getMonth(), d.getDate() + i, 12); if (slots(x).length) o.push(x); } return o; }

  // примерные брони дня для плана зала и кабинета
  var NAMES = ['Анна', 'Дмитрий', 'Екатерина', 'Алексей', 'Мария', 'Игорь', 'Ольга', 'Сергей', 'Наталья', 'Роман', 'Светлана', 'Артём', 'Юлия', 'Павел'];
  var NOTES = ['', '', '', 'День рождения', 'У окна', 'Детский стул', '', 'Годовщина', ''];
  function sample(date) {
    var r = rnd(C.key + date), d = new Date(date + 'T12:00:00'), h = C.hours[d.getDay()] || [720, 1380], close = h[1] <= h[0] ? 1440 : h[1], out = [], n = 5 + Math.floor(r() * 4);
    for (var i = 0; i < n; i++) {
      var s = Math.max(h[0], Math.round((Math.max(h[0] + 60, close - 420) + r() * 300) / 30) * 30);
      out.push({ id: 'd' + i, date: date, s: Math.min(s, close - 120), t: Math.floor(r() * TABLES), g: 2 + Math.floor(r() * 5), n: NAMES[Math.floor(r() * NAMES.length)], p: '+7 9•• •••-••-' + pad(Math.floor(r() * 90) + 10), c: NOTES[Math.floor(r() * NOTES.length)], st: r() > .4 ? 'ok' : 'new', demo: 1 });
    }
    return out;
  }
  function allFor(date) { return sample(date).concat(load().filter(function (b) { return b.date === date; })); }
  function busy(date, s, t) { return allFor(date).some(function (b) { return b.t === t && b.st !== 'off' && s < b.s + DUR && b.s < s + DUR; }); }

  var css = '.fab{transition:opacity .25s}html:not(.scrolled) .fab{opacity:0;pointer-events:none}' +
    '.bk-o{position:fixed;inset:0;z-index:9000;display:flex;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.55);opacity:0;transition:opacity .25s}.bk-o.on{opacity:1}' +
    '.bk{width:100%;max-width:520px;max-height:94dvh;overflow:auto;background:var(--b-bg,#fff);color:var(--b-fg,#111);font-family:var(--b-font,inherit);border-radius:var(--b-r,18px) var(--b-r,18px) 0 0;padding:20px 18px calc(22px + env(safe-area-inset-bottom));transform:translateY(40px);transition:transform .3s cubic-bezier(.2,.8,.2,1);box-sizing:border-box}.bk-o.on .bk{transform:none}' +
    '@media(min-width:700px){.bk-o{align-items:center}.bk{border-radius:var(--b-r,18px)}}' +
    '.bk *{box-sizing:border-box}.bk h3{font:inherit;font-size:21px;font-weight:700;margin:0 40px 4px 0}.bk .sub{opacity:.7;font-size:14px;margin:0 0 14px}.bk .x{position:absolute;right:14px;top:12px;width:40px;height:40px;background:none;border:0;color:inherit;font-size:24px;cursor:pointer}.bk{position:relative}' +
    '.bk .lb{font-size:13px;font-weight:700;margin:14px 0 7px;opacity:.75}.bk .row{display:flex;gap:7px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}.bk .wrap{display:flex;flex-wrap:wrap;gap:7px}' +
    '.bk .c{flex:none;min-height:44px;padding:8px 13px;border-radius:calc(var(--b-r,18px)*.6);border:1px solid var(--b-line,rgba(0,0,0,.2));background:none;color:inherit;font:inherit;font-size:14px;cursor:pointer;line-height:1.15}.bk .c small{display:block;opacity:.65;font-size:11px}.bk .c.on{background:var(--b-acc,#111);color:var(--b-acc-ink,#fff);border-color:transparent}' +
    '.bk .plan{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:10px;border:1px solid var(--b-line,rgba(0,0,0,.2));border-radius:calc(var(--b-r,18px)*.7)}.bk .tb{aspect-ratio:1.25;border-radius:calc(var(--b-r,18px)*.5);border:1px solid var(--b-line,rgba(0,0,0,.25));background:none;color:inherit;font:inherit;font-size:13px;cursor:pointer}.bk .tb[disabled]{opacity:.28;cursor:default;text-decoration:line-through}.bk .tb.on{background:var(--b-acc,#111);color:var(--b-acc-ink,#fff);border-color:transparent}' +
    '.bk input{width:100%;min-height:46px;padding:11px 12px;margin-bottom:8px;font:inherit;font-size:16px;color:inherit;background:none;border:1px solid var(--b-line,rgba(0,0,0,.25));border-radius:calc(var(--b-r,18px)*.6)}.bk input::placeholder{color:inherit;opacity:.5}' +
    '.bk .go{width:100%;min-height:52px;margin-top:10px;border:0;border-radius:calc(var(--b-r,18px)*.6);background:var(--b-acc,#111);color:var(--b-acc-ink,#fff);font:inherit;font-weight:700;font-size:16px;cursor:pointer}.bk .err{min-height:18px;font-size:13px;color:#c0392b;margin-top:4px}.bk .nt{font-size:12px;opacity:.65;margin:10px 0 0}' +
    '.bk .done b{display:block;font-size:22px;margin:0 0 6px}.bk .done p{margin:6px 0}' +
    '#own-admin{position:fixed;inset:0;z-index:9500;overflow:auto;background:#f4f5f7;color:#16181d;font:15px/1.4 -apple-system,"Segoe UI",Roboto,Arial,sans-serif}#own-admin *{box-sizing:border-box}' +
    '.ad-h{position:sticky;top:0;z-index:3;display:flex;align-items:center;gap:10px;padding:12px 14px;background:#16181d;color:#fff}.ad-h b{flex:1;font-size:16px;line-height:1.2}.ad-h small{display:block;font-weight:400;opacity:.65;font-size:12px}.ad-h button{min-height:38px;padding:0 12px;border:1px solid rgba(255,255,255,.3);border-radius:9px;background:none;color:#fff;font:inherit;font-size:13px;cursor:pointer}' +
    '.ad-b{max-width:1040px;margin:0 auto;padding:12px 12px 40px}.ad-d{display:flex;gap:6px;overflow-x:auto;padding-bottom:8px;scrollbar-width:none}.ad-d button{flex:none;min-height:44px;padding:6px 13px;border:1px solid #d5d8de;border-radius:10px;background:#fff;color:inherit;font:inherit;font-size:13px;cursor:pointer}.ad-d button.on{background:#16181d;color:#fff;border-color:#16181d}' +
    '.ad-k{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:6px 0 12px}.ad-k div{background:#fff;border-radius:12px;padding:11px 12px}.ad-k b{display:block;font-size:24px;line-height:1.1}.ad-k span{font-size:12px;color:#646b78}' +
    '.ad-t{background:#fff;border-radius:12px;padding:12px;overflow-x:auto;margin-bottom:12px}.ad-t h4,.ad-l h4{margin:0 0 8px;font-size:14px}.ad-g{position:relative;min-width:620px}.ad-hr{display:flex;margin-left:52px;font-size:11px;color:#646b78;border-bottom:1px solid #e5e7eb;padding-bottom:3px}.ad-hr span{flex:1}.ad-r{display:flex;align-items:center;height:30px;border-bottom:1px solid #f0f1f3}.ad-r i{width:52px;flex:none;font-style:normal;font-size:12px;color:#646b78}.ad-r div{position:relative;flex:1;height:100%}.ad-bk{position:absolute;top:3px;bottom:3px;border-radius:6px;background:#dbe7ff;color:#1b3a7a;font-size:11px;line-height:24px;padding:0 6px;white-space:nowrap;overflow:hidden}.ad-bk.new{background:#ffe9c7;color:#7a4b00}.ad-bk.fresh{background:#16a34a;color:#fff;animation:adp 1.2s 3}@keyframes adp{50%{box-shadow:0 0 0 4px rgba(22,163,74,.3)}}' +
    '.ad-l{background:#fff;border-radius:12px;padding:12px}.ad-i{display:flex;gap:10px;align-items:center;padding:10px 0;border-top:1px solid #f0f1f3;flex-wrap:wrap}.ad-i .tm{font-weight:700;width:48px}.ad-i .wh{flex:1;min-width:150px;font-size:14px}.ad-i .wh small{display:block;color:#646b78;font-size:12px}.ad-i button{min-height:38px;padding:0 11px;border-radius:9px;border:1px solid #d5d8de;background:#fff;color:inherit;font:inherit;font-size:13px;cursor:pointer}.ad-i button.y{background:#16a34a;border-color:#16a34a;color:#fff}.ad-i .tag{font-size:12px;color:#15803d}.ad-i.off{opacity:.4}.ad-n{font-size:12px;color:#646b78;margin:12px 2px 0}' +
    '#own-tg{position:fixed;left:10px;right:10px;top:-180px;z-index:9600;max-width:420px;margin:auto;background:#fff;color:#111;border-radius:16px;padding:12px 14px;font:14px/1.35 -apple-system,"Segoe UI",Roboto,sans-serif;box-shadow:0 12px 32px rgba(0,0,0,.35);transition:top .55s cubic-bezier(.2,.8,.2,1)}#own-tg.on{top:12px}#own-tg .h{display:flex;align-items:center;gap:8px;margin-bottom:5px;color:#555;font-size:12.5px}#own-tg .h i{width:21px;height:21px;border-radius:50%;background:#2aabee}#own-tg b{display:block}' +
    '@media(prefers-reduced-motion:reduce){.bk,.bk-o,#own-tg{transition:none}.ad-bk.fresh{animation:none}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  /* ---------- бронь ---------- */
  var S, ov;
  function open(preset) {
    var ds = days(); if (!ds.length) return;
    S = { day: ymd(ds[0]), time: null, g: 2, zone: ZONES[0], t: null, n: '', p: '', c: '', err: '', ds: ds };
    if (preset && preset.c) S.c = preset.c;
    ov = document.createElement('div'); ov.className = 'bk-o'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'Бронь стола');
    ov.innerHTML = '<div class="bk"></div>'; document.body.appendChild(ov); document.documentElement.style.overflow = 'hidden';
    ov.addEventListener('click', onClick); ov.addEventListener('input', function (e) { if (e.target.name) S[e.target.name] = e.target.value; });
    pickTime(); draw(); requestAnimationFrame(function () { requestAnimationFrame(function () { ov.classList.add('on'); }); });
  }
  function close() { if (!ov) return; ov.remove(); ov = null; document.documentElement.style.overflow = ''; }
  function dObj(s) { return new Date(s + 'T12:00:00'); }
  function pickTime() { var a = slots(dObj(S.day)); S.time = a.filter(function (t) { return t >= 19 * 60; })[0] || a[0]; S.t = null; }
  function draw() {
    var b = ov.querySelector('.bk'), keep = b.scrollTop;
    var a = slots(dObj(S.day));
    b.innerHTML = '<button class="x" data-a="x" aria-label="Закрыть">×</button><h3>Забронировать стол</h3><p class="sub">' + esc(C.name) + '</p>' +
      '<div class="lb">День</div><div class="row">' + S.ds.map(function (d) { var v = ymd(d); return '<button class="c' + (v === S.day ? ' on' : '') + '" data-day="' + v + '">' + dayName(d) + '<small>' + WD[d.getDay()] + '</small></button>'; }).join('') + '</div>' +
      '<div class="lb">Время</div><div class="row bk-times">' + a.map(function (t) { return '<button class="c' + (t === S.time ? ' on' : '') + '" data-time="' + t + '">' + hm(t) + '</button>'; }).join('') + '</div>' +
      '<div class="lb">Гостей</div><div class="wrap">' + [1, 2, 3, 4, 5, 6, 8, 10].map(function (n) { return '<button class="c' + (n === S.g ? ' on' : '') + '" data-g="' + n + '">' + n + '</button>'; }).join('') + '</div>' +
      (ZONES.length > 1 ? '<div class="lb">Где сидеть</div><div class="wrap">' + ZONES.map(function (z) { return '<button class="c' + (z === S.zone ? ' on' : '') + '" data-zone="' + esc(z) + '">' + esc(z) + '</button>'; }).join('') + '</div>' : '') +
      '<div class="lb">Выберите стол: занятые закрыты сами</div><div class="plan">' + Array.apply(null, Array(TABLES)).map(function (_, i) { var bz = busy(S.day, S.time, i); return '<button class="tb' + (i === S.t ? ' on' : '') + '" data-t="' + i + '"' + (bz ? ' disabled aria-label="Стол ' + (i + 1) + ' занят"' : '') + '>' + (i + 1) + '</button>'; }).join('') + '</div>' +
      '<div class="lb">Контакты</div><input name="n" placeholder="Имя" autocomplete="given-name" value="' + esc(S.n) + '"><input name="p" type="tel" inputmode="tel" placeholder="Телефон" autocomplete="tel" value="' + esc(S.p) + '"><input name="c" placeholder="Пожелание: день рождения, детский стул…" value="' + esc(S.c) + '">' +
      '<div class="err" role="alert">' + esc(S.err) + '</div><button class="go" data-a="go">Забронировать</button><p class="nt">Это демонстрация: заявка не уходит в ресторан. Позвонить: <a href="tel:' + esc(C.tel) + '" style="color:inherit">' + esc(C.phone) + '</a></p>';
    b.scrollTop = keep;
    var on = b.querySelector('.bk-times .on'); if (on) on.scrollIntoView({ inline: 'center', block: 'nearest' });
  }
  function onClick(e) {
    if (e.target === ov) return close();
    var b = e.target.closest('button'); if (!b) return; var d = b.dataset;
    if (d.a === 'x') return close();
    if (d.day) { S.day = d.day; pickTime(); }
    else if (d.time) { S.time = +d.time; S.t = null; }
    else if (d.g) S.g = +d.g;
    else if (d.zone) S.zone = d.zone;
    else if (d.t) S.t = +d.t;
    else if (d.a === 'go') return submit();
    else if (d.a === 'admin') { close(); location.hash = 'admin'; return; }
    else return;
    S.err = ''; draw();
  }
  function submit() {
    if (S.t === null) { S.err = 'Выберите стол на плане'; return draw(); }
    if (S.n.trim().length < 2) { S.err = 'Укажите имя'; return draw(); }
    if (S.p.replace(/\D/g, '').length < 10) { S.err = 'Проверьте телефон'; return draw(); }
    var rec = { id: 'b' + Date.now(), date: S.day, s: S.time, t: S.t, g: S.g, z: S.zone, n: S.n.trim(), p: S.p.trim(), c: S.c.trim(), st: 'new', fresh: 1 };
    var all = load(); all.push(rec); save(all);
    var d = dObj(S.day), label = dayName(d) + ', ' + hm(S.time);
    ov.querySelector('.bk').innerHTML = '<button class="x" data-a="x" aria-label="Закрыть">×</button><div class="done" role="status"><b>Стол ' + (S.t + 1) + ' за вами</b><p>' + esc(label) + ' · ' + S.g + ' ' + word(S.g) + (ZONES.length > 1 ? ' · ' + esc(S.zone) : '') + '</p><p>На настоящем сайте заявка сразу пришла бы администратору в Telegram и появилась в его кабинете.</p></div><button class="go" data-a="admin">Посмотреть кабинет владельца</button>';
    toast('Новая бронь · ' + C.name, label + ' · стол ' + (S.t + 1) + ' · ' + S.g + ' ' + word(S.g) + '<br>' + esc(rec.n) + ', ' + esc(rec.p));
  }
  function toast(h, t) {
    var o = document.getElementById('own-tg'); if (o) o.remove();
    o = document.createElement('div'); o.id = 'own-tg'; o.setAttribute('role', 'status');
    o.innerHTML = '<div class="h"><i></i>Telegram · сейчас</div><b>' + esc(h) + '</b>' + t; document.body.appendChild(o);
    requestAnimationFrame(function () { requestAnimationFrame(function () { o.classList.add('on'); }); });
    setTimeout(function () { o.classList.remove('on'); setTimeout(function () { o.remove(); }, 700); }, 5200);
  }

  /* ---------- кабинет владельца ---------- */
  var A;
  function admin() {
    if (document.getElementById('own-admin')) return;
    var ds = days(), fresh = load().filter(function (b) { return b.fresh; })[0];
    A = { day: fresh ? fresh.date : ymd(ds[0]), ds: ds, marks: {} };
    var el = document.createElement('div'); el.id = 'own-admin'; document.body.appendChild(el); document.documentElement.style.overflow = 'hidden';
    el.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.x) { el.remove(); document.documentElement.style.overflow = ''; history.replaceState(null, '', location.pathname); return; }
      if (b.dataset.d) A.day = b.dataset.d;
      if (b.dataset.m) {
        var p = b.dataset.m.split(':'), all = load(), r = all.filter(function (x) { return x.id === p[0]; })[0];
        if (r) { r.st = p[1]; delete r.fresh; save(all); } else A.marks[A.day + p[0]] = p[1];
      }
      drawAdmin();
    });
    drawAdmin();
  }
  function drawAdmin() {
    var el = document.getElementById('own-admin'), list = allFor(A.day).map(function (b) { var m = A.marks[A.day + b.id]; if (m) b.st = m; return b; }).sort(function (a, b) { return a.s - b.s; });
    var d = dObj(A.day), h = C.hours[d.getDay()] || [720, 1380], open = h[0], close = h[1] <= h[0] ? 1440 : h[1], span = close - open, live = list.filter(function (b) { return b.st !== 'off'; });
    var guests = live.reduce(function (s, b) { return s + b.g; }, 0), waiting = live.filter(function (b) { return b.st === 'new'; }).length, used = {}; live.forEach(function (b) { used[b.t] = 1; });
    var hours = []; for (var t = Math.ceil(open / 60) * 60; t < close; t += 120) hours.push(hm(t));
    el.innerHTML = '<div class="ad-h"><b>Кабинет · ' + esc(C.name) + '<small>Демо: примерные брони и ваши заявки из этого браузера</small></b><button data-x="1">Закрыть</button></div><div class="ad-b">' +
      '<div class="ad-d">' + A.ds.map(function (x) { var v = ymd(x); return '<button class="' + (v === A.day ? 'on' : '') + '" data-d="' + v + '">' + dayName(x) + ', ' + WD[x.getDay()] + '</button>'; }).join('') + '</div>' +
      '<div class="ad-k"><div><b>' + live.length + '</b><span>броней</span></div><div><b>' + guests + '</b><span>гостей</span></div><div><b>' + waiting + '</b><span>ждут подтверждения</span></div></div>' +
      '<div class="ad-t"><h4>Столы по времени</h4><div class="ad-g"><div class="ad-hr">' + hours.map(function (x) { return '<span>' + x + '</span>'; }).join('') + '</div>' +
      Array.apply(null, Array(TABLES)).map(function (_, i) { return '<div class="ad-r"><i>Стол ' + (i + 1) + '</i><div>' + live.filter(function (b) { return b.t === i; }).map(function (b) { var l = (b.s - open) / span * 100, w = Math.min(DUR, close - b.s) / span * 100; return '<span class="ad-bk ' + (b.fresh ? 'fresh' : b.st === 'new' ? 'new' : '') + '" style="left:' + l + '%;width:' + w + '%">' + hm(b.s) + ' ' + esc(b.n) + '</span>'; }).join('') + '</div></div>'; }).join('') + '</div></div>' +
      '<div class="ad-l"><h4>Список броней</h4>' + list.map(function (b) {
        return '<div class="ad-i' + (b.st === 'off' ? ' off' : '') + '"><span class="tm">' + hm(b.s) + '</span><span class="wh">' + esc(b.n) + ' · ' + b.g + ' ' + word(b.g) + ' · стол ' + (b.t + 1) + '<small>' + esc(b.p) + (b.c ? ' · ' + esc(b.c) : '') + '</small></span>' +
          (b.st === 'new' ? '<button class="y" data-m="' + b.id + ':ok">Подтвердить</button><button data-m="' + b.id + ':off">Отменить</button>' : b.st === 'ok' ? '<span class="tag">Подтверждена</span><button data-m="' + b.id + ':came">Пришли</button>' : b.st === 'came' ? '<span class="tag">Гости за столом</span>' : '<span>Отменена</span>') + '</div>';
      }).join('') + '</div><p class="ad-n">Настоящие заявки приходят сюда и в Telegram, занятое время закрывается само. Вход по PIN.</p></div>';
    // на телефоне таблица шире экрана: сразу показываем новую бронь или первую бронь дня
    var box = el.querySelector('.ad-t'), mark = el.querySelector('.ad-bk.fresh') || el.querySelector('.ad-bk');
    if (box && mark) box.scrollLeft = Math.max(0, mark.getBoundingClientRect().left - box.getBoundingClientRect().left - 70);
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-book]');
    if (a) { e.preventDefault(); open({ c: a.dataset.book || '' }); }
  });
  function route() { if (location.hash === '#admin') admin(); }
  addEventListener('hashchange', route);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', route); else route();
  window.OWNBOOK = { open: open, admin: admin };
})();
