"""Generate local web assets from the client's original images (Pillow required)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
for source, target, width in [
    ("hero-worker.png", "hero-worker.webp", 1200),
    ("logo-horizontal.jpg", "logo-horizontal.webp", 520),
    ("logo-stacked.jpg", "logo-stacked.webp", 410),
]:
    with Image.open(ROOT / source) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((width, 2000), Image.Resampling.LANCZOS)
        image.save(ROOT / target, "WEBP", quality=82, method=6)
        print(f"{source}: {original.size} -> {target}: {image.size}, {(ROOT / target).stat().st_size:,} bytes")

# JPEG is widely supported by social sharing crawlers.
card = Image.new("RGB", (1200, 630), "#eff8ff")
draw = ImageDraw.Draw(card)
with Image.open(ROOT / "logo-horizontal.jpg") as original:
    logo = original.convert("RGB")
    logo.thumbnail((430, 130), Image.Resampling.LANCZOS)
    card.paste(logo, (70, 55))
font_path = Path("C:/Windows/Fonts/arialbd.ttf")
font = ImageFont.truetype(str(font_path), 66) if font_path.exists() else ImageFont.load_default(size=66)
draw.text((70, 235), "Healthcare built\nfor the trades.", fill="#060e58", font=font, spacing=12)
draw.rectangle((70, 470, 190, 477), fill="#0079ff")
small = ImageFont.truetype(str(font_path), 26) if font_path.exists() else ImageFont.load_default(size=26)
draw.text((70, 520), "Work healthier. Live brighter.", fill="#0758b7", font=small)
with Image.open(ROOT / "hero-worker.webp") as image:
    card.paste(ImageOps.fit(image, (390, 630), centering=(0.6, 0.5)), (810, 0))
card.save(ROOT / "social-card.jpg", quality=85, optimize=True)
