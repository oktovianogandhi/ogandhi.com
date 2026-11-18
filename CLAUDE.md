# ogandhi.com: notes for Claude

Okto Gandhi's personal website. Claude builds and maintains it; Okto approves content.

- Build: `pip install markdown --break-system-packages` (if missing), then `python3 build.py`. It rewrites `docs/`. Always rebuild and commit `docs/` together with source changes; GitHub Pages serves `main:/docs` with no build step.
- Content: `content/pages/*.md` (About and topic pages, front matter at the top), `content/posts/*.md` (writing; the Writing page, nav item and RSS feed appear only when this folder has posts), `content/unpublished/` (not built), `data/publications.py` (keep in step with the project doc "Publication register - Okto Gandhi").
- Before publishing: take screenshots (desktop and mobile) and look at them; check every fact against Okto's own sources (publication register, master experience register, LinkedIn About). Do not invent findings from paper titles.
- Content rules: British English; consultancy-neutral while Okto is at QEERI (no services, rates or "available for consulting"); nothing on live assignments or unpublished SERIS/QEERI data; describe QEERI work broadly. The full record is the project doc "Website ogandhi.com - setup record".
- Design: palette and type are defined in `static/css/site.css`; the amber clear-sky generation curve is the only decorative element. Keep it that way.
