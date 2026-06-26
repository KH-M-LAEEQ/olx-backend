import os
import io
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from accounts.models import User
from categories.models import Category
from ads.models import Ad, AdImage

PEXELS_KEY = 'IRod3n1KsMFCb57g0um9OVhIXreezqDHl2UhZV7qe3tQPtRZOIivDzaK'

SEED_ADS = [
    # Mobiles
    {'title': 'iPhone 14 Pro Max – 256GB Space Black', 'category': 'mobiles', 'price': 280000, 'location': 'Karachi', 'condition': 'used',
     'description': 'Slightly used iPhone 14 Pro Max in excellent condition. No scratches, original box included. Battery health 91%.', 'query': 'iPhone smartphone'},
    {'title': 'Samsung Galaxy S23 Ultra', 'category': 'mobiles', 'price': 220000, 'location': 'Lahore', 'condition': 'used',
     'description': 'Samsung Galaxy S23 Ultra 12GB/256GB. All accessories included. Face and fingerprint unlock working perfectly.', 'query': 'Samsung Galaxy phone'},
    {'title': 'OnePlus 11 5G – Brand New Sealed', 'category': 'mobiles', 'price': 95000, 'location': 'Islamabad', 'condition': 'new',
     'description': 'OnePlus 11 5G sealed box. 16GB RAM, 256GB storage. Snapdragon 8 Gen 2 processor.', 'query': 'OnePlus Android phone'},

    # Cars
    {'title': 'Toyota Corolla 2020 – 1.8 Altis', 'category': 'cars', 'price': 5200000, 'location': 'Karachi', 'condition': 'used',
     'description': 'Well maintained Toyota Corolla Altis 1.8. First owner. 45,000 km driven. All genuine parts.', 'query': 'Toyota Corolla car'},
    {'title': 'Honda Civic 2019 – Turbo 1.5', 'category': 'cars', 'price': 4800000, 'location': 'Lahore', 'condition': 'used',
     'description': 'Honda Civic Turbo 1.5L 2019. Immaculate condition, no accident history. New tyres fitted.', 'query': 'Honda Civic car'},
    {'title': 'Suzuki Alto VXL 2022 – Automatic', 'category': 'cars', 'price': 2100000, 'location': 'Rawalpindi', 'condition': 'used',
     'description': 'Suzuki Alto VXL 2022 automatic transmission. Fuel efficient, low mileage 18,000 km only.', 'query': 'Suzuki small car'},

    # Bikes
    {'title': 'Honda CB125F 2023 – Like New', 'category': 'bikes', 'price': 195000, 'location': 'Faisalabad', 'condition': 'used',
     'description': 'Honda CB125F 2023 model, self-start, alloy wheels. Only 5,000 km driven. All documents clear.', 'query': 'Honda motorcycle bike'},
    {'title': 'Yamaha YBR 125G 2022', 'category': 'bikes', 'price': 155000, 'location': 'Multan', 'condition': 'used',
     'description': 'Yamaha YBR 125G with genuine parts. Good condition, no major repairs. Registration in Multan.', 'query': 'Yamaha motorcycle'},

    # Property
    {'title': '3-Bed Apartment for Sale – DHA Phase 5 Karachi', 'category': 'property', 'price': 22000000, 'location': 'Karachi', 'condition': 'used',
     'description': '1,800 sq ft 3-bedroom, 2-bathroom apartment on 8th floor. Sea facing, covered parking, 24/7 security.', 'query': 'modern apartment building'},
    {'title': '5-Marla House for Sale – Bahria Town Lahore', 'category': 'property', 'price': 18500000, 'location': 'Lahore', 'condition': 'used',
     'description': 'Fully furnished 5-marla house in Bahria Town. 4 bedrooms, 3 bathrooms, servant quarter. Owner built.', 'query': 'residential house property'},

    # Electronics
    {'title': 'Dell XPS 15 Laptop – Core i7 12th Gen', 'category': 'electronics', 'price': 185000, 'location': 'Karachi', 'condition': 'used',
     'description': 'Dell XPS 15 with 16GB DDR5 RAM, 512GB NVMe SSD, NVIDIA RTX 3050. Perfect for professionals.', 'query': 'Dell laptop computer'},
    {'title': 'Sony 55-inch 4K OLED Smart TV', 'category': 'electronics', 'price': 145000, 'location': 'Lahore', 'condition': 'used',
     'description': 'Sony Bravia 55-inch 4K OLED Smart TV. Android TV with Google Assistant. Remote and box included.', 'query': 'Sony smart television TV'},
    {'title': 'Canon EOS R6 Mark II – Body Only', 'category': 'electronics', 'price': 420000, 'location': 'Islamabad', 'condition': 'used',
     'description': 'Canon EOS R6 Mark II mirrorless camera. Only 3,000 actuations. Comes with original strap and charger.', 'query': 'Canon camera photography'},

    # Fashion
    {'title': 'Nike Air Jordan 1 Retro High – Size 42', 'category': 'fashion', 'price': 22000, 'location': 'Karachi', 'condition': 'new',
     'description': 'Brand new Nike Air Jordan 1 Retro High OG Chicago. Size UK 8 / EU 42. Original box included.', 'query': 'Nike sneakers shoes'},
    {'title': 'Levi\'s 501 Original Jeans – 3 Pairs', 'category': 'fashion', 'price': 9500, 'location': 'Lahore', 'condition': 'new',
     'description': 'Levi\'s 501 original fit jeans, sizes 30x32. Genuine import. Pack of 3 different shades.', 'query': 'jeans denim fashion'},

    # Furniture
    {'title': '7-Seater L-Shaped Sofa – Dark Grey', 'category': 'furniture', 'price': 65000, 'location': 'Karachi', 'condition': 'used',
     'description': 'L-shaped 7-seater sofa in dark grey fabric. Excellent condition, no stains. Self-pickup only.', 'query': 'sofa couch furniture living room'},
    {'title': 'King Size Wooden Bed with Mattress', 'category': 'furniture', 'price': 48000, 'location': 'Lahore', 'condition': 'used',
     'description': 'Solid wood king size bed frame with Moltyfoam mattress. 2 years old, no damage.', 'query': 'wooden bed bedroom furniture'},
    {'title': 'Office Workstation – 6-Seat Setup', 'category': 'furniture', 'price': 75000, 'location': 'Islamabad', 'condition': 'used',
     'description': 'Complete 6-seat office workstation setup with dividers and cable management. Moving sale.', 'query': 'office desk workstation furniture'},

    # Animals
    {'title': 'Golden Retriever Puppies – 6 Weeks Old', 'category': 'animals', 'price': 35000, 'location': 'Lahore', 'condition': 'new',
     'description': 'Pure breed Golden Retriever puppies. Both parents on site. Vaccinated and dewormed. Ready in 2 weeks.', 'query': 'Golden Retriever puppy dog'},
    {'title': 'Persian Cat – 1 Year Old Female', 'category': 'animals', 'price': 18000, 'location': 'Karachi', 'condition': 'used',
     'description': 'Beautiful white Persian cat, 1 year old, fully vaccinated. Very friendly and litter trained.', 'query': 'Persian cat white fluffy'},

    # Services
    {'title': 'Professional Home Painting – Interior & Exterior', 'category': 'services', 'price': 15000, 'location': 'Karachi', 'condition': 'new',
     'description': 'Expert painting team. Per room pricing starts from PKR 3,500. Free estimation visit. 10 years experience.', 'query': 'house painting home renovation'},
    {'title': 'Web Development – React & Django Projects', 'category': 'services', 'price': 50000, 'location': 'Islamabad', 'condition': 'new',
     'description': 'Full-stack developer offering React + Django web apps, REST APIs, and e-commerce solutions. Portfolio available.', 'query': 'web developer coding computer'},

    # Jobs
    {'title': 'Hiring – Senior React Developer (Remote)', 'category': 'jobs', 'price': 150000, 'location': 'Karachi', 'condition': 'new',
     'description': 'Startup hiring senior React developer. 3+ years experience required. Monthly salary PKR 150,000–200,000. Remote work.', 'query': 'office job hiring work'},
    {'title': 'Sales Executive Needed – Electronics Store', 'category': 'jobs', 'price': 45000, 'location': 'Lahore', 'condition': 'new',
     'description': 'Electronics retail store needs experienced sales executive. Salary + commission. Apply with CV.', 'query': 'sales executive job interview'},
]


def fetch_pexels_image(query):
    url = 'https://api.pexels.com/v1/search'
    headers = {'Authorization': PEXELS_KEY}
    params = {'query': query, 'per_page': 1, 'orientation': 'landscape'}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        photos = r.json().get('photos', [])
        if photos:
            img_url = photos[0]['src']['large']
            img_r = requests.get(img_url, timeout=15)
            img_r.raise_for_status()
            return img_r.content, f"{query.replace(' ', '_')}.jpg"
    except Exception as e:
        print(f'  Pexels error for "{query}": {e}')
    return None, None


def main():
    # Ensure categories exist
    print('Seeding categories...')
    os.system('python seed_categories.py 2>&1')

    # Create or get demo seller
    seller, created = User.objects.get_or_create(
        username='demo_seller',
        defaults={
            'email': 'demo@olx.pk',
            'first_name': 'Demo',
            'last_name': 'Seller',
            'phone': '03001234567',
            'city': 'Karachi',
        }
    )
    if created:
        seller.set_password('demo1234')
        seller.save()
        print('Created demo_seller user (password: demo1234)')
    else:
        print('Using existing demo_seller user')

    categories = {c.slug: c for c in Category.objects.all()}
    created_count = 0

    for ad_data in SEED_ADS:
        cat = categories.get(ad_data['category'])
        if not cat:
            print(f'  Skipping — category "{ad_data["category"]}" not found')
            continue

        if Ad.objects.filter(title=ad_data['title'], seller=seller).exists():
            print(f'  Exists: {ad_data["title"]}')
            continue

        print(f'  Creating: {ad_data["title"]}')
        ad = Ad.objects.create(
            title=ad_data['title'],
            description=ad_data['description'],
            price=ad_data['price'],
            category=cat,
            seller=seller,
            location=ad_data['location'],
            condition=ad_data['condition'],
        )

        img_bytes, filename = fetch_pexels_image(ad_data['query'])
        if img_bytes:
            ad_image = AdImage(ad=ad, is_cover=True)
            ad_image.image.save(filename, ContentFile(img_bytes), save=True)
            print(f'    + image saved')
        else:
            print(f'    ! no image')

        created_count += 1

    print(f'\nDone. {created_count} ads created.')


if __name__ == '__main__':
    main()
