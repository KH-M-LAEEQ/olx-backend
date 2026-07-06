import urllib.request
import os
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from ads.models import Ad, AdImage, Category

User = get_user_model()

CATEGORIES = [
    {'name': 'Mobiles',     'slug': 'mobiles',     'icon': '📱'},
    {'name': 'Cars',        'slug': 'cars',         'icon': '🚗'},
    {'name': 'Property',    'slug': 'property',     'icon': '🏠'},
    {'name': 'Electronics', 'slug': 'electronics',  'icon': '💻'},
    {'name': 'Jobs',        'slug': 'jobs',         'icon': '💼'},
    {'name': 'Furniture',   'slug': 'furniture',    'icon': '🛋️'},
    {'name': 'Fashion',     'slug': 'fashion',      'icon': '👗'},
    {'name': 'Books',       'slug': 'books',        'icon': '📚'},
    {'name': 'Sports',      'slug': 'sports',       'icon': '⚽'},
    {'name': 'Animals',     'slug': 'animals',      'icon': '🐾'},
]

ADS = [
    # Mobiles
    {'title': 'Samsung Galaxy S24 Ultra – 256GB, Phantom Black', 'price': 295000, 'location': 'Karachi', 'condition': 'new',  'category': 'mobiles',     'desc': 'Brand new sealed box. 200MP camera, S Pen included. Genuine Samsung warranty 1 year.', 'img_seed': 'phone1'},
    {'title': 'iPhone 15 Pro Max – 512GB, Natural Titanium',     'price': 420000, 'location': 'Lahore',  'condition': 'new',  'category': 'mobiles',     'desc': 'PTA approved. Box packed. Apple Store receipt available. No scratches, immaculate condition.', 'img_seed': 'phone2'},
    {'title': 'Oppo Reno 11 Pro – 12GB RAM, 256GB',              'price': 85000,  'location': 'Islamabad','condition': 'used', 'category': 'mobiles',     'desc': 'Only 3 months used, comes with original charger and box. Minor wear on back glass.', 'img_seed': 'phone3'},
    {'title': 'Xiaomi 14 – Leica Camera, 8GB/256GB',             'price': 115000, 'location': 'Rawalpindi','condition':'new', 'category': 'mobiles',     'desc': 'Global version, dual SIM, 90W fast charging. Still sealed.', 'img_seed': 'phone4'},

    # Cars
    {'title': 'Toyota Corolla Altis 1.8 2022 – Pearl White',     'price': 6800000,'location': 'Karachi', 'condition': 'used', 'category': 'cars',        'desc': '42,000 km only. Original paint. All docs clear. Recently serviced at Toyota dealership.', 'img_seed': 'car1'},
    {'title': 'Honda Civic RS Turbo 2023 – Lunar Silver',        'price': 8200000,'location': 'Lahore',  'condition': 'used', 'category': 'cars',        'desc': '12,000 km driven. Sunroof, leather seats, all power accessories. Single owner.', 'img_seed': 'car2'},
    {'title': 'Suzuki Alto VXR 2021 – Solid White',              'price': 2750000,'location': 'Multan',  'condition': 'used', 'category': 'cars',        'desc': 'Family-used, no accident, all original. 55,000 km. Registration Multan. Serious buyers only.', 'img_seed': 'car3'},
    {'title': 'Toyota Hilux Revo 2022 – Diesel Double Cab',      'price': 12500000,'location':'Peshawar','condition': 'used', 'category': 'cars',        'desc': 'Excellent condition, full option, genuine 4x4. 80,000 km. Price negotiable.', 'img_seed': 'car4'},

    # Property
    {'title': '5 Marla House for Sale – DHA Phase 6, Lahore',    'price': 28500000,'location':'Lahore',  'condition': 'used', 'category': 'property',    'desc': '3 bed, 2 bath, lounge, TV lounge, servant quarter. Gas + electricity. Near park.', 'img_seed': 'house1'},
    {'title': '2 Bed Flat for Rent – Gulshan-e-Iqbal, Karachi',  'price': 65000,  'location': 'Karachi', 'condition': 'used', 'category': 'property',    'desc': 'Ground floor, independent entrance, 24hr security. All utilities available. Ready to move.', 'img_seed': 'house2'},
    {'title': '10 Marla Plot – Bahria Town Phase 8, Rawalpindi', 'price': 18000000,'location':'Rawalpindi','condition':'new', 'category': 'property',    'desc': 'Corner plot, facing park. All dues clear. Ideal for construction. Transfer ready.', 'img_seed': 'house3'},

    # Electronics
    {'title': 'Dell XPS 15 Laptop – Core i9, RTX 4060, 32GB',   'price': 380000, 'location': 'Islamabad','condition':'used', 'category': 'electronics', 'desc': '6 months old, perfect for video editing / gaming. Comes with original bag and charger.', 'img_seed': 'laptop1'},
    {'title': 'Samsung 55" QLED 4K Smart TV – QN55Q80C',        'price': 185000, 'location': 'Lahore',  'condition': 'new',  'category': 'electronics', 'desc': 'Box packed, purchased 2 weeks ago. Dolby Atmos, HDMI 2.1. Moving abroad, must sell.', 'img_seed': 'tv1'},
    {'title': 'Sony PlayStation 5 – Disc Edition + 2 Controllers','price': 145000, 'location': 'Karachi', 'condition': 'used', 'category': 'electronics', 'desc': 'Excellent condition, used lightly. Includes 4 games. Original box available.', 'img_seed': 'console1'},

    # Jobs
    {'title': 'Female Receptionist Needed – IT Company Karachi', 'price': 55000,  'location': 'Karachi', 'condition': 'new',  'category': 'jobs',        'desc': 'Min 2 years experience, good communication. Mon–Fri 9–6. Salary 45k–55k depending on experience.', 'img_seed': 'office1'},
    {'title': 'Experienced Cook Required – DHA Lahore Household','price': 35000,  'location': 'Lahore',  'condition': 'new',  'category': 'jobs',        'desc': 'Must know Pakistani, Chinese and continental cuisine. Live-in or live-out. References required.', 'img_seed': 'office2'},

    # Furniture
    {'title': 'L-Shape Sofa Set – 7 Seater, Dark Grey Velvet',   'price': 85000,  'location': 'Karachi', 'condition': 'used', 'category': 'furniture',   'desc': 'Bought 1 year ago, very lightly used. No stains, original cushions. Self-transport required.', 'img_seed': 'sofa1'},
    {'title': 'King Size Wooden Bed + Mattress + Side Tables',    'price': 55000,  'location': 'Lahore',  'condition': 'used', 'category': 'furniture',   'desc': 'Solid sheesham wood, excellent condition. Mattress orthopedic. Relocating, sell ASAP.', 'img_seed': 'bed1'},

    # Fashion
    {'title': 'Men\'s Leather Jacket – XL, Genuine Cowhide',     'price': 18000,  'location': 'Karachi', 'condition': 'new',  'category': 'fashion',     'desc': 'Brand new, never worn. Premium quality, zip pockets. Size XL (fits 40-42 chest).', 'img_seed': 'jacket1'},
    {'title': 'Nike Air Jordan 1 Retro High – US9, Chicago',     'price': 35000,  'location': 'Lahore',  'condition': 'new',  'category': 'fashion',     'desc': 'Authentic pair, bought from US. DS (deadstock) condition. Box included.', 'img_seed': 'shoes1'},
]

def download_image(seed, width=640, height=480):
    url = f'https://picsum.photos/seed/{seed}/{width}/{height}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


class Command(BaseCommand):
    help = 'Seed the database with fake ads and Picsum photos'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating categories...')
        cat_map = {}
        for c in CATEGORIES:
            obj, _ = Category.objects.get_or_create(slug=c['slug'], defaults={'name': c['name'], 'icon': c['icon']})
            cat_map[c['slug']] = obj

        self.stdout.write('Creating demo seller...')
        seller, created = User.objects.get_or_create(
            username='demo_seller',
            defaults={'email': 'demo@olx.pk', 'phone': '03001234567', 'city': 'Karachi'}
        )
        if created:
            seller.set_password('demo1234')
            seller.save()

        self.stdout.write(f'Seeding {len(ADS)} ads with Picsum images...')
        created_count = 0

        for ad_data in ADS:
            if Ad.objects.filter(title=ad_data['title']).exists():
                self.stdout.write(f'  skip (exists): {ad_data["title"][:50]}')
                continue

            category = cat_map.get(ad_data['category'])
            ad = Ad.objects.create(
                title=ad_data['title'],
                description=ad_data['desc'],
                price=ad_data['price'],
                category=category,
                seller=seller,
                location=ad_data['location'],
                condition=ad_data['condition'],
            )

            try:
                img_data = download_image(ad_data['img_seed'])
                filename = f"{ad_data['img_seed']}.jpg"
                ad_image = AdImage(ad=ad, is_cover=True)
                ad_image.image.save(filename, ContentFile(img_data), save=True)
                self.stdout.write(f'  OK: {ad_data["title"][:55]}')
            except Exception as e:
                self.stdout.write(f'  WARN: image failed ({e}), ad saved without image: {ad_data["title"][:40]}')

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'\nDone! Created {created_count} ads.'))
