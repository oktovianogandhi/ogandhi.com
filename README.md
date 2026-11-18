# ogandhi.com

Static personal website of Oktoviano Gandhi. Built by Claude; maintained by Claude on request.

- Edit content in `content/pages/` (About, Experience, and expertise pages), `data/profile_data.py` (home page), `data/publications.py` (publication list, from the publication register), `data/media.py` (media, recognition, and talks), and `content/posts/` (writing).
- Build: `pip install markdown` then `python3 build.py`. Output goes to `docs/`, which GitHub Pages serves at https://ogandhi.com (branch `main`, folder `/docs`).
- `docs/` holds everything to publish: pages, redirect pages for old addresses, `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, `feed.xml` (when there are posts), `CNAME`, fonts (Literata and Atkinson Hyperlegible, SIL Open Font Licence), and images.
- `content/unpublished/` holds the two 2021 posts from the old blog (not published, at Okto's request, 18 Nov 2026). To publish one, move it to `content/posts/` and its figure to `static/img/`; it keeps its original WordPress URL. The Writing page, nav item, and RSS feed appear automatically once `content/posts/` has a post.
