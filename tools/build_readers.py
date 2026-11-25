"""Reader pages (email list, one per book) and the privacy policy.

    python tools/build_readers.py        (build_site.py calls it)

KDP rules (2026-11-23): the book itself never links to a sign-up form and never promises a gift. These pages
live on the website only and are reached from the author pages and the journal. The resource is always pages
that are already inside the book (checked against the live interior), never new content.
The form is Brevo's hosted form with double opt-in, kept in tools/forms/<slug>.html; until that file exists,
the page says sign-up is not open yet, is noindex, and is neither linked nor listed in the sitemap.
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

HEALTH_NOTE = "They are not medical advice and don't replace care from your doctor."
NUM = {4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight"}


def form(slug):
    """Brevo form block for this page (only the Begin/End Brevo Form markup), or "" while sign-up is not open."""
    f = ROOT / "tools" / "forms" / f"{slug}.html"
    return f.read_text(encoding="utf-8") if f.exists() else ""


# Each sheet is one or two pages of the live interior, copied unchanged into the PDF by
# "KDP - Amazon KDP/scripts/readers_printables.py" (same pages, same order). Wording taken from each page.
READERS = {
    "brain-fog": {
        "author": "claire-harmon", "kind": "workbook", "note": HEALTH_NOTE,
        "book": "The Perimenopause Brain Fog Workbook",
        "asin": "B0HSLXYB6S",
        "sheets": [  # live interior candidate-2026-11-20d, checked 2026-11-23 (p. 18, 31, 113, 116, 142, 143)
            ("The Lapse Tally", "Fill in one circle each time a lapse happens; on Day 7, see which column filled up fastest."),
            ("Your Four-Week Fog Calendar", "Shade one circle each evening for a clear, foggy or heavy-fog day. Nothing resets."),
            ("When Did It Start?", "Mark the last twelve months for brain fog, cycle changes and hot flashes, before your appointment."),
            ("Take This Page With You", "Your clean one-page summary to bring to your doctor and read from."),
            ("My Green / Yellow / Red Plan Sheet", "Your plan for any kind of day, to put where you'll see it on a Red day."),
            ("Counting Days, Not Streaks", "Color one light a day and count your Green days at the end of the month."),
        ],
    },
    "perimenopause-anxiety": {
        "author": "claire-harmon", "kind": "workbook", "note": HEALTH_NOTE,
        "book": "Perimenopause Anxiety Workbook",
        "asin": "B0HQFBDRF9",
        "sheets": [  # interior candidate-2026-11-20 (p. 46-47, 51-52, 106, 170-171, 174-175, 221-222)
            ("Your 7-Day Anxiety Intensity Log", "Seven days of same-day notes: intensity, time of day, your profile and the trigger or context."),
            ("Two-Week Three-Point Tracker", "Rate sleep, mood and energy from 1 to 5 each day. The whole entry should take less than 90 seconds."),
            ("6-Week Practice Tracker", "Mark each day you use your chosen tool. Six weeks of daily practice gives a tool a fair trial."),
            ("The Evidence Courtroom", "Argue for one anxious belief, then against it, using only actual evidence, and end with a more balanced version."),
            ("The Perimenopause Thought Record", "Trigger, automatic thought, emotion, evidence for and against, and a more balanced version of the thought."),
            ("My Appointment Preparation Sheet", "Fill it in 24 to 48 hours before your visit: your three questions, the tests to ask about and your goal."),
        ],
    },
    "vagus-nerve": {
        "author": "maya-chen", "kind": "workbook", "note": HEALTH_NOTE,
        "book": "Vagus Nerve Exercises for Anxiety",
        "asin": "B0H19KD54V",
        "sheets": [  # interior candidate-2026-11-20c (p. 25-26, 36, 47, 161-162, 166, 186)
            ("The Nervous System Check-In", "A daily 60-second inventory: where you felt activation, where you felt ease, and which state you're in right now."),
            ("My Nervous System This Week", "A lined page for what you noticed in your body this week."),
            ("The Three States at a Glance", "Ventral vagal, sympathetic and dorsal vagal on one page, to recognize the state you're in."),
            ("28-Day Tracking Log", "Record your daily anxiety rating from 0 to 5. Review it weekly, not daily."),
            ("The Minimum Viable Dose", "For the hardest days: three physiological sighs in the morning and two minutes of humming before sleep."),
            ("Orient, Regulate, Reanchor", "The three-step sequence for an anxiety spike, to memorize before anything else."),
        ],
    },
    "healing-bible-study": {
        "author": "hannah-grace", "kind": "Bible study", "note": "",
        "book": "Healing Bible Study for Women",
        "asin": "B0H17PD38W",
        "sheets": [  # interior candidate-2026-11-20b (p. 28-29, 69, 103-104, 154-155, 184-185, 200)
            ("Your Written Lament", "Write your own lament in four movements: Remember, Acknowledge, Hope, Choose."),
            ("Building Your Healing Declaration", "The lie you are taking captive this week, the Scripture truth that answers it, and your declaration."),
            ("The Seven-Day Healing Covenant Prayer", "Seven days, seven passages, a prayer prompt for each day. Set aside 15 to 20 minutes a day."),
            ("The Four Chambers: A Personal Forgiveness Inventory", "One chamber at a time. You may not complete all four today, and that's expected."),
            ("Mapping Your Section of the Wall", "Name three areas of your inner life where the wall feels most broken right now."),
            ("Your Assigned Section This Week", "One section and one specific action for the coming week: the day, the time and what it will look like."),
        ],
    },
    "prayer-journal": {
        "author": "hannah-grace", "kind": "journal", "note": "",
        "book": "Daily Prayer Journal for Women",
        "asin": "B0HSBT636V",
        "sheets": [  # interior candidate-2026-11-21 (p. 6, 9, 12, 13-14, 15, 64-65)
            ("Four Simple Ways to Pray", "Praise, lay down, ask, thank; pray the verse; pray the Lord's Prayer line by line; or just say the name."),
            ("People I'm Carrying in Prayer", "Names and needs to keep in front of you all year, with the date you started and a box for when God answers."),
            ("Read, Notice, Pray, Live It", "The first week's practice: an old, slow way of reading Scripture, step by step."),
            ("The Daily Pages", "Six days of the daily page: what I praise You for, what I'm laying down, what I'm asking, thank You for."),
            ("Where Was God This Week?", "The seventh-day look back: the days you prayed, where you noticed God, prayers answered and still waiting."),
            ("Looking Back", "The pages that close each part: the week that meant the most, a prayer God answered, a prayer for the weeks ahead."),
        ],
    },
    "scripture-journal": {
        "author": "hannah-grace", "kind": "journal", "note": "",
        "book": "Scripture Journal for Women",
        "asin": "B0HSFNZ2NM",
        "sheets": [  # interior candidate-2026-11-20 (p. 8, 10, 11, 14, 16, 27); reflection pages carry Part 1's questions
            ("My Scripture Writing Tracker", "Shade or check a square each time you finish a passage. The numbers match the passages in the book."),
            ("Write It Out", "Copy the passage slowly, word for word (the book's first passage, Exodus 34:6)."),
            ("Make It Personal", "In my own words, where I need this right now, going deeper, and a short prayer."),
            ("Hide It in My Heart", "Write it again from memory. Peek if you need to. Memory grows by trying."),
            ("Look Closer", "The word that stopped me, what it shows me about God, praying it back, and one way to live it today."),
            ("Looking Back", "The passage you want to memorize, what changed in how you see God, and a prayer to close the part."),
        ],
    },
}


def readers_page(slug, r):
    a = bs.AUTHORS[r["author"]]
    sheets = "".join(f'<li><b>{e(t)}</b><span>{e(d)}</span></li>' for t, d in r["sheets"])
    n = NUM.get(len(r["sheets"]), str(len(r["sheets"])))
    form_html = form(slug)
    if form_html:
        form_block = f'''<div class="readers-form">{form_html}
  <p class="muted small">We'll send a confirmation email first. You only join after you click it, and every email has a one-click unsubscribe. See our <a href="/privacy.html">privacy policy</a>.</p></div>'''
    else:
        form_block = '<div class="readers-form"><p class="muted">Sign-up opens soon.</p></div>'
    body = f'''<section class="page-head"><div class="wrap">
  <p class="eyebrow">From {e(a["name"])}'s {e(r["kind"])}</p>
  <h1>Print fresh copies of the pages <em>you use most.</em></h1>
  <p class="lede">{n} pages from <i>{e(r["book"])}</i>, ready to print, for the sheets you fill in again and again. Leave your email and we'll send them to you, along with a note when {e(a["short"])} publishes a new book.</p>
</div></section>
<section class="sec sec-top0"><div class="wrap readers-grid">
  <div><h2 class="h2">What's in the printable</h2><ul class="readers-list">{sheets}</ul>
  <p class="muted small">These are the same pages that are in the book, so you can keep using them after the book is full. {e(r["note"])}</p></div>
  <div>{form_block}
  <p class="muted small">Don't have the book yet? <a href="https://www.amazon.com/dp/{r["asin"]}">See it on Amazon</a>.</p></div>
</div></section>'''
    out = ROOT / "readers" / slug
    out.mkdir(parents=True, exist_ok=True)
    html_ = bs.page(f'Printable pages from {r["book"]} | Bloom Editorial', f'{n} printable pages from {r["book"]} by {a["name"]}.', f"/readers/{slug}/", body)
    if not form_html:
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
  <p class="lede">Thank you for being here. Your printable pages from <i>{e(r["book"])}</i> are ready below, and a copy of the link is in your inbox too. Print them whenever you need a fresh sheet.</p>
  {f'<p><a class="btn" href="{link}">Download the printable pages (PDF)</a></p>' if link else ''}
  <aside class="review-card" aria-labelledby="review-card-h">
    <p class="eyebrow">One small favor</p>
    <h2 id="review-card-h">Has the book helped you?</h2>
    <p>An honest rating, or one sentence about what you used most, helps another woman find <i>{e(r["book"])}</i> when she needs it.</p>
    <p><a class="btn" href="https://www.amazon.com/review/create-review?asin={r["asin"]}" rel="noopener" target="_blank">Rate the book on Amazon<span class="sr"> (opens in a new tab)</span></a></p>
    <p class="review-card-note">It's never required. Your pages are yours either way.</p>
  </aside>
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
