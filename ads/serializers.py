from rest_framework import serializers
from .models import Ad, AdImage, Category
from accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    ad_count = serializers.IntegerField(source='ads.count', read_only=True)

    class Meta:
        model  = Category
        fields = ('id', 'name', 'slug', 'icon', 'ad_count')


class AdImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AdImage
        fields = ('id', 'image', 'is_cover')


class AdListSerializer(serializers.ModelSerializer):
    cover_image  = serializers.SerializerMethodField()
    category     = CategorySerializer(read_only=True)
    seller_name  = serializers.CharField(source='seller.username', read_only=True)
    is_favourite = serializers.SerializerMethodField()
    is_expired   = serializers.SerializerMethodField()

    class Meta:
        model  = Ad
        fields = ('id', 'title', 'price', 'location', 'category', 'seller_name',
                  'cover_image', 'created_at', 'condition', 'is_active',
                  'expires_at', 'is_favourite', 'is_expired')

    def get_cover_image(self, obj):
        request = self.context.get('request')
        cover = obj.images.filter(is_cover=True).first() or obj.images.first()
        if cover and request:
            return request.build_absolute_uri(cover.image.url)
        return None

    def get_is_favourite(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favourited_by.filter(user=request.user).exists()

    def get_is_expired(self, obj):
        from django.utils import timezone
        return bool(obj.expires_at and timezone.now() > obj.expires_at)


class AdDetailSerializer(serializers.ModelSerializer):
    images       = AdImageSerializer(many=True, read_only=True)
    category     = CategorySerializer(read_only=True)
    seller       = UserSerializer(read_only=True)
    is_favourite = serializers.SerializerMethodField()
    is_expired   = serializers.SerializerMethodField()

    class Meta:
        model  = Ad
        fields = ('id', 'title', 'description', 'price', 'category', 'seller',
                  'location', 'condition', 'images', 'created_at', 'updated_at',
                  'is_active', 'expires_at', 'is_favourite', 'is_expired')

    def get_is_favourite(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favourited_by.filter(user=request.user).exists()

    def get_is_expired(self, obj):
        from django.utils import timezone
        return bool(obj.expires_at and timezone.now() > obj.expires_at)


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model  = Ad
        fields = ('id', 'title', 'description', 'price', 'category', 'location',
                  'condition', 'uploaded_images')

    def create(self, validated_data):
        images = validated_data.pop('uploaded_images', [])
        validated_data['seller'] = self.context['request'].user
        ad = Ad.objects.create(**validated_data)
        for i, img in enumerate(images):
            AdImage.objects.create(ad=ad, image=img, is_cover=(i == 0))
        return ad

    def update(self, instance, validated_data):
        images = validated_data.pop('uploaded_images', [])
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if images:
            instance.images.all().delete()
            for i, img in enumerate(images):
                AdImage.objects.create(ad=instance, image=img, is_cover=(i == 0))
        return instance
