from rest_framework import generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ad
from .serializers import AdListSerializer, AdDetailSerializer, AdCreateUpdateSerializer
from .filters import AdFilter


class AdListView(generics.ListAPIView):
    serializer_class   = AdListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = AdFilter
    search_fields      = ['title', 'description', 'location']
    ordering_fields    = ['price', 'created_at']
    ordering           = ['-created_at']

    def get_queryset(self):
        return Ad.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images')


class AdDetailView(generics.RetrieveAPIView):
    queryset           = Ad.objects.filter(is_active=True)
    serializer_class   = AdDetailSerializer
    permission_classes = [permissions.AllowAny]


class AdCreateView(generics.CreateAPIView):
    serializer_class   = AdCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]


class AdUpdateView(generics.UpdateAPIView):
    serializer_class   = AdCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user)


class AdDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user)


class MyAdsView(generics.ListAPIView):
    serializer_class   = AdListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(seller=self.request.user).prefetch_related('images')
