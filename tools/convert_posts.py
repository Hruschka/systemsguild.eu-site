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
TZ = timezone(timedelta(hours=2))  # posts were published in Europe/Berlin summer time

def _rule_include(text):
    return '{%% include rule.html text="%s" %%}' % text.replace('"', "&quot;")

def html_to_markdown(rendered):
    soup = BeautifulSoup(rendered, "html.parser")
    for block in soup.select("div.wp-block-media-text"):
        content = block.select_one(".wp-block-media-text__content")
        text = " ".join(content.get_text(" ", strip=True).split()) if content else ""
        block.replace_with(soup.new_string("\n\n" + _rule_include(text) + "\n\n"))
    for block in soup.select("div.wp-block-image, figure.wp-block-image"):
        img = block.find("img")
        if not img:
            continue
        fig = block if block.name == "figure" else (block.find("figure") or block)
        classes = " ".join(fig.get("class", []))
        align = "right" if "alignright" in classes else "left"
        src = UPLOADS_RE.sub("/assets/uploads/", img.get("src", ""))
        params = f'src="{src}" alt="{img.get("alt", "").replace(chr(34), "&quot;")}" align="{align}"'
        if img.get("width"):
            params += f' width="{img["width"]}px"'
        block.replace_with(soup.new_string("\n\n{% include figure.html " + params + " %}\n\n"))
    cleaned = UPLOADS_RE.sub("/assets/uploads/", str(soup))
    md = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"],
                        input=cleaned, capture_output=True, text=True, check=True).stdout
    md = md.replace("\\{%", "{%").replace("%\\}", "%}")          # pandoc escapes braces
    md = re.sub(r'(\{% include rule\.html text=")([^"]*)("? %\})',
                lambda m: m.group(1) + htmlmod.unescape(re.sub(r"\\(.)", r"\1", m.group(2))).replace('"', "&quot;") + '" %}', md)
    md = re.sub(r'(\{% include figure\.html )([^\n]*?)( %\})',
                lambda m: m.group(1) + re.sub(r"\\(.)", r"\1", m.group(2)) + m.group(3), md)
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
