from django.urls import path
from .views import AdListView, AdDetailView, AdCreateView, AdUpdateView, AdDeleteView, MyAdsView

urlpatterns = [
    path('',             AdListView.as_view(),   name='ad-list'),
    path('<int:pk>/',    AdDetailView.as_view(),  name='ad-detail'),
    path('create/',      AdCreateView.as_view(),  name='ad-create'),
    path('<int:pk>/update/', AdUpdateView.as_view(), name='ad-update'),
    path('<int:pk>/delete/', AdDeleteView.as_view(), name='ad-delete'),
    path('my-ads/',      MyAdsView.as_view(),     name='my-ads'),
]
