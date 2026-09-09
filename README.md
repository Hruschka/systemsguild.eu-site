# systemsguild.eu

Static website of **The Atlantic Systems Guild**, built with [Jekyll](https://jekyllrb.com) and hosted on GitHub Pages.
Migrated from WordPress in September 2026 (see `docs/migration-plan.md`).

## Editing content

Everything is plain text in this repository. Edit on GitHub (pencil icon) or locally, commit to `main`, and the site is rebuilt and published automatically within about a minute.

### Publish a new Culture Killer post

Create `_posts/YYYY-MM-DD-short-slug.md`:

```markdown
---
title: The Title of the Post
author: james-robertson        # key from _data/authors.yml
tags: [culture, hr]            # tag slugs (URL: /tag/<slug>/)
tag_names: ["#culture", "#hr"] # how the tags are displayed
---
Introductory paragraph …

{% include rule.html text="The unspoken rule, shown next to the skull." %}

More text …
```

The newest post automatically appears on the home page under “This Week’s Culture Killer”, in `/category/culture-killers/`, in the tag pages and in the RSS feed (`/feed.xml`).
Post URLs are `/<slug>/`, taken from the file name after the date.

To place an image: `{% include figure.html src="/assets/uploads/2026/09/photo.jpg" alt="…" align="right" width="200px" %}`

### News sidebar (home page)

Edit `_data/news.yml`. One entry per item, newest first: `image` (optional), `link` (optional, wraps the image), `html` (the text, inline HTML links allowed).

### Guild Books

Edit `_data/books.yml`: `title`, `authors`, `cover`, `blurb` (optional, inline HTML allowed), `links` (list of `label` + `url`).

### Pages

Pages live in `_pages/<slug>.md` with front matter `title` and `permalink: /<slug>/`. Person pages, About, Contact, Culture, Riskology and the Events page are there. The main menu is `_data/navigation.yml`.

### Images and files

Put uploads under `assets/uploads/YYYY/MM/` (the WordPress media library was migrated with this structure) and reference them as `/assets/uploads/YYYY/MM/file.jpg`.

## Local development (Docker only)

Nothing needs to be installed locally except **Docker** and **make**: no Ruby, no Bundler, no Python. This mirrors the arc42 site repositories.

```bash
make build   # once: build the two images (needs network; ~1 minute)
make dev     # Jekyll with file watching at http://localhost:4280
```

Open **http://localhost:4280** (not `0.0.0.0`, Firefox refuses that). Edit any file; Jekyll rebuilds in well under a second. Stop with Ctrl-C or `make stop`.

| Target | What it does |
|---|---|
| `make dev` | Start the dev server on port 4280 with file watching. |
| `make build` | Build the `systemsguild-site` (Jekyll) and `systemsguild-tools` (Python) images. |
| `make site` | Production build (`JEKYLL_ENV=production`, like GitHub Pages) into `_site/`. |
| `make check-links` | Build, then validate internal links, images and HTML with html-proofer. |
| `make test` | Build, run the Python unit tests and verify every old WordPress URL exists in `_site/`. |
| `make check` | `check-links` + `test`: everything worth running before a push. |
| `make shell` | Shell inside the Jekyll container. |
| `make install` / `make update` | Refresh or update gems after editing the `Gemfile`; then rebuild. |
| `make clean` | Remove `_site/` and the Docker cache volumes. |
| `make logs` / `make stop` | Tail or stop the dev container. |

Port **4280** is fixed on purpose: every site in the arc42 family has its own port in the `42xx` block so their dev servers can run side by side (see `raw/port-assignment.md` in meta.arc42.org). The number is stated in the `Makefile`, in `docker-compose.yml` (mapping and `--port`) and in the `Dockerfile` (`EXPOSE` and `CMD`); change all three together.

### macOS notes

- The base images are multi-arch, so on Apple Silicon everything runs natively.
- Jekyll's caches live in named Docker volumes and the dev server writes its output to `/tmp/_site` inside the container, not to the bind-mounted project folder. Writing thousands of small files through the macOS file sharing layer is the slow path on Docker Desktop, and this keeps it off it. `make site` writes `_site/` to the host as usual.
- File changes are detected by polling (`--force_polling`), because Docker Desktop does not reliably forward change events into the container. If it works for you, set `POLLING=` (empty) in `docker-compose.yml` to save CPU.
- After `make update` or any change to `Gemfile.lock`, the container refuses to start until the image is rebuilt: the entrypoint compares the lock file against the gems baked into the image, so stale gems are never served silently.

### GitHub Pages compatibility

The Docker image and the GitHub Actions workflow both build with **Jekyll 4.4 from the same `Gemfile.lock`**, so what `make site` produces is what GitHub Pages publishes. Docker files, the Makefile, `tools/`, `docs/` and `reference/` are excluded in `_config.yml` and never end up in the published site.

## Deployment

`.github/workflows/pages.yml` builds the site with Jekyll 4 on every push to `main` and deploys it to GitHub Pages. Going live on the domain is described in `docs/cutover.md`.

## Layout

`_layouts/` (default, page, post, listing), `_includes/` (header, footer, news, books, rule, figure, post-meta, post-list) and one stylesheet `assets/css/main.css` reproduce the previous WordPress (Impreza) design. Colors are CSS variables at the top of the stylesheet.

## Migration tooling (one-off)

`tools/wp_export.py` pulled all content from the WordPress REST API, `tools/convert_posts.py` converted the posts, `tools/pages_to_markdown.py` produced drafts for the manually converted pages. They are kept for reference; the export itself (`reference/export/`) is not committed. They run inside the tools image, e.g. `docker compose --profile tools run --rm tools python -m tools.wp_export`. `reference/original-site/` holds HTML and screenshots of the old site.

Note for editors: `/events/` lists a single placeholder event (“Killer”, 2021) that was test content in WordPress. It was migrated unchanged and can be removed by deleting `_pages/events.md`. `/sample-page/` is the WordPress default sample page, also kept unchanged.
