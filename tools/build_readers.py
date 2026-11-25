"""Reader pages (email list, one per book) and the privacy policy.

    python tools/build_readers.py        (build_site.py calls it)

KDP rules (2026-11-23): the book itself never links to a sign-up form and never promises a gift. These pages
live on the website only and are reached from the author pages and the journal. The resource is always pages
that are already inside the book (checked against the live interior), never new content.
The form is Brevo's hosted form with double opt-in; until FORM_HTML is filled in, the page says sign-up is
not open yet and is not listed in the sitemap.
"""
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as bs  # noqa: E402

ROOT = bs.ROOT
e = html.escape

# Legal identity for the privacy policy (GDPR Art. 13). Filled in from the site owner; empty = page not built.
CONTROLLER = "Libo and Bloom Editorial are trade names of Victoria Lozano"
CONTACT = "bloom@liboprint.com"
UPDATED = "November 23, 2026"

READERS = {
    "brain-fog": {
        "author": "claire-harmon",
        "book": "The Perimenopause Brain Fog Workbook",
        "asin": "B0HSLXYB6S",
        "sheets": [  # each one is a page of the live interior (candidate-2026-11-20d, checked 2026-11-23)
            # wording taken from each page (p. 18, 31, 113, 116, 142, 143)
            ("The Lapse Tally", "Fill in one circle each time a lapse happens; on Day 7, see which column filled up fastest."),
            ("Your Four-Week Fog Calendar", "Shade one circle each evening for a clear, foggy or heavy-fog day. Nothing resets."),
            ("When Did It Start?", "Mark the last twelve months for brain fog, cycle changes and hot flashes, before your appointment."),
            ("Take This Page With You", "Your clean one-page summary to bring to your doctor and read from."),
            ("My Green / Yellow / Red Plan Sheet", "Your plan for any kind of day, to put where you'll see it on a Red day."),
            ("Counting Days, Not Streaks", "Color one light a day and count your Green days at the end of the month."),
        ],
        "form_html": (ROOT / "tools" / "forms" / "brain-fog.html").read_text(encoding="utf-8"),  # Brevo form "Brain Fog printable pages" (double opt-in)
    },
}


def readers_page(slug, r):
    a = bs.AUTHORS[r["author"]]
    sheets = "".join(f'<li><b>{e(t)}</b><span>{e(d)}</span></li>' for t, d in r["sheets"])
    if r["form_html"]:
        form = f'''<div class="readers-form">{r["form_html"]}
  <p class="muted small">We'll send a confirmation email first. You only join after you click it, and every email has a one-click unsubscribe. See our <a href="/privacy.html">privacy policy</a>.</p></div>'''
    else:
        form = '<div class="readers-form"><p class="muted">Sign-up opens soon.</p></div>'
    body = f'''<section class="page-head"><div class="wrap">
  <p class="eyebrow">From {e(a["name"])}'s workbook</p>
  <h1>Print fresh copies of the pages <em>you use most.</em></h1>
  <p class="lede">Six pages from <i>{e(r["book"])}</i>, ready to print, for the sheets you fill in again and again. Leave your email and we'll send them to you, along with a note when {e(a["short"])} publishes a new book.</p>
</div></section>
<section class="sec sec-top0"><div class="wrap readers-grid">
  <div><h2 class="h2">What's in the printable</h2><ul class="readers-list">{sheets}</ul>
  <p class="muted small">These are the same pages that are in the book, so you can keep using them after the book is full. They are not medical advice and don't replace care from your doctor.</p></div>
  <div>{form}
  <p class="muted small">Don't have the book yet? <a href="https://www.amazon.com/dp/{r["asin"]}">See it on Amazon</a>.</p></div>
</div></section>'''
    out = ROOT / "readers" / slug
    out.mkdir(parents=True, exist_ok=True)
    html_ = bs.page(f'Printable pages from {r["book"]} | Bloom Editorial', f'Six printable pages from {r["book"]} by {a["name"]}.', f"/readers/{slug}/", body)
    if not r["form_html"]:
        html_ = html_.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
    (out / "index.html").write_text(html_, encoding="utf-8")


def thanks_page(slug, r):
    """Where Brevo sends readers after they click the confirmation link (double opt-in)."""
    a = bs.AUTHORS[r["author"]]
    files = sorted((ROOT / "readers" / slug / "files").glob("*.pdf"))
    link = f'/readers/{slug}/files/{files[-1].name}' if files else ""
    body = f'''<section class="page-head"><div class="wrap">
  <p class="eyebrow">You're in</p>
  <h1>Your pages are <em>on their way.</em></h1>
  <p class="lede">Thank you for confirming. The email with your printable pages from <i>{e(r["book"])}</i> should arrive in a minute or two. If you'd rather not wait, here they are.</p>
  {f'<p><a class="btn" href="{link}">Download the printable pages (PDF)</a></p>' if link else ''}
  <p class="muted small">Can't find the email? Check your spam or promotions folder. It comes from Bloom Editorial, bloom@liboprint.com.</p>
  <p><a class="textlink" href="/authors/{r["author"]}.html">More from {e(a["short"])} &rarr;</a></p>
</div></section>'''
    out = ROOT / "readers" / slug / "thanks"
    out.mkdir(parents=True, exist_ok=True)
    html_ = bs.page("Thank you | Bloom Editorial", "Your printable pages are on their way.", f"/readers/{slug}/thanks/", body)
    (out / "index.html").write_text(html_.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1), encoding="utf-8")


def privacy_page():
    body = f'''<section class="page-head"><div class="wrap"><p class="eyebrow">Privacy</p><h1>Privacy policy</h1><p class="lede">Last updated: {UPDATED}</p></div></section>
<section class="sec sec-top0"><div class="wrap prose">
<h2>Who we are</h2>
<p>This website belongs to Bloom Editorial, an imprint of Libo, an independent publisher of workbooks and guided journals. {e(CONTROLLER)}. She is responsible for your data and can be reached at <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
<h2>What we collect and why</h2>
<p><b>Our email list.</b> If you ask for printable pages from one of our books, we collect your email address and, if you choose to give it, your first name. We use them to send you the pages you asked for, news about new books from the same author, and occasional invitations to read a new book before it is published. The legal basis is your consent (GDPR Art. 6(1)(a)), which you give by submitting the form and confirming by email (double opt-in).</p>
<p><b>Visits.</b> We count visits and clicks with Umami, which does not use cookies and does not collect personal data. Our host processes technical data such as your IP address to deliver the website and keep it secure (legitimate interest, GDPR Art. 6(1)(f)). Fonts and icons are served from this website, not from third parties.</p>
<p>We do not use advertising cookies or tracking pixels, and we never sell or rent your data.</p>
<h2>Who processes data for us</h2>
<ul><li>Brevo (Sendinblue SAS, France): stores the email list, sends our emails and serves the sign-up form.</li>
<li>GitHub, Inc. (USA): hosts this website.</li>
<li>Umami Software, Inc.: cookieless visit statistics.</li></ul>
<p>Transfers to the USA are covered by the EU-US Data Privacy Framework and/or Standard Contractual Clauses.</p>
<h2>How long we keep it</h2>
<p>Until you unsubscribe or ask us to delete it. Sign-ups that are never confirmed are deleted within 30 days.</p>
<h2>Your rights</h2>
<p>You can access, correct or delete your data, restrict or object to its use, ask for a copy, and withdraw your consent at any time. Every email has a one-click unsubscribe link. Write to <a href="mailto:{CONTACT}">{CONTACT}</a> to use these rights. If you are not satisfied, you can complain to your data protection authority.</p>
<h2>Children</h2>
<p>Our email list is for adults. We do not knowingly collect data from anyone under 16.</p>
<h2>Reviews</h2>
<p>We never ask for a review in exchange for anything, and receiving our emails never depends on leaving one.</p>
<h2>Changes</h2>
<p>If this policy changes, we will update the date above and, for important changes, tell subscribers by email.</p>
</div></section>'''
    (ROOT / "privacy.html").write_text(bs.page("Privacy policy | Bloom Editorial", "How Bloom Editorial handles your data.", "/privacy.html", body), encoding="utf-8")


def main():
    for slug, r in READERS.items():
        readers_page(slug, r)
        thanks_page(slug, r)
    if CONTROLLER:
        privacy_page()
    print(f"reader pages: {', '.join(READERS)}; privacy: {'built' if CONTROLLER else 'waiting for the controller name'}")


if __name__ == "__main__":
    main()
