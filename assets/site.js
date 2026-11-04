// Bloom Editorial: scroll reveals + catalog filter. No dependencies.
(function () {
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

  var tabs = document.querySelectorAll('.tab[data-filter]');
  if (!tabs.length) return;
  var items = document.querySelectorAll('[data-author]');
  var groups = document.querySelectorAll('.group');
  var out = document.querySelector('[data-showing]');
  function apply(f) {
    var n = 0;
    tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t.dataset.filter === f)); });
    items.forEach(function (el) {
      var show = f === 'all' || el.dataset.author === f;
      el.hidden = !show;
      if (show) n++;
    });
    groups.forEach(function (g) { g.hidden = !g.querySelector('[data-author]:not([hidden])'); });
    if (out) out.textContent = n + (n === 1 ? ' title' : ' titles');
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { apply(t.dataset.filter); }); });
  var start = (location.hash || '').replace('#', '');
  apply(document.querySelector('.tab[data-filter="' + start + '"]') ? start : 'all');
})();
