import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm, QuoteForm
from .models import Enquiry, Product, ProductCategory, Project, Sector, Service

log = logging.getLogger(__name__)

STATS = [
    ("500+", "Fuel stations equipped"),
    ("8", "East African countries"),
    ("24/7", "Breakdown support"),
    ("15+", "Years of experience"),
]


def home(request):
    return render(request, "core/home.html", {
        "categories": ProductCategory.objects.filter(is_active=True).prefetch_related("products"),
        "services": Service.objects.filter(is_active=True).prefetch_related("gallery"),
        "sectors": Sector.objects.filter(is_active=True),
        "featured": Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:6],
        "projects": Project.objects.filter(is_active=True).select_related("sector")[:3],
        "stats": STATS,
    })


def about(request):
    return render(request, "core/about.html", {"stats": STATS, "sectors": Sector.objects.filter(is_active=True)})


def products(request):
    categories = ProductCategory.objects.filter(is_active=True).prefetch_related("products")
    return render(request, "core/products.html", {"categories": categories})


def product_category(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug, is_active=True)
    return render(request, "core/product_category.html", {
        "category": category,
        "products": category.products.filter(is_active=True),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    related = product.category.products.filter(is_active=True).exclude(pk=product.pk)[:3]
    return render(request, "core/product_detail.html", {"product": product, "related": related})


def services(request):
    return render(request, "core/services.html", {"services": Service.objects.filter(is_active=True).prefetch_related("gallery")})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    others = Service.objects.filter(is_active=True).exclude(pk=service.pk)
    return render(request, "core/service_detail.html", {"service": service, "others": others})


def sectors(request):
    return render(request, "core/sectors.html", {"sectors": Sector.objects.filter(is_active=True).prefetch_related("projects")})


def projects(request):
    qs = Project.objects.filter(is_active=True).select_related("sector")
    sector = request.GET.get("sector")
    if sector:
        qs = qs.filter(sector__slug=sector)
    return render(request, "core/projects.html", {
        "projects": qs,
        "sectors": Sector.objects.filter(is_active=True),
        "active_sector": sector,
    })


def _notify(enquiry):
    try:
        send_mail(
            subject=f"[Website] {enquiry}",
            message=(f"Name: {enquiry.name}\nCompany: {enquiry.company}\nEmail: {enquiry.email}\n"
                     f"Phone: {enquiry.phone}\nCountry: {enquiry.country}\nInterest: {enquiry.interest}\n"
                     f"Subject: {enquiry.subject}\n\n{enquiry.message}"),
            from_email=None,
            recipient_list=[settings.ENQUIRY_NOTIFY_EMAIL],
        )
    except Exception:  # never lose an enquiry because mail failed
        log.exception("Failed to send enquiry notification")


def _handle_form(request, form_class, kind, template, success_msg, initial=None):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.kind = kind
            enquiry.save()
            _notify(enquiry)
            messages.success(request, success_msg)
            return redirect(request.path)
    else:
        form = form_class(initial=initial)
    return render(request, template, {"form": form})


def contact(request):
    return _handle_form(request, ContactForm, Enquiry.TYPE_CONTACT, "core/contact.html",
                        "Thank you — your message has been received. Our team will respond within one business day.")


def quote(request):
    return _handle_form(request, QuoteForm, Enquiry.TYPE_QUOTE, "core/quote.html",
                        "Thank you — your quote request has been received. An engineer will contact you shortly.",
                        initial={"interest": request.GET.get("item", "")})
