(function () {
  var header = document.querySelector('.site-header');
  var nav = document.querySelector('.main-nav');
  var toggle = document.querySelector('.nav-toggle');

  // Header background on scroll
  function onScroll() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 40);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile menu
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      header.classList.toggle('menu-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }

  // Product tabs
  document.querySelectorAll('[data-tabs]').forEach(function (root) {
    var tabs = root.querySelectorAll('.tab');
    var panels = root.querySelectorAll('.tab-panel');
    function activate(i) {
      tabs.forEach(function (t, j) { t.classList.toggle('active', i === j); t.setAttribute('aria-selected', i === j); });
      panels.forEach(function (p, j) { p.classList.toggle('active', i === j); });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { activate(i); });
      t.addEventListener('mouseenter', function () { if (window.matchMedia('(hover: hover)').matches) activate(i); });
    });
  });

  // Image sliders: auto-advance, pause on hover, clickable dots
  document.querySelectorAll('[data-slider]').forEach(function (root) {
    var slides = root.querySelectorAll('.slide');
    var dots = root.querySelectorAll('.slider-dots button');
    var caption = root.querySelector('.slider-caption');
    if (slides.length < 2) return;
    var i = 0, timer = null;
    // Hidden slides carry data-src and only download when they are about to be shown.
    function load(n) {
      var img = slides[(n + slides.length) % slides.length];
      if (img && img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); }
    }
    function preloadNext() { load(1); }
    if (document.readyState === 'complete') setTimeout(preloadNext, 800);
    else window.addEventListener('load', function () { setTimeout(preloadNext, 800); });
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var sliding = root.classList.contains('slider-slide');
    function show(n) {
      var prev = i;
      i = (n + slides.length) % slides.length;
      load(i); load(i + 1);
      if (i === prev) return;
      if (sliding) {
        // Park the incoming slide off to the right (no animation) so it always enters right-to-left.
        var inc = slides[i];
        inc.classList.remove('prev', 'active');
        void inc.offsetWidth;
      }
      slides.forEach(function (s, j) {
        s.classList.toggle('active', i === j);
        if (sliding) s.classList.toggle('prev', j === prev);
      });
      dots.forEach(function (d, j) { d.classList.toggle('active', i === j); });
      if (caption) caption.textContent = slides[i].alt;
    }
    function start() { if (!reduce) { stop(); timer = setInterval(function () { show(i + 1); }, +root.dataset.interval || 4500); } }
    function stop() { if (timer) clearInterval(timer); timer = null; }
    dots.forEach(function (d, j) {
      d.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); show(j); start(); });
    });
    var thumbs = root.nextElementSibling && root.nextElementSibling.matches('[data-thumbs]') ? root.nextElementSibling.querySelectorAll('button') : [];
    thumbs.forEach(function (t, j) { t.addEventListener('click', function () { show(j); start(); }); });
    var _show = show;
    show = function (n) { _show(n); thumbs.forEach(function (t, j) { t.classList.toggle('active', i === j); }); };
    var host = root.closest('.tile') || root;
    host.addEventListener('mouseenter', stop);
    host.addEventListener('mouseleave', start);
    start();
  });

  // Reveal on scroll
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  // Black-and-white band: photo gains colour as it scrolls through the viewport
  var bw = document.querySelectorAll('[data-bw]');
  if (bw.length) {
    var bwTick = false;
    function bwUpdate() {
      bw.forEach(function (el) {
        var r = el.getBoundingClientRect(), vh = window.innerHeight;
        var p = (vh - r.top) / (vh + r.height);           // 0 entering -> 1 leaving
        var g = Math.min(1, Math.max(0, 1 - (p - 0.35) / 0.4)); // fully B&W until ~35%, colour by ~75%
        el.style.setProperty('--bw', g.toFixed(3));
      });
      bwTick = false;
    }
    window.addEventListener('scroll', function () { if (!bwTick) { requestAnimationFrame(bwUpdate); bwTick = true; } }, { passive: true });
    bwUpdate();
  }

  // Gentle parallax on photo panels
  var para = document.querySelectorAll('[data-parallax]');
  if (para.length && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var ticking = false;
    function update() {
      para.forEach(function (img) {
        var r = img.parentElement.getBoundingClientRect();
        if (r.bottom < 0 || r.top > window.innerHeight) return;
        var p = (r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight;
        img.style.transform = 'translate3d(0,' + (p * -60).toFixed(1) + 'px,0)';
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () { if (!ticking) { requestAnimationFrame(update); ticking = true; } }, { passive: true });
    update();
  }
})();
