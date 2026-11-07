"""Shrink site photos for faster loading. Safe to re-run (already-small files are skipped).

    python manage.py optimize_images            # media/ and static/img/{stock,pages}
    python manage.py optimize_images --dry-run  # report only

Images are resized so their longest side is at most --max (default 1600 px) and re-encoded
(JPEG/WebP quality 80, PNG optimised). File names and formats stay the same, so every link keeps
working. A file is only replaced if the result is smaller.

It also writes a medium copy next to each photo (name@md.ext, 800 px) that the `md` template
filter uses for cards, thumbnails and menus.
"""
import io
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

FOLDERS = ["media", "static/img/stock", "static/img/pages"]
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


class Command(BaseCommand):
    help = "Resize and recompress site photos."

    def add_arguments(self, parser):
        parser.add_argument("--max", type=int, default=1600, help="Longest side in pixels.")
        parser.add_argument("--quality", type=int, default=80)
        parser.add_argument("--md", type=int, default=800, help="Medium copy size (0 to skip).")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **o):
        before = after = changed = 0
        for folder in FOLDERS:
            for path in sorted((Path(settings.BASE_DIR) / folder).rglob("*")):
                if path.suffix.lower() not in EXTS or not path.is_file() or "@md" in path.stem:
                    continue
                if o["md"] and not o["dry_run"]:
                    self.write_md(path, o["md"], o["quality"])
                old = path.stat().st_size
                before += old
                try:
                    data = self.shrink(path, o["max"], o["quality"])
                except Exception as e:
                    self.stderr.write(f"  skip {path.name}: {e}")
                    after += old
                    continue
                if data and len(data) < old * 0.95:
                    if not o["dry_run"]:
                        path.write_bytes(data)
                    after += len(data)
                    changed += 1
                else:
                    after += old
        verb = "Would save" if o["dry_run"] else "Saved"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} {(before - after) / 1e6:.1f} MB: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB "
            f"({changed} files optimised)."))

    def write_md(self, path, size, quality):
        md = path.with_name(f"{path.stem}@md{path.suffix}")
        if md.exists() and md.stat().st_mtime >= path.stat().st_mtime:
            return
        try:
            with Image.open(path) as im:
                if max(im.size) <= size * 1.15:
                    return  # already small; the filter falls back to the original
            md.write_bytes(self.shrink(path, size, quality))
        except Exception as e:
            self.stderr.write(f"  md skip {path.name}: {e}")

    def shrink(self, path, max_side, quality):
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)
        if max(im.size) > max_side:
            im.thumbnail((max_side, max_side), Image.LANCZOS)
        buf = io.BytesIO()
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        elif ext == ".webp":
            im.save(buf, "WEBP", quality=quality, method=6)
        elif ext == ".png":
            if im.mode in ("RGBA", "LA") or "transparency" in im.info:
                im.save(buf, "PNG", optimize=True)
            else:  # opaque PNG photo: palette-reduce for a much smaller file
                im.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(buf, "PNG", optimize=True)
        return buf.getvalue()
