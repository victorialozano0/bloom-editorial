"""Build the Bloom Editorial journal, article pages and author pages from content/journal/*.json.

Usage (from the repo root):  python tools/build_site.py
Writes: journal/index.html, journal/<slug>.html, authors/<id>.html, authors.html, sitemap.xml, robots.txt,
and refreshes the shared nav + "From the journal" block in index.html (between markers).

Article dates in the JSON-LD and sitemap come from the git history of content/journal, so an article shows
them only once it is committed: commit new or edited articles first, then build and commit the output.

Optional article fields seo_title and seo_description override the <title>, meta description, Open Graph and
JSON-LD text; the visible H1 (title) and subtitle (dek) never change with them.
"""
import html
import json
import pathlib
import re
import subprocess
from xml.sax.saxutils import escape as xml_escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700"
         "&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap")
SITE = "https://bloomeditorial.netlify.app"

AUTHORS = {
    "hannah-grace": {
        "name": "Hannah Grace", "short": "Hannah", "season": "Faith & healing", "panel": "p-rose", "accent": "#c2577a",
        "emblem": "olive.webp", "ew": 360, "eh": 691,
        "tagline": "Bible studies for women in hard seasons.",
        "bio": "Scripture-based studies for women carrying something heavy: grief, anxiety, betrayal, the quiet ache of feeling unseen. Pastoral without being preachy. Built to be worked through with a pen, not just read.",
        "books": [{"title": "Healing Bible Study for Women", "cover": "healing-bible-study-for-women", "ch": 768,
                   "dek": "A 6-week, Scripture-based journey to restore your broken heart and renew your mind.",
                   "links": [("Paperback", "B0H17PD38W"), ("Kindle", "B0H18ZX2SX"), ("Hardcover", "B0HQDCMYZH")],
                   "review": "B0H17PD38W"}],
        "planned": ["Daily Prayer Journal for Women", "Scripture Journal for Women: Write the Word", "Anxiety and Faith",
                    "Psalms for the Brokenhearted", "A Bible Study for Women in Grief", "Proverbs for Women", "Walking Through Fire"],
    },
    "maya-chen": {
        "name": "Maya Chen", "short": "Maya", "season": "Anxiety & nervous system", "panel": "p-mint", "accent": "#2c7d5b",
        "emblem": "tree.webp", "ew": 360, "eh": 361,
        "tagline": "Somatic healing for a nervous system that learned to brace.",
        "bio": "Short, guided vagus nerve and somatic practices, with the science explained in plain language. Books for the bedside table, made to be used on the hard days.",
        "books": [{"title": "Vagus Nerve Exercises for Anxiety", "cover": "vagus-nerve-exercises-for-anxiety", "ch": 768,
                   "dek": "A 10-minute daily reset with step-by-step practices you can actually do.",
                   "links": [("Paperback", "B0H19KD54V"), ("Kindle", "B0H19DC7YS"), ("Hardcover", "B0H19KSCRL")],
                   "review": "B0H19KD54V"}],
        "planned": ["My Nervous System Tracker", "The Vagus Nerve Practice Journal", "Somatic Healing for Trauma",
                    "The Nervous System Reset", "Polyvagal Exercises for Beginners", "Somatic Healing for Women", "Heal Your Nervous System"],
    },
    "clara-bennett": {
        "name": "Clara Bennett", "short": "Clara", "season": "Grief & remembering Mom", "panel": "p-sand", "accent": "#b4651f",
        "emblem": "forget.webp", "ew": 360, "eh": 345,
        "tagline": "Journals and keepsakes for daughters who lost their mother.",
        "bio": "Grief that doesn't follow a timeline or a rulebook. Clara's journals are not about getting over it. They are about carrying it, honoring her, and keeping her close on the anniversaries and the ordinary days.",
        "books": [],
        "planned": ["Grief Journal for the Loss of a Mother", "Mom's Kitchen: A Recipe Memory Book", "My Mother, My Heart",
                    "A Mother's Legacy", "Dear Mom: Letters I Never Got to Send", "A Year Without Mom",
                    "Healing After Losing Your Mother", "The Grief Companion"],
    },
    "claire-harmon": {
        "name": "Claire Harmon", "short": "Claire", "season": "Perimenopause", "panel": "p-lilac", "accent": "#7d52c9",
        "emblem": "lavender.webp", "ew": 360, "eh": 429,
        "tagline": "The emotional side of perimenopause, finally named.",
        "bio": "Workbooks for the anxiety, brain fog, broken sleep and rage that can arrive with perimenopause. Plain language, practical tools, zero shame.",
        "books": [{"title": "Perimenopause Anxiety Workbook", "cover": "perimenopause-anxiety-workbook", "ch": 720,
                   "dek": "A 30-day guided workbook with trackers and 10-minute calm strategies.",
                   "links": [("Paperback", "B0HQFBDRF9")], "review": "B0HQFBDRF9"}],
        "planned": ["My Perimenopause Journal", "Perimenopause Daily Symptom Tracker", "The Perimenopause Brain Fog Workbook",
                    "Sleep Through Perimenopause", "The HRT Decision Workbook", "Perimenopause Mood & Rage Workbook",
                    "The Complete Perimenopause Workbook"],
    },
}
ORDER = list(AUTHORS)
e = html.escape


def nav():
    items = "".join(f'<li><a href="/authors/{a}.html"><img class="avatar" src="/img/authors/{a}-sq.webp" width="240" height="240" alt="" aria-hidden="true">'
                    f'<span><b>{e(d["name"])}</b>{e(d["season"])}</span></a></li>' for a, d in AUTHORS.items())
    return f'''<header class="nav">
  <div class="wrap nav-in">
    <a class="logo" href="/" aria-label="Bloom Editorial, home"><img class="logo-h" src="/img/brand/bloom-logo-horizontal.png" width="2172" height="724" alt="Bloom Editorial"></a>
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
    <a class="logo" href="/" aria-label="Bloom Editorial, home"><img class="logo-h" src="/img/brand/bloom-logo-horizontal.png" width="2172" height="724" alt="Bloom Editorial"></a>
    <ul aria-label="Explore"><li><a href="/journal/">Journal</a></li>{links}</ul>
    <p class="legal">&copy; <span data-year>2026</span> Bloom Editorial. Our books support, but never replace, care from a doctor or licensed therapist.</p>
  </div>
</footer>'''


def page(title, desc, canonical, body, jsonld=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#faf8f4">
<link rel="icon" type="image/png" sizes="32x32" href="/img/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/img/brand/favicon-180.png">
<link rel="canonical" href="{SITE}{canonical}">
<meta name="p:domain_verify" content="83dda4692c602d16284c48a86e32cccb"/>
<meta property="og:type" content="article">
<meta property="og:site_name" content="Bloom Editorial">
<meta property="og:url" content="{SITE}{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/img/og-bloom-launch.jpg">{jsonld}
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


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def article_dates():
    """slug -> (commit that first added the article, last commit that changed its JSON). Uncommitted articles are absent."""
    dates = {}
    for f in sorted((ROOT / "content" / "journal").glob("*.json")):
        rel = f.relative_to(ROOT).as_posix()
        prev = {}
        try:
            for line in git("log", "--reverse", "--format=%H %cI", "--", rel).splitlines():
                sha, when = line.split()
                now = {a["slug"]: a for a in json.loads(git("show", f"{sha}:{rel}"))}
                for slug, a in now.items():
                    if slug not in dates:
                        dates[slug] = (when, when)
                    elif a != prev.get(slug):
                        dates[slug] = (dates[slug][0], when)
                prev = now
        except (OSError, subprocess.CalledProcessError) as err:
            print(f"warning: no git dates for {rel}: {err}")
    return dates


def article_jsonld(a, d, dates):
    """Article schema. Authors are pen names: name and author page only, no credentials."""
    url = f'{SITE}/journal/{a["slug"]}.html'
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a.get("seo_title") or a["title"],
        "description": a.get("seo_description") or a["dek"],
        "author": {"@type": "Person", "name": d["name"], "url": f'{SITE}/authors/{a["author"]}.html'},
        "publisher": {"@type": "Organization", "name": "Bloom Editorial", "url": f"{SITE}/"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    if a["slug"] in dates:
        data["datePublished"], data["dateModified"] = dates[a["slug"]]
    # Escaping "<" keeps any "</script>" in the text from closing the tag
    return '\n<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def build_seo_files(arts, dates):
    """sitemap.xml (real, canonical pages only; catalog.html is a redirect) and robots.txt."""
    paths = ["/", "/journal/", *(f'/journal/{a["slug"]}.html' for a in sorted(arts, key=lambda x: x["slug"])),
             "/authors.html", *(f"/authors/{k}.html" for k in ORDER), "/peek-inside.html"]
    entries = []
    for path in paths:
        rel = path.strip("/")
        target = ROOT / rel / "index.html" if path.endswith("/") else ROOT / rel
        assert target.is_file(), path
        slug = path.removeprefix("/journal/").removesuffix(".html")
        lastmod = f"<lastmod>{dates[slug][1]}</lastmod>" if slug in dates else ""
        entries.append(f"  <url><loc>{xml_escape(SITE + path)}</loc>{lastmod}</url>")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "\n".join(entries) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def banner(text):
    """'Your wound deserves a [name].' -> escaped HTML with <b> around the key words."""
    return re.sub(r"\[(.+?)\]", lambda m: f"<b>{m.group(1)}</b>", e(text))


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
    if b.get("review"):
        # Readers arrive here from the "One small favor" page at the end of each book
        buy += (f'<p class="review-ask">Finished the book? <a href="https://www.amazon.com/review/create-review?asin={b["review"]}" '
                f'rel="noopener" target="_blank">Leave an honest review on Amazon<span class="sr"> (opens in a new tab)</span></a></p>')
    return f'''<div class="side-book"><img src="/img/{b["cover"]}-480.webp" width="480" height="{b["ch"]}" alt="Cover of {e(b["title"])}" loading="lazy">
  <div><p class="eyebrow">The book</p><h3>{e(b["title"])}</h3><p class="muted">{e(b["dek"])}</p>{buy}</div></div>'''


# "Peek inside" (link in bio): real lines and full exercises from the published books. No interior pages.
PEEK = [
    {"id": "calm", "chip": "Calm body", "author": "maya-chen", "book": 0,
     "feeling": "Your mind knows you're okay. Your body hasn't heard.",
     "quotes": ["Your nervous system isn't broken. It's been protecting you with the tools it had. The work now is giving it better ones.",
                "Vagal resilience doesn't mean you stop getting activated. It means you stop staying there."],
     "ex_title": "The Physiological Sigh", "ex_time": "Under a minute",
     "ex_intro": "Something your body already knows how to do. Find a seated or standing position.",
     "safety": "If you're prone to lightheadedness or hyperventilation, go slowly with the double inhale and reduce the exhale duration on your first attempt. If you feel dizzy, return to normal breathing immediately.",
     "steps": ["Inhale fully through your nose. (4 counts)",
               "Without exhaling, take a second, shorter sniff through your nose on top of the first inhale, as if you're topping off a nearly full glass. You'll feel your chest and belly expand further.",
               "Now exhale slowly and completely through your mouth, lips slightly parted, for 6 to 8 counts. Let it be longer than feels necessary. Let your shoulders drop on the way out.",
               "Pause naturally at the bottom of the exhale, 1 to 2 seconds.",
               "Return to normal breathing. Notice the quality of your next few breaths."],
     "outro": "Feeling nothing is also normal. Do 2 or 3 cycles and notice cumulatively."},
    {"id": "faith", "chip": "Faith that feels far", "author": "hannah-grace", "book": 0,
     "feeling": "You keep praying, and you can't feel a thing.",
     "quotes": ["Your wound doesn't have to be the worst wound in the room to deserve a name.",
                "The middle is not evidence that you're failing. It's evidence that you started."],
     "ex_title": "Naming the Wound for the Healer", "ex_time": "A few quiet minutes and a pen",
     "ex_intro": "Name what you're actually bringing. Not the general category (\"my health,\" \"my grief\") but the specific, particular wound you are carrying right now.",
     "safety": "",
     "steps": ["Write a single, specific sentence that names what you most need healing from right now.",
               "Not \"my anxiety\": \"the anxiety that wakes me up at 3 a.m. convinced my marriage is ending.\"",
               "Not \"my grief\": \"the grief over my mother's death that I haven't been able to talk about for two years because everyone expects me to be over it.\""],
     "outro": "The naming is not for His information. He already knows. It's for yours. When we name the wound honestly before God, we stop carrying it in the dark."},
    {"id": "change", "chip": "Perimenopause", "author": "claire-harmon", "book": 0,
     "feeling": "It's 3 a.m. again, and you don't recognize yourself.",
     "quotes": ["You are not your thoughts. You are the person noticing them. That distance is everything.",
                "Your body is not your enemy. It is responding to a real, massive hormonal shift with the tools it has. You're simply giving it better ones."],
     "ex_title": "\"I'm Having the Thought That...\"", "ex_time": "3 to 5 minutes",
     "ex_intro": "This exercise creates distance between you and an anxious thought, not by changing the thought, but by changing your relationship to it.",
     "safety": "If you're currently in acute distress or crisis, please reach out to a mental health professional. This technique works best for the everyday anxiety spiral, not a mental health emergency.",
     "steps": ["Identify the anxious thought that is most active right now. Don't reach for the most logical one. Write the one that actually keeps arriving, exactly as it sounds in your head.",
               "Now rewrite that thought using the stem: \"I'm having the thought that...\"",
               "Read your rewritten sentence aloud or in your head. Notice how it feels different from the original. You don't need to believe it is different. Just notice if there's any shift, even a small one.",
               "Add one more layer if you want to go further: \"I notice that I'm having the thought that...\"",
               "Sit with the defused version for 60 seconds. Breathe normally. You don't need to do anything with the thought. Just let it be there, labeled, at arm's length."],
     "outro": ""},
]


def peek_section(p):
    d = AUTHORS[p["author"]]; b = d["books"][p["book"]]
    quotes = "".join(f'<blockquote class="peek-q">{e(q)}</blockquote>' for q in p["quotes"])
    steps = "".join(f"<li>{e(x)}</li>" for x in p["steps"])
    safety = f'<p class="peek-safety"><b>A safety note.</b> {e(p["safety"])}</p>' if p["safety"] else ""
    outro = f'<p class="peek-outro">{e(p["outro"])}</p>' if p["outro"] else ""
    links = "".join(f'<a class="btn btn-sm{"" if i == 0 else " btn-soft"}" href="https://www.amazon.com/dp/{asin}" rel="noopener" target="_blank">{fmt}<span class="sr"> on Amazon (opens in a new tab)</span></a>'
                    for i, (fmt, asin) in enumerate(b["links"]))
    return f"""<section class="peek-sec" id="{p["id"]}" aria-labelledby="{p["id"]}-h">
  <div class="wrap peek-grid">
    <div class="peek-words {d["panel"]}">
      <p class="eyebrow peek-eyebrow">{e(d["season"])}</p>
      <h2 id="{p["id"]}-h">{e(p["feeling"])}</h2>
      {quotes}
      <p class="peek-from">From <i>{e(b["title"])}</i>, by <a href="/authors/{p["author"]}.html">{e(d["name"])}</a></p>
    </div>
    <div class="peek-ex">
      <p class="eyebrow">Try it now &middot; {e(p["ex_time"])}</p>
      <h3>{e(p["ex_title"])}</h3>
      <p>{e(p["ex_intro"])}</p>
      {safety}
      <ol>{steps}</ol>
      {outro}
      <div class="peek-book"><img src="/img/{b["cover"]}-480.webp" width="480" height="{b["ch"]}" alt="Cover of {e(b["title"])}" loading="lazy">
        <div><p class="peek-book-t">There's more where this came from.</p><p class="muted">{e(b["dek"])}</p><p class="peek-buy">{links}</p></div></div>
    </div>
  </div>
</section>"""


def build_peek():
    chips = "".join(f'<a class="jpill" href="#{p["id"]}">{e(p["chip"])}</a>' for p in PEEK) + '<a class="jpill" href="#mom">Missing your mom</a>'
    body = f"""<section class="page-head"><div class="wrap">
  <p class="eyebrow">Peek inside</p>
  <h1>A true sentence and a small practice, <em>for today.</em></h1>
  <p class="lede">Real words and real exercises from our books. Find the season you're in and try one right now. You don't have to buy anything to begin.</p>
  <nav class="jpills" aria-label="Choose your season">{chips}</nav>
</div></section>
{"".join(peek_section(p) for p in PEEK)}
<section class="peek-sec" id="mom" aria-labelledby="mom-h"><div class="wrap"><div class="peek-mom p-sand">
  <p class="eyebrow peek-eyebrow">{e(AUTHORS["clara-bennett"]["season"])}</p>
  <h2 id="mom-h">You reach for the phone to call her, and then you remember.</h2>
  <p>Clara's journals are still being written. Until then, she wrote this for you.</p>
  <a class="btn btn-sm" href="/journal/reaching-for-the-phone.html">Read Clara's note <span aria-hidden="true">&rarr;</span></a>
</div></div></section>"""
    (ROOT / "peek-inside.html").write_text(page("Peek inside | Bloom Editorial", "Real words and real exercises from Bloom Editorial's books for anxiety, a faith that feels far, perimenopause and missing your mom. Try one today.", "/peek-inside.html", body), encoding="utf-8")


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

    dates = article_dates()
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
    <p class="byline"><img class="avatar" src="/img/authors/{a["author"]}-sq.webp" width="240" height="240" alt="" aria-hidden="true"><span>By <a href="/authors/{a["author"]}.html">{e(d["name"])}</a> &middot; {a["read_minutes"]} min read</span></p>
  </header>
  <div class="article-hero {d["panel"]}" style="--accent:{d["accent"]}">
    <p class="banner" aria-label="{e(a["banner"].replace("[", "").replace("]", ""))}"><span aria-hidden="true">{banner(a["banner"])}</span></p>
    <img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true">
  </div>
  <div class="article-body wrap">{a["body_html"]}</div>
  <aside class="article-end wrap">
    <div class="author-box"><img class="avatar" src="/img/authors/{a["author"]}-sq.webp" width="240" height="240" alt="Portrait of {e(d["name"])}" loading="lazy"><div><p class="eyebrow">About the author</p><h3>{e(d["name"])}</h3><p class="muted">{e(d["bio"])}</p><a class="textlink" href="/authors/{a["author"]}.html">More from {e(d["short"])} &rarr;</a></div></div>
    {book}
  </aside>
</article>
<section class="sec"><div class="wrap"><h2 class="h2">Keep reading</h2><div class="jgrid">{"".join(card(x) for x in more)}</div></div></section>'''
        (ROOT / "journal" / f'{a["slug"]}.html').write_text(page(f'{a.get("seo_title") or a["title"]} | Bloom Editorial Journal', a.get("seo_description") or a["dek"], f'/journal/{a["slug"]}.html', body, article_jsonld(a, d, dates)), encoding="utf-8")

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
        others = "".join(f'<a class="other" href="/authors/{o}.html"><img class="avatar" src="/img/authors/{o}-sq.webp" width="240" height="240" alt="" aria-hidden="true"><span><b>{e(AUTHORS[o]["name"])}</b>{e(AUTHORS[o]["season"])}</span></a>'
                         for o in ORDER if o != k)
        body = f'''<section class="author-hero wrap">
  <div class="author-panel author-photo {d["panel"]}"><img class="portrait" src="/img/authors/{k}.webp" width="800" height="1000" alt="Portrait of {e(d["name"])}"><span class="badge"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true"></span></div>
  <div class="author-intro"><p class="eyebrow">{e(d["season"])}</p><h1>{e(d["name"])}</h1><p class="article-dek">{e(d["tagline"])}</p><p class="muted">{e(d["bio"])}</p></div>
</section>
<section class="sec"><div class="wrap"><h2 class="h2">From {e(d["short"])}'s journal</h2><div class="jgrid">{"".join(card(x) for x in mine)}</div></div></section>
<section class="sec sec-top0"><div class="wrap author-books">{books if books else '<div class="side-book side-empty"><div><p class="eyebrow">The books</p><h3>Her first books are on the way</h3><p class="muted">Clara is writing the journals listed here. They will arrive in print and Kindle.</p></div></div>'}
  <div class="planned"><p class="eyebrow">In the works</p><ul>{planned}</ul></div></div></section>
<section class="sec sec-top0"><div class="wrap"><h2 class="h2">The other authors</h2><div class="others">{others}</div></div></section>'''
        (ROOT / "authors" / f"{k}.html").write_text(page(f'{d["name"]} | Bloom Editorial', d["tagline"], f"/authors/{k}.html", body), encoding="utf-8")

    # authors index
    tiles = "".join(f'<a class="other other-big" href="/authors/{k}.html"><span class="author-panel author-photo {d["panel"]}"><img class="portrait" src="/img/authors/{k}.webp" width="800" height="1000" alt="Portrait of {e(d["name"])}" loading="lazy"><span class="badge"><img src="/img/botanical/{d["emblem"]}" alt="" aria-hidden="true"></span></span><span><b>{e(d["name"])}</b>{e(d["tagline"])}</span></a>' for k, d in AUTHORS.items())
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
    build_peek()
    build_seo_files(arts, dates)
    print(f"built {len(mixed)} articles, {len(AUTHORS)} author pages, journal index, home teaser")


if __name__ == "__main__":
    build()
