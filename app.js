/* Сайт как приложение: установка на экран телефона, работа без сети (sw.js) и кабинет владельца #admin.
   Подключается к странице скриптом tools/make_app.py вместе с иконками и manifest.webmanifest.
   Данные заведения — window.RBOOK (slug, name, phone, tel, api), их ставит tools/add_booking.py.
   Кабинет работает через тот же сервер записи: вход по PIN (лист clients Google-таблицы, строка r-<key>), список броней, отмена. */
(function () {
  'use strict';
  var R = window.RBOOK || {};
  var API = R.api;
  try { API = localStorage.getItem('rbook-api') || API; } catch (e) {}
  var MON = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
  var WD = ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'];
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var hm = function (m) { return pad(Math.floor(m / 60)) + ':' + pad(m % 60); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} }
  };

  // ---------- работа без сети ----------
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
  }

  var css =
    '.ra-bar{position:fixed;left:12px;right:12px;bottom:12px;z-index:60;display:flex;align-items:center;gap:12px;padding:12px 14px;border-radius:14px;' +
    'background:var(--dark,#111);color:var(--dark-ink,#fff);box-shadow:0 10px 30px rgba(0,0,0,.25);font:15px/1.35 var(--bf,system-ui,sans-serif)}' +
    '.ra-bar img{width:44px;height:44px;border-radius:11px;flex:none}.ra-bar b{display:block;font-size:15px}.ra-bar span{font-size:13px;opacity:.8}' +
    '.ra-bar div{flex:1;min-width:0}.ra-bar button{font:inherit;font-weight:600;border:0;border-radius:10px;padding:10px 14px;cursor:pointer;background:var(--acc2,var(--acc,#c90));color:var(--dark,#111)}' +
    '.ra-bar .ra-x{background:transparent;color:inherit;padding:6px 8px;font-size:20px;line-height:1;opacity:.7}' +
    '.ra-own{display:block;text-align:center;font-size:12.5px;opacity:.6;margin:14px 0 0;color:inherit}' +
    '#ra-admin{position:fixed;inset:0;z-index:80;overflow:auto;background:var(--bg,#fff);color:var(--ink,#111);font:15px/1.45 var(--bf,system-ui,sans-serif)}' +
    '#ra-admin .ra-in{max-width:640px;margin:0 auto;padding:18px 16px 60px}' +
    '#ra-admin header{display:flex;align-items:center;gap:12px;margin-bottom:18px}#ra-admin header img{width:48px;height:48px;border-radius:12px}' +
    '#ra-admin h1{font:var(--hw,700) 22px/1.15 var(--hf,serif);margin:0;padding:0;border:0;flex:1;text-transform:none;letter-spacing:0}#ra-admin h1::after,#ra-admin h2::after,#ra-admin h1::before,#ra-admin h2::before{display:none}#ra-admin h2{font:var(--hw,700) 17px/1.2 var(--hf,serif);margin:22px 0 8px;padding:0;border:0;text-transform:none;letter-spacing:0}' +
    '#ra-admin button,#ra-admin input{font:inherit}#ra-admin .ra-btn{border:0;border-radius:10px;padding:11px 16px;cursor:pointer;background:var(--acc,#222);color:var(--acc-ink,#fff);font-weight:600}' +
    '#ra-admin .ra-ghost{background:transparent;color:inherit;border:1px solid var(--line,#ccc)}' +
    '#ra-admin .ra-pin{display:grid;gap:12px;max-width:320px;margin:40px auto;text-align:center}' +
    '#ra-admin .ra-pin input{text-align:center;font-size:24px;letter-spacing:.35em;padding:12px;border-radius:10px;border:1px solid var(--line,#ccc);background:var(--surf,#fff);color:inherit}' +
    '#ra-admin .ra-card{background:var(--surf,#fff);border:1px solid var(--line,#ddd);border-radius:12px;padding:12px 14px;margin:8px 0;display:grid;grid-template-columns:auto 1fr auto;gap:2px 14px;align-items:center}' +
    '#ra-admin .ra-t{font:700 20px/1 var(--hf,serif);grid-row:span 2}#ra-admin .ra-who{font-weight:600}#ra-admin .ra-sub{font-size:13.5px;opacity:.75;grid-column:2}' +
    '#ra-admin .ra-card a{color:inherit;white-space:nowrap}#ra-admin .ra-c{grid-column:1/-1;font-size:13.5px;margin-top:6px;opacity:.85}' +
    '#ra-admin .ra-new{display:inline-block;font-size:11px;font-weight:700;padding:2px 7px;border-radius:99px;background:var(--acc2,#c90);color:var(--dark,#111);margin-left:6px;vertical-align:2px}' +
    '#ra-admin .ra-msg{min-height:1.4em;font-size:14px}#ra-admin .ra-empty{opacity:.7;padding:24px 0;text-align:center}' +
    '#ra-admin .ra-top{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:6px}#ra-admin .ra-top span{flex:1;font-size:14px;opacity:.75}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  // ---------- кнопка «Добавить на экран» ----------
  var standalone = window.matchMedia && matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  var deferred = null;
  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); deferred = e; offerInstall(); });
  var ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
  function offerInstall() {
    if (standalone || store.get('ra-install-off') || document.querySelector('.ra-bar') || location.hash === '#admin') return;
    if (!deferred && !ios) return;
    var bar = document.createElement('div'); bar.className = 'ra-bar'; bar.setAttribute('role', 'dialog'); bar.setAttribute('aria-label', 'Установить приложение');
    bar.innerHTML = '<img src="icon-192.png" alt=""><div><b>' + esc(R.name || document.title) + ' на экране телефона</b><span>' +
      (deferred ? 'Меню и бронь стола в один тап' : 'Нажмите «Поделиться» → «На экран „Домой“»') + '</span></div>' +
      (deferred ? '<button type="button" class="ra-go">Установить</button>' : '') + '<button type="button" class="ra-x" aria-label="Закрыть">×</button>';
    var fab = document.querySelector('a.fab'); if (fab && fab.offsetHeight) bar.style.bottom = (fab.offsetHeight + 24) + 'px'; // над кнопкой брони
    document.body.appendChild(bar);
    var go = bar.querySelector('.ra-go');
    if (go) go.onclick = function () { deferred.prompt(); deferred.userChoice.finally(function () { bar.remove(); deferred = null; }); };
    bar.querySelector('.ra-x').onclick = function () { bar.remove(); store.set('ra-install-off', '1'); };
  }
  if (ios) setTimeout(offerInstall, 4000);

  // ---------- кабинет владельца ----------
  var KEY = 'ra-pin-' + (R.slug || '');
  function call(body) {
    body.slug = R.slug;
    return fetch(API, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(body) }).then(function (r) { return r.json(); });
  }
  function dayTitle(ymd) {
    var p = ymd.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2], 12), t = new Date(); t.setHours(12, 0, 0, 0);
    var diff = Math.round((d - t) / 864e5);
    var base = d.getDate() + ' ' + MON[d.getMonth()] + ', ' + WD[d.getDay()];
    return diff === 0 ? 'Сегодня, ' + base : diff === 1 ? 'Завтра, ' + base : diff === -1 ? 'Вчера, ' + base : base;
  }
  var root;
  function shell(inner) {
    if (!root) { root = document.createElement('div'); root.id = 'ra-admin'; document.body.appendChild(root); document.documentElement.style.overflow = 'hidden'; }
    root.innerHTML = '<div class="ra-in"><header><img src="icon-192.png" alt=""><h1>' + esc(R.name) + '<br><small style="font:14px var(--bf,sans-serif);opacity:.7">Кабинет · брони столов</small></h1>' +
      '<button type="button" class="ra-btn ra-ghost" data-act="close">На сайт</button></header>' + inner + '</div>';
  }
  function closeAdmin() {
    if (root) { root.remove(); root = null; document.documentElement.style.overflow = ''; }
    if (location.hash === '#admin') history.replaceState(null, '', location.pathname + location.search);
  }
  function pinScreen(msg) {
    shell('<form class="ra-pin"><p>Введите PIN владельца</p><input name="pin" inputmode="numeric" autocomplete="one-time-code" maxlength="8" required aria-label="PIN">' +
      '<button class="ra-btn" type="submit">Войти</button><div class="ra-msg" role="status">' + esc(msg || '') + '</div></form>');
    var f = root.querySelector('form'); f.pin.focus();
    f.onsubmit = function (e) {
      e.preventDefault(); var pin = f.pin.value.trim(); if (!pin) return;
      f.querySelector('.ra-msg').textContent = 'Проверяем…';
      call({ action: 'login', pin: pin }).then(function (r) {
        if (r.ok) { store.set(KEY, pin); load(); }
        else f.querySelector('.ra-msg').textContent = r.error === 'locked' ? 'Слишком много попыток. Попробуйте через 15 минут.' : 'Неверный PIN';
      }).catch(function () { f.querySelector('.ra-msg').textContent = 'Нет связи с сервером'; });
    };
  }
  function load() {
    var pin = store.get(KEY); if (!pin) return pinScreen();
    shell('<p class="ra-empty">Загружаем брони…</p>');
    call({ action: 'list', pin: pin }).then(function (r) {
      if (!r.ok) { store.set(KEY, null); return pinScreen(r.error === 'locked' ? 'Слишком много попыток. Попробуйте через 15 минут.' : ''); }
      render(r.bookings || [], pin);
      var unseen = (r.bookings || []).some(function (b) { return b.status === 'new'; });
      if (unseen) call({ action: 'seen', pin: pin }).catch(function () {});
    }).catch(function () { shell('<p class="ra-empty">Нет связи с сервером. <button class="ra-btn" data-act="reload">Ещё раз</button></p>'); });
  }
  function render(list, pin) {
    var today = new Date(); var t = today.getFullYear() + '-' + pad(today.getMonth() + 1) + '-' + pad(today.getDate());
    var future = list.filter(function (b) { return b.date >= t; }).sort(function (a, b) { return (a.date + pad(a.start)).localeCompare(b.date + pad(b.start)); });
    var html = '<div class="ra-top"><span>Предстоящих броней: ' + future.length + '</span><button class="ra-btn ra-ghost" data-act="reload">Обновить</button>' +
      '<button class="ra-btn ra-ghost" data-act="logout">Выйти</button></div>';
    if (!future.length) html += '<p class="ra-empty">Пока броней нет. Новые появятся здесь и придут вам в Telegram.</p>';
    var cur = '';
    future.forEach(function (b) {
      if (b.date !== cur) { cur = b.date; html += '<h2>' + esc(dayTitle(b.date)) + '</h2>'; }
      var tel = String(b.phone || '').replace(/[^\d+]/g, '');
      html += '<div class="ra-card"><div class="ra-t">' + hm(+b.start) + '</div>' +
        '<div class="ra-who">' + esc(b.name) + (b.status === 'new' ? '<span class="ra-new">новая</span>' : '') + '</div>' +
        '<button class="ra-btn ra-ghost" data-act="cancel" data-id="' + esc(b.id) + '">Отменить</button>' +
        '<div class="ra-sub">' + esc(b.svcName) + ' · <a href="tel:' + esc(tel) + '">' + esc(b.phone) + '</a></div>' +
        (b.comment ? '<div class="ra-c">' + esc(b.comment) + '</div>' : '') + '</div>';
    });
    shell(html);
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('#ra-admin [data-act]'); if (!b) return;
    var act = b.getAttribute('data-act');
    if (act === 'close') closeAdmin();
    else if (act === 'reload') load();
    else if (act === 'logout') { store.set(KEY, null); pinScreen(); }
    else if (act === 'cancel') {
      if (!confirm('Отменить эту бронь? Гостю лучше позвонить и предупредить.')) return;
      b.disabled = true; b.textContent = 'Отменяем…';
      call({ action: 'cancel', id: b.getAttribute('data-id'), pin: store.get(KEY) }).then(load).catch(function () { b.disabled = false; b.textContent = 'Отменить'; alert('Нет связи с сервером'); });
    }
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && root) closeAdmin(); });
  function route() { if (location.hash === '#admin') load(); else if (root) closeAdmin(); }
  window.addEventListener('hashchange', route);

  function init() {
    // неприметная ссылка для владельца внизу страницы
    var foot = document.querySelector('footer') || document.body;
    var a = document.createElement('a'); a.href = '#admin'; a.className = 'ra-own'; a.textContent = 'Кабинет владельца';
    foot.appendChild(a);
    route();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
