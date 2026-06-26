import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from categories.models import Category

CATEGORIES = [
    {'name': 'Mobiles',     'slug': 'mobiles',     'icon': '📱'},
    {'name': 'Cars',        'slug': 'cars',        'icon': '🚗'},
    {'name': 'Bikes',       'slug': 'bikes',       'icon': '🏍️'},
    {'name': 'Property',    'slug': 'property',    'icon': '🏠'},
    {'name': 'Electronics', 'slug': 'electronics', 'icon': '💻'},
    {'name': 'Fashion',     'slug': 'fashion',     'icon': '👗'},
    {'name': 'Furniture',   'slug': 'furniture',   'icon': '🛋️'},
    {'name': 'Jobs',        'slug': 'jobs',        'icon': '💼'},
    {'name': 'Animals',     'slug': 'animals',     'icon': '🐾'},
    {'name': 'Services',    'slug': 'services',    'icon': '🔧'},
]

for cat in CATEGORIES:
    obj, created = Category.objects.get_or_create(slug=cat['slug'], defaults=cat)
    print(f"{'Created' if created else 'Exists'}: {obj.name}")

print('Done.')
