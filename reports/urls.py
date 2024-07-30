from django.urls import path
from .views import (
    PoliticsReportInstagram, PoliticsReportFacebook, SearchReport,
    DigitalMealReport, ChatGPTReport
)


urlpatterns = [
    path('politik-instagram/<slug:participant_id>', PoliticsReportInstagram.as_view(), name='politics-report-instagram'),
    path('politik-facebook/<slug:participant_id>', PoliticsReportFacebook.as_view(), name='politics-report-facebook'),
    path('google/<slug:participant_id>', SearchReport.as_view(), name='search-report'),
    path('digital-meal/<slug:participant_id>', DigitalMealReport.as_view(), name='digital-meal-report'),
    path('chat-gpt/<slug:participant_id>', ChatGPTReport.as_view(), name='chatgpt-report'),
]
