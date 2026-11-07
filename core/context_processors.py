from . import images
from .models import ProductCategory, Sector, Service

# Bump to force browsers to reload CSS/JS after changes.
ASSET_VERSION = "25"

COMPANY = {
    "name": "Master Octagon",
    "legal_name": "Master Octagon Limited",
    "tagline": "Petroleum equipment & engineering services for East Africa",
    "phone": "+254 11 8187121",
    "email": "info@octagonmasters.com",
    "address": "Lavington, Gitanga Road, Nairobi, Kenya · East Africa",
    "hours": "Mon – Fri 8:00 – 17:30 · Sat 9:00 – 13:00",
    "countries": ["Kenya", "Uganda", "Tanzania", "Rwanda", "Burundi", "South Sudan", "DR Congo", "Ethiopia"],
}


def company(request):
    return {
        "company": COMPANY,
        "img": images.page_images(),
        "asset_version": ASSET_VERSION,
        "nav_categories": ProductCategory.objects.filter(is_active=True),
        "nav_services": Service.objects.filter(is_active=True),
        "nav_industries": Sector.objects.filter(is_active=True).prefetch_related("gallery"),
    }
