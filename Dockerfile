# Jekyll dev image for systemsguild.eu — same shape as the arc42 site repos
# (arc42.org-site, docs.arc42.org-site, ...): gems are baked into the image from
# the pinned Gemfile.lock, the site itself is bind-mounted at runtime.
#
# ruby:3.4-slim is multi-arch, so on Apple Silicon this runs natively (arm64)
# without emulation. Jekyll 4.4 (see Gemfile) is what GitHub Actions builds
# with too (.github/workflows/pages.yml), so local output == published output.
FROM ruby:3.4-slim

LABEL description="systemsguild.eu Jekyll dev image"

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential git libcurl4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/bundle

COPY Gemfile Gemfile.lock ./

# Use exactly the Bundler version recorded in Gemfile.lock (BUNDLED WITH), so
# the image, GitHub Actions (ruby/setup-ruby reads the same line) and any local
# run resolve gems identically.
RUN BUNDLER_VERSION="$(tail -n1 Gemfile.lock | tr -d '[:space:]')" \
    && gem install bundler:"$BUNDLER_VERSION" \
    && bundle config set path /usr/local/bundle \
    && bundle config set frozen true \
    && bundle install --jobs 4 --retry 3 \
    && mkdir -p /opt/site-deps \
    && sha256sum Gemfile.lock | awk '{ print $1 }' > /opt/site-deps/.gemfile-lock.sha256

COPY docker/jekyll-entrypoint.sh /usr/local/bin/jekyll-entrypoint
RUN chmod +x /usr/local/bin/jekyll-entrypoint

WORKDIR /site

# 4280 is this site's fixed dev port (arc42 42xx block, see
# raw/port-assignment.md in meta.arc42.org). Also passed to Jekyll via --port so
# its "Server address:" banner names the real port.
EXPOSE 4280

ENTRYPOINT ["jekyll-entrypoint"]
CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--port", "4280", "--watch", "--destination", "/tmp/_site"]
