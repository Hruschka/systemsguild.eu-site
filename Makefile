.DEFAULT_GOAL := help

# This site's fixed local dev port: 4280, the next free slot in the arc42 42xx
# block (see raw/port-assignment.md in meta.arc42.org), so this dev server can
# run side by side with the arc42 sites'. Changing it here is not enough:
# docker-compose.yml and the Dockerfile pass the same number to Jekyll so its
# startup banner names the real port.
SITE_PORT ?= 4280

COMPOSE       := docker compose
TOOLS         := $(COMPOSE) --profile tools run --rm tools

.PHONY: help dev build stop site check check-links test clean install update shell logs

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

dev: ## Start the local Jekyll dev server with file watching (http://localhost:4280)
	@echo "==> Open http://localhost:$(SITE_PORT)  (NOT http://0.0.0.0:$(SITE_PORT) — Firefox refuses to connect to 0.0.0.0)"
	@$(COMPOSE) down --remove-orphans >/dev/null 2>&1 || true
	@holder=$$(docker ps --filter "publish=$(SITE_PORT)" --format '{{.Names}}'); \
	if [ -n "$$holder" ]; then \
		echo "==> Port $(SITE_PORT) is already in use by another container: $$holder"; \
		echo "==> Stop it first, e.g.:  docker stop $$holder"; \
		exit 1; \
	fi
	$(COMPOSE) up --build jekyll

build: ## Build the Docker images (systemsguild-site, systemsguild-tools) from the pinned dependencies
	$(COMPOSE) --profile tools build

stop: ## Stop and remove the running dev container
	$(COMPOSE) down --remove-orphans

site: build ## Generate the static site into _site/ (production build, like GitHub Pages)
	@# JEKYLL_ENV=production mirrors the GitHub Actions build. Output goes to
	@# ./_site on the bind mount; only the dev server writes elsewhere.
	$(COMPOSE) run --rm -e JEKYLL_ENV=production jekyll bundle exec jekyll build
	@echo "==> Site generated in _site/"

check-links: site ## Validate internal links, images and HTML in _site (html-proofer)
	@# The ignore pattern skips one legacy HTML file that came over from the
	@# WordPress media library (assets/uploads/2019/05/TDMHome.html).
	$(COMPOSE) run --rm jekyll \
		bundle exec htmlproofer ./_site --disable-external --no-enforce-https \
		--ignore-files "/uploads/"

test: site ## Run the Python unit tests and verify every old WordPress URL exists in _site
	$(TOOLS) python -m unittest discover -s tools/tests -t . -v
	$(TOOLS) python -m tools.check_urls

check: check-links test ## Everything CI would complain about: build, link check, tests, URL parity

clean: ## Remove generated _site AND the Docker cache volumes (a true reset)
	@# Volumes first: .jekyll-cache/.sass-cache are mountpoints for named
	@# volumes owned by root inside the container; tearing them down first
	@# empties them so the host rm below cannot hit "Permission denied".
	-$(COMPOSE) --profile tools down -v --remove-orphans
	rm -rf _site .jekyll-metadata
	-rm -rf .sass-cache .jekyll-cache

install: build ## Install/refresh gems into the dev image after editing the Gemfile
	$(COMPOSE) run --rm jekyll bundle install

update: build ## Update gems to their latest allowed versions (rewrites Gemfile.lock), then rebuild
	$(COMPOSE) run --rm jekyll bundle update
	$(COMPOSE) build jekyll

shell: build ## Open a shell inside the Jekyll container for debugging
	$(COMPOSE) run --rm jekyll bash

logs: ## Tail logs from the running dev container
	$(COMPOSE) logs -f jekyll
