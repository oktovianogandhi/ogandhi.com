#!/usr/bin/env python3
"""Build ogandhi.com into ./docs (served by GitHub Pages from the main branch, /docs folder).

Content lives in content/pages (about and topic pages) and content/posts (writing).
Publication data lives in data/publications.py. Static files are in static/.
Run:  python3 build.py
Needs: Python 3.9+ and the 'markdown' package (pip install markdown).
"""
import html
import json
import math
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
DIST = ROOT / "docs"  # GitHub Pages serves main /docs
SITE = "https://ogandhi.com"
NAME = "Oktoviano Gandhi"
EMAIL = "hello@ogandhi.com"  # to be set up with Cloudflare Email Routing
LINKEDIN = "https://www.linkedin.com/in/oktovianogandhi/"
SCHOLAR = "https://scholar.google.com.sg/citations?user=0H3VhVQAAAAJ&hl=en"
ORCID = "https://orcid.org/0000-0002-7003-2986"
TODAY = date.today().isoformat()

sys.path.insert(0, str(ROOT / "data"))
from publications import JOURNAL, BOOKS, REPORTS, CONFERENCE  # noqa: E402

TOPICS = [
    ("fpv", "floating-pv", "Floating PV"),
    ("grid", "grid-integration", "Grid integration of PV and battery storage"),
    ("climate", "pv-in-hot-climates", "PV performance in hot climates"),
    ("access", "southeast-asia", "Southeast Asian power systems and energy access"),
]
TOPIC_SHORT = {"fpv": "Floating PV", "grid": "Grid integration", "climate": "Hot climates", "access": "Southeast Asia and energy access"}

PERSON_ID = SITE + "/#person"
PERSON = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": NAME,
    "alternateName": "Okto Gandhi",
    "url": SITE + "/",
    "image": SITE + "/img/okto-720.jpg",
    "jobTitle": "Scientist",
    "worksFor": {"@type": "Organization", "name": "Qatar Environment and Energy Research Institute (QEERI), Hamad Bin Khalifa University", "url": "https://www.hbku.edu.qa/en/qeeri"},
    "alumniOf": [
        {"@type": "CollegeOrUniversity", "name": "National University of Singapore"},
        {"@type": "CollegeOrUniversity", "name": "University of Oxford"},
    ],
    "knowsAbout": ["Solar photovoltaics", "Floating photovoltaics", "Battery energy storage systems", "Grid integration of renewable energy",
                   "Ancillary services", "Reactive power", "Solar forecasting", "PV performance in hot climates", "Power sector regulation in Indonesia"],
    "knowsLanguage": ["English", "Indonesian", "Malay"],
    "sameAs": [LINKEDIN, SCHOLAR, ORCID],
}


# ---------- helpers ----------

def esc(s):
    return html.escape(s, quote=True)


def read_md(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for line in fm.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body.strip()


def md(text):
    return markdown.markdown(text, extensions=["footnotes", "attr_list", "sane_lists", "tables"],
                             extension_configs={"footnotes": {"BACKLINK_TEXT": "↩"}})


def authors_html(a):
    a = esc(a)
    return re.sub(r"\bO Gandhi\b", "<strong>O Gandhi</strong>", a)


def day_curve(width=1200, height=240, base=196, peak=168, small=False):
    """A clear-sky day of PV output: zero before 06:00 and after 18:00, peaking at noon."""
    x0, x1 = width * 0.25, width * 0.75
    pts = []
    for i in range(0, 121):
        x = x0 + (x1 - x0) * i / 120
        s = math.sin(math.pi * i / 120)
        y = base - peak * (s ** 1.6)
        pts.append((x, y))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = d + f" L {x1:.1f} {base} L {x0:.1f} {base} Z"
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    if small:
        return (f'<svg viewBox="{x0 - 20:.0f} {base - peak - 12} {x1 - x0 + 40:.0f} {peak + 16}" aria-hidden="true" focusable="false">'
                f'<path d="{area}" fill="#E7A33E" opacity="0.18"/><path d="{d}" fill="none" stroke="#E7A33E" stroke-width="22" stroke-linecap="round"/>'
                f'<line x1="{x0 - 20:.0f}" y1="{base}" x2="{x1 + 20:.0f}" y2="{base}" stroke="#13233A" stroke-width="12"/></svg>')
    ticks = ""
    for h in (0, 6, 12, 18, 24):
        x = width * h / 24
        anchor = "start" if h == 0 else "end" if h == 24 else "middle"
        ticks += f'<line class="tick" x1="{x:.0f}" y1="{base}" x2="{x:.0f}" y2="{base + 8}"/>'
        ticks += f'<text x="{x:.0f}" y="{base + 30}" text-anchor="{anchor}">{h:02d}:00</text>'
    return (f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Line showing the power output of a solar PV system over one clear day, rising from sunrise at 06:00 to a peak at noon and falling to zero at 18:00">'
            f'<path class="area" d="{area}"/><path class="curve" d="{d}" style="--len:{length:.0f}"/>'
            f'<line class="baseline" x1="0" y1="{base}" x2="{width}" y2="{base}"/>{ticks}</svg>')


NAV = [("/topics/", "Topics"), ("/publications/", "Publications"), ("/writing/", "Writing"), ("/about/", "About"), ("#contact", "Contact")]
HAS_POSTS = any((ROOT / "content" / "posts").glob("*.md"))
if not HAS_POSTS:
    NAV = [n for n in NAV if n[0] != "/writing/"]


def page(path, title, description, body, active=None, jsonld=None, og_type="website", full_title=None):
    url = SITE + path
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>' for href, label in NAV)
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"
    t = full_title or (f"{title} | {NAME}" if title else f"{NAME}: solar PV, battery storage and grid integration")
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<meta name="author" content="{NAME}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title or NAME)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/og.jpg">
<meta property="og:site_name" content="{NAME}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{RSS_LINK if HAS_POSTS else ""}
<link rel="preload" href="/fonts/literata-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="site-name" href="/">{day_curve(small=True)}<span>{NAME}</span></a>
    <nav class="nav" aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer" id="contact">
  <div class="wrap">
    <h2>Contact</h2>
    <p>For research collaboration, speaking or media requests, email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    <ul class="links">
      <li><a href="{LINKEDIN}">LinkedIn</a></li>
      <li><a href="{SCHOLAR}">Google Scholar</a></li>
      <li><a href="{ORCID}">ORCID</a></li>
      {RSS_LI if HAS_POSTS else ""}
    </ul>
    <p class="small">© {date.today().year} {NAME}. Views on this site are my own.</p>
  </div>
</footer>
{FILTER_JS if path == "/publications/" else ""}
</body>
</html>
"""


RSS_LINK = f'<link rel="alternate" type="application/rss+xml" title="Writing by {NAME}" href="/feed.xml">'
RSS_LI = '<li><a href="/feed.xml">RSS feed</a></li>'

FILTER_JS = """<script>
(function () {
  var buttons = document.querySelectorAll('.filters button');
  var items = document.querySelectorAll('.pub[data-tags]');
  var groups = document.querySelectorAll('.pub-group');
  function apply(tag) {
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.tag === tag)); });
    items.forEach(function (li) { li.hidden = tag !== 'all' && li.dataset.tags.split(' ').indexOf(tag) < 0; });
    groups.forEach(function (g) { g.hidden = !g.querySelector('.pub:not([hidden])'); });
    var url = new URL(window.location.href);
    if (tag === 'all') { url.searchParams.delete('topic'); } else { url.searchParams.set('topic', tag); }
    history.replaceState(null, '', url);
  }
  buttons.forEach(function (b) { b.addEventListener('click', function () { apply(b.dataset.tag); }); });
  var start = new URLSearchParams(window.location.search).get('topic');
  if (start && document.querySelector('.filters button[data-tag="' + start + '"]')) { apply(start); }
})();
</script>"""


def pub_li(p, with_tags=True):
    title = esc(p["title"])
    t = f'<a class="title" href="{esc(p["url"])}">{title}</a>' if p.get("url") else f'<span class="title">{title}</span>'
    tags = f' data-tags="{" ".join(p.get("tags", []))}"' if with_tags else ""
    year = "" if p.get("undated") else str(p["year"])
    return (f'<li class="pub"{tags}><span class="year">{year}</span><div>{t}'
            f'<span class="authors">{authors_html(p["authors"])}</span><span class="venue">{esc(p["venue"])}</span></div></li>')


def pub_ld(p, kind):
    item = {"@type": kind, "name": p["title"], "author": {"@id": PERSON_ID}, "datePublished": str(p["year"])}
    if p.get("url"):
        item["url"] = p["url"]
    item["isPartOf"] = p["venue"]
    return item


def write(path, content):
    out = DIST / path.lstrip("/")
    if path.endswith("/"):
        out = out / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


# ---------- build ----------

def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    urls = []

    # Pages
    pages = {}
    for f in sorted((ROOT / "content" / "pages").glob("*.md")):
        meta, body = read_md(f)
        pages[meta["slug"]] = (meta, body)

    posts = []
    for f in (ROOT / "content" / "posts").glob("*.md"):
        meta, body = read_md(f)
        posts.append((meta, body))
    posts.sort(key=lambda m: m[0]["date"], reverse=True)

    all_pubs = [(p, "ScholarlyArticle") for p in JOURNAL] + [(p, "Book") for p in BOOKS] + [(p, "Report") for p in REPORTS] + [(p, "ScholarlyArticle") for p in CONFERENCE]

    # Home
    topics_html = "".join(
        f'<li><h3><a href="/topics/{slug}/">{esc(pages["topics/" + slug][0]["title"])}</a></h3><p>{esc(pages["topics/" + slug][0]["summary"])}</p></li>'
        for tag, slug, _ in TOPICS)
    featured = [p for p in JOURNAL if p.get("featured")]
    books_html = "".join(
        f'<li class="book"><picture><source srcset="/img/{b["cover"]}.webp" type="image/webp"><img src="/img/{b["cover"]}.png" alt="Cover of {esc(b["title"].split(":")[0])}" width="400" height="444" loading="lazy"></picture>'
        f'<div><h3><a href="{esc(b["url"])}">{esc(b["title"])}</a></h3><p>{esc(b["authors"])}. {esc(b["venue"])}, {b["year"]}.</p></div></li>'
        for b in BOOKS)
    posts_html = "".join(
        f'<li><h3><a href="/{m["slug"]}/">{esc(m["title"])}</a></h3><p>{esc(m["description"])}</p><span class="meta">{esc(m["date_label"])}</span></li>'
        for m, _ in posts[:3])
    writing_section = (f'''<section class="section" aria-labelledby="writing-h">
  <div class="wrap">
    <h2 id="writing-h">Writing</h2>
    <ul class="posts">{posts_html}</ul>
    <p class="more"><a href="/writing/">All writing</a></p>
  </div>
</section>''') if posts else ""
    home_body = f"""
<section class="hero" aria-labelledby="intro-name">
  <div class="wrap">
    <div class="day">{day_curve()}</div>
    <div class="intro">
      <div>
        <h1 id="intro-name">{NAME}</h1>
        <p class="lede">I work on solar PV, battery storage and their integration into power systems, mostly in Southeast Asia.</p>
        <p class="standing">I am a Scientist at the Qatar Environment and Energy Research Institute (QEERI), Hamad Bin Khalifa University. Before that, I spent eleven years at the Solar Energy Research Institute of Singapore (SERIS), National University of Singapore, and co-founded Alva Energi, a solar company in Indonesia.</p>
        <ul class="links"><li><a href="/about/">More about me</a></li><li><a href="/publications/">Publications</a></li><li><a href="{SCHOLAR}">Google Scholar</a></li><li><a href="{LINKEDIN}">LinkedIn</a></li></ul>
      </div>
      <figure><picture><source srcset="/img/okto-360.webp 360w, /img/okto-720.webp 720w" sizes="15rem" type="image/webp"><img src="/img/okto-720.jpg" alt="Portrait of Oktoviano Gandhi" width="720" height="900"></picture></figure>
    </div>
  </div>
</section>
<section class="section" aria-labelledby="topics-h">
  <div class="wrap">
    <h2 id="topics-h">What I work on</h2>
    <p class="section-intro">Each topic page summarises the questions I have worked on and links to the papers and reports behind them.</p>
    <ul class="topics">{topics_html}</ul>
  </div>
</section>
<section class="section" aria-labelledby="pubs-h">
  <div class="wrap">
    <h2 id="pubs-h">Selected publications</h2>
    <p class="section-intro">More than 3,000 citations on Google Scholar. <a href="/publications/">See all publications</a>.</p>
    <ul class="pubs prose">{"".join(pub_li(p, False) for p in featured)}</ul>
    <ul class="books">{books_html}</ul>
  </div>
</section>
{writing_section}"""
    home_ld = {"@context": "https://schema.org", "@graph": [PERSON, {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME, "publisher": {"@id": PERSON_ID}, "inLanguage": "en-GB"}]}
    write("/", page("/", "", "Oktoviano Gandhi works on solar PV, battery storage and grid integration, mostly in Southeast Asia. Scientist at QEERI; previously at SERIS, National University of Singapore.", home_body, jsonld=home_ld))
    urls.append("/")

    # About
    meta, body = pages["about"]
    about_body = f"""
<div class="wrap page-head"><h1>About</h1></div>
<div class="wrap page-body"><div class="about-grid"><div class="prose">{md(body)}</div>
<figure><picture><source srcset="/img/okto-360.webp 360w, /img/okto-720.webp 720w" sizes="15rem" type="image/webp"><img src="/img/okto-720.jpg" alt="Portrait of Oktoviano Gandhi" width="720" height="900"></picture></figure></div></div>"""
    about_ld = {"@context": "https://schema.org", "@type": "ProfilePage", "dateModified": TODAY, "mainEntity": PERSON}
    write("/about/", page("/about/", "About", meta["description"], about_body, active="/about/", jsonld=about_ld, og_type="profile"))
    urls.append("/about/")

    # Topics
    t_index = "".join(
        f'<li><h3><a href="/topics/{slug}/">{esc(pages["topics/" + slug][0]["title"])}</a></h3><p>{esc(pages["topics/" + slug][0]["summary"])}</p></li>'
        for tag, slug, _ in TOPICS)
    write("/topics/", page("/topics/", "Topics", "The topics Oktoviano Gandhi works on: floating PV, grid integration of PV and battery storage, PV performance in hot climates, and Southeast Asian power systems.",
                           f'<div class="wrap page-head"><h1>Topics</h1><p class="dek">What I work on, with the papers and reports behind each topic.</p></div><div class="wrap page-body"><ul class="topics">{t_index}</ul></div>', active="/topics/"))
    urls.append("/topics/")
    for tag, slug, _ in TOPICS:
        meta, body = pages["topics/" + slug]
        related = [p for p, _ in all_pubs if tag in p.get("tags", [])]
        related.sort(key=lambda p: (-p["year"], not p.get("first", False)))
        rel_html = "".join(pub_li(p, False) for p in related[:12])
        more = f'<p class="more"><a href="/publications/?topic={tag}">All {len(related)} publications on this topic</a></p>' if len(related) > 12 else ""
        tbody = f"""
<div class="wrap page-head"><h1>{esc(meta["title"])}</h1><p class="dek">{esc(meta["summary"])}</p></div>
<div class="wrap page-body"><div class="prose">{md(body)}
<h2>Publications on this topic</h2><ul class="pubs">{rel_html}</ul>{more}</div></div>"""
        ld = {"@context": "https://schema.org", "@type": "WebPage", "name": meta["title"], "description": meta["description"], "author": {"@id": PERSON_ID},
              "about": meta["title"], "dateModified": TODAY, "mentions": [pub_ld(p, "ScholarlyArticle") for p in related[:12]]}
        write(f"/topics/{slug}/", page(f"/topics/{slug}/", meta["title"], meta["description"], tbody, active="/topics/", jsonld=ld))
        urls.append(f"/topics/{slug}/")

    # Publications
    filt = '<div class="filters" role="group" aria-label="Filter by topic"><button type="button" data-tag="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-tag="{tag}" aria-pressed="false">{esc(TOPIC_SHORT[tag])}</button>' for tag, _, _ in TOPICS) + "</div>"
    groups = [("Books", BOOKS), ("Journal articles", JOURNAL), ("Reports and articles", REPORTS), ("Conference papers", CONFERENCE)]
    groups_html = "".join(f'<section class="pub-group"><h2>{g}</h2><ul class="pubs">{"".join(pub_li(p) for p in items)}</ul></section>' for g, items in groups)
    pub_body = f"""
<div class="wrap page-head"><h1>Publications</h1><p class="dek">Books, journal articles, reports and conference papers. More than 3,000 citations and an h-index of 27 on <a href="{SCHOLAR}">Google Scholar</a> (October 2026).</p></div>
<div class="wrap page-body"><div class="prose">{filt}{groups_html}</div></div>"""
    pub_ld_all = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Publications by {NAME}", "author": {"@id": PERSON_ID},
                  "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": pub_ld(p, k)} for i, (p, k) in enumerate(all_pubs)]}}
    write("/publications/", page("/publications/", "Publications", f"Books, journal articles, reports and conference papers by {NAME} on solar PV, floating PV, battery storage and grid integration.",
                                 pub_body, active="/publications/", jsonld=pub_ld_all))
    urls.append("/publications/")

    # Writing
    if posts:
        build_writing(posts, urls)

    # 404
    _rest(urls, posts)


def build_writing(posts, urls):
    w_list = "".join(
        f'<li><h3><a href="/{m["slug"]}/">{esc(m["title"])}</a></h3><p>{esc(m["description"])}</p><span class="meta">{esc(m["date_label"])}. Series: {esc(m.get("series", ""))}</span></li>'
        for m, _ in posts)
    write("/writing/", page("/writing/", "Writing", f"Articles by {NAME} on solar PV, grid integration and research practice.",
                            f'<div class="wrap page-head"><h1>Writing</h1><p class="dek">New articles on solar PV and power systems will appear here. The two posts below are from my earlier blog.</p></div><div class="wrap page-body"><ul class="posts">{w_list}</ul></div>',
                            active="/writing/"))
    urls.append("/writing/")
    for m, body in posts:
        pbody = f"""
<article>
<div class="wrap page-head"><p class="meta">{esc(m["date_label"])}. Series: {esc(m.get("series", ""))}</p><h1>{esc(m["title"])}</h1></div>
<div class="wrap page-body"><div class="prose">{md(body)}</div></div>
</article>"""
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": m["title"], "description": m["description"], "datePublished": m["date"],
              "author": {"@id": PERSON_ID, "@type": "Person", "name": NAME, "url": SITE + "/about/"}, "mainEntityOfPage": f"{SITE}/{m['slug']}/", "inLanguage": "en-GB"}
        write(f"/{m['slug']}/", page(f"/{m['slug']}/", m["title"], m["description"], pbody, active="/writing/", jsonld=ld, og_type="article"))
        urls.append(f"/{m['slug']}/")


def _rest(urls, posts):
    # 404
    write("/404.html", page("/404.html", "Page not found", "This page does not exist.",
                            '<div class="wrap page-head"><h1>Page not found</h1><p class="dek">This address has no page. Try the <a href="/">home page</a>, <a href="/topics/">topics</a> or <a href="/publications/">publications</a>.</p></div>'))

    # Favicon
    (DIST / "favicon.svg").write_text(day_curve(small=True).replace('aria-hidden="true" focusable="false"', 'xmlns="http://www.w3.org/2000/svg"'), encoding="utf-8")

    # Sitemap, robots, feed, CNAME
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>', encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    if posts:
        items = "".join(
            f"<item><title>{esc(m['title'])}</title><link>{SITE}/{m['slug']}/</link><guid>{SITE}/{m['slug']}/</guid><description>{esc(m['description'])}</description><pubDate>{date.fromisoformat(m['date']).strftime('%a, %d %b %Y')} 00:00:00 +0000</pubDate></item>"
            for m, _ in posts)
        (DIST / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Writing by {NAME}</title><link>{SITE}/writing/</link><description>Articles on solar PV, battery storage and grid integration.</description><language>en-gb</language>{items}</channel></rss>', encoding="utf-8")
    (DIST / "CNAME").write_text("ogandhi.com\n", encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(urls)} pages into {DIST}")


if __name__ == "__main__":
    build()
