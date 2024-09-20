from django.urls import path
from ddl.views import ProjectDataAPIAlt
from ddl.apis import ResponsesAPIAlt


urlpatterns = [
    path('project/<int:pk>/data-alt', ProjectDataAPIAlt.as_view(), name='ddm-data-api'),
    path('project/<int:pk>/responses-alt', ResponsesAPIAlt.as_view(), name='alt-response-api'),
]
