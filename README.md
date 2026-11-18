# ogandhi.com

Static personal website of Oktoviano Gandhi. Built by Claude; maintained by Claude on request.

- Edit content in `content/pages/` (About and topic pages), `content/posts/` (writing) and `data/publications.py` (publication list, from the publication register).
- Build: `pip install markdown` then `python3 build.py`. Output goes to `docs/`, which GitHub Pages serves at https://ogandhi.com (branch `main`, folder `/docs`).
- `docs/` holds everything to publish: pages, `sitemap.xml`, `robots.txt`, `feed.xml`, `CNAME`, fonts (Literata and Atkinson Hyperlegible, SIL Open Font Licence) and images.
- `content/unpublished/` holds the two 2021 posts from the old blog (not published, at Okto's request, 18 Nov 2026). To publish one, move it to `content/posts/` and its figure to `static/img/`; it keeps its original WordPress URL. The Writing page, nav item and RSS feed appear automatically once `content/posts/` has a post.
