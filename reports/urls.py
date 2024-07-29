from django.urls import path
from .views import PoliticsReport


urlpatterns = [
    path('politik/<slug:participant_id>', PoliticsReport.as_view(), name='politics-report'),
]
