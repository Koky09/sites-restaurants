/* Анимации индивидуальных сайтов (без внешних библиотек): первый экран, проявление при прокрутке, счётчики, кнопка к курсору.
   [data-hero] — дети появляются по очереди; [data-reveal] — дети проявляются при прокрутке; [data-count="4.9"] — отсчёт;
   .magnet — кнопка тянется к курсору. Класс anim на <html> ставится в head и снимается всегда, чтобы экран не остался пустым. */
(function () {
  'use strict';
  var root = document.documentElement, still = matchMedia('(prefers-reduced-motion:reduce)').matches;
  function done() { root.classList.remove('anim'); }
  setTimeout(done, 2500);
  function up(el, delay, y) {
    if (still || !el.animate) return;
    el.animate([{ opacity: 0, transform: 'translateY(' + (y || 26) + 'px)' }, { opacity: 1, transform: 'none' }], { duration: 760, delay: delay, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'backwards' });
  }
  function count(el) {
    var to = parseFloat(el.dataset.count), dec = (el.dataset.count.split('.')[1] || '').length, t0 = performance.now();
    if (still) { el.textContent = el.dataset.count.replace('.', ','); return; }
    (function step(t) {
      var k = Math.min(1, (t - t0) / 1300), v = to * (1 - Math.pow(1 - k, 3));
      el.textContent = v.toFixed(dec).replace('.', ',');
      if (k < 1) requestAnimationFrame(step); else el.textContent = el.dataset.count.replace('.', ',');
    })(t0);
  }
  function init() {
    var sc = function () { root.classList.toggle('scrolled', scrollY > innerHeight * .6); };
    addEventListener('scroll', sc, { passive: true }); sc();
    document.querySelectorAll('[data-hero]').forEach(function (h) { [].forEach.call(h.children, function (c, i) { up(c, 120 + i * 130); }); });
    done();
    var io = 'IntersectionObserver' in window && new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return; io.unobserve(e.target);
        if (e.target.dataset.count) return count(e.target);
        e.target.classList.add('seen');
        [].forEach.call(e.target.children, function (c, i) { up(c, Math.min(i, 8) * 80); });
      });
    }, { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    document.querySelectorAll('[data-reveal],[data-count]').forEach(function (el) { if (io) io.observe(el); else if (el.dataset.count) count(el); });
    if (!still && matchMedia('(pointer:fine)').matches) document.querySelectorAll('.magnet').forEach(function (b) {
      b.addEventListener('mousemove', function (e) { var r = b.getBoundingClientRect(); b.style.transform = 'translate(' + (e.clientX - r.left - r.width / 2) * .18 + 'px,' + (e.clientY - r.top - r.height / 2) * .28 + 'px)'; });
      b.addEventListener('mouseleave', function () { b.style.transition = 'transform .5s cubic-bezier(.2,1.6,.4,1)'; b.style.transform = ''; setTimeout(function () { b.style.transition = ''; }, 500); });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
