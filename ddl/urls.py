from django.urls import path
from ddl.views import ProjectDataAPIAlt


urlpatterns = [
    path('project/<int:pk>/data-alt', ProjectDataAPIAlt.as_view(), name='ddm-data-api'),
]
