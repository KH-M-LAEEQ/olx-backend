import json
import os
import urllib.error
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from ads.models import Ad, AdImage, Category

User = get_user_model()

PEXELS_URL = 'https://api.pexels.com/v1/search'

CATEGORIES = [
    {'name': 'Mobiles',     'slug': 'mobiles',     'icon': '📱'},
    {'name': 'Cars',        'slug': 'cars',        'icon': '🚗'},
    {'name': 'Property',    'slug': 'property',    'icon': '🏠'},
    {'name': 'Electronics', 'slug': 'electronics', 'icon': '💻'},
    {'name': 'Jobs',        'slug': 'jobs',        'icon': '💼'},
    {'name': 'Furniture',   'slug': 'furniture',   'icon': '🛋️'},
    {'name': 'Fashion',     'slug': 'fashion',     'icon': '👗'},
    {'name': 'Books',       'slug': 'books',       'icon': '📚'},
    {'name': 'Sports',      'slug': 'sports',      'icon': '⚽'},
    {'name': 'Animals',     'slug': 'animals',     'icon': '🐾'},
]

# 'query' is the Pexels search term. 'pick' chooses which result to use
# (0-based) so two ads sharing a query don't end up with the same photo.
ADS = [
    # Mobiles
    {'title': 'Samsung Galaxy S24 Ultra – 256GB, Phantom Black', 'price': 295000, 'location': 'Karachi', 'condition': 'new', 'category': 'mobiles', 'desc': 'Brand new sealed box. 200MP camera, S Pen included. Genuine Samsung warranty 1 year.', 'img_seed': 'phone1', 'query': 'smartphone', 'pick': 0},
    {'title': 'iPhone 15 Pro Max – 512GB, Natural Titanium', 'price': 420000, 'location': 'Lahore', 'condition': 'new', 'category': 'mobiles', 'desc': 'PTA approved. Box packed. Apple Store receipt available. No scratches, immaculate condition.', 'img_seed': 'phone2', 'query': 'iphone', 'pick': 0},
    {'title': 'Oppo Reno 11 Pro – 12GB RAM, 256GB', 'price': 85000, 'location': 'Islamabad', 'condition': 'used', 'category': 'mobiles', 'desc': 'Only 3 months used, comes with original charger and box. Minor wear on back glass.', 'img_seed': 'phone3', 'query': 'smartphone', 'pick': 1},
    {'title': 'Xiaomi 14 – Leica Camera, 8GB/256GB', 'price': 115000, 'location': 'Rawalpindi', 'condition': 'new', 'category': 'mobiles', 'desc': 'Global version, dual SIM, 90W fast charging. Still sealed.', 'img_seed': 'phone4', 'query': 'smartphone', 'pick': 2},

    # Cars
    {'title': 'Toyota Corolla Altis 1.8 2022 – Pearl White', 'price': 6800000, 'location': 'Karachi', 'condition': 'used', 'category': 'cars', 'desc': '42,000 km only. Original paint. All docs clear. Recently serviced at Toyota dealership.', 'img_seed': 'car1', 'query': 'car', 'pick': 0},
    {'title': 'Honda Civic RS Turbo 2023 – Lunar Silver', 'price': 8200000, 'location': 'Lahore', 'condition': 'used', 'category': 'cars', 'desc': '12,000 km driven. Sunroof, leather seats, all power accessories. Single owner.', 'img_seed': 'car2', 'query': 'car', 'pick': 1},
    {'title': 'Suzuki Alto VXR 2021 – Solid White', 'price': 2750000, 'location': 'Multan', 'condition': 'used', 'category': 'cars', 'desc': 'Family-used, no accident, all original. 55,000 km. Registration Multan. Serious buyers only.', 'img_seed': 'car3', 'query': 'car', 'pick': 2},
    {'title': 'Toyota Hilux Revo 2022 – Diesel Double Cab', 'price': 12500000, 'location': 'Peshawar', 'condition': 'used', 'category': 'cars', 'desc': 'Excellent condition, full option, genuine 4x4. 80,000 km. Price negotiable.', 'img_seed': 'car4', 'query': 'pickup truck', 'pick': 0},

    # Property
    {'title': '5 Marla House for Sale – DHA Phase 6, Lahore', 'price': 28500000, 'location': 'Lahore', 'condition': 'used', 'category': 'property', 'desc': '3 bed, 2 bath, lounge, TV lounge, servant quarter. Gas + electricity. Near park.', 'img_seed': 'house1', 'query': 'house', 'pick': 0},
    {'title': '2 Bed Flat for Rent – Gulshan-e-Iqbal, Karachi', 'price': 65000, 'location': 'Karachi', 'condition': 'used', 'category': 'property', 'desc': 'Ground floor, independent entrance, 24hr security. All utilities available. Ready to move.', 'img_seed': 'house2', 'query': 'living room', 'pick': 0},
    {'title': '10 Marla Plot – Bahria Town Phase 8, Rawalpindi', 'price': 18000000, 'location': 'Rawalpindi', 'condition': 'new', 'category': 'property', 'desc': 'Corner plot, facing park. All dues clear. Ideal for construction. Transfer ready.', 'img_seed': 'house3', 'query': 'land field', 'pick': 0},

    # Electronics
    {'title': 'Dell XPS 15 Laptop – Core i9, RTX 4060, 32GB', 'price': 380000, 'location': 'Islamabad', 'condition': 'used', 'category': 'electronics', 'desc': '6 months old, perfect for video editing / gaming. Comes with original bag and charger.', 'img_seed': 'laptop1', 'query': 'laptop', 'pick': 0},
    {'title': 'Samsung 55" QLED 4K Smart TV – QN55Q80C', 'price': 185000, 'location': 'Lahore', 'condition': 'new', 'category': 'electronics', 'desc': 'Box packed, purchased 2 weeks ago. Dolby Atmos, HDMI 2.1. Moving abroad, must sell.', 'img_seed': 'tv1', 'query': 'television', 'pick': 0},
    {'title': 'Sony PlayStation 5 – Disc Edition + 2 Controllers', 'price': 145000, 'location': 'Karachi', 'condition': 'used', 'category': 'electronics', 'desc': 'Excellent condition, used lightly. Includes 4 games. Original box available.', 'img_seed': 'console1', 'query': 'video game controller', 'pick': 0},

    # Jobs
    {'title': 'Female Receptionist Needed – IT Company Karachi', 'price': 55000, 'location': 'Karachi', 'condition': 'new', 'category': 'jobs', 'desc': 'Min 2 years experience, good communication. Mon–Fri 9–6. Salary 45k–55k depending on experience.', 'img_seed': 'office1', 'query': 'office', 'pick': 0},
    {'title': 'Experienced Cook Required – DHA Lahore Household', 'price': 35000, 'location': 'Lahore', 'condition': 'new', 'category': 'jobs', 'desc': 'Must know Pakistani, Chinese and continental cuisine. Live-in or live-out. References required.', 'img_seed': 'office2', 'query': 'chef kitchen', 'pick': 0},

    # Furniture
    {'title': 'L-Shape Sofa Set – 7 Seater, Dark Grey Velvet', 'price': 85000, 'location': 'Karachi', 'condition': 'used', 'category': 'furniture', 'desc': 'Bought 1 year ago, very lightly used. No stains, original cushions. Self-transport required.', 'img_seed': 'sofa1', 'query': 'sofa', 'pick': 0},
    {'title': 'King Size Wooden Bed + Mattress + Side Tables', 'price': 55000, 'location': 'Lahore', 'condition': 'used', 'category': 'furniture', 'desc': 'Solid sheesham wood, excellent condition. Mattress orthopedic. Relocating, sell ASAP.', 'img_seed': 'bed1', 'query': 'bedroom bed', 'pick': 0},

    # Fashion
    {'title': "Men's Leather Jacket – XL, Genuine Cowhide", 'price': 18000, 'location': 'Karachi', 'condition': 'new', 'category': 'fashion', 'desc': 'Brand new, never worn. Premium quality, zip pockets. Size XL (fits 40-42 chest).', 'img_seed': 'jacket1', 'query': 'leather jacket', 'pick': 0},
    {'title': 'Nike Air Jordan 1 Retro High – US9, Chicago', 'price': 35000, 'location': 'Lahore', 'condition': 'new', 'category': 'fashion', 'desc': 'Authentic pair, bought from US. DS (deadstock) condition. Box included.', 'img_seed': 'shoes1', 'query': 'sneakers', 'pick': 0},
]


class Command(BaseCommand):
    help = 'Seed the database with demo ads and matching Pexels photos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Delete existing demo ads and re-create them with fresh images.',
        )

    def handle(self, *args, **options):
        api_key = os.environ.get('PEXELS_API_KEY', '')

        # Diagnostics: everything goes to stdout so it shows in Render's log.
        self.stdout.write(f'PEXELS key present: {bool(api_key)}')
        if api_key:
            self.stdout.write(
                f'PEXELS key length: {len(api_key)} '
                f'(starts "{api_key[:4]}", ends "{api_key[-4:]}")'
            )
        else:
            self.stdout.write(
                'PEXELS_API_KEY is not set — add it in Render > Environment.'
            )
            return

        self.api_key = api_key.strip()
        self._photo_cache = {}

        self.stdout.write('Creating categories...')
        cat_map = {}
        for c in CATEGORIES:
            obj, _ = Category.objects.get_or_create(
                slug=c['slug'],
                defaults={'name': c['name'], 'icon': c['icon']},
            )
            cat_map[c['slug']] = obj

        self.stdout.write('Creating demo seller...')
        seller, created = User.objects.get_or_create(
            username='demo_seller',
            defaults={'email': 'demo@bazaario.app', 'phone': '03001234567', 'city': 'Karachi'},
        )
        if created:
            seller.set_password('demo1234')
            seller.save()

        if options['force']:
            deleted, _ = Ad.objects.filter(seller=seller).delete()
            self.stdout.write(f'Deleted {deleted} existing demo objects.')

        self.stdout.write(f'Seeding {len(ADS)} ads with Pexels images...')
        created_count = 0

        for ad_data in ADS:
            if Ad.objects.filter(title=ad_data['title']).exists():
                self.stdout.write(f'  skip (exists): {ad_data["title"][:50]}')
                continue

            ad = Ad.objects.create(
                title=ad_data['title'],
                description=ad_data['desc'],
                price=ad_data['price'],
                category=cat_map.get(ad_data['category']),
                seller=seller,
                location=ad_data['location'],
                condition=ad_data['condition'],
            )

            photo_url = self._photo_for(ad_data['query'], ad_data.get('pick', 0))
            if photo_url:
                try:
                    img_data = self._download(photo_url)
                    ad_image = AdImage(ad=ad, is_cover=True)
                    ad_image.image.save(
                        f"{ad_data['img_seed']}.jpg",
                        ContentFile(img_data),
                        save=True,
                    )
                    self.stdout.write(
                        f'  OK ({len(img_data) // 1024} kB): {ad_data["title"][:45]}'
                    )
                except Exception as e:
                    self.stdout.write(
                        f'  DOWNLOAD FAILED {type(e).__name__}: {e} '
                        f'— {ad_data["title"][:35]}'
                    )
            else:
                self.stdout.write(
                    f'  NO PHOTO for "{ad_data["query"]}" — {ad_data["title"][:35]}'
                )

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'\nDone! Created {created_count} ads.'))

    # ── helpers ─────────────────────────────────────────────────────────────

    def _photo_for(self, query, pick):
        """Return one image URL for a search term, caching results per query."""
        if query not in self._photo_cache:
            self._photo_cache[query] = self._search(query)

        urls = self._photo_cache[query]
        if not urls:
            return None
        return urls[pick % len(urls)]

    def _search(self, query):
        params = urllib.parse.urlencode({
            'query': query,
            'per_page': 5,
            'orientation': 'landscape',
        })
        url = f'{PEXELS_URL}?{params}'
        request = urllib.request.Request(
            url,
            headers={
                'Authorization': self.api_key,
                'User-Agent': 'Mozilla/5.0',
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read().decode('utf-8')
                payload = json.loads(raw)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:300]
            self.stdout.write(f'PEXELS HTTP {e.code} for "{query}": {body}')
            return []
        except Exception as e:
            self.stdout.write(f'PEXELS FAILED for "{query}": {type(e).__name__}: {e}')
            return []

        photos = payload.get('photos', [])
        self.stdout.write(f'PEXELS "{query}": {len(photos)} photos returned')

        return [
            p['src']['large']
            for p in photos
            if p.get('src', {}).get('large')
        ]

    def _download(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
