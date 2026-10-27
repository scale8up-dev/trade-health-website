"""Package only public site files for Netlify Drop. No JS toolchain required."""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"
FILES = [
    "index.html", "how-it-works.html", "pricing.html", "faq.html",
    "partners.html", "get-started.html", "privacy.html", "terms.html",
    "thank-you.html", "404.html", "style.css", "launch.css", "app.js",
    "hero-worker.webp", "logo-horizontal.webp", "logo-stacked.webp",
    "social-card.jpg", "favicon.svg", "robots.txt", "sitemap.xml",
    "_headers", "_redirects",
]
OUTPUT.mkdir(exist_ok=True)
# Netlify can restore/write its configuration inside the publish directory.
# It is known build metadata, not a public asset or an unexpected user file.
metadata = OUTPUT / "netlify.toml"
build_metadata = {metadata.name} if metadata.is_file() else set()
unexpected = {p.name for p in OUTPUT.iterdir()} - set(FILES) - build_metadata
if unexpected:
    raise SystemExit(f"Unexpected files in dist; inspect before packaging: {unexpected}")
if metadata.is_file():
    metadata.unlink()
for name in FILES:
    shutil.copy2(ROOT / name, OUTPUT / name)
with zipfile.ZipFile(ROOT / "tradehealth-netlify.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for name in FILES:
        archive.write(OUTPUT / name, name)
print(f"Ready: {OUTPUT} ({len(FILES)} files) and tradehealth-netlify.zip")
