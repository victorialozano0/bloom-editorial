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

  document.querySelectorAll('[data-year]').forEach(function (e) { e.textContent = new Date().getFullYear(); });
})();
