/* Онлайн-бронь стола для демо-сайтов ресторанов.
   Данные заведения — в window.RBOOK (добавляет tools/add_booking.py): slug, name, phone, hours {0..6: [open, close] в минутах}.
   Заявка уходит на сервер записи (Google Apps Script, тот же, что у tver-demo); о новой брони пишет Telegram-бот. */
(function () {
  'use strict';
  var R = window.RBOOK; if (!R) return;
  var API = R.api;
  try { API = localStorage.getItem('rbook-api') || API; } catch (e) {}
  var TABLES = R.tables || 6, DUR = 120, STEP = 30, DAYS = 30;
  var WD = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'];
  var MON = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var ymd = function (d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); };
  var hm = function (m) { return pad(Math.floor(m / 60)) + ':' + pad(m % 60); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var guestsWord = function (n) { var a = n % 10, b = n % 100; return a >= 1 && a <= 4 && (b < 11 || b > 14) ? 'гостя' : 'гостей'; }; // на 1, 2, 4 гостя; на 5, 12 гостей

  // Старт брони: не раньше открытия, последний стол — за час до закрытия (или до полуночи, если работают ночью)
  function slots(date) {
    var h = R.hours[date.getDay()]; if (!h) return [];
    var open = h[0], close = h[1] <= h[0] ? 1440 : Math.min(h[1], 1440);
    var now = new Date(), out = [], min = 0;
    if (ymd(date) === ymd(now)) min = now.getHours() * 60 + now.getMinutes() + 45;
    for (var t = Math.ceil(open / STEP) * STEP; t <= close - 60; t += STEP) if (t >= min) out.push(t);
    return out;
  }
  function days() {
    var out = [], d = new Date(); d.setHours(12, 0, 0, 0);
    for (var i = 0; i < DAYS; i++) { var x = new Date(d); x.setDate(d.getDate() + i); if (slots(x).length) out.push(x); }
    return out;
  }
  var dayLabel = function (x, i) {
    var t = ymd(new Date()), tm = new Date(); tm.setDate(tm.getDate() + 1);
    var base = x.getDate() + ' ' + MON[x.getMonth()] + ', ' + WD[x.getDay()];
    return ymd(x) === t ? 'Сегодня, ' + base : ymd(x) === ymd(tm) ? 'Завтра, ' + base : base;
  };

  var css = 'html,body{overflow-x:clip}' + /* декоративные ленты и списки не должны давать прокрутку вбок на телефоне */
    '.rb{display:grid;grid-template-columns:1fr 1fr;gap:12px 14px;text-align:left}.rb .full{grid-column:1/-1}' +
    '.rb label{display:grid;gap:6px;font-size:14px;font-weight:600}' +
    '.rb input,.rb select,.rb textarea{font:inherit;font-weight:400;width:100%;min-height:46px;padding:11px 12px;border-radius:10px;border:1px solid currentColor;border-color:color-mix(in srgb,currentColor 35%,transparent);background:transparent;color:inherit}' +
    '.rb textarea{min-height:70px;resize:vertical}.rb option{color:#111;background:#fff}' +
    '.rb button{width:100%;justify-content:center;cursor:pointer}.rb button[disabled]{opacity:.6;cursor:default}' +
    '.rb-msg{grid-column:1/-1;min-height:1.4em;font-size:14px}.rb-note{grid-column:1/-1;font-size:12.5px;opacity:.75;margin:0}' +
    '.rb-done{text-align:left;padding:22px;border-radius:14px;border:1px solid currentColor;border-color:color-mix(in srgb,currentColor 30%,transparent)}' +
    '.rb-done b{display:block;font-size:20px;margin-bottom:6px}.rb-done p{margin:6px 0 0}' +
    '@media(max-width:560px){.rb{grid-template-columns:1fr}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function render(host) {
    var ds = days();
    var form = document.createElement('form');
    form.className = 'bf rb'; form.id = 'bf'; form.noValidate = true;
    form.innerHTML =
      '<label class="full">Имя<input name="n" required autocomplete="given-name" placeholder="Как к вам обращаться"></label>' +
      '<label class="full">Телефон<input name="p" type="tel" inputmode="tel" required autocomplete="tel" placeholder="+7 900 000-00-00"></label>' +
      '<label>Дата<select name="d">' + ds.map(function (x, i) { return '<option value="' + ymd(x) + '">' + esc(dayLabel(x, i)) + '</option>'; }).join('') + '</select></label>' +
      '<label>Время<select name="t"></select></label>' +
      '<label class="full">Гостей<select name="g">' + [1, 2, 3, 4, 5, 6, 7, 8, 10, 12].map(function (n) { return '<option' + (n === 2 ? ' selected' : '') + '>' + n + '</option>'; }).join('') + '</select></label>' +
      '<label class="full">Пожелания<textarea name="c" placeholder="Например: у окна, детский стул, день рождения"></textarea></label>' +
      '<button class="btn full" type="submit">Забронировать стол</button>' +
      '<div class="rb-msg" role="status" aria-live="polite"></div>' +
      '<p class="rb-note">Нажимая «Забронировать стол», вы соглашаетесь на обработку имени и телефона для связи по брони.</p>';
    host.replaceWith(form);
    var dSel = form.elements.d, tSel = form.elements.t, msg = form.querySelector('.rb-msg');
    var fillTimes = function () {
      var p = dSel.value.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2], 12);
      var s = slots(d), keep = tSel.value;
      tSel.innerHTML = s.map(function (t) { return '<option value="' + t + '">' + hm(t) + '</option>'; }).join('');
      var pref = s.indexOf(+keep) >= 0 ? +keep : (s.filter(function (t) { return t >= 19 * 60; })[0] || s[0]);
      if (pref != null) tSel.value = String(pref);
    };
    dSel.addEventListener('change', fillTimes); fillTimes();
    if (!ds.length) { msg.textContent = 'Онлайн-бронь сейчас недоступна, позвоните: ' + R.phone; }

    form._rbSubmit = function () {
      var v = form.elements, name = v.n.value.trim(), phone = v.p.value.trim();
      if (name.length < 2) { msg.textContent = 'Укажите имя'; v.n.focus(); return; }
      if (phone.replace(/\D/g, '').length < 10) { msg.textContent = 'Проверьте номер телефона'; v.p.focus(); return; }
      var s = +v.t.value, g = +v.g.value, date = v.d.value;
      var btn = form.querySelector('button'); btn.disabled = true; btn.textContent = 'Отправляем…'; msg.textContent = '';
      fetch(API, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify({
        action: 'book', slug: R.slug, svcId: 'table', svcName: 'Стол на ' + g + ' ' + guestsWord(g), price: 0,
        intervals: [{ date: date, s: s, e: Math.min(s + DUR, 1440) }], boxes: TABLES, boxLabel: 'Стол', clientName: R.name,
        name: name, phone: phone, comment: v.c.value.trim(), source: 'app' }) })
        .then(function (r) { return r.json(); })
        .then(function (r) {
          if (r.ok) {
            var opt = dSel.options[dSel.selectedIndex].text;
            var done = document.createElement('div'); done.className = 'rb-done'; done.setAttribute('role', 'status');
            done.innerHTML = '<b>Заявка на бронь отправлена</b><p>' + esc(opt) + ', ' + hm(s) + ' · ' + g + ' ' + guestsWord(g) + '</p>' +
              '<p>Мы перезвоним на ' + esc(phone) + ', чтобы подтвердить бронь. Если планы изменятся, позвоните: <a href="tel:' + esc(R.tel) + '">' + esc(R.phone) + '</a></p>';
            form.replaceWith(done);
            return;
          }
          btn.disabled = false; btn.textContent = 'Забронировать стол';
          msg.textContent = r.error === 'taken' ? 'На это время все столы заняты. Выберите другое время.' :
            r.error === 'rate' ? 'Слишком много заявок подряд. Попробуйте через несколько минут или позвоните: ' + R.phone :
            'Проверьте имя, телефон и время брони.';
        })
        .catch(function () { btn.disabled = false; btn.textContent = 'Забронировать стол'; msg.textContent = 'Нет связи с сервером. Попробуйте ещё раз или позвоните: ' + R.phone; });
    };
  }

  // Старый обработчик формы открывал WhatsApp: перехватываем отправку раньше него
  document.addEventListener('submit', function (e) {
    var f = e.target; if (!f || !f._rbSubmit) return;
    e.preventDefault(); e.stopPropagation(); f._rbSubmit();
  }, true);

  function init() {
    var book = document.getElementById('book'); if (!book) return;
    var host = book.querySelector('form') || book.querySelector('.callcard');
    if (host) render(host);
    document.querySelectorAll('a.fab[href^="tel:"]').forEach(function (a) { a.href = '#book'; a.textContent = 'Забронировать столик'; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
