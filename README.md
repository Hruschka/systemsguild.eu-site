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

## Local preview

```bash
bundle install          # once (Ruby 3.3 or newer)
bundle exec jekyll serve
open http://127.0.0.1:4000/
```

## Checks

```bash
bundle exec jekyll build
bundle exec htmlproofer ./_site --disable-external --no-enforce-https --ignore-files "/assets\/uploads\/.*\.html/"
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python -m unittest discover -s tools/tests -t .
.venv/bin/python -m tools.check_urls   # every old WordPress URL still resolves
```

## Deployment

`.github/workflows/pages.yml` builds the site with Jekyll 4 on every push to `main` and deploys it to GitHub Pages. Going live on the domain is described in `docs/cutover.md`.

## Layout

`_layouts/` (default, page, post, listing), `_includes/` (header, footer, news, books, rule, figure, post-meta, post-list) and one stylesheet `assets/css/main.css` reproduce the previous WordPress (Impreza) design. Colors are CSS variables at the top of the stylesheet.

## Migration tooling (one-off)

`tools/wp_export.py` pulled all content from the WordPress REST API, `tools/convert_posts.py` converted the posts, `tools/pages_to_markdown.py` produced drafts for the manually converted pages. They are kept for reference; the export itself (`reference/export/`) is not committed. `reference/original-site/` holds HTML and screenshots of the old site.

Note for editors: `/events/` lists a single placeholder event (“Killer”, 2021) that was test content in WordPress. It was migrated unchanged and can be removed by deleting `_pages/events.md`. `/sample-page/` is the WordPress default sample page, also kept unchanged.
