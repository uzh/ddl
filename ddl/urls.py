from django.urls import path

from .apis import ZipPostAPI


urlpatterns = [
    path(
        'api/zip/<slug:project_url_id>',
        ZipPostAPI.as_view(),
        name='zip_post'
    ),
]
