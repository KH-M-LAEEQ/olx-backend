from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve
from ads.views import CategoryListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',       include('accounts.urls')),
    path('api/ads/',        include('ads.urls')),
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/messages/', include('messaging.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
