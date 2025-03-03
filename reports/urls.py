from django.urls import path
from .views import SearchReport, DigitalMealReport, ChatGPTReport


urlpatterns = [
    path('google/<slug:participant_id>', SearchReport.as_view(), name='search-report'),
    path('digital-meal/<slug:participant_id>', DigitalMealReport.as_view(), name='digital-meal-report'),
    path('chat-gpt/<slug:participant_id>', ChatGPTReport.as_view(), name='chatgpt-report'),
]
