"""Create/update the eight industries (Sector records) shown in the Industries menu. Safe to re-run.

    python manage.py load_industries

Photos: an image uploaded on the industry in the admin wins; otherwise the default photo in
core/images.py (SECTOR) is used.
"""
from django.core.management.base import BaseCommand

from core.models import Sector

INDUSTRIES = [
    ("retail-fuel-stations", "Retail Fuel Stations", "station",
     "From single independent sites to national networks, we equip and maintain forecourts that are safe, accurate and profitable: new builds, rebrands and upgrades.",
     "New station design and construction\nDispenser supply and upgrades\nTank automation and leak detection\nForecourt controllers and payments\nPreventive maintenance contracts\nCalibration and verification"),
    ("commercial-fleet", "Commercial & Fleet Operations", "truck",
     "On-site fuelling for transport companies, logistics fleets, bus operators and delivery networks, with the control and reporting needed to stop fuel loss.",
     "Private fleet fuelling stations\nHigh-flow truck dispensers\nFleet cards, tags and fuel management\nAdBlue (DEF) dispensing\nMobile and skid tanks\nUsage reporting by vehicle and driver"),
    ("terminals-depots", "Oil Depots & Terminals", "terminal",
     "Equipment and engineering for bulk fuel terminals and storage depots: receiving, storing, metering and loading product safely and accurately.",
     "Bulk storage tank works\nTanker unloading and metering skids\nTransfer pumps and pipework\nCustody-transfer metering\nTank gauging and inventory control\nIntegrity testing and maintenance"),
    ("industrial-fuel", "Industrial & Manufacturing", "factory",
     "Reliable fuel supply infrastructure for factories, processing plants, mines, quarries and construction sites that cannot afford downtime.",
     "Above-ground and bunded tanks\nOn-site dispensing for plant and machinery\nBoiler and process fuel systems\nTransfer pumps and filtration\nFuel polishing and tank cleaning\nSafety and compliance audits"),
    ("aviation-fuel", "Aviation Fuel Infrastructure", "plane",
     "Support for airports, airstrips and aviation fuel operators: storage, filtration, metering and dispensing equipment built for strict aviation fuel quality standards.",
     "Aviation fuel storage and handling\nFiltration and water separation\nPrecision metering\nHydrant and bowser equipment support\nQuality and safety inspections\nPlanned maintenance"),
    ("marine-port", "Marine & Port Operations", "ship",
     "Fuel handling for ports, harbours, marinas and bunkering operations, where corrosion resistance, spill prevention and accurate transfer are critical.",
     "Port and marina fuel stations\nBunkering transfer and metering\nCorrosion-resistant pipework\nSpill containment and safety\nStorage tank installation\nInspection and maintenance"),
    ("energy-power", "Energy & Power Facilities", "bolt",
     "Fuel systems for power stations, independent power producers and standby generation, keeping engines supplied and fuel stocks accurately measured.",
     "Bulk and day-tank systems\nGenerator fuel supply and transfer\nTank gauging and remote monitoring\nFuel polishing and filtration\nLeak detection\n24/7 maintenance support"),
    ("government-facilities", "Government & Industrial Facilities", "govt",
     "Secure, compliant fuel installations for government institutions, hospitals, security services and large industrial estates, including standby power fuel systems.",
     "Standby generator fuel systems\nSecure on-site fuel stations\nAccess-controlled dispensing\nCompliance-focused installations\nTank testing and certification\nLong-term maintenance contracts"),
]


class Command(BaseCommand):
    help = "Create/update the eight industries."

    def handle(self, *args, **opts):
        for order, (slug, name, icon, summary, caps) in enumerate(INDUSTRIES):
            obj, created = Sector.objects.update_or_create(slug=slug, defaults=dict(
                name=name, icon=icon, summary=summary, capabilities=caps, order=order, is_active=True))
            self.stdout.write(f"{'+' if created else '~'} {name}")
        keep = [i[0] for i in INDUSTRIES]
        hidden = Sector.objects.exclude(slug__in=keep).update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"{len(INDUSTRIES)} industries loaded; {hidden} other(s) hidden."))
