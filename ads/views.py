from rest_framework import generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Ad, Favourite, AdReport
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
        from django.utils import timezone
        from django.db.models import Q
        return (
            Ad.objects
            .filter(is_active=True)
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
            .select_related('category', 'seller')
            .prefetch_related('images')
        )


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


class FavouriteToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk)
        fav, created = Favourite.objects.get_or_create(user=request.user, ad=ad)
        if not created:
            fav.delete()
            return Response({'is_favourite': False})
        return Response({'is_favourite': True})


class FavouriteListView(generics.ListAPIView):
    serializer_class   = AdListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(
            favourited_by__user=self.request.user,
            is_active=True
        ).select_related('category', 'seller').prefetch_related('images')


class AdReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk)
        if ad.seller_id == request.user.id:
            return Response({'detail': 'You cannot report your own ad.'}, status=400)
        reason  = request.data.get('reason', 'other')
        details = request.data.get('details', '')
        _, created = AdReport.objects.get_or_create(
            ad=ad, reporter=request.user,
            defaults={'reason': reason, 'details': details}
        )
        if not created:
            return Response({'detail': 'You have already reported this ad.'}, status=400)
        return Response({'detail': 'Report submitted. Thank you.'}, status=201)


class ToggleActiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk, seller=request.user)
        ad.is_active = not ad.is_active
        ad.save()
        return Response({'is_active': ad.is_active})


class RenewAdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from django.utils import timezone
        from datetime import timedelta
        ad = get_object_or_404(Ad, pk=pk, seller=request.user)
        ad.expires_at = timezone.now() + timedelta(days=60)
        ad.is_active  = True
        ad.save()
        return Response({'expires_at': ad.expires_at, 'is_active': ad.is_active})
