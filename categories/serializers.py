from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    ad_count = serializers.IntegerField(source='ads.count', read_only=True)

    class Meta:
        model  = Category
        fields = ('id', 'name', 'slug', 'icon', 'ad_count')
