# systemsguild.eu WordPress → Jekyll Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild https://systemsguild.eu/ as a Jekyll 4 site in this repository, with every WordPress page, post, event and media file migrated, the original layout reproduced, and deployment via GitHub Pages.

**Architecture:** Content lives as Markdown (posts, pages) and YAML data files (news, books, navigation). Three Liquid layouts plus a handful of includes and one hand-written CSS file reproduce the Impreza look. Python scripts under `tools/` pull content from the open WordPress REST API and convert posts automatically; pages are converted by hand from pandoc output. A GitHub Actions workflow builds with Jekyll 4.4 and deploys to GitHub Pages.

**Tech Stack:** Jekyll 4.4, jekyll-feed, jekyll-seo-tag, jekyll-sitemap, jekyll-redirect-from, html-proofer (test), Python 3 (venv: pyyaml, beautifulsoup4), pandoc 3, GitHub Actions, GitHub Pages, `gh` CLI.

**Spec:** `docs/migration-plan.md`

## Global Constraints

- No paid software. Only open-source gems/tools listed above.
- No content is dropped: all 15 pages, 28 posts, 1 event, 98 media files, contact details (spec §5.3).
- Every existing public URL keeps working (spec §3 Phase 4): posts and pages at `/<slug>/`, `/category/culture-killers/`, `/tag/<slug>/`, `/author/<slug>/`, `/events/`, `/event/killer`, `/feed`.
- Layout as close as possible to the original: header `#2c3e50`, header text `#edf0f2`, active/hover `#fc4349`, body text `#46515c`, headings `#2c3e50`, links `#43a9d1`, alt background `#f2f4f5`, footer `#384b5f` with text `#9aa7b5`, content width 1140px, system sans-serif fonts, mobile nav below 900px.
- All internal links and asset URLs go through the `relative_url` filter so the site works both under the temporary `https://<user>.github.io/<repo>/` URL and under `https://systemsguild.eu/`.
- Editors edit Markdown/YAML directly; no CMS.
- Commit after every task. Commit messages end with the attribution lines given in the session.
- Local Ruby is 4.0: the Gemfile must include `csv`, `base64`, `bigdecimal`, `webrick`, `logger`.
- Reference material (do not modify): `reference/original-site/`.

## File structure (target)

```
.
├── .github/workflows/pages.yml     # build + deploy
├── .gitignore
├── Gemfile                         # jekyll 4.4 + plugins
├── _config.yml
├── README.md                       # how to edit and publish
├── index.html                      # home: hero, latest post, NEWS sidebar
├── 404.html
├── _layouts/default.html           # <html>, header, footer
├── _layouts/page.html              # plain page
├── _layouts/post.html              # culture-killer post
├── _layouts/listing.html           # category/tag/author post lists
├── _includes/head.html
├── _includes/header.html           # nav from _data/navigation.yml
├── _includes/footer.html
├── _includes/rule.html             # skull + unspoken-rule quote
├── _includes/figure.html           # floated image
├── _includes/news.html             # NEWS sidebar from _data/news.yml
├── _includes/books.html            # book list from _data/books.yml
├── _includes/post-list.html        # used by listing layout
├── _data/navigation.yml
├── _data/news.yml
├── _data/books.yml
├── _data/authors.yml               # author slug -> name, page
├── _posts/2025-MM-DD-<slug>.md     # 28 files
├── _pages/<slug>.md                # 15 pages incl. people, events, leftovers
├── category/culture-killers.md
├── tag/<slug>.md                   # 13 files
├── author/james-robertson.md, author/tom-demarco.md
├── feed/index.html                 # redirect /feed -> /feed.xml
├── assets/css/main.css
├── assets/uploads/YYYY/MM/<file>   # mirrors wp-content/uploads
├── tools/requirements.txt
├── tools/wp_export.py              # REST -> reference/export/*.json + media download
├── tools/convert_posts.py          # export json -> _posts/*.md, tag/*.md
├── tools/pages_to_markdown.py      # export json -> reference/export/pages-md/*.md (starting points)
├── tools/check_urls.py             # every WP URL resolves in _site
└── tools/tests/test_convert_posts.py, test_wp_export.py
```

---

### Task 1: Repository skeleton that builds

**Files:**
- Create: `.gitignore`, `Gemfile`, `_config.yml`, `index.html`, `_layouts/default.html`, `_includes/head.html`

**Interfaces:**
- Produces: `_config.yml` keys used everywhere later: `title`, `description`, `url`, `permalink`, `collections.pages`, `defaults`. Build command `bundle exec jekyll build` (output in `_site/`).

- [ ] **Step 1: Initialise git and ignore build output**

```bash
cd /Users/gernotstarke/projects/arc42/systemsguild.eu-site
git init -b main
cat > .gitignore <<'EOF'
_site/
.jekyll-cache/
.jekyll-metadata
.sass-cache/
vendor/
.bundle/
.venv/
__pycache__/
.DS_Store
reference/export/
EOF
```

- [ ] **Step 2: Gemfile**

```ruby
source "https://rubygems.org"

gem "jekyll", "~> 4.4"

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
  gem "jekyll-redirect-from"
end

# Ruby >= 3.4 no longer bundles these
gem "csv"
gem "base64"
gem "bigdecimal"
gem "webrick"
gem "logger"

group :test do
  gem "html-proofer"
end
```

- [ ] **Step 3: _config.yml**

```yaml
title: The Atlantic Systems Guild
description: The members of the Atlantic Systems Guild practice, teach, and improve the fields of system requirements definition, team leadership, and project management.
url: "https://systemsguild.eu"
baseurl: ""
lang: en
timezone: Europe/Berlin

permalink: /:title/
excerpt_separator: "\n\n"

plugins:
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-sitemap
  - jekyll-redirect-from

feed:
  path: feed.xml

collections:
  pages:
    output: true
    permalink: /:title/

defaults:
  - scope: { path: "" }
    values: { layout: page }
  - scope: { path: "", type: posts }
    values: { layout: post, category: culture-killers }
  - scope: { path: "", type: pages }
    values: { layout: page }

exclude:
  - Gemfile
  - Gemfile.lock
  - vendor
  - node_modules
  - tools
  - reference
  - docs
  - README.md
  - LICENSE
```

- [ ] **Step 4: Minimal default layout, head include and index**

`_includes/head.html`:
```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{% seo %}
<link rel="stylesheet" href="{{ '/assets/css/main.css' | relative_url }}">
{% feed_meta %}
```

`_layouts/default.html`:
```html
<!doctype html>
<html lang="{{ site.lang }}">
<head>
{% include head.html %}
</head>
<body class="{{ page.body_class | default: 'page' }}">
{% include header.html %}
<main class="l-main">
{{ content }}
</main>
{% include footer.html %}
</body>
</html>
```

Temporary `_includes/header.html` and `_includes/footer.html` each containing one line (`<header class="l-header"></header>` / `<footer class="l-footer"></footer>`); Task 2 replaces them.

`index.html`:
```html
---
layout: default
title: Home
---
<p>Placeholder</p>
```

- [ ] **Step 5: Install and build**

```bash
bundle config set --local path vendor
bundle install
bundle exec jekyll build
ls _site
```
Expected: `_site/index.html`, `_site/feed.xml`, `_site/sitemap.xml`, `_site/robots.txt` exist; no error lines (Ruby "warning:" lines are acceptable).

- [ ] **Step 6: Commit**

```bash
git add .gitignore Gemfile Gemfile.lock _config.yml index.html _layouts _includes docs reference
git commit -m "chore: Jekyll 4 skeleton, migration plan and reference snapshot"
```

---

### Task 2: Layout and CSS reproducing the Impreza look

**Files:**
- Create: `_data/navigation.yml`, `_includes/header.html`, `_includes/footer.html`, `_layouts/page.html`, `assets/css/main.css`
- Modify: `index.html` (temporary content to exercise the layout)

**Interfaces:**
- Produces: CSS classes `l-header`, `l-nav`, `l-main`, `l-content` (1140px column), `l-footer`, `two-col` (67/28 split), `bg-alt`; body class `home` set via `page.body_class`.

- [ ] **Step 1: Navigation data**

`_data/navigation.yml`:
```yaml
- title: This Week’s Culture Killer
  url: /
- title: About the Guild
  url: /about-the-guild/
- title: Guild Books
  url: /guild-books/
- title: Contact
  url: /contact/
```

- [ ] **Step 2: Header include**

`_includes/header.html`:
```html
<header class="l-header">
  <div class="l-content l-header-inner">
    <a class="site-title" href="{{ '/' | relative_url }}">{{ site.title }}</a>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="Open menu">
    <label for="nav-toggle" class="nav-toggle-label"><span></span><span></span><span></span></label>
    <nav class="l-nav">
      <ul>
      {% for item in site.data.navigation %}
        {% assign active = false %}
        {% if item.url == page.url or (item.url == '/' and page.url == '/') %}{% assign active = true %}{% endif %}
        {% if item.url == '/' and page.layout == 'post' %}{% assign active = true %}{% endif %}
        <li{% if active %} class="active"{% endif %}><a href="{{ item.url | relative_url }}">{{ item.title }}</a></li>
      {% endfor %}
      </ul>
    </nav>
    <a class="mail-link" href="mailto:cultureproject@systemsguild.com">&#9993; MAIL</a>
  </div>
</header>
```

- [ ] **Step 3: Footer include and page layout**

`_includes/footer.html`:
```html
<footer class="l-footer">
  <div class="l-content">
    <p>&copy; {{ 'now' | date: '%Y' }} The Atlantic Systems Guild</p>
  </div>
</footer>
```

`_layouts/page.html`:
```html
---
layout: default
---
<article class="l-content page-content">
{% if page.show_title %}<h1>{{ page.title }}</h1>{% endif %}
{{ content }}
</article>
```

- [ ] **Step 4: Stylesheet**

`assets/css/main.css`:
```css
:root{
  --c-header-bg:#2c3e50; --c-header-text:#edf0f2; --c-accent:#fc4349;
  --c-text:#46515c; --c-heading:#2c3e50; --c-link:#43a9d1; --c-link-hover:#fc4349;
  --c-bg:#ffffff; --c-bg-alt:#f2f4f5; --c-border:#e3e6e8;
  --c-footer-bg:#384b5f; --c-footer-text:#9aa7b5; --c-footer-link:#edf0f2;
  --content-width:1140px; --header-h:60px;
}
*{box-sizing:border-box}
html{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.7;color:var(--c-text);background:var(--c-bg)}
body{margin:0;padding-top:var(--header-h)}
a{color:var(--c-link);text-decoration:none}
a:hover{color:var(--c-link-hover)}
h1,h2,h3,h4{color:var(--c-heading);font-weight:400;line-height:1.3;margin:0 0 .6em}
h1{font-size:2rem}h2{font-size:1.6rem}h3{font-size:1.3rem}h4{font-size:1.15rem;font-weight:700}
p{margin:0 0 1.5rem}
img{max-width:100%;height:auto}
.l-content{max-width:var(--content-width);margin:0 auto;padding:0 1.5rem}

/* header */
.l-header{position:fixed;top:0;left:0;right:0;height:var(--header-h);background:var(--c-header-bg);color:var(--c-header-text);box-shadow:0 1px 3px rgba(0,0,0,.2);z-index:10}
.l-header-inner{display:flex;align-items:center;height:100%;gap:1.5rem}
.site-title{color:var(--c-header-text);font-size:.95rem;white-space:nowrap}
.l-nav{flex:1;display:flex;justify-content:center}
.l-nav ul{list-style:none;margin:0;padding:0;display:flex;gap:2rem}
.l-nav a{color:var(--c-header-text);font-size:.95rem}
.l-nav a:hover,.l-nav li.active a{color:var(--c-accent)}
.mail-link{color:var(--c-header-text);font-size:.85rem;font-weight:600;white-space:nowrap}
.nav-toggle,.nav-toggle-label{display:none}

/* main */
.l-main{padding:2.5rem 0 4rem;min-height:60vh}
.page-content h1{text-transform:uppercase;font-size:1.7rem;margin-bottom:.5rem}
.two-col{display:flex;gap:5%;align-items:flex-start}
.two-col .col-main{width:67%}
.two-col .col-side{width:28%}
.bg-alt{background:var(--c-bg-alt)}

/* home */
.hero{margin:0 0 1.5rem}
.hero img{display:block;width:100%}
.latest-post{padding:1.5rem;background:var(--c-bg-alt)}
.latest-post h2{text-align:center;color:#8b0000;font-size:1.7rem}
.news h2{font-size:1.6rem;text-transform:uppercase;margin-bottom:1rem}
.news-item{display:flex;gap:1rem;padding:1rem 0;border-bottom:1px solid var(--c-link);font-size:.9rem}
.news-item:nth-child(even){flex-direction:row-reverse}
.news-item img{width:40%;flex:none;object-fit:contain;align-self:flex-start}
.news-item p{margin:0}

/* posts */
.rule{display:flex;align-items:center;gap:1.5rem;margin:1.5rem 0 1.5rem 3rem}
.rule img{width:15%;max-width:110px;flex:none}
.rule h4{margin:0;font-size:1.4rem;font-weight:700}
.post-meta{font-size:.85rem;color:#7a8794;margin:1rem 0}
.post-meta a{margin-right:.3rem}
.post-list{list-style:none;padding:0}
.post-list li{padding:1rem 0;border-bottom:1px solid var(--c-border)}
.post-list .date{color:#7a8794;font-size:.85rem;margin-left:.5rem}

/* figures */
.figure{margin:0 0 1rem}
.figure.left{float:left;margin:0 1.5rem 1rem 0;max-width:40%}
.figure.right{float:right;margin:0 0 1rem 1.5rem;max-width:40%}
.clearfix::after{content:"";display:table;clear:both}

/* books */
.book{display:flex;gap:2rem;padding:2rem 0;border-bottom:1px solid var(--c-border)}
.book img{width:200px;flex:none;align-self:flex-start;box-shadow:0 1px 4px rgba(0,0,0,.15)}
.book h3{font-size:1rem;font-weight:700}
.book .by{font-weight:700}
.book ul{list-style:none;padding:0;margin:0}

/* footer */
.l-footer{background:var(--c-footer-bg);color:var(--c-footer-text);text-align:center;padding:3rem 0;font-size:.9rem}
.l-footer a{color:var(--c-footer-link)}
.l-footer p{margin:0}

/* mobile (Impreza switches at 900px) */
@media (max-width:900px){
  .nav-toggle-label{display:flex;flex-direction:column;gap:5px;cursor:pointer;margin-left:auto}
  .nav-toggle-label span{display:block;width:24px;height:2px;background:var(--c-header-text)}
  .mail-link{display:none}
  .l-nav{position:absolute;top:var(--header-h);left:0;right:0;background:var(--c-header-bg);display:none}
  .l-nav ul{flex-direction:column;gap:0;padding:.5rem 1.5rem 1rem}
  .l-nav li{padding:.5rem 0}
  .nav-toggle:checked ~ .l-nav{display:block}
  .two-col{flex-direction:column}
  .two-col .col-main,.two-col .col-side{width:100%}
  .news-item,.news-item:nth-child(even){flex-direction:column}
  .news-item img{width:60%}
  .book{flex-direction:column}
  .figure.left,.figure.right{float:none;max-width:100%;margin:0 0 1rem}
  .rule{margin-left:0}
}
```

- [ ] **Step 5: Temporary index content to exercise the layout**

Replace `index.html` body with:
```html
<div class="l-content two-col">
  <div class="col-main latest-post"><h2>Workplace Culture: This Week’s Culture Killer</h2><p>Lorem ipsum placeholder to check the layout.</p></div>
  <aside class="col-side news"><h2>News</h2><div class="news-item"><p>Placeholder</p></div></aside>
</div>
```

- [ ] **Step 6: Build and screenshot**

```bash
bundle exec jekyll build
/Applications/Firefox.app/Contents/MacOS/firefox --headless --no-remote --profile /tmp/ffprof-sg --window-size=1400,1200 --screenshot "$PWD/_site/shot-home.png" "file://$PWD/_site/index.html"
```
Look at `_site/shot-home.png` next to `reference/original-site/screenshots/home.png`: dark bar, centered menu, MAIL on the right, grey post box left, News right. Adjust CSS until the header and column proportions match. (The CSS link is `/assets/css/main.css`; for the `file://` check either open via `bundle exec jekyll serve` at http://127.0.0.1:4000/ instead, which is the preferred way.)

- [ ] **Step 7: Commit**

```bash
git add _data _includes _layouts assets index.html
git commit -m "feat: base layout and stylesheet reproducing the original design"
```

---

### Task 3: GitHub repository and Pages deployment workflow

**Files:**
- Create: `.github/workflows/pages.yml`, `404.html`

**Interfaces:**
- Produces: public repo `gernotstarke/systemsguild.eu-site` (can be transferred to a Guild organisation later), deploy URL printed by the workflow. Every push to `main` deploys.

- [ ] **Step 1: Workflow file** (GitHub's documented Jekyll 4 workflow)

`.github/workflows/pages.yml`:
```yaml
name: Deploy Jekyll site to Pages
on:
  push:
    branches: ["main"]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: "pages"
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: "3.3"
          bundler-cache: true
      - id: pages
        uses: actions/configure-pages@v5
      - run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
      - uses: actions/upload-pages-artifact@v3
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: 404 page**

`404.html`:
```html
---
layout: page
title: Page not found
permalink: /404.html
show_title: true
sitemap: false
---
<p>The page you were looking for does not exist. <a href="{{ '/' | relative_url }}">Back to the home page.</a></p>
```

- [ ] **Step 3: Create the repo, push, enable Pages via Actions**

```bash
git add .github 404.html && git commit -m "ci: GitHub Pages deployment workflow and 404 page"
gh repo create gernotstarke/systemsguild.eu-site --public --source=. --remote=origin --description "Static Jekyll site for systemsguild.eu (migrated from WordPress)" --push
gh api -X POST repos/gernotstarke/systemsguild.eu-site/pages -f build_type=workflow
gh run watch --exit-status
gh api repos/gernotstarke/systemsguild.eu-site/pages --jq .html_url
```
Expected: run succeeds; `curl -sI <html_url>` returns 200 and the page shows the placeholder with the dark header (CSS loaded via `relative_url`, so the `/systemsguild.eu-site/` prefix is respected).

If `gh api -X POST .../pages` fails with 409 (already exists), run `gh api -X PUT repos/gernotstarke/systemsguild.eu-site/pages -f build_type=workflow`.

---

### Task 4: WordPress export tooling

**Files:**
- Create: `tools/requirements.txt`, `tools/wp_export.py`, `tools/tests/test_wp_export.py`
- Produces on disk: `reference/export/{posts,pages,media,tags,categories,users,events}.json`, media under `assets/uploads/YYYY/MM/<file>`

**Interfaces:**
- Produces: `wp_export.local_path(url) -> str` mapping `https://systemsguild.eu/wp-content/uploads/2021/06/x.png` to `assets/uploads/2021/06/x.png`; JSON files are the raw REST arrays (all fields, `per_page=100`, paginated until `X-WP-TotalPages`).

- [ ] **Step 1: venv and requirements**

```bash
printf 'pyyaml>=6\nbeautifulsoup4>=4.12\n' > tools/requirements.txt
python3 -m venv .venv && .venv/bin/pip install -q -r tools/requirements.txt
```

- [ ] **Step 2: Failing test**

`tools/tests/test_wp_export.py`:
```python
import unittest
from tools.wp_export import local_path, UPLOAD_PREFIX

class LocalPathTest(unittest.TestCase):
    def test_maps_upload_url_to_assets(self):
        self.assertEqual(
            local_path("https://systemsguild.eu/wp-content/uploads/2021/06/TrasnIndentedSkull.png"),
            "assets/uploads/2021/06/TrasnIndentedSkull.png")

    def test_protocol_relative_url(self):
        self.assertEqual(local_path("//systemsguild.eu/wp-content/uploads/2018/11/a.jpg"),
                         "assets/uploads/2018/11/a.jpg")

    def test_non_upload_url_returns_none(self):
        self.assertIsNone(local_path("https://example.org/x.png"))

if __name__ == "__main__":
    unittest.main()
```

Run: `.venv/bin/python -m unittest tools.tests.test_wp_export -v` (needs empty `tools/__init__.py` and `tools/tests/__init__.py`). Expected: FAIL, `No module named 'tools.wp_export'`.

- [ ] **Step 3: Implementation**

`tools/wp_export.py`:
```python
"""Export all content of the WordPress site via its public REST API.

Usage:  .venv/bin/python -m tools.wp_export [--skip-media]
Writes reference/export/<type>.json and downloads media to assets/uploads/.
"""
import json, os, re, sys, urllib.request

BASE = "https://systemsguild.eu"
API = BASE + "/wp-json/wp/v2/"
UPLOAD_PREFIX = "/wp-content/uploads/"
EXPORT_DIR = "reference/export"
ENDPOINTS = {
    "posts": "posts", "pages": "pages", "media": "media", "tags": "tags",
    "categories": "categories", "users": "users", "events": "tribe_events",
}

def local_path(url):
    """Map an uploads URL to its path inside the repo, or None if not an upload."""
    m = re.match(r"^(?:https?:)?//systemsguild\.eu" + re.escape(UPLOAD_PREFIX) + r"(.+)$", url)
    return "assets/uploads/" + m.group(1) if m else None

def fetch_all(endpoint):
    items, page = [], 1
    while True:
        req = urllib.request.Request(f"{API}{endpoint}?per_page=100&page={page}",
                                     headers={"User-Agent": "systemsguild-export"})
        with urllib.request.urlopen(req) as r:
            items += json.load(r)
            total_pages = int(r.headers.get("X-WP-TotalPages", "1"))
        if page >= total_pages:
            return items
        page += 1

def download(url, dest):
    if os.path.exists(dest):
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "systemsguild-export"})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())
    return True

def main(argv):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    data = {}
    for name, ep in ENDPOINTS.items():
        data[name] = fetch_all(ep)
        with open(f"{EXPORT_DIR}/{name}.json", "w") as f:
            json.dump(data[name], f, indent=1, ensure_ascii=False)
        print(f"{name}: {len(data[name])}")
    if "--skip-media" in argv:
        return
    n = 0
    for m in data["media"]:
        dest = local_path(m["source_url"])
        if dest and download(m["source_url"], dest):
            n += 1
    # also fetch every upload URL referenced in content but not in the media list (e.g. resized variants)
    referenced = set()
    for coll in ("posts", "pages", "events"):
        for item in data[coll]:
            referenced.update(re.findall(r"(?:https?:)?//systemsguild\.eu/wp-content/uploads/[^\s\"'<>)]+",
                                         item["content"]["rendered"]))
    for url in sorted(referenced):
        dest = local_path(url)
        if dest and download(("https:" + url) if url.startswith("//") else url, dest):
            n += 1
    print(f"downloaded {n} media files")

if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 4: Test passes, run export**

```bash
touch tools/__init__.py tools/tests/__init__.py
.venv/bin/python -m unittest tools.tests.test_wp_export -v
.venv/bin/python -m tools.wp_export
ls reference/export; find assets/uploads -type f | wc -l; du -sh assets/uploads
```
Expected: tests PASS; counts `posts: 28`, `pages: 15`, `media: 98`, `tags: 14`, `categories: 10`, `users: 3`, `events: 1`; roughly 100 to 130 files under `assets/uploads` (media list plus resized variants referenced in content).

- [ ] **Step 5: Commit** (export JSON is ignored via `.gitignore`; media is committed)

```bash
git add tools assets/uploads
git commit -m "feat: WordPress REST export tool and migrated media files"
```

---

### Task 5: Automatic post conversion, post layout, listings, feed redirect

**Files:**
- Create: `tools/convert_posts.py`, `tools/tests/test_convert_posts.py`, `_includes/rule.html`, `_includes/post-meta.html`, `_includes/post-list.html`, `_layouts/post.html`, `_layouts/listing.html`, `_data/authors.yml`, `category/culture-killers.md`, `author/james-robertson.md`, `author/tom-demarco.md`, `feed/index.html`, 28 files in `_posts/`, 13 files in `tag/`

**Interfaces:**
- Consumes: `reference/export/posts.json`, `tags.json`, `users.json` (Task 4)
- Produces: post front matter fields `title`, `date`, `author` (user slug: `james-robertson` / `tom-demarco`), `tags` (list of tag *slugs*), `tag_names` (list of display names such as `#culture`), `permalink: /<slug>/`, `wp_id`. Include `rule.html` with parameter `text`.

- [ ] **Step 1: Failing tests**

`tools/tests/test_convert_posts.py`:
```python
import unittest
from tools.convert_posts import html_to_markdown, front_matter, post_filename

SKULL = ('<p>Intro.</p>\n<div class="wp-block-media-text alignwide is-stacked-on-mobile" style="grid-template-columns:15% auto">'
         '<figure class="wp-block-media-text__media"><img loading="lazy" width="680" height="400" '
         'src="https://systemsguild.eu/wp-content/uploads/2021/06/TrasnIndentedSkull.png" alt="" class="wp-image-701 size-full" /></figure>'
         '<div class="wp-block-media-text__content">\n<h4><strong><strong>Teamwork means doing what you’re told.</strong></strong></h4>\n</div></div>\n<p>After.</p>')

class HtmlToMarkdownTest(unittest.TestCase):
    def test_skull_block_becomes_rule_include(self):
        md = html_to_markdown(SKULL)
        self.assertIn('{% include rule.html text="Teamwork means doing what you’re told." %}', md)
        self.assertNotIn("wp-block-media-text", md)
        self.assertIn("Intro.", md)
        self.assertIn("After.", md)

    def test_upload_urls_rewritten(self):
        md = html_to_markdown('<p><img src="https://systemsguild.eu/wp-content/uploads/2025/05/resting.jpg" alt="x"></p>')
        self.assertIn("/assets/uploads/2025/05/resting.jpg", md)
        self.assertNotIn("wp-content", md)

    def test_quotes_in_rule_text_are_escaped(self):
        html = SKULL.replace("Teamwork means doing what you’re told.", 'Say "no" never.')
        self.assertIn('text="Say &quot;no&quot; never."', html_to_markdown(html))

class FrontMatterTest(unittest.TestCase):
    def test_front_matter_fields(self):
        post = {"id": 647, "slug": "the-stepford-hires", "date": "2025-09-29T01:00:00",
                "title": {"rendered": "The Stepford Hires"}, "author": 3, "tags": [17, 14]}
        tags = {17: {"slug": "culture", "name": "#culture"}, 14: {"slug": "hiring", "name": "hiring"}}
        users = {3: "james-robertson"}
        fm = front_matter(post, tags, users)
        self.assertEqual(fm["title"], "The Stepford Hires")
        self.assertEqual(fm["date"], "2025-09-29 01:00:00 +0200")
        self.assertEqual(fm["author"], "james-robertson")
        self.assertEqual(fm["tags"], ["culture", "hiring"])
        self.assertEqual(fm["tag_names"], ["#culture", "hiring"])
        self.assertEqual(fm["permalink"], "/the-stepford-hires/")
        self.assertEqual(fm["wp_id"], 647)

    def test_filename(self):
        self.assertEqual(post_filename({"slug": "followership", "date": "2025-06-02T01:00:00"}),
                         "_posts/2025-06-02-followership.md")

if __name__ == "__main__":
    unittest.main()
```

Run: `.venv/bin/python -m unittest tools.tests.test_convert_posts -v`. Expected: FAIL, module not found.

- [ ] **Step 2: Implementation**

`tools/convert_posts.py`:
```python
"""Convert exported WordPress posts to Jekyll posts and generate tag pages.

Usage: .venv/bin/python -m tools.convert_posts
Reads reference/export/{posts,tags,users}.json, writes _posts/*.md and tag/*.md.
Requires pandoc on PATH.
"""
import html as htmlmod, json, os, re, subprocess
from datetime import datetime, timezone, timedelta
import yaml
from bs4 import BeautifulSoup

EXPORT = "reference/export"
UPLOADS_RE = re.compile(r"(?:https?:)?//systemsguild\.eu/wp-content/uploads/")
TZ = timezone(timedelta(hours=2))  # site content is Europe/Berlin summer time; Jekyll uses timezone from _config

def _rule_include(text):
    return '{%% include rule.html text="%s" %%}' % text.replace('"', "&quot;")

def html_to_markdown(rendered):
    soup = BeautifulSoup(rendered, "html.parser")
    for block in soup.select("div.wp-block-media-text"):
        content = block.select_one(".wp-block-media-text__content")
        text = " ".join(content.get_text(" ", strip=True).split()) if content else ""
        block.replace_with(soup.new_string("\n\n" + _rule_include(text) + "\n\n"))
    cleaned = UPLOADS_RE.sub("/assets/uploads/", str(soup))
    md = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"],
                        input=cleaned, capture_output=True, text=True, check=True).stdout
    md = md.replace("\\{%", "{%").replace("%\\}", "%}")          # pandoc escapes braces
    md = re.sub(r'(\{% include rule\.html text=")([^"]*)("? %\})',
                lambda m: m.group(1) + htmlmod.unescape(m.group(2)).replace('"', "&quot;") + '" %}', md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"

def front_matter(post, tags, users):
    dt = datetime.fromisoformat(post["date"]).replace(tzinfo=TZ)
    ids = [t for t in post.get("tags", []) if t in tags]
    return {
        "title": htmlmod.unescape(post["title"]["rendered"]),
        "date": dt.strftime("%Y-%m-%d %H:%M:%S %z"),
        "author": users.get(post.get("author"), "james-robertson"),
        "tags": [tags[t]["slug"] for t in ids],
        "tag_names": [tags[t]["name"] for t in ids],
        "permalink": f"/{post['slug']}/",
        "wp_id": post["id"],
    }

def post_filename(post):
    return f"_posts/{post['date'][:10]}-{post['slug']}.md"

def dump(fm, body):
    return "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n" + body

def write_tag_pages(tags, used):
    os.makedirs("tag", exist_ok=True)
    for t in tags.values():
        if t["slug"] not in used:
            continue
        fm = {"layout": "listing", "title": f"Posts tagged {t['name']}", "tag": t["slug"],
              "permalink": f"/tag/{t['slug']}/", "sitemap": False}
        with open(f"tag/{t['slug']}.md", "w") as f:
            f.write(dump(fm, ""))

def main():
    posts = json.load(open(f"{EXPORT}/posts.json"))
    tags = {t["id"]: {"slug": t["slug"], "name": htmlmod.unescape(t["name"])}
            for t in json.load(open(f"{EXPORT}/tags.json"))}
    users = {u["id"]: u["slug"].replace("_", "-").lower() for u in json.load(open(f"{EXPORT}/users.json"))}
    os.makedirs("_posts", exist_ok=True)
    used = set()
    for p in posts:
        fm = front_matter(p, tags, users)
        used.update(fm["tags"])
        with open(post_filename(p), "w") as f:
            f.write(dump(fm, html_to_markdown(p["content"]["rendered"])))
    write_tag_pages(tags, used)
    print(f"wrote {len(posts)} posts, {len(used)} tag pages")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Tests pass**

```bash
.venv/bin/python -m unittest tools.tests.test_convert_posts -v
```
Expected: 5 tests PASS. If the pandoc escaping differs (`\{%` vs `{\%`), print `md` from one failing test, adjust the two `replace` calls, re-run.

- [ ] **Step 4: Includes and layouts**

`_includes/rule.html`:
```html
<div class="rule">
  <img src="{{ '/assets/uploads/2021/06/TrasnIndentedSkull.png' | relative_url }}" alt="Culture killer skull">
  <h4>{{ include.text }}</h4>
</div>
```

`_data/authors.yml`:
```yaml
james-robertson:
  name: James Robertson
  url: /james-robertson/
tom-demarco:
  name: Tom DeMarco
  url: /tom-demarco/
peter-hruschka:
  name: Peter Hruschka
  url: /peter-hruschka/
```

`_includes/post-meta.html`:
```html
<p class="post-meta">
  {% assign a = site.data.authors[page.author] %}
  {% if a %}By <a href="{{ a.url | relative_url }}">{{ a.name }}</a> ·{% endif %}
  <time datetime="{{ page.date | date_to_xmlschema }}">{{ page.date | date: "%B %-d, %Y" }}</time>
  {% if page.tags.size > 0 %} ·
    {% for slug in page.tags %}{% assign name = page.tag_names[forloop.index0] %}<a href="{{ '/tag/' | append: slug | append: '/' | relative_url }}">{{ name }}</a>{% unless forloop.last %}, {% endunless %}{% endfor %}
  {% endif %}
</p>
```

`_layouts/post.html`:
```html
---
layout: default
---
<article class="l-content post-content">
  <h1>{{ page.title }}</h1>
  {{ content }}
  {% include post-meta.html %}
</article>
```

`_includes/post-list.html` (expects variable `posts`):
```html
<ul class="post-list">
{% for post in posts %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a><span class="date">{{ post.date | date: "%B %-d, %Y" }}</span></li>
{% endfor %}
</ul>
```

`_layouts/listing.html`:
```html
---
layout: default
---
<section class="l-content">
  <h1>{{ page.title }}</h1>
  {{ content }}
  {% if page.tag %}{% assign posts = site.tags[page.tag] %}
  {% elsif page.author_slug %}{% assign posts = site.posts | where: "author", page.author_slug %}
  {% else %}{% assign posts = site.posts %}{% endif %}
  {% include post-list.html posts=posts %}
</section>
```

`category/culture-killers.md`:
```markdown
---
layout: listing
title: Culture Killers
permalink: /category/culture-killers/
---
All Culture Killer posts, newest first.
```

`author/james-robertson.md`:
```markdown
---
layout: listing
title: Posts by James Robertson
author_slug: james-robertson
permalink: /author/james-robertson/
sitemap: false
---
```
`author/tom-demarco.md` likewise with `tom-demarco` and title `Posts by Tom DeMarco`.

`feed/index.html`:
```html
---
permalink: /feed/
redirect_to: /feed.xml
sitemap: false
---
```

- [ ] **Step 5: Run conversion and build**

```bash
.venv/bin/python -m tools.convert_posts
ls _posts | wc -l; ls tag | wc -l
bundle exec jekyll build
ls _site/followership/index.html _site/tag/culture/index.html _site/category/culture-killers/index.html _site/feed/index.html
grep -c 'class="rule"' _site/followership/index.html
```
Expected: 28 posts, 13 tag files, all listed outputs exist, followership has 2 rule blocks. Open `_site/followership/index.html` in the browser (`bundle exec jekyll serve`) and compare with `reference/original-site/screenshots/followership.png`.

Spot-check three posts by eye in the Markdown: `_posts/*followership.md`, `*the-stepford-hires.md`, `*bullshit-jobs.md` – no leftover `<div`, `srcset`, or `wp-` strings:
```bash
grep -l 'wp-block\|srcset\|wp-content' _posts/*.md || echo "clean"
```

- [ ] **Step 6: Commit**

```bash
git add tools _posts tag category author feed _includes _layouts _data
git commit -m "feat: convert all 28 Culture Killer posts, tag/category/author listings, feed redirect"
```

---

### Task 6: Home page (hero, latest post, NEWS sidebar)

**Files:**
- Create: `_data/news.yml`, `_includes/news.html`, `tools/pages_to_markdown.py`
- Modify: `index.html`

**Interfaces:**
- Consumes: `reference/export/pages.json` (the front page is the page with slug `culture-killer`, id visible in `pages.json`; its `link` is `https://systemsguild.eu/`).
- Produces: `_data/news.yml` entries `{image, html}`; `tools/pages_to_markdown.py` writes `reference/export/pages-md/<slug>.md` for every page as manual-conversion starting points (used again in Tasks 7 to 9).

- [ ] **Step 1: Page pre-conversion tool** (no unit test: it is a throwaway helper whose output is reviewed by hand)

`tools/pages_to_markdown.py`:
```python
"""Write pandoc Markdown drafts of every WordPress page for manual conversion.
Usage: .venv/bin/python -m tools.pages_to_markdown   -> reference/export/pages-md/<slug>.md
WPBakery wrapper divs are unwrapped first so pandoc sees plain content."""
import json, os, re, subprocess
from bs4 import BeautifulSoup
EXPORT = "reference/export"
UPLOADS_RE = re.compile(r"(?:https?:)?//systemsguild\.eu/wp-content/uploads/")

def unwrap_builder(rendered):
    soup = BeautifulSoup(rendered, "html.parser")
    for tag in soup.find_all(["div", "section", "span"]):
        cls = " ".join(tag.get("class", []))
        if re.search(r"\b(vc_|wpb_|w-|g-cols|l-section|us_)", cls) or not tag.get("class"):
            tag.unwrap()
    for tag in soup.find_all(["style", "script"]):
        tag.decompose()
    return UPLOADS_RE.sub("/assets/uploads/", str(soup))

def main():
    os.makedirs(f"{EXPORT}/pages-md", exist_ok=True)
    for p in json.load(open(f"{EXPORT}/pages.json")):
        md = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"],
                            input=unwrap_builder(p["content"]["rendered"]), capture_output=True, text=True, check=True).stdout
        with open(f"{EXPORT}/pages-md/{p['slug']}.md", "w") as f:
            f.write(f"<!-- wp id {p['id']} link {p['link']} title {p['title']['rendered']} -->\n\n{md}")
        print(p["slug"], len(md))

if __name__ == "__main__":
    main()
```
Run `.venv/bin/python -m tools.pages_to_markdown`; expect 15 files.

- [ ] **Step 2: Transcribe NEWS items**

Read `reference/export/pages-md/culture-killer.md` (the front page). The intro paragraph "A culture killer is what ruins workplace culture…" and the closing italic paragraph "You must have a story or two…" belong to the home page itself (not to the post). Everything under "NEWS" becomes `_data/news.yml`, one entry per item, in the original order, keeping links and emphasis as inline HTML:

```yaml
- image: /assets/uploads/<path of Dark Harbor House cover as found in the draft>
  html: 'New in 2025: Audiobook of Tom DeMarco’s earlier comic novel, <em>Dark Harbor House</em>, is now available. <a href="…">Click for details.</a>'
- image: /assets/uploads/<Adrenalin-Junkies cover>
  html: 'Neue und erweiterte Auflage 2 jetzt verfügbar. <strong>Adrenalin-Junkies und Formular-Zombies: Typisches Verhalten in Projekten</strong>. Hardback <a href="…">Amazon.de</a>'
# … continue for every item in the draft (about 12 items: One-Way Time Traveler, Modern Analyst article, Happy to Work Here EN, DE edition, six YouTube items, Business Analysis Agility video, …)
```
Every image path must exist under `assets/uploads/`; check with `ls`.

- [ ] **Step 3: News include and home page**

`_includes/news.html`:
```html
<aside class="col-side news">
  <h2>News</h2>
  {% for item in site.data.news %}
  <div class="news-item">
    {% if item.image %}<img src="{{ item.image | relative_url }}" alt="">{% endif %}
    <p>{{ item.html }}</p>
  </div>
  {% endfor %}
</aside>
```

`index.html`:
```html
---
layout: default
title: This Week’s Culture Killer
body_class: home
---
<div class="l-content">
  <div class="hero">
    <img src="{{ '/assets/uploads/2018/11/Systemsguild_FotoMallorca.jpg' | relative_url }}"
         alt="The principals of the Atlantic Systems Guild: Tom DeMarco, Steve McMenamin, Peter Hruschka, Suzanne Robertson, Tim Lister, James Robertson">
  </div>
  <div class="two-col">
    <div class="col-main">
      {% assign post = site.posts.first %}
      <section class="latest-post">
        <h2>Workplace Culture: This Week’s Culture Killer</h2>
        <div class="intro">
          <img class="figure left" src="{{ '/assets/uploads/2021/06/TrasnIndentedSkull.png' | relative_url }}" alt="">
          <p>A culture killer is what ruins workplace culture in spite of your every effort. … (full intro paragraph from the draft, links preserved)</p>
        </div>
        <p class="clearfix">This week’s Unspoken Rule is the one that enables:</p>
        <h2 class="post-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        {{ post.content }}
        {% include post-meta.html page=post %}
      </section>
      <p><em>You must have a story or two about the cultures … Tell us about it: <a href="mailto:cultureproject@systemsguild.com">cultureproject@systemsguild.com</a></em></p>
    </div>
    {% include news.html %}
  </div>
</div>
```
(`{% include post-meta.html page=post %}`: inside the include `page` then refers to `include.page`; change `post-meta.html` to start with `{% assign p = include.page | default: page %}` and use `p.` instead of `page.` throughout.)

The hero photo in the original has the six names overlaid via Slider Revolution. Check the exported `Systemsguild_FotoMallorca.jpg`: if the names are not part of the image, add a caption row under the image:
```html
<p class="hero-names">Tom DeMarco · Steve McMenamin · Peter Hruschka · Suzanne Robertson · Tim Lister · James Robertson</p>
```
with CSS `.hero-names{text-align:center;font-size:.9rem;margin-top:-.5rem}`.

- [ ] **Step 4: Build, compare, commit**

```bash
bundle exec jekyll build && bundle exec jekyll serve --detach && sleep 2
/Applications/Firefox.app/Contents/MacOS/firefox --headless --no-remote --profile /tmp/ffprof-sg --window-size=1400,3000 --screenshot "$PWD/_site/shot-home.png" http://127.0.0.1:4000/
pkill -f "jekyll serve"
```
Compare `_site/shot-home.png` with `reference/original-site/screenshots/home.png`; fix spacing in CSS where needed. Then:
```bash
git add index.html _data/news.yml _includes tools assets/css
git commit -m "feat: home page with hero, latest culture killer and news sidebar"
```

---

### Task 7: Text pages and person pages (11 pages)

**Files:**
- Create in `_pages/`: `about-the-guild.md`, `contact.md`, `culture.md`, `culture-at-work.md`, `riskology.md`, `tom-demarco.md`, `tim-lister.md`, `peter-hruschka.md`, `steve-mcmenamin.md`, `suzanne-robertson.md`, `james-robertson.md`
- Create: `_includes/figure.html`

**Interfaces:**
- Consumes: `reference/export/pages-md/<slug>.md` drafts (Task 6), `assets/uploads/` (Task 4)
- Produces: pages with front matter `title`, `permalink: /<slug>/`, `wp_id`; `figure.html` include with params `src`, `alt`, `align` (`left`|`right`), `width` (optional CSS width).

- [ ] **Step 1: Figure include**

`_includes/figure.html`:
```html
<figure class="figure {{ include.align | default: 'left' }}"{% if include.width %} style="max-width:{{ include.width }}"{% endif %}>
  <img src="{{ include.src | relative_url }}" alt="{{ include.alt | default: '' }}">
  {% if include.caption %}<figcaption>{{ include.caption }}</figcaption>{% endif %}
</figure>
```

- [ ] **Step 2: Convert each page**

For each slug: open the draft, remove pandoc noise (empty `<div>`s, `{.class}` attributes, stray `\`), keep every paragraph, heading, link and image. Images that were floated in the original (person portraits, book covers) become `{% include figure.html src="/assets/uploads/…" alt="…" align="right" width="35%" %}`. Uppercase headings such as "ABOUT THE ATLANTIC SYSTEMS GUILD" become `# About the Atlantic Systems Guild` (CSS uppercases `h1`). Front matter template:

```markdown
---
title: About the Guild
permalink: /about-the-guild/
wp_id: 42
---
```
(`wp_id` from the HTML comment at the top of the draft; `layout: page` comes from `_config.yml` defaults.)

Content check per page against the live site (`https://systemsguild.eu/<slug>`), because the reference screenshots miss lazy-loaded images:
- `about-the-guild`: two intro paragraphs, "The Guild is:" then one paragraph per principal with name linked to the person page (`/suzanne-robertson/` etc.).
- `contact`: heading "Contacting the Guild", one block per person: name, e-mail as `mailto:` link, phone. Keep all five entries exactly.
- `riskology`: text plus link to `/assets/uploads/…/RiskologyManual.pdf` (find with `ls assets/uploads/*/*/RiskologyManual.pdf`).
- `culture`, `culture-at-work`: text and any images.
- six person pages: bio text, floated images, external links (Amazon, publishers). `tom-demarco` has the sub-heading "DeMarco’s Other Side".

- [ ] **Step 3: Build and check**

```bash
bundle exec jekyll build
for s in about-the-guild contact culture culture-at-work riskology tom-demarco tim-lister peter-hruschka steve-mcmenamin suzanne-robertson james-robertson; do test -f _site/$s/index.html && echo "ok $s" || echo "MISSING $s"; done
grep -o 'src="[^"]*"' _site/tom-demarco/index.html | sed 's/src="//;s/"//' | while read u; do test -f "_site$u" || echo "missing image $u"; done
```
Expected: 11 × ok, no missing images. Visually compare `about-the-guild` and `tom-demarco` with the reference screenshots.

- [ ] **Step 4: Commit**

```bash
git add _pages _includes/figure.html
git commit -m "feat: migrate about, contact, culture, riskology and six principal pages"
```

---

### Task 8: Guild Books page from a data file

**Files:**
- Create: `_data/books.yml`, `_includes/books.html`, `_pages/guild-books.md`

**Interfaces:**
- Produces: `books.yml` entries `{title, authors, cover, blurb (html string), links: [{label, url}]}`.

- [ ] **Step 1: Transcribe all books**

From `reference/export/pages-md/guild-books.md` (and the live page), one entry per book in original order. Example for the first two:

```yaml
- title: Business Analysis Agility – Solve the Real Problem, Deliver Real Value
  authors: Suzanne and James Robertson
  cover: /assets/uploads/<path from draft>
  blurb: To deliver real value, you must understand what your customers truly value, and solve the problems they really need solved. Business analysis can help you do this—and it’s as crucial in agile environments now as it always has been.
  links:
    - label: Amazon
      url: https://www.amazon.com/…
- title: Business Analysis und Requirements Engineering – Produkte und Prozesse nachhaltig verbessern
  authors: Peter Hruschka (in German)
  cover: /assets/uploads/<path>
  blurb: 'Successful cooperation between Business and IT; … <br>This book covers all of IREB’s foundation level, as well as the advanced levels “Requirements Modeling” and “RE@Agile”'
  links:
    - label: Amazon
      url: https://…
```
Count the entries against the number of book covers on the live page (about 20). Every `cover` path must exist under `assets/uploads/`.

- [ ] **Step 2: Include and page**

`_includes/books.html`:
```html
{% for b in site.data.books %}
<div class="book">
  {% if b.cover %}<img src="{{ b.cover | relative_url }}" alt="Cover of {{ b.title }}">{% endif %}
  <div>
    <h3>{{ b.title }}</h3>
    <p class="by">by: {{ b.authors }}</p>
    <p>{{ b.blurb }}</p>
    <ul>{% for l in b.links %}<li><a href="{{ l.url }}">{{ l.label }}</a></li>{% endfor %}</ul>
  </div>
</div>
{% endfor %}
```

`_pages/guild-books.md`:
```markdown
---
title: Guild Books
permalink: /guild-books/
wp_id: <id>
---
Over the last few decades members of the Atlantic Systems Guild have published many books. And there is always at least one more book in the queue.

{% include books.html %}
```

- [ ] **Step 3: Build, compare with `reference/original-site/screenshots/guild-books.png`, commit**

```bash
bundle exec jekyll build && grep -c 'class="book"' _site/guild-books/index.html
git add _data/books.yml _includes/books.html _pages/guild-books.md
git commit -m "feat: Guild Books page driven by _data/books.yml"
```
Expected count equals the number of entries in `books.yml`.

---

### Task 9: Remaining pages: events, template redirect page, WordPress leftovers

**Files:**
- Create in `_pages/`: `events.md`, `guildsite-robs-template-html.md`, `sample-page.md`, `culture-killer.md`

- [ ] **Step 1: Events page with the one event and the old detail URL**

`_pages/events.md`:
```markdown
---
title: Events
permalink: /events/
redirect_from:
  - /event/killer
  - /event/killer/
sitemap: false
---
There are no upcoming events.

## Past events

- **Killer** (June 9, 2021) — <content of the event from reference/export/events.json, unchanged>
```
(The exported event is placeholder text "kiler text …" created when the calendar plugin was tried out; it is kept verbatim per the no-content-dropped decision and flagged in the README as a candidate for removal by the editors.)

- [ ] **Step 2: Volere template page**

`_pages/guildsite-robs-template-html.md`:
```markdown
---
title: Volere Requirements Specification Template
permalink: /guildsite-robs-template-html/
sitemap: false
---
The Template has moved. You will now find it on the [Volere site](https://www.volere.org/templates/volere-requirements-specification-template/).
```

- [ ] **Step 3: Leftover pages**

`_pages/sample-page.md`: front matter `title: Sample Page`, `permalink: /sample-page/`, `sitemap: false`; body = the draft text.
`_pages/culture-killer.md`: this page *is* the WordPress front page and is fully represented by `index.html`. WordPress served it only at `/`; `/culture-killer` was never a public URL (not in the sitemap). Create it as a redirect so nothing is lost:
```markdown
---
title: Culture Killer
permalink: /culture-killer/
redirect_to: /
sitemap: false
---
```

- [ ] **Step 4: Build, check, commit**

```bash
bundle exec jekyll build
ls _site/events/index.html _site/event/killer/index.html _site/guildsite-robs-template-html/index.html _site/sample-page/index.html _site/culture-killer/index.html
git add _pages
git commit -m "feat: events, Volere template notice and remaining WordPress pages"
```

---

### Task 10: URL parity check, link check, README

**Files:**
- Create: `tools/check_urls.py`, `tools/tests/test_check_urls.py`, `README.md`

**Interfaces:**
- Produces: `check_urls.url_to_site_path(url) -> str` mapping `https://systemsguild.eu/followership` → `_site/followership/index.html`; `main()` exits non-zero if any URL from `reference/original-site/sitemap-summary.txt` has no output file (except `/event/killer`, `/feed`, `/culture-killer` which are redirects and are checked for `redirect` files instead).

- [ ] **Step 1: Failing test**

`tools/tests/test_check_urls.py`:
```python
import unittest
from tools.check_urls import url_to_site_path, expected_paths

class UrlMapTest(unittest.TestCase):
    def test_root(self):
        self.assertEqual(url_to_site_path("https://systemsguild.eu/"), "_site/index.html")
    def test_slug(self):
        self.assertEqual(url_to_site_path("https://systemsguild.eu/followership"), "_site/followership/index.html")
    def test_nested_with_trailing_slash(self):
        self.assertEqual(url_to_site_path("https://systemsguild.eu/events/"), "_site/events/index.html")
    def test_expected_paths_parses_summary(self):
        text = "== post: 1 urls\nhttps://systemsguild.eu/a\n== page: 1 urls\nhttps://systemsguild.eu/\n"
        self.assertEqual(expected_paths(text), ["_site/a/index.html", "_site/index.html"])

if __name__ == "__main__":
    unittest.main()
```
Run: `.venv/bin/python -m unittest tools.tests.test_check_urls -v` → FAIL (module missing).

- [ ] **Step 2: Implementation**

`tools/check_urls.py`:
```python
"""Verify that every URL of the old WordPress site exists in the Jekyll build.
Usage: bundle exec jekyll build && .venv/bin/python -m tools.check_urls"""
import os, sys
SUMMARY = "reference/original-site/sitemap-summary.txt"

def url_to_site_path(url):
    path = url.split("systemsguild.eu", 1)[1].strip("/")
    return "_site/index.html" if not path else f"_site/{path}/index.html"

def expected_paths(text):
    return [url_to_site_path(l.strip()) for l in text.splitlines() if l.startswith("http")]

def main():
    missing = [p for p in expected_paths(open(SUMMARY).read()) if not os.path.exists(p)]
    for p in ("_site/event/killer/index.html", "_site/feed/index.html"):
        if not os.path.exists(p):
            missing.append(p)
    if missing:
        print("MISSING:\n  " + "\n  ".join(missing)); sys.exit(1)
    print("all old URLs are present in _site")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Tests pass, run both checks**

```bash
.venv/bin/python -m unittest discover -s tools/tests -t . -v
bundle exec jekyll build
.venv/bin/python -m tools.check_urls
bundle exec htmlproofer ./_site --disable-external --ignore-urls "/^http:\/\/127.0.0.1/" --no-enforce-https
```
Expected: all tests pass; "all old URLs are present in _site"; htmlproofer reports 0 failures. Fix any broken internal link or missing image it reports (usually a wrong `assets/uploads` path in `news.yml`/`books.yml`).

- [ ] **Step 4: Mobile check**

```bash
bundle exec jekyll serve --detach && sleep 2
/Applications/Firefox.app/Contents/MacOS/firefox --headless --no-remote --profile /tmp/ffprof-sg --window-size=414,2200 --screenshot "$PWD/_site/shot-mobile.png" http://127.0.0.1:4000/
pkill -f "jekyll serve"
```
Compare with `reference/original-site/screenshots/home-mobile.png`: hamburger menu, stacked columns, readable text.

- [ ] **Step 5: README for editors**

`README.md` covering: repository purpose; how to add a weekly post (`_posts/YYYY-MM-DD-slug.md`, front matter example with `title`, `author`, `tags`, `tag_names`, and the `{% include rule.html text="…" %}` snippet); how to add a news item (`_data/news.yml`), a book (`_data/books.yml`), a page (`_pages/`); image upload location (`assets/uploads/YYYY/MM/`); local preview (`bundle install`, `bundle exec jekyll serve`); deployment (push to `main` → GitHub Actions → Pages, about one minute); the `tools/` scripts and that they were one-off migration helpers; note about the placeholder "Killer" event.

- [ ] **Step 6: Commit and push, verify deployment**

```bash
git add tools README.md
git commit -m "test: URL parity and link checks; editor documentation"
git push
gh run watch --exit-status
```
Open the Pages URL from Task 3 and click through home, a post, Guild Books, a person page.

---

### Task 11: Cutover preparation (no DNS change without the user)

**Files:**
- Create: `docs/cutover.md`

- [ ] **Step 1: Write the cutover checklist**

`docs/cutover.md`:
```markdown
# Cutover checklist systemsguild.eu → GitHub Pages

1. In the repository: add file `CNAME` containing `systemsguild.eu`, commit, push. (Only now: `_config.yml` `url` is already `https://systemsguild.eu`.)
2. GitHub → repo Settings → Pages → Custom domain: `systemsguild.eu`, wait for the DNS check, then tick "Enforce HTTPS".
3. At the domain registrar (currently IONOS/1&1 hosting):
   - `A` records for apex `systemsguild.eu` → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
   - `AAAA` records → 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153
   - `CNAME` for `www` → `gernotstarke.github.io` (or the organisation's `<org>.github.io` after a transfer)
   - remove the old A record pointing at the WordPress host
4. Wait for propagation (minutes to 24 h). Verify: `curl -sI https://systemsguild.eu/followership/ | head -1` → 200, certificate issued by Let's Encrypt.
5. Keep the WordPress installation for 2 to 4 weeks (set it to read-only / stop publishing), then cancel the WordPress hosting and delete the installation. Export a final WordPress backup (Tools → Export) before deleting.
6. Optional: transfer the repository to a Guild GitHub organisation (Settings → Transfer); GitHub keeps redirects for the old repo URL.
```

- [ ] **Step 2: Commit and push**

```bash
git add docs/cutover.md && git commit -m "docs: cutover checklist" && git push
```

- [ ] **Step 3: Report to the user** with the Pages preview URL and the two actions only they can do: DNS change at the registrar and adding the `CNAME` file when they want to go live.

---

## Self-review

- **Spec coverage:** §1 inventory → Tasks 5 (posts), 7 (11 pages), 8 (books), 9 (events, template, leftovers), 6 (home = `culture-killer` page); §1 layout → Task 2; §2 feature table → Tasks 2 (theme, hero, mail link), 5 (posts, tags, category, feed, authors), 6 (news), 8 (books), 4 (media), 3 (hosting/SSL), 11 (domain); §3 phases 0 to 5 → Tasks 1 to 11; §4 editorial workflow → README in Task 10; §5 decisions → global constraints.
- **Placeholders:** the `<…>` markers in `news.yml`/`books.yml`/`wp_id` are values to be read from the export drafts during execution, with the exact lookup command given; no logic is deferred.
- **Type consistency:** `local_path` (Task 4) reused conceptually in Task 5's `UPLOADS_RE`; `rule.html` param `text` used identically in Task 5 code and README; `listing` layout keys `tag` / `author_slug` match Task 5 pages; `post-meta.html` variable change (`p`) noted in Task 6 applies to Task 5's file.
