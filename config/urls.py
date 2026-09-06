from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.http import HttpResponse
from django.views.static import serve
from ads.views import CategoryListView

admin.site.site_header = 'Bazaario Administration'
admin.site.site_title = 'Bazaario Admin'
admin.site.index_title = 'Bazaario Administration'

GOOGLE_VERIFY = 'google68b09f5de3bed367.html'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',       include('accounts.urls')),
    path('api/ads/',        include('ads.urls')),
    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/messages/', include('messaging.urls')),
    path(
        GOOGLE_VERIFY,
        lambda request: HttpResponse(
            f'google-site-verification: {GOOGLE_VERIFY}',
            content_type='text/html',
        ),
        name='google-verify',
    ),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
