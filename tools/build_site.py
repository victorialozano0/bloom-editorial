"""Build the Bloom Editorial journal, article pages and author pages from content/journal/*.json.

Usage (from the repo root):  python tools/build_site.py
Writes: journal/index.html, journal/<slug>.html, authors/<id>.html, authors.html,
and refreshes the shared nav + "From the journal" block in index.html (between markers).
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700"
         "&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap")
SITE = "https://bloomeditorial.netlify.app"

AUTHORS = {
    "hannah-grace": {
        "name": "Hannah Grace", "short": "Hannah", "season": "Faith & healing", "panel": "p-rose",
        "emblem": "olive.webp", "ew": 360, "eh": 691,
        "tagline": "Bible studies for women in hard seasons.",
        "bio": "Scripture-based studies for women carrying something heavy: grief, anxiety, betrayal, the quiet ache of feeling unseen. Pastoral without being preachy. Built to be worked through with a pen, not just read.",
        "books": [{"title": "Healing Bible Study for Women", "cover": "healing-bible-study-for-women", "ch": 768,
                   "dek": "A 6-week, Scripture-based journey to restore your broken heart and renew your mind.",
                   "links": [("Paperback", "B0H17PD38W"), ("Kindle", "B0H18ZX2SX")]}],
        "planned": ["Daily Prayer Journal for Women", "Scripture Journal for Women: Write the Word", "Anxiety and Faith",
                    "Psalms for the Brokenhearted", "A Bible Study for Women in Grief", "Proverbs for Women", "Walking Through Fire"],
    },
    "maya-chen": {
        "name": "Maya Chen", "short": "Maya", "season": "Anxiety & nervous system", "panel": "p-mint",
        "emblem": "tree.webp", "ew": 360, "eh": 361,
        "tagline": "Somatic healing for a nervous system that learned to brace.",
        "bio": "Short, guided vagus nerve and somatic practices, with the science explained in plain language. Books for the bedside table, made to be used on the hard days.",
        "books": [{"title": "Vagus Nerve Exercises for Anxiety", "cover": "vagus-nerve-exercises-for-anxiety", "ch": 768,
                   "dek": "A 10-minute daily reset with step-by-step practices you can actually do.",
                   "links": [("Paperback", "B0H19KD54V"), ("Kindle", "B0H19DC7YS"), ("Hardcover", "B0H19KSCRL")]}],
        "planned": ["My Nervous System Tracker", "The Vagus Nerve Practice Journal", "Somatic Healing for Trauma",
                    "The Nervous System Reset", "Polyvagal Exercises for Beginners", "Somatic Healing for Women", "Heal Your Nervous System"],
    },
    "clara-bennett": {
        "name": "Clara Bennett", "short": "Clara", "season": "Grief & remembering Mom", "panel": "p-sand",
        "emblem": "forget.webp", "ew": 360, "eh": 345,
        "tagline": "Journals and keepsakes for daughters who lost their mother.",
        "bio": "Grief that doesn't follow a timeline or a rulebook. Clara's journals are not about getting over it. They are about carrying it, honoring her, and keeping her close on the anniversaries and the ordinary days.",
        "books": [],
        "planned": ["Grief Journal for the Loss of a Mother", "Mom's Kitchen: A Recipe Memory Book", "My Mother, My Heart",
                    "A Mother's Legacy", "Dear Mom: Letters I Never Got to Send", "A Year Without Mom",
                    "Healing After Losing Your Mother", "The Grief Companion"],
    },
    "claire-harmon": {
        "name": "Claire Harmon", "short": "Claire", "season": "Perimenopause", "panel": "p-lilac",
        "emblem": "lavender.webp", "ew": 360, "eh": 429,
        "tagline": "The emotional side of perimenopause, finally named.",
        "bio": "Workbooks for the anxiety, brain fog, broken sleep and rage that can arrive with perimenopause. Plain language, practical tools, zero shame.",
        "books": [{"title": "Perimenopause Anxiety Workbook", "cover": "perimenopause-anxiety-workbook", "ch": 720,
                   "dek": "A 30-day guided workbook with trackers and 10-minute calm strategies.", "links": []}],
        "planned": ["My Perimenopause Journal", "Perimenopause Daily Symptom Tracker", "The Perimenopause Brain Fog Workbook",
                    "Sleep Through Perimenopause", "The HRT Decision Workbook", "Perimenopause Mood & Rage Workbook",
                    "The Complete Perimenopause Workbook"],
    },
}
ORDER = list(AUTHORS)
e = html.escape


def nav():
    items = "".join(f'<li><a href="/authors/{a}.html"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true">'
                    f'<span><b>{e(d["name"])}</b>{e(d["season"])}</span></a></li>' for a, d in AUTHORS.items())
    return f'''<header class="nav">
  <div class="wrap nav-in">
    <a class="logo" href="/"><img src="/img/botanical/olive.webp" width="18" height="35" alt="" aria-hidden="true">bloom editorial</a>
    <nav aria-label="Main" class="main-nav" id="main-nav">
      <ul class="nav-list">
        <li><a href="/journal/">Journal</a></li>
        <li class="dd">
          <button type="button" class="dd-btn" aria-expanded="false" aria-controls="dd-authors">Authors <i class="ph ph-caret-down" aria-hidden="true"></i></button>
          <ul class="dd-menu" id="dd-authors">{items}</ul>
        </li>
        <li><a href="/#inside">Look inside</a></li>
        <li><a href="/#books">The books</a></li>
      </ul>
    </nav>
    <a class="btn btn-sm nav-cta" href="/#books">Browse the books</a>
    <button type="button" class="menu-btn" aria-expanded="false" aria-controls="main-nav" aria-label="Open menu"><i class="ph ph-list" aria-hidden="true"></i></button>
  </div>
</header>'''


def foot():
    links = "".join(f'<li><a href="/authors/{a}.html">{e(d["name"])}</a></li>' for a, d in AUTHORS.items())
    return f'''<footer class="foot">
  <div class="wrap foot-in">
    <a class="logo" href="/"><img src="/img/botanical/olive.webp" width="18" height="35" alt="" aria-hidden="true">bloom editorial</a>
    <ul aria-label="Explore"><li><a href="/journal/">Journal</a></li>{links}</ul>
    <p class="legal">&copy; <span data-year>2026</span> Bloom Editorial. Our books support, but never replace, care from a doctor or licensed therapist.</p>
  </div>
</footer>'''


def page(title, desc, canonical, body):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#faf8f4">
<link rel="canonical" href="{SITE}{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/img/og-bloom-launch.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">
<link rel="stylesheet" href="/assets/bloom.css">
<script>document.documentElement.classList.add('js')</script>
</head>
<body class="inner">
<a class="skip" href="#main">Skip to content</a>
{nav()}
<main id="main">
{body}
</main>
{foot()}
<script src="/assets/bloom.js" defer></script>
</body>
</html>
'''


def card(a, big=False):
    d = AUTHORS[a["author"]]
    cls = "jcard jcard-big" if big else "jcard"
    return f'''<a class="{cls} rv" href="/journal/{a["slug"]}.html" data-author="{a["author"]}">
  <span class="jcard-top {d["panel"]}"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true" loading="lazy"><q>{e(a["pull_quote"])}</q></span>
  <span class="jcard-body"><span class="jcard-meta">{e(d["name"])} &middot; {a["read_minutes"]} min read</span>
  <strong>{e(a["title"])}</strong><span class="jcard-dek">{e(a["dek"])}</span></span>
</a>'''


def book_block(b):
    links = "".join(f'<a href="https://www.amazon.com/dp/{asin}" rel="noopener" target="_blank">{fmt}<span class="sr"> on Amazon (opens in a new tab)</span></a>'
                    for fmt, asin in b["links"])
    buy = f'<p class="formats">{links}</p>' if links else '<p class="soon">Coming soon</p>'
    return f'''<div class="side-book"><img src="/img/{b["cover"]}-480.webp" width="480" height="{b["ch"]}" alt="Cover of {e(b["title"])}" loading="lazy">
  <div><p class="eyebrow">The book</p><h3>{e(b["title"])}</h3><p class="muted">{e(b["dek"])}</p>{buy}</div></div>'''


def build():
    arts = []
    for f in sorted((ROOT / "content" / "journal").glob("*.json")):
        arts += json.loads(f.read_text(encoding="utf-8"))
    for a in arts:
        assert a["author"] in AUTHORS, a["author"]
        assert "—" not in json.dumps(a, ensure_ascii=False) and "–" not in json.dumps(a, ensure_ascii=False), a["slug"]
    # interleave authors so lists feel varied
    by = {k: [x for x in arts if x["author"] == k] for k in ORDER}
    mixed = []
    for i in range(max(len(v) for v in by.values())):
        mixed += [by[k][i] for k in ORDER if i < len(by[k])]

    (ROOT / "journal").mkdir(exist_ok=True)
    # article pages
    for a in mixed:
        d = AUTHORS[a["author"]]
        more = [x for x in mixed if x["slug"] != a["slug"]]
        more = [x for x in more if x["author"] == a["author"]][:1] + [x for x in more if x["author"] != a["author"]][:2]
        book = book_block(d["books"][0]) if d["books"] else ""
        body = f'''<article class="article">
  <header class="article-head wrap">
    <p class="crumbs"><a href="/journal/">Journal</a> <span aria-hidden="true">/</span> <a href="/authors/{a["author"]}.html">{e(d["name"])}</a></p>
    <h1>{e(a["title"])}</h1>
    <p class="article-dek">{e(a["dek"])}</p>
    <p class="byline"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true"><span>By <a href="/authors/{a["author"]}.html">{e(d["name"])}</a> &middot; {a["read_minutes"]} min read</span></p>
  </header>
  <div class="article-hero {d["panel"]}"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true"></div>
  <div class="article-body wrap">{a["body_html"]}</div>
  <aside class="article-end wrap">
    <div class="author-box"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true"><div><p class="eyebrow">About the author</p><h3>{e(d["name"])}</h3><p class="muted">{e(d["bio"])}</p><a class="textlink" href="/authors/{a["author"]}.html">More from {e(d["short"])} &rarr;</a></div></div>
    {book}
  </aside>
</article>
<section class="sec"><div class="wrap"><h2 class="h2">Keep reading</h2><div class="jgrid">{"".join(card(x) for x in more)}</div></div></section>'''
        (ROOT / "journal" / f'{a["slug"]}.html').write_text(page(f'{a["title"]} | Bloom Editorial Journal', a["dek"], f'/journal/{a["slug"]}.html', body), encoding="utf-8")

    # journal index
    pills = '<button type="button" class="jpill" aria-pressed="true" data-filter="all">All</button>' + "".join(
        f'<button type="button" class="jpill" aria-pressed="false" data-filter="{k}">{e(d["short"])}</button>' for k, d in AUTHORS.items())
    body = f'''<section class="page-head"><div class="glow g1" aria-hidden="true"></div><div class="wrap">
  <p class="eyebrow">The Bloom Journal</p>
  <h1>Short reads for <em>hard seasons.</em></h1>
  <p class="lede">Reflections, practices and notes from our four authors. Five minutes, a cup of tea, and something to carry into your day.</p>
  <div class="jpills" role="group" aria-label="Filter by author">{pills}</div>
</div></section>
<section class="sec sec-top0"><div class="wrap"><div class="jgrid jgrid-index">{card(mixed[0], big=True)}{"".join(card(x) for x in mixed[1:])}</div></div></section>'''
    (ROOT / "journal" / "index.html").write_text(page("The Bloom Journal | Bloom Editorial", "Short reflections, practices and notes from Bloom Editorial's authors.", "/journal/", body), encoding="utf-8")

    # author pages
    for k, d in AUTHORS.items():
        mine = [x for x in mixed if x["author"] == k]
        books = "".join(book_block(b) for b in d["books"])
        planned = "".join(f"<li>{e(t)}</li>" for t in d["planned"])
        others = "".join(f'<a class="other" href="/authors/{o}.html"><img src="/img/botanical/{AUTHORS[o]["emblem"]}" alt="" aria-hidden="true"><span><b>{e(AUTHORS[o]["name"])}</b>{e(AUTHORS[o]["season"])}</span></a>'
                         for o in ORDER if o != k)
        body = f'''<section class="author-hero wrap">
  <div class="author-panel {d["panel"]}"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true"></div>
  <div class="author-intro"><p class="eyebrow">{e(d["season"])}</p><h1>{e(d["name"])}</h1><p class="article-dek">{e(d["tagline"])}</p><p class="muted">{e(d["bio"])}</p></div>
</section>
<section class="sec"><div class="wrap"><h2 class="h2">From {e(d["short"])}'s journal</h2><div class="jgrid">{"".join(card(x) for x in mine)}</div></div></section>
<section class="sec sec-top0"><div class="wrap author-books">{books if books else '<div class="side-book side-empty"><div><p class="eyebrow">The books</p><h3>Her first books are on the way</h3><p class="muted">Clara is writing the journals listed here. They will arrive in print and Kindle.</p></div></div>'}
  <div class="planned"><p class="eyebrow">In the works</p><ul>{planned}</ul></div></div></section>
<section class="sec sec-top0"><div class="wrap"><h2 class="h2">The other authors</h2><div class="others">{others}</div></div></section>'''
        (ROOT / "authors" / f"{k}.html").write_text(page(f'{d["name"]} | Bloom Editorial', d["tagline"], f"/authors/{k}.html", body), encoding="utf-8")

    # authors index
    tiles = "".join(f'<a class="other other-big" href="/authors/{k}.html"><span class="author-panel {d["panel"]}"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true"></span><span><b>{e(d["name"])}</b>{e(d["tagline"])}</span></a>' for k, d in AUTHORS.items())
    body = f'''<section class="page-head"><div class="wrap"><p class="eyebrow">Our authors</p><h1>Four authors, <em>four seasons.</em></h1><p class="lede">Each author writes for one hard season, and only that one.</p></div></section>
<section class="sec sec-top0"><div class="wrap"><div class="others others-big">{tiles}</div></div></section>'''
    (ROOT / "authors.html").write_text(page("Our authors | Bloom Editorial", "Meet the four authors of Bloom Editorial.", "/authors.html", body), encoding="utf-8")

    # home: shared nav + journal teaser
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    teaser = f'''<section class="sec" id="journal" aria-labelledby="journal-h">
  <div class="wrap">
    <div class="head-row rv"><div><h2 class="h2" id="journal-h">From the journal</h2><p class="sub">Short reads from our authors, for the days that ask more of you.</p></div>
    <a class="btn btn-ghost" href="/journal/">Read the journal <span aria-hidden="true">&rarr;</span></a></div>
    <div class="jgrid">{"".join(card(x) for x in mixed[:4])}</div>
  </div>
</section>'''
    home = re.sub(r"<!-- NAV:START -->.*?<!-- NAV:END -->", f"<!-- NAV:START -->\n{nav()}\n<!-- NAV:END -->", home, flags=re.S)
    home = re.sub(r"<!-- JOURNAL:START -->.*?<!-- JOURNAL:END -->", f"<!-- JOURNAL:START -->\n{teaser}\n<!-- JOURNAL:END -->", home, flags=re.S)
    (ROOT / "index.html").write_text(home, encoding="utf-8")
    print(f"built {len(mixed)} articles, {len(AUTHORS)} author pages, journal index, home teaser")


if __name__ == "__main__":
    build()
