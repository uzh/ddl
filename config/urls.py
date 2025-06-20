from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


urlpatterns = [
    path(
        '',
        RedirectView.as_view(url=f'/{settings.LANGUAGE_CODE}/', permanent=False)
    ),
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'cms/',
        include(wagtailadmin_urls)
    ),
    path(
        'documents/',
        include(wagtaildocs_urls)
    ),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='ddl/robots.txt', content_type='text/plain')
    ),
    path(
        'cookies/',
        include('cookie_consent.urls')
    ),
    path(
        '', include('ddl.urls')
    ),
    path(
        'reports/',
        include('reports.urls')
    )
]

# DDM Integration
urlpatterns += [
    path(
        r'ddm/',
        include('ddm.core.urls')
    ),
    path(
        'oidc/',
        include('mozilla_django_oidc.urls')
    ),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='ddl/registration/login.html'),
        name='login'
    ),
    path(
        'ddm/login/',
        auth_views.LoginView.as_view(
            template_name='ddl/auth/oidc_login.html'),
        name='ddm_login'
    ),
    path(
        'ddm/logout/',
        auth_views.LogoutView.as_view(),
        name='ddm_logout'
    ),
    path(
        'oidc/callback/ddm/login/failed/',
        RedirectView.as_view(url='/ddm/login/failed/', permanent=False),
        name='ddm_login_failed_redirect'
    ),
    path(
        'ddm/login/failed/',
        TemplateView.as_view(template_name='ddl/auth/oidc_login_failed.html'),
        name='ddm_login_failed'
    ),
    path(
        'ddm/contact/',
        TemplateView.as_view(template_name='ddl/custom-ddm/contact.html'),
        name='ddm-contact'
    ),
    path(
        'ckeditor5/',
        include('django_ckeditor_5.urls')
    ),
    path(
        '',
        include('gpt.urls')
    )
]

urlpatterns += i18n_patterns(
    path('', include(wagtail_urls)),
    path('', include('ddl.urls')),
    prefix_default_language=True
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
                   static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'ddl.views.custom_404_view'
handler500 = 'ddl.views.custom_500_view'
