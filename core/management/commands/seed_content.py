"""Load starter website content. Safe to re-run: existing records (by slug/title) are updated.

All content here is placeholder copy — edit it in the Django admin to match real products, brands and projects.
"""
from django.core.management.base import BaseCommand

from core.models import Product, ProductCategory, Project, Sector, Service

CATEGORIES = [
    ("fuel-dispensers", "Fuel Dispensers", "pump",
     "Electronic and mechanical fuel dispensers for petrol, diesel and kerosene — single, multi-product and high-flow models for retail forecourts and fleet depots.",
     [
         ("Multi-product retail dispenser", "Four-nozzle electronic dispenser for busy forecourts.",
          "A robust, high-accuracy dispenser designed for high-traffic retail stations. Supports up to four products with simultaneous fuelling on both sides.",
          "Up to 4 products / 8 nozzles\nElectronic totalisers and backlit display\nPre-set by volume or amount\nForecourt controller ready\nCorrosion-resistant stainless cladding", True),
         ("High-flow diesel dispenser", "80–130 L/min dispensing for trucks and buses.",
          "Engineered for truck stops, transport depots and mining fleets where fast refuelling reduces vehicle downtime.",
          "Flow rates up to 130 L/min\nSatellite dispenser option\nHeavy-duty 1\" hose and nozzle\nFleet card integration", True),
         ("Compact mechanical dispenser", "Reliable mechanical meter for off-grid and rural sites.",
          "A simple, rugged unit for locations with unreliable power or low throughput, with optional solar-powered pumping.",
          "Mechanical register — no electronics to fail\nSuitable for rural and farm sites\nOptional solar pump kit", False),
     ]),
    ("storage-tanks", "Storage Tanks", "tank",
     "Underground and above-ground storage tanks in steel and composite construction, single or double-wall, fabricated to international standards.",
     [
         ("Double-wall underground tank", "Steel/FRP double-wall tank with interstitial monitoring.",
          "Double-wall underground storage tanks give a secondary containment barrier and continuous leak monitoring to protect groundwater.",
          "Capacities 10,000 – 100,000 L\nSingle or multi-compartment\nInterstitial leak monitoring\nAnti-corrosion coating", True),
         ("Above-ground skid tank", "Self-bunded tank with integrated pump for industrial sites.",
          "A complete, transportable fuelling station for construction, mining, agriculture and generator sites.",
          "Self-bunded 110% containment\nIntegrated pump, meter and hose reel\nLockable cabinet\nCapacities 2,000 – 60,000 L", True),
     ]),
    ("tank-automation", "Tank Gauging & Automation", "gauge",
     "Automatic tank gauges, leak detection, forecourt controllers and station management systems that give real-time visibility of stock and sales.",
     [
         ("Automatic tank gauge (ATG)", "Real-time stock, water and temperature monitoring.",
          "Magnetostrictive probes and a console that report fuel level, water ingress and temperature for every tank, with alarms and delivery reconciliation.",
          "Accuracy to ±1 mm\nWater detection and alarms\nDelivery and variance reports\nRemote monitoring over the internet", True),
         ("Forecourt controller & station software", "Centralised control of pumps, prices and sales.",
          "Connects dispensers, tank gauges and payment terminals into one system for price control, shift reports and head-office reporting.",
          "Remote price changes\nShift and attendant reconciliation\nCard, mobile money and fleet payments\nCloud dashboards for multi-site networks", False),
     ]),
    ("terminal-equipment", "Terminal & Depot Equipment", "terminal",
     "Loading arms, flow meters, batch controllers and pumping systems for bulk fuel terminals, depots and aviation fuel facilities.",
     [
         ("Bottom & top loading arms", "Safe, efficient road tanker loading.",
          "Loading arms with vapour recovery options for terminals and depots, configured to your gantry layout.",
          "Top and bottom loading configurations\nVapour recovery connections\nDry-break couplers\nOverfill protection integration", False),
         ("Custody-transfer metering skid", "Positive displacement or Coriolis metering with batch control.",
          "Pre-assembled meter skids for accurate custody transfer at loading bays and receipt points.",
          "PD or Coriolis meters\nBatch controllers and additive injection\nProver connections\nFactory tested before delivery", True),
     ]),
    ("pumps-valves", "Pumps, Valves & Piping", "valve",
     "Submersible turbine pumps, transfer pumps, valves, flexible piping and fittings for fuel systems.",
     [
         ("Submersible turbine pump", "Quiet, efficient pumping from underground tanks.",
          "Submersible pumps deliver fuel from the tank to multiple dispensers with consistent pressure and line leak detection.",
          "Variable-speed options\nMechanical or electronic line leak detection\nSuitable for petrol, diesel and ethanol blends", False),
         ("Flexible underground piping", "Double-wall, corrosion-free fuel piping.",
          "Flexible piping systems reduce joints, installation time and leak risk compared with rigid steel lines.",
          "Double-wall with interstitial monitoring\nNo underground joints\nUL-listed components", False),
     ]),
    ("accessories-safety", "Accessories & Safety", "shield",
     "Nozzles, hoses, breakaways, spill containment, fire suppression and signage that keep forecourts safe and compliant.",
     [
         ("Automatic nozzles & breakaways", "Auto shut-off nozzles and safety breakaway couplings.",
          "Quality nozzles and breakaways minimise spills and prevent damage when a vehicle drives off with the nozzle attached.",
          "Automatic shut-off\nReconnectable breakaways\nVapour recovery versions", False),
         ("Spill containment & sumps", "Tank and dispenser sumps, spill buckets and manholes.",
          "Containment sumps under dispensers and at tank tops capture drips and leaks before they reach the soil.",
          "Watertight entry fittings\nSensors for sump monitoring\nTraffic-rated manhole covers", False),
     ]),
]

CODES = {'fuel-dispensers': 'DSP', 'storage-tanks': 'UST', 'tank-automation': 'ATG', 'terminal-equipment': 'TRM', 'pumps-valves': 'PVP', 'accessories-safety': 'SAF'}

SERVICES = [
    ("station-design-construction", "Station Design & Construction", "build",
     "Turnkey design and build of new retail fuel stations and depot upgrades.",
     "We manage the full project — from feasibility, site layout and approvals through civil works, canopy, mechanical and electrical installation to commissioning. One contract, one accountable team.",
     "Site survey and feasibility\nForecourt layout and engineering drawings\nRegulatory and environmental approvals support\nCivil, canopy and building works\nMechanical and electrical installation\nTesting, commissioning and handover"),
    ("equipment-installation", "Equipment Installation & Commissioning", "wrench",
     "Professional installation of dispensers, tanks, pumps, piping and automation.",
     "Our certified technicians install and commission petroleum equipment to manufacturer specifications and applicable standards, with pressure testing and full documentation.",
     "Tank installation and pressure testing\nDispenser and pump installation\nPiping and hazardous-area electrical works\nATG and forecourt controller set-up\nCommissioning reports and as-built drawings"),
    ("maintenance-repair", "Maintenance & Repair", "clipboard",
     "Planned preventive maintenance and 24/7 breakdown support.",
     "Keep your sites running with scheduled maintenance contracts and fast emergency response. We stock critical spares locally to minimise downtime.",
     "Preventive maintenance contracts\n24/7 breakdown call-out\nSpare parts supply\nDispenser refurbishment\nService reports and asset records"),
    ("calibration-verification", "Calibration & Verification", "calibrate",
     "Accurate metering through dispenser and meter calibration.",
     "We calibrate dispensers, flow meters and tank charts using certified measures so every litre sold is accounted for, and prepare sites for weights and measures verification.",
     "Dispenser calibration with certified provers\nFlow meter calibration\nTank calibration and charting\nPre-verification inspections"),
    ("tank-testing-cleaning", "Tank Testing, Cleaning & Integrity", "tank",
     "Tank and line tightness testing, cleaning and remediation.",
     "Protect your stock and the environment with periodic tank and line integrity testing, tank cleaning and fuel polishing, and leak investigation.",
     "Tank and line tightness testing\nTank cleaning and sludge removal\nFuel polishing and water removal\nLeak investigation and repair"),
    ("safety-compliance", "Safety & Compliance Audits", "shield",
     "Inspections and audits to keep facilities safe and compliant.",
     "Our engineers inspect forecourts and depots against regulatory and industry standards, identify risks and recommend practical corrective actions.",
     "Site safety and hazardous-area audits\nFire protection system checks\nEnvironmental compliance assessments\nStaff safety awareness training"),
]

SECTORS = [
    ("retail-fuel-stations", "Retail Fuel Stations", "station",
     "From single independent sites to national networks, we equip and maintain forecourts that are safe, accurate and profitable — new builds, rebrands and upgrades.",
     "New station design and construction\nDispenser supply and upgrades\nTank automation and leak detection\nForecourt controllers and payments\nPreventive maintenance contracts\nCalibration and verification"),
    ("terminals-depots", "Terminals & Depots", "terminal",
     "We support bulk fuel terminals, storage depots and aviation fuel facilities with loading, metering and storage equipment and specialist engineering.",
     "Loading arms and gantry equipment\nCustody-transfer metering skids\nBatch controllers and automation\nBulk storage tank works\nPumping and piping systems\nIntegrity testing and maintenance"),
    ("industrial-fuel", "Industrial Fuel Operations", "factory",
     "On-site fuelling for fleets, mining, construction, agriculture, manufacturing and power generation — with tight control of fuel use.",
     "Self-bunded skid tanks\nHigh-flow fleet dispensers\nFuel management and fleet tags\nGenerator fuel systems\nMobile and containerised stations\nFuel polishing and tank cleaning"),
]

PROJECTS = [
    ("New-build retail fuel station", "Nairobi", "Kenya", "retail-fuel-stations", 2025,
     "Turnkey construction of a six-pump forecourt including double-wall tanks, flexible piping, ATG and forecourt controller."),
    ("Depot loading bay upgrade", "Mombasa", "Kenya", "terminals-depots", 2024,
     "Replacement of loading arms and installation of custody-transfer metering skids with batch control on four loading bays."),
    ("Mine-site fuelling facility", "Geita", "Tanzania", "industrial-fuel", 2024,
     "Supply and installation of above-ground bunded tanks and high-flow dispensers with fleet fuel management for haul trucks."),
    ("Network-wide dispenser upgrade", "Kampala", "Uganda", "retail-fuel-stations", 2023,
     "Replacement of legacy dispensers across multiple stations, with calibration and integration into central station software."),
    ("Generator fuel system", "Kigali", "Rwanda", "industrial-fuel", 2023,
     "Bulk storage, transfer pumps and day-tank automation for a standby power plant."),
    ("Tank integrity programme", "Nakuru", "Kenya", "retail-fuel-stations", 2022,
     "Tank and line tightness testing, cleaning and remediation across a regional station network."),
]


class Command(BaseCommand):
    help = "Seed starter content (categories, products, services, sectors, projects)."

    def handle(self, *args, **opts):
        from django.utils.text import slugify

        for i, (slug, name, icon, summary, products) in enumerate(CATEGORIES):
            cat, _ = ProductCategory.objects.update_or_create(
                slug=slug, defaults=dict(name=name, code=CODES.get(slug, ''), icon=icon, summary=summary, order=i))
            for j, (pname, psum, pdesc, feats, featured) in enumerate(products):
                Product.objects.update_or_create(
                    slug=slugify(pname), defaults=dict(category=cat, name=pname, summary=psum, description=pdesc,
                                                       features=feats, is_featured=featured, order=j))

        for i, (slug, name, icon, summary, desc, deliv) in enumerate(SERVICES):
            Service.objects.update_or_create(slug=slug, defaults=dict(
                name=name, icon=icon, summary=summary, description=desc, deliverables=deliv, order=i))

        sectors = {}
        for i, (slug, name, icon, summary, caps) in enumerate(SECTORS):
            sectors[slug], _ = Sector.objects.update_or_create(slug=slug, defaults=dict(
                name=name, icon=icon, summary=summary, capabilities=caps, order=i))

        for i, (title, loc, country, sector, year, summary) in enumerate(PROJECTS):
            Project.objects.update_or_create(title=title, defaults=dict(
                location=loc, country=country, sector=sectors[sector], year=year, summary=summary, order=i))

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {ProductCategory.objects.count()} categories, {Product.objects.count()} products, "
            f"{Service.objects.count()} services, {Sector.objects.count()} sectors, {Project.objects.count()} projects."))
