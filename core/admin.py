from django.contrib import admin

from .models import Enquiry, Product, ProductCategory, ProductImage, Project, Sector, SectorImage, Service, ServiceImage

admin.site.site_header = "Master Octagon Admin"
admin.site.site_title = "Master Octagon"
admin.site.index_title = "Website content"


class ProductInline(admin.TabularInline):
    model = Product
    fields = ("name", "brand", "order", "is_active", "is_featured")
    extra = 0
    show_change_link = True


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductInline]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ("image", "caption", "order")
    extra = 1
    verbose_name = "gallery image"
    verbose_name_plural = "Gallery images (shown as a slideshow on the product page)"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ("name", "category", "brand", "is_featured", "is_active", "order")
    list_filter = ("category", "is_featured", "is_active")
    list_editable = ("is_featured", "is_active", "order")
    search_fields = ("name", "brand", "summary")
    prepopulated_fields = {"slug": ("name",)}


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    fields = ("image", "caption", "order")
    extra = 1
    verbose_name = "slideshow image"
    verbose_name_plural = "Slideshow images (shown as a slider on the service card and page)"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "slides", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceImageInline]

    @admin.display(description="Slideshow images")
    def slides(self, obj):
        return obj.gallery.count()


class SectorImageInline(admin.TabularInline):
    model = SectorImage
    fields = ("image", "caption", "order")
    extra = 1
    verbose_name = "slideshow image"
    verbose_name_plural = "Slideshow images (slide right to left on the sector card)"


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    inlines = [SectorImageInline]
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "country", "sector", "year", "is_active")
    list_filter = ("country", "sector", "is_active")
    search_fields = ("title", "client", "location")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "company", "email", "phone", "interest", "status", "created_at")
    list_filter = ("kind", "status", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "company", "email", "message")
    readonly_fields = ("kind", "name", "company", "email", "phone", "country", "subject", "interest", "message", "created_at")
