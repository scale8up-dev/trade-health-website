# TradeHealth public website

Static, client-facing marketing site based on the supplied six-page design. No application server, paid API, account credentials or JavaScript build toolchain is required.

## Deploy by dragging a folder

1. Drag **`dist/`** into [Netlify Drop](https://app.netlify.com/drop), or upload `tradehealth-netlify.zip`. The folder/ZIP contains `index.html` at its top level. **Do not upload the whole project**: it includes internal handoff notes and original image files.
2. Both existing forms submit to **Formspree**, not Netlify Forms, at `https://formspree.io/f/maeeovpp`. No Netlify form detection or notification setup is needed.
3. In the Formspree dashboard, confirm the form is active, verify the notification recipient, review spam protection/allowed domains and check submission limits. Both forms share the endpoint; their `form-name` and `_subject` fields distinguish employer and partner inquiries. No secret key is embedded in the website.
4. Submit one test inquiry through each form on the deployed URL. Verify the entries in Formspree and notification delivery to the configured recipient. Formspree acceptance does not prove email arrived in the recipient’s inbox.
5. Add `www.tradehealthnetwork.com` under **Domain management**, set it as the primary domain, and add `tradehealthnetwork.com` as an alias. At GoDaddy, follow the DNS targets shown by **this Netlify site**. Preserve existing MX, SPF, DKIM and DMARC records. Do not reuse the former ChatGPT hosting targets. Wait for DNS verification and HTTPS certificates for both domains.

The source includes `netlify.toml` for Git-connected deployment from `main`. **Netlify Drop does not run a build command**; `dist/` is already built. `_headers` and `_redirects` are inside the deploy folder so manual deployments receive security headers and redirects too. This is a multi-page site with a real custom 404, not an SPA.

The site uses its existing vanilla JavaScript AJAX handler rather than adding a CDN dependency. It posts all existing fields to Formspree, requests a JSON response, preserves pending/error/retry behavior and navigates to the local thank-you page only on confirmed acceptance. Without JavaScript, native HTML POST uses Formspree’s hosted response page. The honeypot is Formspree’s `_gotcha` field. The CSP explicitly allows Formspree for connections and native submissions while keeping other external origins blocked.

## Before sharing with prospective clients

- The owner must approve the supplied clinical, availability and pricing claims, including the Idaho/Utah launch, $20/$35 dependent add-ons, the paid 90-day launch and Founder Rate duration/renewal terms.
- Privacy and website terms pages have been added for this marketing site's actual data flow; **owner/legal approval is still required**. They are not a clinical privacy notice, compliance certification or membership agreement.
- Founder Rate availability is confirmed by the team. There is intentionally no invented live allocation count, guaranteed reservation or automated enrollment.
- Forms collect **business inquiries only**, not patient records. They request follow-up, not a booked appointment. Do not use these forms for clinical information.
- Employer portals, clinical care, billing and enrollment are separate services, not features implemented by this marketing site.

## Rebuild after edits

```powershell
python scripts/build.py
```

This copies an explicit public-file allowlist into `dist/` and writes `tradehealth-netlify.zip`. It does not publish internal notes, scripts, tests, Git metadata or original images. Upload the regenerated folder after every change.

### Images

The supplied hero PNG is preserved. Its WebP version is **120,984 bytes versus 2,079,547 bytes** (94% smaller). The two optimized WebP logos total approximately 9 KB rather than 712 KB. Image dimensions reserve layout space; the footer logo is lazy-loaded and the hero is prioritized. All page assets are local; there are no third-party fonts or trackers.

To regenerate image outputs after replacing originals, install Pillow in your Python environment and run:

```powershell
python scripts/optimize_images.py
python scripts/build.py
```

`social-card.jpg` is generated locally for social sharing. Its absolute production URL requires the custom domain to be connected. Originals and the duplicate supplied logo are retained in source, but excluded from deployment.

## Preview and test

```powershell
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. Forms post directly to Formspree even from a local preview, subject to its allowed-domain/spam settings. Use the mocked regression suite below to avoid sending real test inquiries unintentionally.

Browser tests require Python Playwright and Beautiful Soup:

```powershell
python -m pip install playwright beautifulsoup4
python -m playwright install chromium
python scripts/check_site.py
```

Run the last command while the preview server is running. Tests cover internal links/assets, desktop/mobile layouts, loaded images, mobile navigation, FAQ keyboard behavior, all six calculator combinations and invalid inputs, form validation, and mocked Formspree success/failure/retry under the production CSP. Real Formspree requests are blocked during the regression suite. Screenshots are saved to `test-results/`. Mocked submissions do not prove live Formspree storage or email delivery.

After deployment, an explicitly authorized live check can send **two real, clearly labeled test notifications** (one employer and one partner) through the published forms:

```powershell
python scripts/test_formspree_live.py --send
```

It uses fictional contact information, sends no automatic retries, records Formspree responses under `test-results/`, and verifies navigation to the thank-you page. The owner must still confirm actual notification receipt in their inbox. Do not run repeatedly or use it as a load test.

## Source notes

`START_HERE.txt` is the original client handoff, retained unchanged for reference. Its prototype limitations describe the original export; this README describes the current implementation and remaining owner/hosting tasks. Neither document is deployed.
