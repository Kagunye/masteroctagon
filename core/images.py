"""Site photography.

How to use your own images:
- Products, categories, services, sectors, projects: upload an image on the record in the admin.
- Page banners (home hero, page headers, etc.): put a file in static/img/pages/ named after
  the page key, e.g. static/img/pages/hero.jpg, about.jpg, products.jpg (jpg, jpeg, png or webp).
  Keys: bw (home black-and-white band), hero, home_intro (home "Built on engineering" image), intro (About page), why, about, products, services, sectors, projects, contact, quote.

Anything you haven't supplied falls back to a placeholder photo from Unsplash
(free licence: https://unsplash.com/license).
"""
from django.conf import settings
from django.templatetags.static import static

PAGE_DIR = settings.BASE_DIR / "static" / "img" / "pages"
EXTS = ("jpg", "jpeg", "png", "webp")

def unsplash(photo_id, w=1600):
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={w}&q=75"


PHOTOS = {
    "refinery_dusk": "1786532852011-443cba5dc9fe",
    "refinery_night": "1588011930968-eadac80e6a5a",
    "tank_farm_port": "1755267657872-9c456513cd22",
    "storage_tanks": "1780882899461-0b158f457b44",
    "station_night": "1695561324569-5e47c76dc0a3",
    "nozzles": "1654334036171-e01e52b2ce8e",
    "tanker": "1656988826404-bbb5ccb779bc",
    "pipes": "1620203853151-496c7228306c",
    "engineer": "1621905252507-b35492cc74b4",
    "technician": "1688841747582-41097036109d",
    "fleet_trucks": "1565793298595-6a879b1d9492",
    "aircraft_refuel": "1541612529637-7f8d12b21635",
    "tankers_anchor": "1569350818415-ffe59f37e028",
    "power_plant": "1509390288171-ce2088f7d08e",
    "standby_generator": "1780445392484-38a4852a1fd8",
}

# Page-level imagery
PAGE = {
    "hero": "refinery_dusk",
    "intro": "engineer",
    "home_intro": "engineer",
    "why": "refinery_night",
    "bw": "technician",
    "about": "tank_farm_port",
    "products": "nozzles",
    "services": "pipes",
    "sectors": "storage_tanks",
    "projects": "tanker",
    "contact": "station_night",
    "quote": "tank_farm_port",
}

CATEGORY = {
    "fuel-dispensers": "nozzles",
    "storage-tanks": "storage_tanks",
    "tank-automation": "station_night",
    "terminal-equipment": "refinery_night",
    "pumps-valves": "pipes",
    "accessories-safety": "technician",
}

SERVICE = {
    "station-design-construction": "station_night",
    "equipment-installation": "engineer",
    "maintenance-repair": "technician",
    "calibration-verification": "nozzles",
    "tank-testing-cleaning": "storage_tanks",
    "safety-compliance": "pipes",
}

SECTOR = {
    "retail-fuel-stations": "station_night",
    "commercial-fleet": "fleet_trucks",
    "terminals-depots": "storage_tanks",
    "industrial-fuel": "pipes",
    "aviation-fuel": "aircraft_refuel",
    "marine-port": "tankers_anchor",
    "energy-power": "power_plant",
    "government-facilities": "standby_generator",
}


def photo(key, w=1600):
    return unsplash(PHOTOS.get(key, PHOTOS["refinery_dusk"]), w)


def _local(name):
    for ext in EXTS:
        if (PAGE_DIR / f"{name}.{ext}").exists():
            return static(f"img/pages/{name}.{ext}")
    return None


def page_images(w=2000):
    return {name: _local(name) or photo(key, w) for name, key in PAGE.items()}
