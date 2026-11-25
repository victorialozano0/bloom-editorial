// Bloom Editorial analytics. Counts page views and clicks to Amazon without cookies, local storage or personal data.
// Provider: Umami Cloud (cookieless). It only loads when umamiId is set; until then the click handler runs
// and keeps events in window.__bloomEvents, which is what the tests read.
(function () {
  var CFG = {
    umamiId: '000a5d47-04d4-442b-9d14-f32586ef14d7',   // Umami Cloud website ID (given by the site owner, 2026-11-23)
    src: 'https://cloud.umami.is/script.js'
  };

  var events = (window.__bloomEvents = []);

  function track(name, data) {
    events.push({ name: name, data: data });
    try {
      if (window.umami && typeof window.umami.track === 'function') window.umami.track(name, data);
    } catch (e) { /* analytics must never break the page */ }
  }
  window.bloomTrack = track;

  // Respect Do Not Track / Global Privacy Control: no provider script at all for those visitors.
  var optedOut = navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true;
  if (CFG.umamiId && !optedOut) {
    var s = document.createElement('script');
    s.defer = true;
    s.src = CFG.src;
    s.setAttribute('data-website-id', CFG.umamiId);
    s.setAttribute('data-do-not-track', 'true');
    document.head.appendChild(s);
  }

  function isAmazon(href) { return /^https?:\/\/([a-z0-9-]+\.)*(amazon\.[a-z.]+|a\.co|amzn\.to)\//i.test(href); }

  function placement(a) {
    if (/create-review/.test(a.href)) return 'review-link';
    if (a.closest('.side-book')) return 'book-box';
    if (a.closest('.article-body')) return 'in-text';
    if (a.closest('.article-pin')) return 'pin-image';
    if (a.closest('.foot')) return 'footer';
    return 'page';
  }

  // Where this page view came from: the utm_source of the landing URL, or the referring site. Nothing is stored.
  function source() {
    var m = /[?&]utm_source=([^&#]+)/i.exec(location.search);
    if (m) return decodeURIComponent(m[1]).toLowerCase();
    try {
      if (document.referrer) {
        var h = new URL(document.referrer).hostname;
        return h === location.hostname ? 'internal' : h.replace(/^www\./, '');
      }
    } catch (e) { /* ignore */ }
    return 'direct';
  }

  // Amazon links open in a new tab, so the reader keeps the article and the click event is not cut short.
  document.querySelectorAll('a[href]').forEach(function (a) {
    if (isAmazon(a.href) && !a.target) { a.target = '_blank'; a.rel = 'noopener'; }
  });

  function onClick(e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    if (isAmazon(a.href)) {
      var m = /(?:\/dp\/|\/gp\/product\/|asin=)([A-Z0-9]{10})/.exec(a.href);
      track('amazon-click', { asin: m ? m[1] : '', page: location.pathname, placement: placement(a), source: source() });
    } else if (a.hostname && a.hostname !== location.hostname && /^https?:$/.test(a.protocol)) {
      track('outbound-click', { host: a.hostname.replace(/^www\./, ''), page: location.pathname });
    }
  }
  document.addEventListener('click', onClick, true);
  document.addEventListener('auxclick', function (e) { if (e.button === 1) onClick(e); }, true);   // middle click

  // One "article-read" event when the reader reaches the end of the article body (not on short visits).
  // Counted once the end of the text is on screen or already above it, so a jump past it (a click on the book box,
  // a fast flick on a phone) still counts; a visit that never gets there does not.
  var body = document.querySelector('.article-body');
  if (body) {
    var end = document.createElement('span');
    end.setAttribute('aria-hidden', 'true');
    body.appendChild(end);
    var read = false, queued = false;
    function checkRead() {
      queued = false;
      if (read) return;
      if (end.getBoundingClientRect().top < window.innerHeight) {
        read = true;
        track('article-read', { page: location.pathname, source: source() });
        window.removeEventListener('scroll', onScroll);
      }
    }
    function onScroll() { if (!queued) { queued = true; window.requestAnimationFrame(checkRead); } }
    window.addEventListener('scroll', onScroll, { passive: true });
  }
})();
