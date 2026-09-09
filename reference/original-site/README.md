# Reference snapshot of the original WordPress site

Captured 2026-09-09 from https://systemsguild.eu/ (WordPress 6.0.14, Impreza theme).

- `html/` – raw HTML of the home page and 14 sample pages/posts, as served by WordPress
- `screenshots/` – full-page headless-Firefox screenshots at 1400px (and one at 414px for mobile).
  Note: some lazy-loaded images did not render in headless mode; the live site shows them.
- `wp-json/` – REST API listings of all posts, pages and media (ids, slugs, URLs)
- `sitemap-summary.txt` – every URL from the Yoast sitemaps, grouped by type

Use this as the layout and content reference during migration. Do not publish the raw HTML:
it contains the paid Impreza theme's CSS/JS.
