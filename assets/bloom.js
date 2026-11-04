// Bloom Editorial home: scroll reveals, breathing guide, 0-5 check-in. No dependencies.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // scroll reveals
  var rv = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    rv.forEach(function (el) { io.observe(el); });
  } else {
    rv.forEach(function (el) { el.classList.add('in'); });
  }

  // breathing guide: physiological sigh (inhale 3s, sniff 1s, exhale 7s, pause 2s), 3 rounds
  var box = document.querySelector('[data-breath]');
  var toggle = document.querySelector('[data-breath-toggle]');
  if (box && toggle) {
    var orb = box.querySelector('.orb');
    var label = box.querySelector('.breath-label');
    var count = box.querySelector('.breath-count');
    var phases = [
      { text: 'Breathe in', secs: 3, scale: 0.9 },
      { text: 'One more sniff', secs: 1, scale: 1 },
      { text: 'Slowly out', secs: 7, scale: 0.55 },
      { text: 'Rest', secs: 2, scale: 0.55 }
    ];
    var rounds = 3, timer = null, running = false;

    function stop(msg) {
      clearTimeout(timer); running = false;
      toggle.textContent = 'Start breathing';
      label.textContent = msg || 'Press start';
      count.textContent = '';
      orb.style.transitionDuration = '1s';
      orb.style.transform = 'scale(.62)';
    }
    function run(round, i) {
      if (!running) return;
      if (i >= phases.length) { round++; i = 0; }
      if (round > rounds) { stop('Well done. Notice how you feel.'); return; }
      var p = phases[i];
      label.textContent = p.text;
      count.textContent = 'Round ' + round + ' of ' + rounds;
      orb.style.transitionDuration = (reduce ? 0 : p.secs) + 's';
      orb.style.transform = 'scale(' + p.scale + ')';
      timer = setTimeout(function () { run(round, i + 1); }, p.secs * 1000);
    }
    toggle.addEventListener('click', function () {
      if (running) { stop(); return; }
      running = true; toggle.textContent = 'Stop';
      run(1, 0);
    });
  }

  // 0-5 check-in (scale text from Vagus Nerve Exercises for Anxiety)
  var levels = [
    'Calm. Present. No notable tension.',
    'Mild background hum. Aware but functional.',
    'Noticeable anxiety. Some physical tension. Still managing.',
    'Significant activation. Difficulty concentrating. Body feels tight. Try the physiological sigh above.',
    'High anxiety. Intrusive thoughts, physical symptoms. Hard to regulate. Try the physiological sigh above.',
    'Acute distress. Unable to feel grounded. If you feel unsafe, please reach out to someone you trust or call or text 988 (US).'
  ];
  var btns = document.querySelectorAll('[data-level]');
  var desc = document.querySelector('[data-scale-desc]');
  btns.forEach(function (b) {
    b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', function () {
      btns.forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
      desc.textContent = b.dataset.level + ': ' + levels[+b.dataset.level];
    });
  });

  // flip-through preview: one Swiper per book, built on first view, plus a zoom lightbox
  var flipPages = {
    hannah: ['Title page', 'Contents', 'Chapter 1 opener', 'Memory verse and the story of Carolyn', 'Integration bridge and reflection questions', 'Reflection questions: five questions for the journey', 'The seven-day healing covenant prayer', 'Memory verse: Mark 5:19'],
    maya: ['Title page', 'Contents', 'Chapter 1 opener', 'Opening page: 11:47pm on a Tuesday', 'Your heart rate variability', 'Exercise 02: your personal vagal state journal', 'The 0 to 5 anxiety scale', 'The full sequence at a glance'],
    claire: ['Title page', 'Contents', 'Chapter 1 opener', 'Opening page: it\'s 3 a.m.', 'Exercise 01: anxiety log', 'Tool 01: the physiological sigh', '3-day blood sugar and anxiety diary', 'The values anchor']
  };
  var flips = {};
  var modal = document.getElementById('flip-modal');
  var modalImg = modal ? modal.querySelector('img') : null;
  function openModal(src, alt) {
    modalImg.src = src; modalImg.alt = alt;
    modal.hidden = false; document.body.style.overflow = 'hidden';
    modal.querySelector('.flip-close').focus();
  }
  function closeModal() { modal.hidden = true; document.body.style.overflow = ''; }
  function buildFlip(el) {
    var book = el.dataset.book, label = el.dataset.label, wrap = el.querySelector('.swiper-wrapper');
    flipPages[book].forEach(function (name, i) {
      var slide = document.createElement('div');
      slide.className = 'swiper-slide';
      var img = document.createElement('img');
      img.src = 'img/flip/' + book + '/' + String(i + 1).padStart(2, '0') + '.webp';
      img.alt = label + ', page preview: ' + name;
      img.width = 640; img.height = 960; img.loading = i < 2 ? 'eager' : 'lazy'; img.draggable = false;
      img.addEventListener('click', function () { openModal(img.src, img.alt); });
      slide.appendChild(img); wrap.appendChild(slide);
    });
    if (!window.Swiper) { el.classList.add('no-swiper'); return; }
    flips[book] = new Swiper(el, {
      slidesPerView: 1.15, spaceBetween: 16, centeredSlides: true, grabCursor: true, speed: reduce ? 0 : 500,
      keyboard: { enabled: true, onlyInViewport: true },
      navigation: { nextEl: el.querySelector('.swiper-button-next'), prevEl: el.querySelector('.swiper-button-prev') },
      pagination: { el: el.querySelector('.swiper-pagination'), clickable: true },
      breakpoints: { 768: { slidesPerView: 1.6, spaceBetween: 30 }, 1024: { slidesPerView: 2.1, spaceBetween: 40 } }
    });
  }
  var flipTabs = Array.prototype.slice.call(document.querySelectorAll('.flip-tabs [role="tab"]'));
  function showFlip(tab, focus) {
    flipTabs.forEach(function (t) {
      var on = t === tab, panel = document.getElementById(t.getAttribute('aria-controls'));
      t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; panel.hidden = !on;
      if (on) {
        if (!panel.dataset.built) { panel.dataset.built = '1'; buildFlip(panel); }
        else if (flips[panel.dataset.book]) flips[panel.dataset.book].update();
      }
    });
    if (focus) tab.focus();
  }
  if (flipTabs.length) {
    flipTabs.forEach(function (t, i) {
      t.addEventListener('click', function () { showFlip(t); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight') n = flipTabs[(i + 1) % flipTabs.length];
        if (e.key === 'ArrowLeft') n = flipTabs[(i - 1 + flipTabs.length) % flipTabs.length];
        if (n) { e.preventDefault(); showFlip(n, true); }
      });
    });
    showFlip(flipTabs[0]);
    modal.addEventListener('click', function (e) { if (e.target === modal || e.target.closest('.flip-close')) closeModal(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !modal.hidden) closeModal(); });
  }

  // nav: authors dropdown + mobile menu
  var dd = document.querySelector('.dd'), ddBtn = document.querySelector('.dd-btn');
  if (dd && ddBtn) {
    ddBtn.addEventListener('click', function () {
      var open = !dd.classList.contains('open');
      dd.classList.toggle('open', open); ddBtn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function (e) {
      if (!dd.contains(e.target)) { dd.classList.remove('open'); ddBtn.setAttribute('aria-expanded', 'false'); }
    });
  }
  var menuBtn = document.querySelector('.menu-btn'), mainNav = document.getElementById('main-nav');
  if (menuBtn && mainNav) {
    menuBtn.addEventListener('click', function () {
      var open = !mainNav.classList.contains('open');
      mainNav.classList.toggle('open', open); menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      menuBtn.querySelector('.ph').className = 'ph ' + (open ? 'ph-x' : 'ph-list');
    });
    mainNav.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { mainNav.classList.remove('open'); }); });
  }

  // journal: filter cards by author (also reads #author-id from the URL)
  var pills = document.querySelectorAll('.jpill');
  if (pills.length) {
    var cards = document.querySelectorAll('.jgrid-index .jcard');
    function filter(f) {
      pills.forEach(function (p) { p.setAttribute('aria-pressed', String(p.dataset.filter === f)); });
      cards.forEach(function (c) { c.hidden = !(f === 'all' || c.dataset.author === f); c.classList.add('in'); });
    }
    pills.forEach(function (p) { p.addEventListener('click', function () { filter(p.dataset.filter); }); });
    var h = location.hash.replace('#', '');
    if (h && document.querySelector('.jpill[data-filter="' + h + '"]')) filter(h);
  }

  document.querySelectorAll('[data-year]').forEach(function (e) { e.textContent = new Date().getFullYear(); });
})();
