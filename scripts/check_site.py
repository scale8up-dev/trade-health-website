"""Run against a local static server: python -m http.server 8000 --directory dist."""
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "dist"
RESULTS = ROOT / "test-results"
RESULTS.mkdir(exist_ok=True)
BASE = "http://localhost:8000"
pages = sorted(SITE.glob("*.html"))

for file in pages:
    soup = BeautifulSoup(file.read_text(encoding="utf-8"), "html.parser")
    assert len(soup.select("h1")) == 1, file.name
    ids = [el["id"] for el in soup.select("[id]")]
    assert len(ids) == len(set(ids)), f"Duplicate IDs in {file.name}"
    for el in soup.select("[href], [src]"):
        url = urlparse(el.get("href") or el.get("src"))
        if url.scheme or url.netloc:
            continue
        path = SITE / unquote(url.path).lstrip("/") if url.path else file
        if path.is_dir():
            path = path / "index.html"
        assert path.is_file(), (file.name, str(url))
        if url.fragment:
            target = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            assert target.find(id=url.fragment), (file.name, url.fragment)
    for form in soup.select("form"):
        assert form.get("data-netlify") == "true"
        assert form.get("method").upper() == "POST"
        assert form.select_one('input[name="form-name"]')["value"] == form["name"]
        assert form.select_one('input[name="bot-field"]')
        assert form.select_one('input[name="contact-consent"][required]')
print(f"PASS: {len(pages)} pages: internal links, anchors, assets, unique IDs and Netlify form markup")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    for width in (320, 390, 768, 1440):
        page.set_viewport_size({"width": width, "height": 1000})
        for file in pages:
            response = page.goto(f"{BASE}/{file.name}")
            assert response.ok, file.name
            page.wait_for_load_state("networkidle")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (file.name, width, "overflow")
            assert page.locator("img").evaluate_all("imgs => imgs.every(i => i.complete && i.naturalWidth > 0 || i.loading === 'lazy')"), file.name
        if width in (390, 1440):
            page.goto(BASE)
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(RESULTS / f"home-{width}.png"), full_page=True)
    assert not errors, errors
    print("PASS: all pages at 320, 390, 768 and 1440px, no overflow or JavaScript exceptions")

    page.set_viewport_size({"width": 390, "height": 850})
    page.goto(BASE)
    page.keyboard.press("Tab")
    expect(page.get_by_role("link", name="Skip to content")).to_be_focused()
    page.get_by_role("button", name="Toggle menu").click()
    expect(page.locator("#main-nav")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator(".menu")).to_have_attribute("aria-expanded", "false")
    expect(page.locator(".menu")).to_be_focused()
    page.goto(f"{BASE}/faq.html")
    summary = page.locator("summary").first
    summary.focus()
    page.keyboard.press("Enter")
    expect(page.locator("details").first).to_have_attribute("open", "")
    print("PASS: skip link, mobile menu Escape/focus and keyboard FAQ expansion")

    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(BASE)
    secondary = page.locator(".hero .btn.secondary")
    secondary.hover()
    expect(secondary).to_have_css("color", "rgb(255, 255, 255)")
    expect(secondary).to_have_css("background-color", "rgb(6, 14, 88)")
    secondary.focus()
    expect(secondary).to_have_css("color", "rgb(255, 255, 255)")
    expect(page.locator(".hero-photo")).to_have_css("animation-name", "photo-arrive")
    page.emulate_media(reduced_motion="reduce")
    page.reload()
    expect(page.locator(".hero-photo")).to_have_css("animation-name", "none")
    secondary.hover()
    expect(secondary).to_have_css("transform", "none")
    page.emulate_media(reduced_motion="no-preference")
    print("PASS: secondary button hover/focus colors, entrance animation and reduced-motion fallback")

    page.goto(f"{BASE}/pricing.html")
    for tier, discount in (("founder", 10), ("standard", 0)):
        page.locator("#rate-tier").select_option(tier)
        for amount in (59, 79, 94):
            page.locator("#membership").select_option(str(amount))
            page.locator("#crew").fill("15")
            expect(page.locator("#monthly")).to_have_text(f"${15 * (amount - discount):,}")
            expect(page.locator("#annual")).to_have_text(f"${180 * (amount - discount):,}")
    for value in ("0", "-1", "1.5", "10001", ""):
        page.locator("#crew").fill(value)
        expect(page.locator("#monthly")).to_have_text("—")
        assert not page.locator("#crew").evaluate("el => el.checkValidity()")
    page.locator("#crew").fill("10000")
    expect(page.locator("#monthly")).to_have_text("$940,000")
    print("PASS: six pricing combinations, invalid crew inputs and upper boundary")

    for file, name in (("get-started.html", "employer-inquiry"), ("partners.html", "partner-inquiry")):
        page.goto(f"{BASE}/{file}?ref=test-partner&interest=founder-rate")
        assert not page.locator("form").evaluate("el => el.checkValidity()")
        page.locator("#yourname").fill("Test Person")
        page.locator("#businessname" if name == "employer-inquiry" else "#firmname").fill("Test Business")
        page.locator("#email").fill("test@example.com")
        page.locator("#phone").fill("555-0100")
        page.locator("#state").select_option("Other")
        if name == "employer-inquiry":
            expect(page.locator("#state-note")).to_be_visible()
            expect(page.locator("#referralcode")).to_have_value("test-partner")
            expect(page.locator("#interest")).to_have_value("founder-rate")
            page.locator("#numberofemployees").select_option(index=1)
            page.locator("#typeofbusiness").select_option("HVAC")
        else:
            page.locator("#partnertype").select_option("Payroll")
            page.locator("#approximatenumberofcontractorclients").fill("5")
        page.locator('[name="contact-consent"]').check()
        assert page.locator("form").evaluate("el => el.checkValidity()")
        def fail(route):
            if route.request.method == "POST":
                route.fulfill(status=503, body="Unavailable")
            else:
                route.continue_()
        page.route(f"{BASE}/", fail)
        page.locator('[type="submit"]').click()
        expect(page.locator(".form-status")).to_contain_text("couldn’t confirm")
        expect(page.locator("#yourname")).to_have_value("Test Person")
        expect(page.locator('[type="submit"]')).to_be_enabled()
        page.unroute(f"{BASE}/", fail)
        captured = []
        def succeed(route):
            if route.request.method == "POST":
                captured.append(parse_qs(route.request.post_data))
                route.fulfill(status=200, body="OK")
            else:
                route.continue_()
        page.route(f"{BASE}/", succeed)
        page.locator('[type="submit"]').click()
        page.wait_for_url("**/thank-you.html")
        assert captured[0]["form-name"] == [name]
        assert captured[0]["contact-consent"] == ["yes"]
        page.unroute(f"{BASE}/", succeed)
    print("PASS: both inquiry forms: validation, mocked failure/retry, encoded payload and success navigation")

    context = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 850})
    no_js = context.new_page()
    no_js.goto(BASE)
    expect(no_js.locator("#main-nav")).to_be_visible()
    no_js.goto(f"{BASE}/get-started.html")
    expect(no_js.locator("form")).to_have_attribute("action", "/thank-you.html")
    context.close()
    browser.close()
    print("PASS: no-JavaScript navigation and native form fallback")

print("All local checks passed. Live Netlify capture/email/DNS still need deployment verification.")
