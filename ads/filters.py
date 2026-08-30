import django_filters
from .models import Ad


class AdFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category  = django_filters.CharFilter(field_name='category__slug')
    location  = django_filters.CharFilter(field_name='location', lookup_expr='icontains')

    class Meta:
        model  = Ad
        fields = ['category', 'location', 'min_price', 'max_price', 'condition']
