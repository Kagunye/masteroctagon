"""Load the Ecotec product catalogue (supplier partnership) with photos from their Alibaba listings.

    python manage.py load_ecotec_catalogue            # download photos + update products
    python manage.py load_ecotec_catalogue --no-download   # update text only, keep existing photos

Safe to re-run. Each entry updates an existing product (matched by `match` slug, else `slug`)
or creates it. Photos are saved to media/products/gallery/<slug>-<n>.<ext> and replace the
product's gallery. Descriptions are our own wording based on the supplier's specifications.
"""
import io
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image

from core.models import Product, ProductCategory, ProductImage

SUPPLIER = "https://ecotecenergy.en.alibaba.com/"
CDN = "https://s.alicdn.com/@sc04/kf/"

CATALOGUE = [
    # ---------------- Fuel dispensers ----------------
    dict(
        match="multi-product-retail-dispenser", slug="multi-product-retail-dispenser",
        category="fuel-dispensers", name="Six-nozzle submersible fuel dispenser", featured=True,
        summary="High-accuracy multi-product dispenser for busy retail forecourts, fed by a submersible pump.",
        description=(
            "A commercial-grade dispenser built for high-traffic retail stations. Six nozzles let one island "
            "serve several vehicles and products at once, while the submersible-pump configuration keeps "
            "delivery smooth across all hoses.\n\n"
            "Metering is accurate to ±0.3%, and the unit is compatible with Fuelplus station management for "
            "remote pricing, shift reports and sales monitoring. Master Octagon supplies, installs and "
            "commissions the dispenser, and supports it with local spares."
        ),
        features="6 nozzles for multi-product forecourts\nMetering accuracy ±0.3%\nSubmersible-pump supply, 45 L/min per nozzle\nPetrol, diesel and kerosene\nCompatible with Fuelplus station management\n220 V supply, 0.75 kW\n2-year warranty",
        source="https://www.alibaba.com/product-detail/Ecotec-6-Nozzles-Ecotec-Submersible-Type_1602004490251.html",
        images=["H98c434f2a2d248308fc759079253e5ca4.jpg", "Hd2387895725d4ca9b1164784d7e07d94y.jpg", "H14534a7aef20452f80173549370c5475z.jpg", "Hd276647e14b2434baede3b719b1afc290.jpg", "H9de483f599354f75a328c9919eec8883r.jpg", "H75de966f104f43dfb57f7e695fa7f3c9z.jpg"],
        clear_main_image=True,
    ),
    dict(
        match="high-flow-diesel-dispenser", slug="high-flow-diesel-dispenser",
        category="fuel-dispensers", name="High-flow diesel dispenser", featured=True,
        summary="Robust dual-nozzle dispenser for truck stops, transport depots and fleet yards.",
        description=(
            "Engineered for transport depots, truck stops and mining fleets where fast, reliable refuelling "
            "reduces vehicle downtime. A heavy-duty cabinet, clear dual displays and robust hydraulics make it "
            "suited to demanding, high-throughput sites.\n\n"
            "Available in several cabinet and display styles, with options for fleet card control and "
            "integration with station management software."
        ),
        features="Dual nozzles with independent displays\nHeavy-duty hydraulics for high throughput\nSuitable for diesel, petrol and kerosene\nFleet card and station software integration\nMultiple cabinet and colour options",
        source="https://www.alibaba.com/product-detail/Eco-Por-La-Presente-Dispensador-De_1601386962362.html",
        images=None,  # keeps the six photos already loaded from this listing
    ),
    dict(
        match="compact-mechanical-dispenser", slug="mobile-fuel-dispenser",
        category="fuel-dispensers", name="Mobile fuel dispenser (M111)",
        summary="Compact dispenser with 10 m hose for tankers, bowsers and remote sites.",
        description=(
            "A compact, self-contained dispenser for mounting on fuel trucks, bowsers, skid tanks or at "
            "remote sites without a fixed forecourt. It runs on 12 V, 24 V, 220 V or 380 V, so it can be "
            "powered from a vehicle battery or mains supply.\n\n"
            "A 10-metre hose with automatic shut-off nozzle reaches vehicles and machinery directly, and the "
            "meter delivers around 45 L/min."
        ),
        features="12 V / 24 V / 220 V / 380 V options\nFlow rate approx. 45 L/min\n10 m hose with automatic shut-off nozzle\nDiesel, petrol and kerosene\nIdeal for tankers, bowsers and remote sites\nCE and ISO certified",
        source="https://www.alibaba.com/product-detail/Ecotec-Mobile-Fuel-Dispenser-with-10_1600454801884.html",
        images=["Hf58958f76bd84394afbfa3e7b0aac9e4Y.jpg", "H75219567bb0e4d48a47930a50be0ece68.jpg", "Ha062272fec3b4443b17215990d165706e.jpg", "H8a5de6d8fe0b464193ffef74724820feI.jpg", "Hdeeb1d2c0eac4cb0984e2e3e0d27a4743.jpg", "H4f02aabc95de4780995a2b07578f8776R.jpg"],
    ),
    # ---------------- Storage tanks ----------------
    dict(
        match="double-wall-underground-tank", slug="double-wall-underground-tank",
        category="storage-tanks", name="Double-walled underground storage tank", featured=True,
        summary="Sealed double-wall fuel tank from 5,000 to 100,000 litres for filling stations.",
        description=(
            "A sealed, double-walled cylindrical tank for underground fuel storage at filling stations. The "
            "secondary wall provides containment and an interstitial space for continuous leak monitoring, "
            "protecting soil and groundwater.\n\n"
            "Tanks are built to the capacity and dimensions your site requires, and are supplied with test "
            "reports and outgoing inspection video. Master Octagon handles excavation, installation, pressure "
            "testing and connection to your pipework."
        ),
        features="Capacities from 5,000 L to 100,000 L\nDouble-wall construction with leak monitoring\nSingle or multi-compartment\nBuilt to site dimensions\nFactory test report and inspection video provided",
        source="https://www.alibaba.com/product-detail/Double-Walled-Safety-Storage-Tank-for_1601400424363.html",
        images=["Hb8a03fcce1c445999e25eb6106405e63u.jpg", "H7a0b248cff414002a010a485f4794fbcF.png", "H07e59cc63d2e458685465c1850120ff7J.jpg", "Hb4fe9a13727544e1a43980f2ab005c9fd.jpg", "Hfdedf85e38514292973441e31abf25b4A.jpg", "H7616891cbd064158a35c38ad9a863dccA.jpg"],
    ),
    dict(
        match="above-ground-skid-tank", slug="fuel-cube-container-station",
        category="storage-tanks", name="Fuel cube container station (5,000 L)", featured=True,
        summary="Self-contained, double-wall tank with built-in dispenser for site and fleet fuelling.",
        description=(
            "A complete, transportable fuelling station: a double-walled carbon-steel tank with an integrated "
            "dispenser, ready to place on site and connect. It suits construction projects, mines, farms, "
            "generator sites and fleet depots that need secure on-site fuel without building a forecourt.\n\n"
            "The 6 mm steel shell and double wall give strong protection against leaks and damage."
        ),
        features="5,000 L capacity (other sizes available)\nDouble-wall carbon steel, 6 mm\nIntegrated fuel dispenser\nTransportable and quick to commission\nFor construction, mining, agriculture and fleets",
        source="https://www.alibaba.com/product-detail/FUEL-CUBE-Mobile-Container-Station-with_62311380188.html",
        images=["Hb87e389a24ed4c9a880f8fea365f18ccE.jpg"],
    ),
    # ---------------- Tank gauging & automation ----------------
    dict(
        match="automatic-tank-gauge-atg", slug="automatic-tank-gauge-atg",
        category="tank-automation", name="Automatic tank gauge with wireless probes (ATG)", featured=True,
        summary="Console and magnetostrictive probes reporting fuel and water levels to 0.01 mm.",
        description=(
            "An automatic tank gauging system that measures fuel level, water ingress and temperature in every "
            "tank. Probes communicate wirelessly over LoRa, so there is no need to trench new cables across a "
            "working forecourt.\n\n"
            "Readings resolve to 0.01 mm for both oil and water, supporting accurate stock reconciliation, "
            "delivery checks and early leak warnings. Probe lengths from 1 to 3.5 m suit most tank sizes, and "
            "electronics are housed in an ATEX-rated enclosure."
        ),
        features="Fuel and water level resolution 0.01 mm\nWireless LoRa probes, no new cabling\nProbe lengths 1 to 3.5 m\nATEX-rated electronics box\nLow power, 40 mA or less\nStock, delivery and variance reporting",
        source="https://www.alibaba.com/product-detail/Ecotec-Automatic-Tank-Monitor-Console-Fuel_1700000617501.html",
        images=["Hab6059db50444aa9be595d7d2a372902c.jpg", "H69b88f9c2cbb41f79c2fa8e3b0721b93e.jpg", "H16f8e4598fa14de9b05c2be6f0dbad96B.jpg", "Ubcdc454c10c54a539555886f28d7d4dcX.jpg", "Haa417757f16445a790197da8675e2458q.jpg", "H8b6d2aba128f4b7db7ee7602de58d0ebk.jpg"],
    ),
    dict(
        match="forecourt-controller-station-software", slug="pts-station-management-system",
        category="tank-automation", name="PTS controller and station management system",
        summary="Connects dispensers and tank gauges for remote pricing, reports and app monitoring.",
        description=(
            "The PTS controller links your dispensers and automatic tank gauges into one station management "
            "system. Owners and managers can change prices, review sales and shift reports, and monitor tank "
            "stock from a web dashboard or mobile app.\n\n"
            "It supports 1 to 8 nozzles per controller and works with ATEX and OIML-compliant equipment, making "
            "it a practical upgrade for independent stations and growing networks."
        ),
        features="Controls 1 to 8 nozzles per unit\nIntegrates automatic tank gauges (ATG)\nRemote price changes and sales reports\nMobile app and web dashboard\nShift and attendant reconciliation\nDesigned for a 10-year service life",
        source="https://www.alibaba.com/product-detail/Ecotec-Pts-Controller-Fuel-Station-Management_1600392173201.html",
        images=["Hca3338d33b5a4938aec9b00ebbe76103W.jpg", "Hb6e5d60875264feb9d5c4a636de8b713u.jpg", "H3cf39f3ebce048a38a5abda54e9923f4n.jpg", "H9f03f7261a8343dfa53d9e379a198763h.jpg", "He3e14c98b5904657abfc2655953e995e5.jpg", "H91c8a498ad3b4315a03570db1c55bb74i.jpg"],
    ),
    # ---------------- Terminal & depot equipment ----------------
    dict(
        match="custody-transfer-metering-skid", slug="electronic-discharging-meter-skid",
        category="terminal-equipment", name="Electronic discharging meter skid (250 L/min)", featured=True,
        summary="Metered unloading skid that measures every delivery from tanker to storage tank.",
        description=(
            "A pre-assembled unloading skid that meters fuel as it is discharged from road tankers into station "
            "or depot tanks, so every delivery is verified against the delivery note.\n\n"
            "The skid combines an LC positive-displacement meter, electronic display, explosion-proof electrical "
            "box and two rubber hoses, rated to 1.6 MPa and built to ATEX and OIML standards."
        ),
        features="Up to 250 L/min unloading rate\nLC positive-displacement meter\nElectronic display with explosion-proof box\nTwo rubber delivery hoses included\nMax pressure 1.6 MPa\nATEX and OIML standards",
        source="https://www.alibaba.com/product-detail/Ecotec-250LPM-Discharging-Flow-Meter-Unloading_1600481159814.html",
        images=["Hd1cc5fa6e72d4e2ba8d8b50ed28ed740k.jpg", "Hb072cc14a36b4575b239d1789273bd40K.jpg", "H7b352703c2d444d5922f1cadaa0caea0k.jpg", "Hcffa68b1226544809d4685a7dfae744fv.jpg", "H007b3ebdbffe4b7aa4593cb640775c02X.jpg", "Hc6ef87be73244e4992d740c91da3b44e9.jpg"],
    ),
    dict(
        match="bottom-top-loading-arms", slug="tank-truck-discharging-meter",
        category="terminal-equipment", name="3-inch tank truck discharging meter",
        summary="Industrial 3-inch meter skid for high-volume tanker unloading at depots.",
        description=(
            "A heavy-duty 3-inch metering skid for depots and large stations receiving bulk deliveries. It "
            "gives an accurate, independent record of the volume unloaded from each tank truck.\n\n"
            "Built around an LC meter with mechanical register and display, explosion-proof electrics and "
            "rubber hoses, rated to 1.6 MPa to ATEX and OIML standards."
        ),
        features="3-inch connections for bulk unloading\nLC meter with register and display\nExplosion-proof electrical box\nMax pressure 1.6 MPa\nATEX and OIML standards\n12-month warranty",
        source="https://www.alibaba.com/product-detail/Ecotec-3-Inch-Industrial-Discharging-Meter_1600481204695.html",
        images=["H64c46739ae984c7582f6d36c1452f05aG.jpg", "Hcb919489aaa4441eafaf7e42c7a0d096W.jpg", "H2cc54daadc884bc3990a083f1e788c803.jpg", "H9b917f9becc6479fa9e17b76ba462719s.jpg", "H36a0d725c769474caa50bcd8f373ae60G.jpg", "Hc7027257b0a143c4aa671586fa853fcfc.jpg"],
    ),
    # ---------------- Pumps, valves & piping ----------------
    dict(
        match="submersible-turbine-pump", slug="submersible-turbine-pump",
        category="pumps-valves", name="ATEX submersible turbine pump (1 to 2 HP)",
        summary="Explosion-proof submersible pump delivering up to 240 L/min to multiple dispensers.",
        description=(
            "An ATEX-certified submersible pump installed inside the underground tank to push fuel to several "
            "dispensers at once. It delivers consistent pressure and flow, quieter operation and fewer "
            "suction problems than dispenser-mounted pumps.\n\n"
            "Available in 1, 1.5 and 2 HP versions for 220 V or 380 V supply, with a 1.5-inch inlet and "
            "2-inch outlet."
        ),
        features="1 HP, 1.5 HP and 2 HP options\nMax flow up to 240 L/min\nATEX explosion-proof certified\n220 V / 380 V, 1.1 kW\n1.5-inch inlet, 2-inch outlet\nFeeds multiple dispensers from one tank",
        source="https://www.alibaba.com/product-detail/Ecotec-1HP-1-5HP-2HP-Submersible_62255729598.html",
        images=["Hb070b8b09aa34820b5059d6eb943182dw.jpg", "H89b27faa4c384a2cb90b56dff59835d7i.jpg", "H0878ecdacbb24ab2bb8387726625bcd9K.jpg", "H3116f0ec382a4a3886488d9e9b540042e.jpg", "H0dcdc963479743a49661596c00d9563bd.jpg", "H8daf31e6b81447adbebc41f305c2bf95a.jpg"],
    ),
    dict(
        match="flexible-underground-piping", slug="underground-petroleum-pipe",
        category="pumps-valves", name="HDPE underground petroleum pipe (UPP)",
        summary="Corrosion-free 1.5 and 2-inch HDPE fuel piping with a service life of up to 50 years.",
        description=(
            "Flexible HDPE underground petroleum pipe for connecting tanks, submersible pumps and dispensers. "
            "Unlike steel, it cannot corrode, and long continuous runs reduce buried joints and leak points.\n\n"
            "Supplied in 1.5-inch and 2-inch sizes in custom lengths, with matching elbows, tees and fittings, "
            "and a working life of up to 50 years."
        ),
        features="HDPE construction, corrosion-free\n1.5-inch and 2-inch sizes\nCustom lengths to minimise joints\nElbows, tees and fittings available\nService life up to 50 years",
        source="https://www.alibaba.com/product-detail/Ecotec-Oil-Station-Equipment-50mm-Single_1601365586801.html",
        images=["He8243f443b434de5b75b275b62b29079Q.jpg", "H8dfe253a9fde4dc1aa18a8c63fa20e4eS.jpg", "H2aba34c610964d01bf77a1ec42c8af59L.jpg", "He3a81ee759824854a19e7eb70b13d550L.png", "H439571448fab444aab22014ffabb21cep.jpg", "H11da4472992d4dfda1fdd53276f4a8b7U.jpg"],
    ),
    dict(
        match="rotary-vane-transfer-pump", slug="rotary-vane-transfer-pump",
        category="pumps-valves", name="YB-80 rotary vane transfer pump (3-inch)",
        summary="Industrial 3-inch vane pump for bulk transfer and tanker loading, 5 to 1,000 L/min.",
        description=(
            "A heavy-duty rotary vane pump for bulk fuel transfer at depots, terminals and on tank trucks. It "
            "self-primes reliably and handles a wide flow range, from 5 up to 1,000 L/min.\n\n"
            "Supplied as a complete set with a 7.5 kW motor and 3-inch connections, and certified to ATEX, "
            "OIML and MID standards."
        ),
        features="Flow range 5 to 1,000 L/min\n3-inch connections\n7.5 kW 380 V motor set\nRated speed 640 rpm\nATEX, OIML, MID and ISO certified\nFor depot transfer and tanker loading",
        source="https://www.alibaba.com/product-detail/Ecotec-Yb-Series-Rotary-Vane-Pump_1601201330850.html",
        images=["He9f81ae6c7a2435cb316394cafa6aa4fw.png", "Hf9c48ceea62b46bb915c6242ba215fe7t.jpg", "H11b9e3236671412b9247aec8855bfa26Z.png", "Hdfdb155e4ddc48ccbcd60dde732e8991g.jpg", "Ha5d14024873f4d829a79a9c83842d02aP.jpg", "H3f098d06adb143ffac090a3090e4f185T.png"],
    ),
    # ---------------- Accessories & safety ----------------
    dict(
        match="automatic-nozzles-breakaways", slug="automatic-fuel-nozzle",
        category="accessories-safety", name="High-flow automatic fuel nozzle",
        summary="Automatic shut-off nozzle for retail and fleet dispensers, up to 80 L/min.",
        description=(
            "An automatic shut-off nozzle that stops flow as soon as the tank is full, preventing spills and "
            "overfills. Suited to both retail and high-flow fleet dispensers.\n\n"
            "Fitted with a 3/4-inch spout and available with BSPF or NPT inlet threads to match your hoses."
        ),
        features="Automatic shut-off\nFlow up to 80 L/min\n3/4-inch spout\nBSPF or NPT inlet thread\nFor petrol, diesel and kerosene",
        source="https://www.alibaba.com/product-detail/Ecotec-High-Flow-Nozzle-Automatic-Nozzle_62244468021.html",
        images=["H27564f4f06d24cef8212793afa16c304p.jpg", "Hb0a1436ea9b44ddea56fc80b89e8e2667.jpg", "H7d1bdd9b9f584d92b7c09b921a1f917dh.jpg", "H51f930bdce1e4cc1b1ea62206dd740d59.jpg", "H7f6004181bb744d4b8f27ab5616c52eel.jpg", "H74b10d6d00fd4965ac2f6f827dc2a83b2.jpg"],
    ),
    dict(
        match="breakaway-valve", slug="breakaway-valve",
        category="accessories-safety", name="1-inch safety breakaway valve",
        summary="Separates the hose safely if a vehicle drives off with the nozzle still attached.",
        description=(
            "A safety breakaway coupling fitted between the dispenser hose and nozzle. If a driver pulls away "
            "with the nozzle still in the tank, it separates cleanly and seals both sides, preventing spills "
            "and damage to the dispenser.\n\n"
            "Rated to 18 bar and -40 °C to +120 °C, with a 1-inch connection."
        ),
        features="Seals both sides on separation\n1-inch connection\nWorking pressure 18 bar\nOperating range -40 °C to +120 °C\nProtects hoses and dispensers from drive-offs",
        source="https://www.alibaba.com/product-detail/Safety-Accessories-Breakaway-Valve-for-Fuel_1600489442451.html",
        images=["H3b200731b74449cc8ea08e2642a2a1a5H.jpg", "H90a1eede8a9e446cb93f7e31a1c78373F.jpg", "H7e6e942ad886428ba9de2e4abe1a2c47Z.jpg", "Hf0764a060e7e4abcadc5839c6f2d8eaeJ.jpg", "H22ff41105a89467fb5c0806a867370ce2.jpg", "H15b2f01afa934accb39c6f126446c4aex.jpg"],
    ),
    dict(
        match="spill-containment-sumps", slug="tank-manhole-cover",
        category="accessories-safety", name="Tank manhole and cover (16 or 20-inch)",
        summary="Durable SMC manhole for tank access chambers, round or square, flange-connected.",
        description=(
            "A tough SMC composite manhole and cover for underground tank access chambers. It keeps water and "
            "debris out of the tank-top area while giving easy access for gauging, maintenance and deliveries.\n\n"
            "Available in 16-inch and 20-inch diameters, round or square, with a flanged connection rated to "
            "0.9 MPa."
        ),
        features="SMC composite, corrosion-resistant\n16-inch or 20-inch diameter\nRound or square options\nFlanged connection, 0.9 MPa\nISO certified",
        source="https://www.alibaba.com/product-detail/Ecotec-Fuel-Station-Equipment-Manhole-Cover_1601365594758.html",
        images=["H0a49b8d56f7d47eaa877109f6fa2c699o.jpg", "Hc13acf1bcbc14a4e84b6fe8991232f4ad.jpg", "H45a4a63c62fc4983a85a9bf01d48c91dH.jpg", "H7a52a0f37d104e14a46dfd0c88ed1298E.jpg", "He504c4675a8348bb88c4a5ec28f0d125w.jpg", "H723a1529e4724304a1e674621691e019B.jpg"],
    ),
    # ---------------- Additional range ----------------
    dict(
        match="smart-fuel-dispenser", slug="smart-fuel-dispenser",
        category="fuel-dispensers", name="Smart fuel dispenser with large display",
        summary="Modern twin-pump dispenser with an oversized, easy-read display for retail forecourts.",
        description=(
            "A modern retail dispenser with a large, high-visibility display that customers and attendants can "
            "read at a glance, even in bright sunlight. Twin Tatsuno pumps support a wide flow range for both "
            "cars and light commercial vehicles.\n\n"
            "It runs on 110 V, 220 V or 380 V supplies and suits new builds and forecourt upgrades alike."
        ),
        features="Large high-visibility display\nTwin Tatsuno pump units\nFlow range 5 to 120 L/min\n110 / 220 / 380 V supply\nPetrol and diesel\n1-year warranty",
        source="https://www.alibaba.com/product-detail/Smart-Fuel-Dispenser-with-Large-Display_1601986289898.html",
        images=["H3afca129a37740308f27652d33641990H.png", "Hfabecde56ce84945854443ca7b05465dG.jpg", "Hf1fac17a722f4309997d68c587bc02ecl.jpg", "Hfb60275ad9544740adec654c14cdd77dS.jpg", "H5567c5b2f6274a7189d435a5a4fe5545D.jpg", "H9fbbe29173064ed5ac8f333f50562c4ag.jpg"],
    ),
    dict(
        match="heavy-duty-truck-dispenser", slug="heavy-duty-truck-dispenser",
        category="fuel-dispensers", name="Heavy-duty truck dispenser (200 L/min)",
        summary="Single-nozzle, 200 L/min dispenser for fast refuelling of trucks, buses and mining fleets.",
        description=(
            "Built for commercial stations, transport yards and mines where large tanks need filling fast. A "
            "YB vane pump and 2-inch LC flow meter deliver up to 200 L/min while holding accuracy to ±0.3%.\n\n"
            "The aluminium cabinet is robust and corrosion-resistant, and the unit runs on a 380 V, 5.5 kW supply."
        ),
        features="Up to 200 L/min flow rate\nYB vane pump with 2-inch LC meter\nAccuracy ±0.3%\n380 V, 5.5 kW\nAluminium cabinet\n2-year warranty",
        source="https://www.alibaba.com/product-detail/High-Flow-Rate-Heavy-Duty-Fuel_1601959175219.html",
        images=["H622f194008354f1c837bd9e77ebcf400C.jpg", "H27594f2a3ce24a719af0e26fea467de0Q.jpg", "H5db351d483ad46c09c8850ecf1e37f9fe.jpg", "Hcd8b92030e0b401a8ef408b60a4be4c1X.jpg", "H583f447239854e6fac81a2939677770aL.jpg", "H4540cf79670d4bc8a2ea153f5e0b3661c.jpg"],
    ),
    dict(
        match="lpg-dispenser", slug="lpg-dispenser",
        category="fuel-dispensers", name="LPG dispenser with Coriolis mass flow meter",
        summary="ATEX-certified autogas dispenser with mass flow metering for LPG stations.",
        description=(
            "A dedicated LPG (autogas) dispenser for stations adding gas to their offer. A Coriolis mass flow "
            "meter measures accurately regardless of temperature, and the unit is rated to 2 MPa working "
            "pressure.\n\n"
            "It delivers up to 45 L/min, operates from -40 °C to +55 °C and draws under 100 W."
        ),
        features="Coriolis mass flow meter\nUp to 45 L/min\nRated working pressure 2 MPa\nOperating range -40 °C to +55 °C\nATEX certified\nLow power, under 100 W",
        source="https://www.alibaba.com/product-detail/Ecotec-LPG-Dispenser-with-Atex-Certificate_1600498890645.html",
        images=["H595470008337410688dcdc37bfc6cca8W.jpg", "H5658632ad4794b22a24056579d688c8eB.jpg", "H5d33552e50494ad189863bcb829ad972D.jpg", "H03793c8722ef4e4e8303ba0e8f6cc245w.jpg", "H3d20b78118a146af92c8de60e340e7a3H.jpg", "H56a31437d0714c4fb92968d55dcf84715.jpg"],
    ),
    dict(
        match="adblue-dispenser", slug="adblue-dispenser",
        category="fuel-dispensers", name="AdBlue (urea) dispenser, stainless steel",
        summary="Stainless-steel DEF dispenser for stations serving modern diesel trucks and buses.",
        description=(
            "A stainless-steel dispenser for diesel exhaust fluid (AdBlue / urea), which modern Euro 5 and "
            "Euro 6 trucks need. Stainless construction resists the corrosive fluid and keeps it uncontaminated.\n\n"
            "It delivers 50 L/min with ±0.3% accuracy from a compact 64 x 48 x 148 cm cabinet."
        ),
        features="Stainless-steel construction\n50 L/min flow rate\nAccuracy ±0.3%\n220 V, 0.75 kW\nCompact 64 x 48 x 148 cm cabinet\n2-year warranty",
        source="https://www.alibaba.com/product-detail/ECOTEC-Stainless-Steel-Dispenser-with-Urea_1601209076768.html",
        images=["Hee2fc66264aa4e4ebeefd68072e0163cy.jpg", "H4c2d0221e5fe4deeba9cf2383af14883B.jpg", "H89506a34e3744f7c8d9d6b2ffb2396a7M.jpg", "H7c00de89477f495391e4e293bc5371abZ.jpg", "H8165cdccf1c443aaa47b836e5f2fa252p.jpg", "Hef91c860ba2d49f7aeaba18ee32f414ek.jpg"],
    ),
    dict(
        match="container-station-40ft", slug="container-station-40ft",
        category="storage-tanks", name="40 ft container fuel station (68,000 L)",
        summary="A complete fuel station inside a 40 ft container: double-wall tank and dispenser.",
        description=(
            "A full-scale fuel station built into a 40 ft container, with a double-walled 6 mm carbon-steel tank "
            "and integrated dispensing. It can be delivered, placed and commissioned far faster than a "
            "conventional forecourt build.\n\n"
            "Ideal for remote sites, mining camps, construction projects and new markets where speed matters."
        ),
        features="68,000 L capacity\nDouble-wall carbon steel, 6 mm\nIntegrated fuel dispenser\nShips as a standard 40 ft container\nRapid deployment for remote sites",
        source="https://www.alibaba.com/product-detail/40FT-Mobile-Container-Station-with-Capacity_62311030261.html",
        images=["H611f6ef6191a40c5a1d33431f86afa89l.jpg", "Hafa0aecff9284cbd9e0561291138e79eZ.jpg"],
    ),
    dict(
        match="portable-diesel-tank", slug="portable-diesel-tank",
        category="storage-tanks", name="Portable diesel dispensing tank (400 L)",
        summary="HDPE tank with 12 V pump, 4 m hose and automatic nozzle for workshops and farms.",
        description=(
            "A self-contained 400-litre HDPE tank with built-in 12 V pump, 4-metre delivery hose and automatic "
            "nozzle. It brings diesel to generators, machinery and vehicles on farms, workshops and building "
            "sites.\n\n"
            "The safe fill level is 380 L, and the tough HDPE body will not rust."
        ),
        features="400 L HDPE tank (380 L safe fill)\n12 V electric pump\n4 m hose with automatic nozzle\nRust-free, lightweight construction\nFor farms, workshops and sites",
        source="https://www.alibaba.com/product-detail/Ecotec-Petrol-Station-Equipment-Portable-Diesel_1601370205241.html",
        images=["H0d7b9c7bf3de43fa92f27986ca3b0d291.png", "H22e76d5c269b4f47831876dfd635fef37.png", "Hecf9b3f8b58741f3afd8af2320893e9c3.png", "Haf0579db2dc74068ab9e9398a7e95357Y.png", "H7f295b54726e4c0c92be8add59e34b82a.png", "H207259e325194697883741ba1b18bcd1l.png"],
    ),
    dict(
        match="atg-tank-probe-system", slug="atg-tank-probe-system",
        category="tank-automation", name="ATG tank probe system (wired)",
        summary="Stainless-steel magnetostrictive probes and console for continuous tank monitoring.",
        description=(
            "A wired automatic tank gauging system with stainless-steel magnetostrictive probes and a console. "
            "It continuously reports fuel level, water at the tank bottom and temperature for each tank.\n\n"
            "A dependable choice for new builds where cabling can be laid during construction, and for sites "
            "replacing manual dipping."
        ),
        features="Stainless-steel magnetostrictive probes\nFuel level, water and temperature\nConsole with alarms and reports\nReplaces manual dipping\nISO 9001 certified manufacturer",
        source="https://www.alibaba.com/product-detail/Ecotec-Automatic-Tank-Gauging-System-Tank_62306311640.html",
        images=["H20a7698d782a4a579167932fc7e62bc6g.jpg", "H577c4c4d72a54b47a462c4504af637180.jpg", "H2284d7486f7344d18f4e20663793da7fv.jpg", "Hcdbf1056a4bd492e90fd86f1f91f7aadd.jpg", "H874f5bcb3bee4a58ad7794a9467f0f75d.jpg", "Hcf55d22f489a4cf492a7ded0b9ca1e14A.png"],
    ),
    dict(
        match="mc-flow-meter", slug="mc-flow-meter",
        category="terminal-equipment", name="2-inch MC flow meter with IC card preset",
        summary="Positive-displacement meter, 55 to 250 L/min, accurate to ±0.2%, with card control.",
        description=(
            "A 2-inch positive-displacement flow meter for bulk delivery, tanker loading and fleet fuelling "
            "points. An IC card function lets authorised users preset and record each fill.\n\n"
            "It measures 55 to 250 L/min with ±0.2% accuracy and repeatability of 0.07% or better, and reads in "
            "litres or gallons."
        ),
        features="2-inch connections\nFlow range 55 to 250 L/min\nAccuracy ±0.2%, repeatability 0.07% or better\nIC card preset and authorisation\nLitres, US or imperial gallons\nMax pressure 10 bar",
        source="https://www.alibaba.com/product-detail/Ecotec-MC-Flow-Meter-IC-Card_1602003362009.html",
        images=["H79e6ab2d8ccd4690b581c0a83a89b55a4.png", "Hdae17d359abe4ee9a155effab2c00db4r.jpg", "Hfd8491a743aa4b50940dae328ad0d749F.jpg", "Hc93b7af8abec49c5a73da49ac07e4a23j.jpg", "H35a1e2c0ab7e435ab664d08ca03d77beu.jpg", "H7ee62d2b83044c47a232c6111fa01118w.jpg"],
    ),
    dict(
        match="mini-transfer-pump", slug="mini-transfer-pump",
        category="pumps-valves", name="Mini diesel transfer pump (12 / 24 V)",
        summary="Compact gear pump moving 20 to 40 L/min from drums, tanks and bowsers.",
        description=(
            "A compact gear pump set for transferring diesel and kerosene from drums, skid tanks and bowsers. "
            "12 V and 24 V versions run straight from a vehicle battery, with mains versions also available.\n\n"
            "It moves 20 to 40 L/min at up to 3 bar."
        ),
        features="12 V / 24 V DC or mains versions\nFlow 20 to 40 L/min\nMax operating pressure 3 bar\nFor diesel and kerosene\n12-month warranty",
        source="https://www.alibaba.com/product-detail/Ecotec-Mini-Transfer-Pump-220V-24V_62255476836.html",
        images=["H04a8b39cbd014be582a6c3da2a8d077fA.jpg", "H2c3933ebd3a740cc9560126d25a23752r.jpg", "H03e6904d92724a47bc6bd1e5a476219fB.jpg", "H341788e99a114a5796b4b1c68bd4ea8cq.jpg", "H74106c249cf64226b74af165f4a0b218t.jpg", "H0f0c7ae64bce4b90962ac9f1bb49306fC.jpg"],
    ),
    dict(
        match="dispenser-fuel-filter", slug="dispenser-fuel-filter",
        category="accessories-safety", name="Dispenser fuel filter (30 micron)",
        summary="Particulate filter that protects meters and customers' engines from dirt and debris.",
        description=(
            "A replacement 30-micron particulate filter for fuel dispensers. It traps dirt and debris before "
            "they reach the meter or the customer's tank, protecting accuracy and engines alike.\n\n"
            "Rated at 25 GPM with a 1-inch 12 UNF thread, and interchangeable with common 300-10 and 70010 "
            "filter models."
        ),
        features="30-micron particulate filtration\n1 in. - 12 UNF thread\nFlow rating 25 GPM\nCellulose element\nInterchangeable with 300-10 and 70010 types",
        source="https://www.alibaba.com/product-detail/ECOTEC-Fuel-Dispenser-Spare-Parts-BF414_1601659518255.html",
        images=["H25f47cb4af9643c7a8837aca598733421.jpg", "H1cb82645ede941fe8db7f709832976bfq.jpg", "H07e48661c54248679368ee00e34140722.jpg", "Hfdf0a3be5a774a54ad680e35efc517dai.jpg", "H60b04ea4e9dd4e459ad2da380abbfb97g.jpg", "H049a653397c344cf8a49325d34413cc4F.jpg"],
    ),
]


class Command(BaseCommand):
    help = "Load Ecotec products and photos from their Alibaba listings."

    def add_arguments(self, parser):
        parser.add_argument("--no-download", action="store_true", help="Update text only; keep current photos.")

    def fetch(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MasterOctagonCatalogue)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        im = Image.open(io.BytesIO(data))
        im.verify()  # raises if not a valid image
        return data, (im.format or "JPEG").lower()

    def handle(self, *args, **opts):
        gallery_dir = Path(settings.MEDIA_ROOT) / "products" / "gallery"
        gallery_dir.mkdir(parents=True, exist_ok=True)

        for order, item in enumerate(CATALOGUE):
            cat = ProductCategory.objects.get(slug=item["category"])
            product = (Product.objects.filter(slug=item["match"]).first()
                       or Product.objects.filter(slug=item["slug"]).first()
                       or Product(slug=item["slug"]))
            product.slug = item["slug"]
            product.category = cat
            product.name = item["name"]
            product.brand = "Ecotec"
            product.summary = item["summary"]
            product.description = item["description"]
            product.features = item["features"]
            product.is_featured = item.get("featured", False)
            product.is_active = True
            product.order = order
            if item.get("clear_main_image"):
                product.image = ""
            product.save()

            if item["images"] and not opts["no_download"]:
                saved = []
                for n, name in enumerate(item["images"], 1):
                    try:
                        data, fmt = self.fetch(CDN + name)
                    except Exception as e:  # skip a bad photo, keep going
                        self.stderr.write(f"  ! {product.slug} photo {n}: {e}")
                        continue
                    ext = {"jpeg": "jpg", "mpo": "jpg"}.get(fmt, fmt)
                    rel = f"products/gallery/{product.slug}-{n}.{ext}"
                    (Path(settings.MEDIA_ROOT) / rel).write_bytes(data)
                    saved.append(rel)
                if saved:
                    product.gallery.all().delete()
                    for n, rel in enumerate(saved, 1):
                        ProductImage.objects.create(product=product, image=rel, caption=f"{product.name}, photo {n}", order=n)
            self.stdout.write(f"{product.category.code or product.category.name:>4}  {product.name}  ({product.gallery.count()} photos)")

        # Hide any old placeholder products that are not part of the catalogue
        keep = {i["slug"] for i in CATALOGUE}
        hidden = Product.objects.exclude(slug__in=keep).filter(is_active=True).update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"Catalogue loaded: {len(CATALOGUE)} Ecotec products. Hidden {hidden} old placeholder product(s). Supplier: {SUPPLIER}"))
