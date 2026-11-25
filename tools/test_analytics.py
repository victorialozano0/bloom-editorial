"""End-to-end test of assets/analytics.js on the built site.

Serves the repository locally, opens real pages in a headless browser, clicks the Amazon links a reader
would click and checks the events that would be sent. Amazon is never contacted: those requests are blocked.

Usage:  python tools/test_analytics.py          (exit code 1 if any check fails)
Run it after every change to analytics.js or to the article template, and before publishing.
"""
import functools
import re
import http.server
import pathlib
import sys
import threading

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8791
fails: list[str] = []


def check(ok: bool, msg: str) -> None:
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok:
        fails.append(msg)


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def events(page):
    return page.evaluate("window.__bloomEvents")


def main() -> int:
    srv = serve()
    base = f"http://127.0.0.1:{PORT}"
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 900})
        ctx.route("**/*amazon.*/**", lambda r: r.abort())          # never reach Amazon from a test
        ctx.route("**/cloud.umami.is/**", lambda r: r.abort())

        def new_page():
            pg = ctx.new_page()
            pg.on("popup", lambda pop: pop.close())                 # Amazon links open a new tab: close it at once
            return pg

        # 1) article reached from a Pinterest link: clicks in the text, in the book box and on the review link
        page = new_page()
        sent = []
        page.add_init_script("window.umami = { track: function (n, d) { (window.__sent = window.__sent || []).push({ name: n, data: d }); } };")
        page.goto(base + "/journal/physiological-sigh.html?utm_source=Pinterest&utm_medium=organic", wait_until="load")
        print("article page")
        check(page.evaluate("typeof window.bloomTrack") == "function", "analytics.js loaded on the article page")
        cfg = re.search(r"umamiId: '([^']*)'", (ROOT / "assets" / "analytics.js").read_text(encoding="utf-8")).group(1)
        got = page.evaluate("document.querySelector('script[src*=\"umami\"]')?.getAttribute('data-website-id') || ''")
        check(got == cfg, f"provider script present only with the configured website ID ({cfg or 'none'})")
        check(page.evaluate("document.cookie") == "", "no cookies set")
        check(page.evaluate("localStorage.length + sessionStorage.length") == 0, "nothing written to local or session storage")
        amazon = page.locator("a[href*='amazon.com/dp/']")
        check(amazon.count() >= 2, f"article has Amazon links in the text and in the book box ({amazon.count()})")
        check(page.evaluate("[...document.querySelectorAll('a[href*=\"amazon.\"]')].every(a => a.target === '_blank' && a.rel.includes('noopener'))"),
              "every Amazon link opens in a new tab with rel=noopener")
        in_text = page.locator(".article-body a[href*='amazon.com/dp/']").first
        in_text.scroll_into_view_if_needed(); in_text.click(); page.wait_for_timeout(400)
        box = page.locator(".side-book a[href*='amazon.com/dp/']").first
        box.scroll_into_view_if_needed(); box.click(); page.wait_for_timeout(400)
        review = page.locator(".side-book a[href*='create-review']").first
        if review.count():
            review.scroll_into_view_if_needed(); review.click(); page.wait_for_timeout(400)
        ev = events(page)
        clicks = [e for e in ev if e["name"] == "amazon-click"]
        places = [e["data"]["placement"] for e in clicks]
        check("in-text" in places, f"click in the text recorded as in-text ({places})")
        check("book-box" in places, "click in the book box recorded as book-box")
        check((not review.count()) or "review-link" in places, "click on the review link recorded as review-link")
        check(all(len(e["data"]["asin"]) == 10 for e in clicks), f"every click carries a 10-character ASIN ({[e['data']['asin'] for e in clicks]})")
        check(all(e["data"]["page"] == "/journal/physiological-sigh.html" for e in clicks), "every click carries the page path")
        check(all(e["data"]["source"] == "pinterest" for e in clicks), "source is read from utm_source (pinterest)")
        check(any(e["name"] == "article-read" for e in ev), "article-read fires when the end of the article is reached")
        check(len(page.evaluate("window.__sent || []")) == len(ev), "every event is forwarded to the provider when it is present")
        page.close()

        # 2) a short visit that does not scroll must not count as a read
        page = new_page()
        page.goto(base + "/journal/evening-extended-exhale.html", wait_until="load"); page.wait_for_timeout(600)
        print("short visit")
        check(not any(e["name"] == "article-read" for e in events(page)), "no article-read without reaching the end")
        check(events(page) == [], "no events at all without interaction")
        page.close()

        # 3) the other page types load the script and track their Amazon links
        for path in ("/", "/authors/maya-chen.html", "/peek-inside.html", "/journal/"):
            page = new_page()
            page.goto(base + path, wait_until="load")
            print(path)
            check(page.evaluate("typeof window.bloomTrack") == "function", "analytics.js loaded")
            link = page.locator("a[href*='amazon.com/dp/']").first
            if link.count():
                link.scroll_into_view_if_needed(); link.click(force=True); page.wait_for_timeout(400)
                c = [e for e in events(page) if e["name"] == "amazon-click"]
                check(len(c) == 1 and c[0]["data"]["source"] == "direct", "Amazon click recorded with source=direct")
            page.close()

        # 4) a visitor with Do Not Track never loads the provider, even once it is configured
        page = new_page()
        page.add_init_script("Object.defineProperty(navigator, 'doNotTrack', { get: () => '1' });")
        js = re.sub(r"umamiId: '[^']*'", "umamiId: 'test-id'", (ROOT / "assets" / "analytics.js").read_text(encoding="utf-8"))
        page.route("**/assets/analytics.js", lambda r: r.fulfill(body=js, content_type="application/javascript"))
        page.goto(base + "/journal/physiological-sigh.html", wait_until="load")
        print("do not track")
        check(page.evaluate("document.querySelectorAll('script[src*=\"umami\"]').length") == 0, "provider script not injected for a Do Not Track visitor")
        page.close()
        page = new_page()
        page.route("**/assets/analytics.js", lambda r: r.fulfill(body=js, content_type="application/javascript"))
        page.goto(base + "/journal/physiological-sigh.html", wait_until="load")
        print("provider configured")
        check(page.evaluate("document.querySelector('script[src*=\"umami\"]')?.getAttribute('data-website-id')") == "test-id", "provider script injected with the website ID once configured")
        page.close()
        b.close()
    srv.shutdown()
    print(f"\n{'ALL CHECKS PASS' if not fails else str(len(fails)) + ' CHECK(S) FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
