from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Simple line icons (24x24, stroke = currentColor)
ICONS = {
    "pump": '<path d="M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16"/><path d="M3 21h12"/><path d="M6 8h6"/><path d="M14 10h2a2 2 0 0 1 2 2v4a1.5 1.5 0 0 0 3 0V8l-3-3"/>',
    "tank": '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "gauge": '<path d="M12 14l4-4"/><circle cx="12" cy="14" r="1"/><path d="M3.3 19a10 10 0 1 1 17.4 0"/>',
    "valve": '<path d="M2 12h4"/><path d="M18 12h4"/><path d="M6 7l12 10V7L6 17z"/><path d="M12 12V4"/><path d="M9 4h6"/>',
    "hose": '<path d="M4 4h4v6a4 4 0 0 0 8 0V8"/><path d="M14 4h4v4h-4z"/><path d="M12 14v6"/><path d="M9 20h6"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "build": '<path d="M3 21h18"/><path d="M5 21V10l7-5 7 5v11"/><path d="M9 21v-6h6v6"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M9 11h6M9 15h4"/>',
    "calibrate": '<circle cx="12" cy="12" r="8"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/><circle cx="12" cy="12" r="2"/>',
    "station": '<path d="M3 21h18"/><path d="M2 8h20l-2-4H4z"/><path d="M5 8v13M19 8v13"/><rect x="9" y="12" width="6" height="9" rx="1"/>',
    "terminal": '<path d="M3 21h18"/><ellipse cx="7" cy="10" rx="4" ry="2"/><path d="M3 10v9h8v-9"/><ellipse cx="17" cy="13" rx="4" ry="2"/><path d="M13 13v6h8v-6"/>',
    "factory": '<path d="M3 21V11l5 3V11l5 3V7h3l1 14"/><path d="M17 7V3h3v18"/><path d="M2 21h20"/>',
    "plane": '<path d="M21 15l-8-4V4.5a1.5 1.5 0 0 0-3 0V11l-8 4v2l8-2v4l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-4l8 2z"/>',
    "check": '<path d="M5 12l5 5L20 7"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "chevron": '<path d="M6 9l6 6 6-6"/>',
    "arrow-up-right": '<path d="M7 17L17 7"/><path d="M8 7h9v9"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "truck": '<path d="M2 7h11v9H2z"/><path d="M13 10h4l3 3v3h-7z"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="16.5" cy="17.5" r="1.8"/>',
    "ship": '<path d="M3 15l2 5h14l2-5z"/><path d="M5 15V9h14v6"/><path d="M9 9V5h6v4"/><path d="M2 21c2 0 2-1 4-1s2 1 4 1 2-1 4-1 2 1 4 1 2-1 4-1"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "govt": '<path d="M3 21h18"/><path d="M4 10h16"/><path d="M12 3l9 5H3z"/><path d="M6 10v8M10 10v8M14 10v8M18 10v8"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "leaf": '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19l7-7"/>',
}


@register.simple_tag
def icon(name, size=24, cls=""):
    sw = "2" if int(size) <= 16 else "1.5"
    body = ICONS.get(name, ICONS["pump"])
    return mark_safe(
        f'<svg class="icon {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


_md_cache = {}


@register.filter
def md(url):
    """Medium (800 px) version of a local photo URL if one exists (see optimize_images), else the URL."""
    if not url or url.startswith("http"):
        return url
    if url in _md_cache:
        return _md_cache[url]
    from pathlib import Path
    from django.conf import settings

    result = url
    path_part, dot, ext = url.rpartition(".")
    candidate = f"{path_part}@md.{ext}" if dot else url
    if url.startswith(settings.MEDIA_URL):
        fs = Path(settings.MEDIA_ROOT) / candidate[len(settings.MEDIA_URL):]
    elif url.startswith("/static/"):
        fs = Path(settings.BASE_DIR) / "static" / candidate[len("/static/"):]
    else:
        fs = None
    if fs is not None and fs.exists():
        result = candidate
    _md_cache[url] = result
    return result
