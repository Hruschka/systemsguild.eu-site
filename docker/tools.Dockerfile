# Tooling image for the Python helpers under tools/: unit tests, the URL-parity
# check (tools/check_urls.py) and the one-off WordPress migration scripts.
# Kept separate from the Jekyll image so the Ruby side stays small; pandoc is
# needed by tools/convert_posts.py and tools/pages_to_markdown.py.
FROM python:3.12-slim

LABEL description="systemsguild.eu Python tooling image (tests, URL checks, migration scripts)"

RUN apt-get update && apt-get install -y --no-install-recommends pandoc \
    && rm -rf /var/lib/apt/lists/*

COPY tools/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /site
CMD ["python", "-m", "unittest", "discover", "-s", "tools/tests", "-t", "."]
