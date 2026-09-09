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
    try:
        with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
            f.write(r.read())
    except urllib.error.HTTPError as e:
        print(f"  skip {url}: HTTP {e.code}")
        return False
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
