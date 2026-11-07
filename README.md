# Master Octagon — company website

Django site for Master Octagon: petroleum equipment and engineering services for retail fuel stations, terminals and industrial fuel operations across East Africa.

## Pages
Home · About · Products (by category, with detail pages) · Services · Industries · Projects (filter by industry) · Contact · Request a Quote

Contact and quote submissions are saved as **Enquiries** in the admin and an email notification is sent to `ENQUIRY_NOTIFY_EMAIL` (printed to the console in development).

## Run locally
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata site_content   # all products, services, industries, galleries (photos are in media/)
python manage.py createsuperuser   # for /admin/
python manage.py runserver
```
Open http://127.0.0.1:8000 and http://127.0.0.1:8000/admin/.

## Product catalogue (Ecotec)
Products come from our supplier Wenzhou Ecotec Energy Equipment Co. (https://ecotecenergy.en.alibaba.com/).
Load or refresh them, including photos downloaded from their Alibaba listings, with:
```bash
python manage.py load_ecotec_catalogue
```
A fresh clone does not need it: `loaddata site_content` restores everything, using the photos
committed in `media/`. After editing content in the admin, refresh the export with
`PYTHONUTF8=1 python manage.py dumpdata core --exclude core.Enquiry --indent 1 -o core/fixtures/site_content.json`. Product text and listing photo IDs live in
`core/management/commands/load_ecotec_catalogue.py`; edit there or in the admin. Products have a
"Gallery images" section in the admin that drives the product-page slideshow.

## Images
Stock photos (originally from Unsplash) are saved in `static/img/stock/`; your own images replace them.
- **Products, categories, services, sectors, projects:** upload an image on the record in the admin.
- **Page banners:** drop files into `static/img/pages/` named `hero`, `intro`, `why`, `about`, `products`, `services`, `sectors`, `projects`, `contact`, `quote` (`.jpg`, `.png` or `.webp`). See the README in that folder.
- After adding photos, run `python manage.py optimize_images` to resize them (max 1600 px) and create the
  800 px `@md` copies used by cards, thumbnails and menus.
- After changing CSS/JS, bump `ASSET_VERSION` in `core/context_processors.py` so browsers reload them.

## Editing content
- Products, categories, services, sectors and projects: Django admin.
- Company phone, email, address, hours and countries: `core/context_processors.py` (`COMPANY`).
- Homepage stats: `STATS` in `core/views.py`.
- Icons: keys in `core/templatetags/octagon.py` (pump, tank, gauge, valve, shield, wrench, build, clipboard, calibrate, station, terminal, factory …).

## Deploying on Vercel
The repo is ready for Vercel (`vercel.json`, `config/wsgi.py` exposes `app`). Import the GitHub repo in
Vercel, then set these environment variables in the project settings:

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | a long random string (**required**; the site will not start without it) |
| `DATABASE_URL` | optional: a Postgres URL (e.g. Vercel Postgres / Neon) so enquiries and admin edits are kept |

Without `DATABASE_URL`, each cold start builds a temporary database from `core/fixtures/site_content.json`:
all pages work, but contact/quote submissions and admin changes are lost when the instance restarts.
With Postgres, run once from your machine: `DATABASE_URL=... python manage.py migrate && python manage.py loaddata site_content && python manage.py createsuperuser`.
Static files are served by WhiteNoise and photos from `media/`, so no extra storage is needed.
The live host `masteroctagon-grwj.vercel.app` is already in `ALLOWED_HOSTS`.

## Production settings (environment variables)
| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Secret key (required in production) |
| `DJANGO_DEBUG` | `0` to disable debug |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames |
| `ENQUIRY_NOTIFY_EMAIL` | Where enquiry notifications go |

Also configure a real `EMAIL_BACKEND` / SMTP settings and run `python manage.py collectstatic`.

## Tests
```bash
python manage.py test core
```
