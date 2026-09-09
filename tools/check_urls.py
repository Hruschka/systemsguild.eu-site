"""Verify that every URL of the old WordPress site exists in the Jekyll build.
Usage: bundle exec jekyll build && .venv/bin/python -m tools.check_urls"""
import os, sys
SUMMARY = "reference/original-site/sitemap-summary.txt"
EXTRA = ("_site/event/killer/index.html", "_site/feed/index.html", "_site/culture-killer/index.html")

def url_to_site_path(url):
    path = url.split("systemsguild.eu", 1)[1].strip("/")
    return "_site/index.html" if not path else f"_site/{path}/index.html"

def expected_paths(text):
    return [url_to_site_path(l.strip()) for l in text.splitlines() if l.startswith("http")]

def main():
    wanted = expected_paths(open(SUMMARY).read()) + list(EXTRA)
    missing = [p for p in wanted if not os.path.exists(p)]
    if missing:
        print("MISSING:\n  " + "\n  ".join(missing)); sys.exit(1)
    print(f"all {len(wanted)} old URLs are present in _site")

if __name__ == "__main__":
    main()
