"""WSGI entry point. Vercel's Python runtime looks for a module-level ``app``."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()


def _bootstrap_on_vercel():
    """Prepare the database on a Vercel cold start: apply migrations and, if it is empty,
    load the site content (products, services, industries, galleries)."""
    from django.core.management import call_command
    from core.models import Product

    call_command("migrate", interactive=False, verbosity=0)
    if not Product.objects.exists():
        call_command("loaddata", "site_content", verbosity=0)


if os.environ.get("VERCEL"):
    _bootstrap_on_vercel()

app = application
