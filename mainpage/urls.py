from django.urls import path, include


urlpatterns = [
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    path(r'ddm/', include('ddm.urls'))
]
