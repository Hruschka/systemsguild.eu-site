# Cutover checklist systemsguild.eu → GitHub Pages

Prerequisite: the repository is on GitHub, the Pages workflow has run successfully, and the preview URL has been reviewed.

1. In the repository: add a file `CNAME` containing exactly `systemsguild.eu`, commit and push. (`_config.yml` already has `url: https://systemsguild.eu`.)
2. GitHub → repository Settings → Pages → Custom domain: enter `systemsguild.eu`, save, wait for the DNS check to pass, then tick **Enforce HTTPS** (the certificate comes from Let's Encrypt and is managed by GitHub).
   Then re-run the Pages workflow (Actions → Deploy Jekyll site to Pages → Run workflow): builds made before the custom domain was set use the base path `/systemsguild.eu-site`, so CSS and links break on the custom domain.
3. At the domain registrar / DNS provider (the WordPress site is hosted at IONOS/1&1):
   - `A` records for the apex `systemsguild.eu` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `AAAA` records → `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`
   - `CNAME` for `www` → `<owner>.github.io` (currently `Hruschka.github.io`, or the organisation's name after a transfer)
   - remove the old `A` (`217.160.0.133`) and `AAAA` (`2001:8d8:100f:f000::2de`) records of the WordPress host, for the apex and for `www` (`www` is currently an `A` record and must be deleted before the `CNAME` can be created)
   - leave `MX` (`mx00`/`mx01.ionos.de`) and the SPF `TXT` record untouched, otherwise mail breaks
   - keep the IONOS nameservers (`ns10xx.ui-dns.*`); only records change
4. Wait for propagation (minutes up to 24 h). Verify:
   ```bash
   curl -sI https://systemsguild.eu/followership/ | head -1     # HTTP/2 200
   curl -sI https://systemsguild.eu/followership | head -1      # 301 to the trailing-slash URL
   curl -s  https://systemsguild.eu/feed.xml | head -3
   ```
5. Keep the WordPress installation for 2 to 4 weeks as a fallback (stop publishing there). Take a final WordPress export (Tools → Export) as a backup, then cancel the WordPress hosting and delete the installation.
6. Optional: transfer the repository to a Guild GitHub organisation (Settings → Transfer). GitHub keeps redirects for the old repository URL; update the `www` CNAME to the new `<org>.github.io`.

Not migrated on purpose (no content involved): comment forms (there were no comments), the dead Google Universal Analytics tag, the theme's search widget.
