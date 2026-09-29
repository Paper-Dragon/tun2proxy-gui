"""Generate multi-size application icon from resources/icon.png (or draw fallback)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PNG = ROOT / "resources" / "icon.png"
ICO = ROOT / "resources" / "icon.ico"


def make_ico_from_png(
    png_path: Path,
    ico_path: Path,
    sizes: tuple[int, ...] = (16, 32, 48, 64, 128, 256),
) -> None:
    from PIL import Image

    img = Image.open(png_path).convert("RGBA")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    ico_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(ico_path, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"wrote {ico_path} ({ico_path.stat().st_size} bytes)")


if __name__ == "__main__":
    if not PNG.exists():
        raise SystemExit(f"missing source image: {PNG}")
    make_ico_from_png(PNG, ICO)
