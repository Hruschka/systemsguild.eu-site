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
