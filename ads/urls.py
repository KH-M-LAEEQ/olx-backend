from django.urls import path
from .views import (
    AdListView, AdDetailView, AdCreateView, AdUpdateView, AdDeleteView,
    MyAdsView, FavouriteToggleView, FavouriteListView, AdReportView,
    ToggleActiveView, RenewAdView,
)

urlpatterns = [
    path('',                         AdListView.as_view(),          name='ad-list'),
    path('<int:pk>/',                 AdDetailView.as_view(),         name='ad-detail'),
    path('create/',                   AdCreateView.as_view(),         name='ad-create'),
    path('<int:pk>/update/',          AdUpdateView.as_view(),         name='ad-update'),
    path('<int:pk>/delete/',          AdDeleteView.as_view(),         name='ad-delete'),
    path('my-ads/',                   MyAdsView.as_view(),            name='my-ads'),
    path('<int:pk>/favourite/',       FavouriteToggleView.as_view(),  name='ad-favourite'),
    path('<int:pk>/report/',          AdReportView.as_view(),         name='ad-report'),
    path('<int:pk>/toggle-active/',   ToggleActiveView.as_view(),     name='ad-toggle-active'),
    path('<int:pk>/renew/',           RenewAdView.as_view(),          name='ad-renew'),
    path('favourites/',               FavouriteListView.as_view(),    name='ad-favourites'),
]
