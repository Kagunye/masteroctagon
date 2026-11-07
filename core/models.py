from django.db import models
from django.urls import reverse

from . import images


class Ordered(models.Model):
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first.")
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class ProductCategory(Ordered):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    code = models.CharField(max_length=6, blank=True, help_text="Short label shown beside the name, e.g. DSP.")
    icon = models.CharField(max_length=40, default="pump", help_text="Icon key, e.g. pump, tank, gauge, valve, hose, shield.")
    summary = models.TextField()
    image = models.ImageField(upload_to="categories/", blank=True)

    class Meta(Ordered.Meta):
        verbose_name_plural = "product categories"

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        # Use the first active product's photo (uploaded image or gallery) before falling back to stock.
        for p in self.products.filter(is_active=True).order_by("order", "id"):
            if p.image:
                return p.image.url
            first = p.gallery.first()
            if first:
                return first.image.url
        return images.photo(images.CATEGORY.get(self.slug, ""))

    @property
    def has_product_photo(self):
        return not self.image and not self.image_url.startswith("http")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product_category", args=[self.slug])


class Product(Ordered):
    category = models.ForeignKey(ProductCategory, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    brand = models.CharField(max_length=80, blank=True)
    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text="One feature per line.")
    image = models.ImageField(upload_to="products/", blank=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product_detail", args=[self.slug])

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        first = self.gallery.first()
        return first.image.url if first else self.category.image_url

    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"{self.product} image {self.pk}"


class Service(Ordered):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=40, default="wrench")
    summary = models.CharField(max_length=255)
    description = models.TextField()
    deliverables = models.TextField(blank=True, help_text="One item per line.")
    image = models.ImageField(upload_to="services/", blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:service_detail", args=[self.slug])

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        first = self.gallery.first()
        return first.image.url if first else images.photo(images.SERVICE.get(self.slug, ""))

    def deliverable_list(self):
        return [d.strip() for d in self.deliverables.splitlines() if d.strip()]


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="services/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"{self.service} image {self.pk}"


class Sector(Ordered):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=40, default="station")
    summary = models.TextField()
    capabilities = models.TextField(blank=True, help_text="One item per line.")
    image = models.ImageField(upload_to="sectors/", blank=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        first = self.gallery.first()
        return first.image.url if first else images.photo(images.SECTOR.get(self.slug, ""))

    def slides(self):
        """Main image (if any) followed by gallery images, for the sliding card."""
        out = [(self.image.url, self.name)] if self.image else []
        out += [(g.image.url, g.caption or self.name) for g in self.gallery.all()]
        return out

    def capability_list(self):
        return [c.strip() for c in self.capabilities.splitlines() if c.strip()]


class SectorImage(models.Model):
    sector = models.ForeignKey(Sector, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="sectors/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"{self.sector} image {self.pk}"


class Project(Ordered):
    title = models.CharField(max_length=160)
    client = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120)
    country = models.CharField(max_length=60, default="Kenya")
    sector = models.ForeignKey(Sector, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects")
    year = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField()
    image = models.ImageField(upload_to="projects/", blank=True)

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return self.sector.image_url if self.sector else images.photo("refinery_dusk")


class Enquiry(models.Model):
    TYPE_CONTACT = "contact"
    TYPE_QUOTE = "quote"
    TYPES = [(TYPE_CONTACT, "General enquiry"), (TYPE_QUOTE, "Quote request")]
    STATUS = [("new", "New"), ("in_progress", "In progress"), ("closed", "Closed")]

    kind = models.CharField(max_length=10, choices=TYPES, default=TYPE_CONTACT)
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=160, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=60, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    interest = models.CharField(max_length=160, blank=True, help_text="Product or service of interest.")
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.get_kind_display()} from {self.name}"
