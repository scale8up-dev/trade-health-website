# Launch verification

Verified locally on October 27, 2026 using Python 3.12, Node 22 and headless Chromium through Playwright.

## Passed

- `python scripts/build.py`: 22 allowlisted public files; deploy ZIP has `index.html` at its root.
- `python scripts/test_build.py`: clean/repeated builds, Netlify-injected `dist/netlify.toml` excluded from publication, and unknown-file protection. The metadata regression reproduced the exact reported Netlify failure before the fix.
- `node --check app.js`: JavaScript syntax.
- Python `tomllib`: Netlify configuration parses.
- `python scripts/check_site.py` against `dist/`: all 10 pages at 320, 390, 768 and 1440px without horizontal page overflow or JavaScript exceptions.
- Internal page links, anchors, local assets, unique element IDs and Formspree endpoint/honeypot/subject declarations.
- Desktop and mobile homepage screenshots visually inspected; supplied brand colors, hexagonal photo treatment and original photography retained.
- Keyboard skip link, mobile menu toggle/Escape/focus restoration and native FAQ expansion.
- Employee, spouse and family calculations at Founder and standard rates; empty, fractional, negative, zero and out-of-range crew inputs; 10,000-employee boundary.
- Both forms under the production CSP: required-field validation, consent requirement, URL-encoded form names and fields, simulated server and Formspree validation errors with retained entries, retry and simulated success navigation.
- Referral and founder-interest prefills and other-state note.
- Mobile navigation without JavaScript and native form action markup.
- Secondary-button hover/focus contrast regression, hero entrance animation and reduced-motion fallback. Same-origin view transitions are a progressive enhancement; unsupported browsers use normal navigation.

The design detector reported one aesthetic warning for the error message's colored left border; it is intentionally retained as an existing error-state cue, not a general card treatment.

The first managed-server test run timed out during repeated page loads. Running the same suite with server request logs redirected to a file passed; the site code was unchanged for that rerun.

## Requires the deployed Netlify account / owner

- Verify real Formspree submissions and notification email recipients. Local tests mock HTTP responses, not Formspree storage or inbox delivery. Netlify Forms is no longer used.
- Connect custom-domain DNS, verify apex-to-www redirect and HTTPS certificates. No DNS records or existing hosting were changed.
- Approve clinical readiness, service claims, Founder Rate availability/duration and membership terms. There is no allocation/enrollment backend in this marketing site.
- Review and approve privacy/website terms. No legal or accessibility compliance certification is claimed.
- Live security-header behavior, real missing-path 404 status and social-sharing crawler fetches require a deployed URL.

Screenshots and temporary server logs are excluded from Git and the deploy artifact.

## Formspree integration verification

- The existing visible fields and submit-button labels in both forms were compared with the previous commit and are unchanged.
- The updated regression suite passes with Formspree mocked and the production Content Security Policy applied to page responses. It cannot send real submissions.
- Two clearly labeled, fictional integration-test inquiries were submitted through the **updated local build** to `https://formspree.io/f/maeeovpp`. Formspree returned HTTP 200 and `{"next":"/thanks","ok":true}` for both employer and partner forms; both navigated to the local thank-you page.
- An initial employer test reached the success navigation before the test runner could read its response body. The runner was fixed to capture a cloned response before navigation; the first attempt may have generated an additional test notification.
- These tests confirm Formspree acceptance, **not delivery to the owner's inbox**. The owner must check the configured recipient and Formspree dashboard/spam folder.
- After the first push to `main`, the custom domain and Netlify subdomain still served the previous Netlify Forms implementation during a bounded deployment check. GitHub reported no deployment check/status for that commit. Confirm Netlify's connected repository/production branch and trigger a deployment if needed; the prepared `dist/` folder remains an alternative for manual deployment.
