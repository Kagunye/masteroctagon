import io
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Enquiry, Product, Service


class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", stdout=io.StringIO())

    def test_pages_render(self):
        names = ["home", "about", "products", "services", "sectors", "projects", "contact", "quote"]
        for n in names:
            with self.subTest(page=n):
                self.assertEqual(self.client.get(reverse(f"core:{n}")).status_code, 200)

    def test_detail_pages(self):
        p = Product.objects.first()
        s = Service.objects.first()
        for url in [p.get_absolute_url(), p.category.get_absolute_url(), s.get_absolute_url()]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get("/products/nope/").status_code, 404)

    def test_project_filter(self):
        r = self.client.get(reverse("core:projects"), {"sector": "industrial-fuel"})
        self.assertTrue(all(p.sector.slug == "industrial-fuel" for p in r.context["projects"]))

    def test_quote_submission(self):
        r = self.client.post(reverse("core:quote"), {
            "name": "Jane", "email": "jane@example.com", "interest": "Dispensers", "message": "Need 4 units",
        }, follow=True)
        self.assertContains(r, "quote request has been received")
        self.assertEqual(Enquiry.objects.get().kind, Enquiry.TYPE_QUOTE)

    def test_honeypot_blocks_spam(self):
        self.client.post(reverse("core:contact"), {
            "name": "Bot", "email": "b@example.com", "message": "spam", "website": "http://x",
        })
        self.assertEqual(Enquiry.objects.count(), 0)


class FixtureTests(TestCase):
    def test_site_content_fixture_loads(self):
        call_command("loaddata", "site_content", verbosity=0)
        self.assertEqual(Product.objects.filter(is_active=True).count(), 25)
        self.assertEqual(self.client.get(reverse("core:sectors")).status_code, 200)
