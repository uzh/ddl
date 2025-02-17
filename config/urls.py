from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

from ddl import apis as dm_apis

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('robots.txt', TemplateView.as_view(template_name="ddl/robots.txt", content_type='text/plain')),
    path(r'ddm/', include('ddm.core.urls')),
    path(r'ddm/', include('gpt.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='ddl/registration/login.html'), name='login'),
    path('ddm/login/', auth_views.LoginView.as_view(template_name='ddl/auth/oidc_login.html'), name='ddm_login'),
    path('ddm/logout/', auth_views.LogoutView.as_view(), name='ddm_logout'),
    path('ddm/contact/', TemplateView.as_view(template_name='ddl/custom-ddm/contact.html'), name='ddm-contact'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),  # This is the endpoint that handles file uploads through the CKEditor.
    path('dm-api/<int:pk>/class-data', dm_apis.ClassReportAPI.as_view(), name='class_data_api'),  # int:pk relates to ID of DDM project (must be named 'pk' due to ddm authentication scheme).
    path('dm-api/<int:pk>/class-overview', dm_apis.ClassOverviewAPI.as_view(), name='class_overview_api'),  # int:pk relates to ID of DDM project.
    path('dm-api/<int:pk>/individual-data', dm_apis.IndividualReportAPI.as_view(), name='individual_data_api'),  # int:pk relates to ID of DDM project.
    path('cookies/', include('cookie_consent.urls')),
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
