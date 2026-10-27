"""Send exactly two clearly labeled test inquiries, only with explicit --send.

This verifies Formspree acceptance, not receipt in the owner's email inbox.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--send", action="store_true", help="Authorize two real Formspree submissions")
parser.add_argument("--base-url", choices=["https://www.tradehealthnetwork.com", "http://localhost:8000"], default="https://www.tradehealthnetwork.com", help="Test the published site or the updated local build; both send real inquiries")
args = parser.parse_args()
if not args.send:
    parser.error("Pass --send to authorize exactly two real test submissions.")

BASE = args.base_url
ENDPOINT = "https://formspree.io/f/maeeovpp"
results = []
test_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    def record_response(entry):
        results.append(entry)
        print(json.dumps(entry))
    page.expose_function("recordFormspreeTest", record_response)
    # Read a clone before returning the response to the site's handler. Otherwise
    # its successful navigation can discard the DevTools response body first.
    page.add_init_script("""(() => {
      const originalFetch = window.fetch;
      window.fetch = async (...args) => {
        const response = await originalFetch(...args);
        if (String(args[0]) === 'https://formspree.io/f/maeeovpp') {
          const text = await response.clone().text();
          let payload;
          try { payload = JSON.parse(text); } catch { payload = {non_json_response: true}; }
          await window.recordFormspreeTest({
            kind: document.querySelector('form[data-inquiry]').name,
            http_status: response.status,
            accepted: response.ok && payload.ok === true,
            response: payload
          });
        }
        return response;
      };
    })();""")
    try:
        for path, kind in (("get-started", "employer"), ("partners", "partner")):
            page.goto(f"{BASE}/{path}.html", wait_until="networkidle")
            form = page.locator("form[data-inquiry]")
            if form.get_attribute("action") != ENDPOINT:
                raise RuntimeError("Selected site is not using the Formspree endpoint yet; no test was sent.")
            page.locator("#yourname").fill(f"TEST ONLY — {kind.title()} Integration Check")
            page.locator("#businessname" if kind == "employer" else "#firmname").fill("TEST ONLY — TradeHealth Website")
            page.locator("#email").fill("website-integration-test@example.com")
            page.locator("#phone").fill("202-555-0100")
            page.locator("#state").select_option("Idaho")
            if kind == "employer":
                page.locator("#numberofemployees").select_option(index=1)
                page.locator("#typeofbusiness").select_option("HVAC")
            else:
                page.locator("#partnertype").select_option("Payroll")
                page.locator("#approximatenumberofcontractorclients").fill("1")
            page.locator("#message").fill(
                f"AUTOMATED INTEGRATION TEST ONLY ({test_id}) — {kind} form. "
                "Sent at the site owner's request to verify the website's Formspree integration. "
                "Not a real lead, booking, patient or enrollment. Do not call or reply. "
                "All contact details are fictional. Please confirm receipt in your notification inbox."
            )
            page.locator('[name="_subject"]').evaluate(
                "(el, subject) => el.value = subject",
                f"[TEST {test_id}] TradeHealth {kind} form integration",
            )
            page.locator('[name="contact-consent"]').check()
            # No automatic retries: a timeout may still represent an accepted submission.
            with page.expect_response(lambda response: response.url == ENDPOINT and response.request.method == "POST", timeout=30000) as response_info:
                page.locator('[type="submit"]').click()
            page.wait_for_url("**/thank-you*", timeout=15000)
            if not results[-1]["accepted"]:
                raise RuntimeError(f"Formspree did not accept the {kind} test; no retry was attempted.")
    finally:
        browser.close()
        output = Path(__file__).resolve().parents[1] / "test-results" / "formspree-live.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps({"test_id": test_id, "base_url": BASE, "results": results}, indent=2), encoding="utf-8")
print("Both live inquiries were accepted. Inbox delivery must be confirmed by the Formspree account owner.")
