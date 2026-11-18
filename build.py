#!/usr/bin/env python3
"""Build ogandhi.com into ./docs (served by GitHub Pages from the main branch, /docs folder).

Content: content/pages (About, Experience, and expertise pages) and content/posts (writing).
Data: data/publications.py, data/profile.py (home-page positioning), data/media.py (media, recognition, and talks).
Static files: static/.
Run:  python3 build.py
Needs: Python 3.9+ and the 'markdown' package (pip install markdown).
"""
import html
import json
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
EMAIL = "hello@ogandhi.com"  # Cloudflare Email Routing
LINKEDIN = "https://www.linkedin.com/in/oktovianogandhi/"
SCHOLAR = "https://scholar.google.com.sg/citations?user=0H3VhVQAAAAJ&hl=en"
ORCID = "https://orcid.org/0000-0002-7003-2986"
HBKU = "https://www.hbku.edu.qa/en/staff/oktoviano-gandhi"
ALVA_URL = "https://alvaenergi.com/"
TODAY = date.today().isoformat()

sys.path.insert(0, str(ROOT / "data"))
from publications import JOURNAL, BOOKS, REPORTS, CONFERENCE  # noqa: E402
import profile_data as P  # noqa: E402
from media import NEWS, RECOGNITION, TALKS  # noqa: E402

# Expertise areas: (tag, slug, short label for filters)
TOPICS = [
    ("fpv", "floating-pv", "Floating PV"),
    ("grid", "grid-integration", "Grid integration and regulation"),
    ("forecast", "solar-forecasting", "Solar forecasting"),
    ("perf", "pv-performance", "PV performance and technology"),
    ("econ", "techno-economics", "Techno-economics"),
    ("offgrid", "off-grid-and-islands", "Off-grid and island systems"),
]
TOPIC_SHORT = {tag: short for tag, _, short in TOPICS}

PERSON_ID = SITE + "/#person"
PERSON = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": NAME,
    "givenName": "Oktoviano",
    "familyName": "Gandhi",
    "honorificPrefix": "Dr",
    "alternateName": ["Okto Gandhi", "Dr Oktoviano Gandhi", "Oktoviano Gandhi, PhD", "O. Gandhi"],
    "url": SITE + "/",
    "image": {"@type": "ImageObject", "url": SITE + "/img/okto-720.jpg", "width": 720, "height": 900},
    "description": ("Solar PV and power systems specialist working on floating PV, battery storage, grid integration, "
                    "and techno-economics, mostly in Southeast Asia. Scientist at QEERI, Hamad Bin Khalifa University; "
                    "previously eleven years at SERIS, National University of Singapore; co-founder of Alva Energi."),
    "jobTitle": "Scientist",
    "worksFor": {"@type": "ResearchOrganization", "name": "Qatar Environment and Energy Research Institute (QEERI)",
                 "url": "https://www.hbku.edu.qa/en/qeeri",
                 "parentOrganization": {"@type": "CollegeOrUniversity", "name": "Hamad Bin Khalifa University", "url": "https://www.hbku.edu.qa/"}},
    "alumniOf": [
        {"@type": "CollegeOrUniversity", "name": "National University of Singapore", "url": "https://www.nus.edu.sg/"},
        {"@type": "CollegeOrUniversity", "name": "University of Oxford", "url": "https://www.ox.ac.uk/"},
    ],
    "nationality": {"@type": "Country", "name": "Indonesia"},
    "knowsAbout": ["Solar photovoltaics", "Floating photovoltaics", "Offshore floating photovoltaics", "Battery energy storage systems",
                   "Grid integration of renewable energy", "Ancillary services", "Reactive power", "Hosting capacity",
                   "Solar forecasting", "Levelised cost of electricity", "Power purchase agreements", "Feasibility studies",
                   "Bifacial PV and single-axis trackers", "PV soiling", "Off-grid and hybrid power systems", "Diesel replacement",
                   "Rural electrification", "Power sector regulation in Indonesia", "Electricity markets", "Capacity building"],
    "knowsLanguage": ["English", "Indonesian", "Malay"],
    "award": ["Springer Thesis Award (2020)", "Global Goals List, Vanity Fair and One Young World (2020)", "Gen.T List, Tatler Asia (2021)",
              "Leader of Tomorrow, St. Gallen Symposium (2019)", "BP Advancing Energy Scholar, One Young World (2019)"],
    "memberOf": [{"@type": "Organization", "name": "IEEE"}, {"@type": "Organization", "name": "Asosiasi Energi Surya Indonesia (AESI)"}],
    "sameAs": [LINKEDIN, SCHOLAR, ORCID, HBKU],
}
ALVA = {"@type": "Organization", "@id": SITE + "/#alva-energi", "name": "Alva Energi", "legalName": "PT Alva Energi Lestari",
        "url": ALVA_URL, "foundingDate": "2017", "founder": {"@id": PERSON_ID}, "areaServed": "Indonesia"}


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


def strip_md(text):
    """Markdown to plain text, for llms-full.txt."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("**", "").replace("*", "")


def authors_html(a):
    a = esc(a)
    return re.sub(r"\bO Gandhi\b", "<strong>O Gandhi</strong>", a)


MARK = '<span class="mark" aria-hidden="true">OG</span>'

NAV = [("/expertise/", "Expertise"), ("/experience/", "Experience"), ("/publications/", "Publications"), ("/writing/", "Writing"),
       ("/media/", "Media"), ("/about/", "About"), ("#contact", "Contact")]
HAS_POSTS = any((ROOT / "content" / "posts").glob("*.md"))
if not HAS_POSTS:
    NAV = [n for n in NAV if n[0] != "/writing/"]


def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def page(path, title, description, body, active=None, jsonld=None, og_type="website", full_title=None, noindex=False):
    url = SITE + path
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{href}"{cur if href == active else ""}>{label}</a>' for href, label in NAV)
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"
    t = full_title or (f"{title} | {NAME}" if title else f"{NAME} | Solar PV, floating PV, battery storage, and grid integration")
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1"
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="author" content="{NAME}">
<meta name="theme-color" content="#13233A">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="en_GB">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title or NAME)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Oktoviano Gandhi: solar PV, floating PV, battery storage, and grid integration">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title or NAME)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE}/img/og.jpg">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="me" href="{LINKEDIN}">
<link rel="me" href="{ORCID}">
<link rel="me" href="{SCHOLAR}">
<link rel="me" href="{HBKU}">
{RSS_LINK if HAS_POSTS else ""}
<link rel="preload" href="/fonts/literata-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="site-name" href="/">{MARK}<span>{NAME}</span></a>
    <nav class="nav" aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer" id="contact">
  <div class="wrap">
    <h2>Contact</h2>
    <p>To discuss a study, a collaboration, a talk, or a media request, email <a href="mailto:{EMAIL}">{EMAIL}</a> or message me on <a href="{LINKEDIN}">LinkedIn</a>.</p>
    <ul class="links">
      <li><a href="{LINKEDIN}" rel="me">LinkedIn</a></li>
      <li><a href="{SCHOLAR}" rel="me">Google Scholar</a></li>
      <li><a href="{ORCID}" rel="me">ORCID</a></li>
      <li><a href="{HBKU}" rel="me">HBKU profile</a></li>
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
    doi_txt = f' · <span class="doi">doi:{esc(p["doi"])}</span>' if p.get("doi") else ""
    return (f'<li class="pub"{tags}><span class="year">{year}</span><div>{t}'
            f'<span class="authors">{authors_html(p["authors"])}</span><span class="venue">{esc(p["venue"])}{doi_txt}</span></div></li>')


def pub_ld(p, kind):
    item = {"@type": kind, "name": p["title"], "author": {"@id": PERSON_ID}, "creator": p["authors"], "datePublished": str(p["year"])}
    if p.get("url"):
        item["url"] = p["url"]
    if p.get("doi"):
        item["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": p["doi"]}
        item["sameAs"] = "https://doi.org/" + p["doi"]
    item["isPartOf"] = p["venue"]
    return item


def write(path, content):
    out = DIST / path.lstrip("/")
    if path.endswith("/"):
        out = out / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def portrait(sizes="15rem", eager=True):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="portrait"><picture><source srcset="/img/okto-360.webp 360w, /img/okto-720.webp 720w" sizes="{sizes}" type="image/webp">'
            f'<img src="/img/okto-720.jpg" alt="Portrait of Oktoviano Gandhi" width="720" height="900" {load}></picture></figure>')


def media_li(m):
    t = f'<a href="{esc(m["url"])}">{esc(m["title"])}</a>' if m.get("url") else esc(m["title"])
    note = f'<span class="note-line">{esc(m["note"])}</span>' if m.get("note") else ""
    return (f'<li class="media-item"><span class="year">{esc(m["date"][:4])}</span><div><span class="outlet">{esc(m["outlet"])}</span>'
            f'<span class="m-title">{t}</span>{note}</div></li>')


def news_ld(m):
    item = {"@type": m.get("schema", "NewsArticle"), "headline": m["title"], "datePublished": m["date"],
            "publisher": {"@type": "Organization", "name": m["outlet"]}, "about": {"@id": PERSON_ID}}
    if m.get("url"):
        item["url"] = m["url"]
    return item


# ---------- build ----------

def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    urls = []

    pages = {}
    for f in sorted((ROOT / "content" / "pages").glob("*.md")):
        meta, body = read_md(f)
        pages[meta["slug"]] = (meta, body)

    posts = []
    for f in (ROOT / "content" / "posts").glob("*.md"):
        meta, body = read_md(f)
        posts.append((meta, body))
    posts.sort(key=lambda m: m[0]["date"], reverse=True)

    all_pubs = ([(p, "ScholarlyArticle") for p in JOURNAL] + [(p, "Book") for p in BOOKS] + [(p, "Report") for p in REPORTS]
                + [(p, "ScholarlyArticle") for p in CONFERENCE])
    subject_of = [news_ld(m) for m in NEWS if m.get("url")]
    person = dict(PERSON, subjectOf=subject_of) if subject_of else PERSON

    def topic_meta(slug):
        return pages["expertise/" + slug][0]

    topics_html = "".join(
        f'<li><h3><a href="/expertise/{slug}/">{esc(topic_meta(slug)["title"])}</a></h3><p>{esc(topic_meta(slug)["summary"])}</p></li>'
        for tag, slug, _ in TOPICS)

    # Home (low-key: describe the work and its evidence; no pitch)
    highlights_html = "".join(
        f'<li><h3><a href="{h[3]}">{esc(h[0])}</a></h3><p class="who">{esc(h[1])}</p><p>{esc(h[2])}</p></li>' for h in P.HIGHLIGHTS)
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
    media_home = "".join(media_li(m) for m in NEWS[:3])
    orgs_html = "".join(f'<div><h3>{esc(g)}</h3><ul>{"".join(f"<li>{esc(o)}</li>" for o in items)}</ul></div>' for g, items in P.ORGS)
    orgs_section = f'<div class="orgs">{orgs_html}</div><p class="small-note">{esc(P.ORGS_NOTE)}</p>'
    home_body = f"""
<section class="hero" aria-labelledby="intro-name">
  <div class="wrap">
    <div class="intro">
      <div>
        <h1 id="intro-name">{NAME}</h1>
        <p class="lede">{esc(P.LEDE)}</p>
        <p class="standing">{esc(P.STANDING)}</p>
        <ul class="links"><li><a href="/about/">More about me</a></li><li><a href="/publications/">Publications</a></li><li><a href="{SCHOLAR}">Google Scholar</a></li><li><a href="{LINKEDIN}">LinkedIn</a></li></ul>
      </div>
      {portrait()}
    </div>
  </div>
</section>
<section class="section" aria-labelledby="topics-h">
  <div class="wrap">
    <h2 id="topics-h">What I work on</h2>
    <p class="section-intro">Each page summarises what the work found and where it has been applied, with the publications behind it.</p>
    <ul class="topics">{topics_html}</ul>
  </div>
</section>
<section class="section" aria-labelledby="work-h">
  <div class="wrap">
    <h2 id="work-h">Selected work</h2>
    <ul class="highlights">{highlights_html}</ul>
    <p class="more"><a href="/experience/">More on my experience</a></p>
  </div>
</section>
<section class="section" aria-labelledby="orgs-h">
  <div class="wrap">
    <h2 id="orgs-h">Organisations I have worked with</h2>
    {orgs_section}
  </div>
</section>
<section class="section" aria-labelledby="media-h">
  <div class="wrap">
    <h2 id="media-h">In the media</h2>
    <ul class="media-list prose">{media_home}</ul>
    <p class="more"><a href="/media/">Media, recognition, and talks</a></p>
  </div>
</section>
<section class="section" aria-labelledby="pubs-h">
  <div class="wrap">
    <h2 id="pubs-h">Selected publications</h2>
    <p class="section-intro">More than 50 peer-reviewed publications, cited more than 3,000 times on Google Scholar. <a href="/publications/">See all publications</a>.</p>
    <ul class="pubs prose">{"".join(pub_li(p, False) for p in featured)}</ul>
    <ul class="books">{books_html}</ul>
  </div>
</section>
{writing_section}"""
    home_ld = {"@context": "https://schema.org", "@graph": [
        person, ALVA,
        {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME, "publisher": {"@id": PERSON_ID}, "inLanguage": "en-GB"},
        {"@type": "ProfilePage", "@id": SITE + "/#profilepage", "url": SITE + "/", "mainEntity": {"@id": PERSON_ID}, "dateModified": TODAY}]}
    home_desc = ("Dr Oktoviano (Okto) Gandhi works on solar PV, floating PV, battery storage, grid integration, and techno-economics, "
                 "mostly in Southeast Asia. Scientist at QEERI, Hamad Bin Khalifa University; previously eleven years at SERIS, National University of Singapore.")
    write("/", page("/", "", home_desc, home_body, jsonld=home_ld))
    urls.append("/")

    # About
    meta, body = pages["about"]
    about_body = f"""
<div class="wrap page-head"><h1>About</h1></div>
<div class="wrap page-body"><div class="about-grid"><div class="prose">{md(body)}</div>
{portrait(eager=False)}</div></div>"""
    about_ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "url": SITE + "/about/", "dateModified": TODAY, "mainEntity": person},
        crumbs([("Home", "/"), ("About", "/about/")])]}
    write("/about/", page("/about/", "About", meta["description"], about_body, active="/about/", jsonld=about_ld, og_type="profile"))
    urls.append("/about/")

    # Experience
    meta, body = pages["experience"]
    exp_body = f"""
<div class="wrap page-head"><h1>{esc(meta["title"])}</h1><p class="dek">{esc(meta["summary"])}</p></div>
<div class="wrap page-body"><div class="prose experience">{md(body)}</div><h2>Organisations I have worked with</h2>{orgs_section}</div>"""
    exp_ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "url": SITE + "/experience/", "name": f"Experience of {NAME}", "description": meta["description"],
         "about": {"@id": PERSON_ID}, "dateModified": TODAY},
        crumbs([("Home", "/"), ("Experience", "/experience/")])]}
    write("/experience/", page("/experience/", "Experience", meta["description"], exp_body, active="/experience/", jsonld=exp_ld))
    urls.append("/experience/")

    # Expertise
    write("/expertise/", page("/expertise/", "Expertise",
                              f"{NAME}'s expertise: floating PV, grid integration and regulation, solar forecasting, PV performance and technology choice, techno-economics and feasibility, and off-grid and island power systems.",
                              f'<div class="wrap page-head"><h1>Expertise</h1><p class="dek">What I work on: what the work found, where it has been applied, and the publications behind it.</p></div><div class="wrap page-body"><ul class="topics">{topics_html}</ul></div>',
                              active="/expertise/", jsonld={"@context": "https://schema.org", **crumbs([("Home", "/"), ("Expertise", "/expertise/")])}))
    urls.append("/expertise/")
    for tag, slug, _ in TOPICS:
        meta, body = pages["expertise/" + slug]
        related = [p for p, _ in all_pubs if tag in p.get("tags", [])]
        related.sort(key=lambda p: (-p["year"], not p.get("featured", False)))
        rel_html = "".join(pub_li(p, False) for p in related[:12])
        more = f'<p class="more"><a href="/publications/?topic={tag}">All {len(related)} publications on this topic</a></p>' if len(related) > 12 else ""
        others = "".join(f'<li><a href="/expertise/{s}/">{esc(topic_meta(s)["title"])}</a></li>' for t2, s, _ in TOPICS if s != slug)
        tbody = f"""
<div class="wrap page-head"><p class="kicker"><a href="/expertise/">Expertise</a></p><h1>{esc(meta["title"])}</h1><p class="dek">{esc(meta["summary"])}</p></div>
<div class="wrap page-body"><div class="prose">{md(body)}
<h2>Publications</h2><ul class="pubs">{rel_html}</ul>{more}
<h2>Other expertise</h2><ul class="plain">{others}</ul></div></div>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebPage", "url": f"{SITE}/expertise/{slug}/", "name": meta["title"], "description": meta["description"],
             "author": {"@id": PERSON_ID}, "about": {"@type": "Thing", "name": meta["title"]}, "dateModified": TODAY,
             "mentions": [pub_ld(p, "ScholarlyArticle") for p in related[:12]]},
            crumbs([("Home", "/"), ("Expertise", "/expertise/"), (meta["title"], f"/expertise/{slug}/")])]}
        write(f"/expertise/{slug}/", page(f"/expertise/{slug}/", meta["title"], meta["description"], tbody, active="/expertise/", jsonld=ld))
        urls.append(f"/expertise/{slug}/")

    # Publications
    filt = '<div class="filters" role="group" aria-label="Filter by topic"><button type="button" data-tag="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-tag="{tag}" aria-pressed="false">{esc(TOPIC_SHORT[tag])}</button>' for tag, _, _ in TOPICS) + "</div>"
    groups = [("Books", BOOKS), ("Journal articles", JOURNAL), ("Reports and articles", REPORTS), ("Conference papers", CONFERENCE)]
    groups_html = "".join(f'<section class="pub-group"><h2>{g}</h2><ul class="pubs">{"".join(pub_li(p) for p in items)}</ul></section>' for g, items in groups)
    pub_body = f"""
<div class="wrap page-head"><h1>Publications</h1><p class="dek">Books, journal articles, reports, and conference papers. More than 3,000 citations and an h-index of 27 on <a href="{SCHOLAR}">Google Scholar</a> (October 2026).</p></div>
<div class="wrap page-body"><div class="prose">{filt}{groups_html}</div></div>"""
    pub_ld_all = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "url": SITE + "/publications/", "name": f"Publications by {NAME}", "author": {"@id": PERSON_ID},
         "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": pub_ld(p, k)} for i, (p, k) in enumerate(all_pubs)]}},
        crumbs([("Home", "/"), ("Publications", "/publications/")])]}
    write("/publications/", page("/publications/", "Publications",
                                 f"Books, journal articles, reports, and conference papers by {NAME} on floating PV, grid integration, solar forecasting, PV performance, techno-economics, and off-grid power systems.",
                                 pub_body, active="/publications/", jsonld=pub_ld_all))
    urls.append("/publications/")

    # Media
    news_html = "".join(media_li(m) for m in NEWS)
    rec_html = "".join(media_li(m) for m in RECOGNITION)
    talks_html = "".join(media_li(m) for m in TALKS)
    media_body = f"""
<div class="wrap page-head"><h1>Media, recognition, and talks</h1><p class="dek">Coverage of my work, awards, and selected talks and panels. For media requests, email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div>
<div class="wrap page-body"><div class="prose">
<h2>In the media</h2><ul class="media-list">{news_html}</ul>
<h2>Recognition</h2><ul class="media-list">{rec_html}</ul>
<h2>Talks and panels</h2><ul class="media-list">{talks_html}</ul>
</div></div>"""
    media_ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "url": SITE + "/media/", "name": f"{NAME} in the media", "about": {"@id": PERSON_ID},
         "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": news_ld(m)} for i, m in enumerate(NEWS)]}},
        crumbs([("Home", "/"), ("Media", "/media/")])]}
    write("/media/", page("/media/", "Media", f"{NAME} in the media, including AP News on floating solar, with awards and selected talks on floating PV, grid integration, and the energy transition in Southeast Asia.",
                          media_body, active="/media/", jsonld=media_ld))
    urls.append("/media/")

    if posts:
        build_writing(posts, urls)

    _rest(urls, posts, pages, all_pubs)


def build_writing(posts, urls):
    w_list = "".join(
        f'<li><h3><a href="/{m["slug"]}/">{esc(m["title"])}</a></h3><p>{esc(m["description"])}</p><span class="meta">{esc(m["date_label"])}. Series: {esc(m.get("series", ""))}</span></li>'
        for m, _ in posts)
    write("/writing/", page("/writing/", "Writing", f"Articles by {NAME} on solar PV, grid integration, and research practice.",
                            f'<div class="wrap page-head"><h1>Writing</h1><p class="dek">New articles on solar PV and power systems will appear here.</p></div><div class="wrap page-body"><ul class="posts">{w_list}</ul></div>',
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


# Old addresses (the 2023 WordPress site and the first 2026 build) and where they now point.
REDIRECTS = {
    "/topics/": "/expertise/",
    "/topics/floating-pv/": "/expertise/floating-pv/",
    "/topics/grid-integration/": "/expertise/grid-integration/",
    "/topics/pv-in-hot-climates/": "/expertise/pv-performance/",
    "/topics/southeast-asia/": "/experience/",
}
try:
    from redirects import OLD_SITE  # noqa: E402  (old WordPress paths, from the Wayback Machine)
    REDIRECTS.update(OLD_SITE)
except ImportError:
    pass


def redirect_page(old, new):
    target = SITE + new
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>Moved</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={new}">
<script>location.replace({json.dumps(new)} + location.search + location.hash);</script>
</head><body><p>This page has moved to <a href="{new}">{target}</a>.</p></body></html>
"""


def llms_txt(pages):
    lines = [f"# {NAME}", "",
             "> Dr Oktoviano (Okto) Gandhi is a solar PV and power systems specialist: floating PV, battery storage, grid integration and ancillary services, "
             "solar forecasting, PV performance, and techno-economics, mostly in Southeast Asia. Scientist at the Qatar Environment and Energy Research Institute "
             "(QEERI), Hamad Bin Khalifa University; previously eleven years at the Solar Energy Research Institute of Singapore (SERIS), National University of Singapore; "
             "co-founder of Alva Energi, Indonesia. Indonesian; works in English, Indonesian, and Malay.", "",
             "Key facts: feasibility studies for more than 7 GWp of PV and 1 GWh of battery storage (ADB, World Bank, IDB, USAID, and private clients); "
             "maintained the SERIS Global Floating PV Database (about 1,700 projects in 66 countries, 2022 to 2026); one of three main authors of GIZ studies for "
             "Indonesia's Ministry of Energy and Mineral Resources on ancillary services and on battery storage regulation; led PV grid integration in Singapore's "
             "national solar forecasting programme for the Energy Market Authority and Singapore Power (2019 to 2022); more than 50 peer-reviewed publications "
             "with more than 3,000 citations; PhD, National University of Singapore; MPhys, University of Oxford.", "",
             "## Profile", "",
             f"- [About]({SITE}/about/): biography, education, memberships, and recognition",
             f"- [Experience]({SITE}/experience/): selected assignments since 2015, by type of problem",
             f"- [Media, recognition, and talks]({SITE}/media/): press coverage (including AP News, 2026), awards, and talks",
             f"- [Publications]({SITE}/publications/): books, journal articles, reports, and conference papers, with DOIs", "",
             "## Expertise", ""]
    for tag, slug, _ in TOPICS:
        m = pages["expertise/" + slug][0]
        lines.append(f"- [{m['title']}]({SITE}/expertise/{slug}/): {m['summary']}")
    lines += ["", "## Elsewhere", "", f"- [LinkedIn]({LINKEDIN})", f"- [Google Scholar]({SCHOLAR})", f"- [ORCID]({ORCID})", f"- [Hamad Bin Khalifa University staff profile]({HBKU})", f"- [Alva Energi]({ALVA_URL})", "",
              "## Optional", "", f"- [Full text of the main pages]({SITE}/llms-full.txt)", "", f"Contact: {EMAIL}", ""]
    return "\n".join(lines)


def llms_full(pages, all_pubs):
    out = [f"# {NAME}: full text of ogandhi.com", f"Source: {SITE}/ (generated {TODAY})", ""]
    for key, url in [("about", "/about/"), ("experience", "/experience/")]:
        m, body = pages[key]
        out += [f"## {m['title']} ({SITE}{url})", "", strip_md(body), ""]
    for tag, slug, _ in TOPICS:
        m, body = pages["expertise/" + slug]
        out += [f"## {m['title']} ({SITE}/expertise/{slug}/)", "", m["summary"], "", strip_md(body), ""]
    out += ["## Media and recognition", ""]
    for m in NEWS + RECOGNITION:
        out.append(f"- {m['date'][:4]}. {m['outlet']}: {m['title']}" + (f" {m['url']}" if m.get("url") else ""))
    out += ["", "## Publications", ""]
    for p, _ in all_pubs:
        out.append(f"- {p['authors']} ({p['year']}). {p['title']}. {p['venue']}." + (f" {p['url']}" if p.get("url") else ""))
    return "\n".join(out) + "\n"


def _rest(urls, posts, pages, all_pubs):
    write("/404.html", page("/404.html", "Page not found", "This page does not exist.",
                            '<div class="wrap page-head"><h1>Page not found</h1><p class="dek">This address has no page. Try the <a href="/">home page</a>, <a href="/expertise/">expertise</a>, <a href="/experience/">experience</a>, or <a href="/publications/">publications</a>.</p></div>',
                            noindex=True))
    for old, new in REDIRECTS.items():
        if old in urls:
            continue  # a real page lives here now
        write(old if old.endswith("/") or old.endswith(".html") else old + "/", redirect_page(old, new))

    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>', encoding="utf-8")
    bots = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
            "Claude-User", "PerplexityBot", "Perplexity-User", "Applebot-Extended", "CCBot"]
    robots = "# Search engines and AI assistants are welcome to read and cite this site.\n\n" + "".join(
        f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"
    (DIST / "robots.txt").write_text(robots, encoding="utf-8")
    (DIST / "llms.txt").write_text(llms_txt(pages), encoding="utf-8")
    (DIST / "llms-full.txt").write_text(llms_full(pages, all_pubs), encoding="utf-8")
    if posts:
        items = "".join(
            f"<item><title>{esc(m['title'])}</title><link>{SITE}/{m['slug']}/</link><guid>{SITE}/{m['slug']}/</guid><description>{esc(m['description'])}</description><pubDate>{date.fromisoformat(m['date']).strftime('%a, %d %b %Y')} 00:00:00 +0000</pubDate></item>"
            for m, _ in posts)
        (DIST / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Writing by {NAME}</title><link>{SITE}/writing/</link><description>Articles on solar PV, battery storage, and grid integration.</description><language>en-gb</language>{items}</channel></rss>', encoding="utf-8")
    (DIST / "CNAME").write_text("ogandhi.com\n", encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(urls)} pages and {len(REDIRECTS)} redirects into {DIST}")


if __name__ == "__main__":
    build()
