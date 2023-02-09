from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path(r'ddm/', include('ddm.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='ddl/registration/login.html'), name='login'),
    path('ddm/login/', auth_views.LoginView.as_view(template_name='ddm/admin/auth/login.html'), name='ddm-login'),
    path('ddm/logout/', auth_views.LogoutView.as_view(), name='ddm-logout'),
]

urlpatterns += i18n_patterns(
    path('', include(wagtail_urls)),
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
                   static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
