from django.urls import path
from .views import BriefingViewGPT, DataDonationViewGPT

urlpatterns = [
    path('gpt-studie/<slug:slug>/briefing/', BriefingViewGPT.as_view(), name='briefing-gpt'),
    path('gpt-studie/<slug:slug>/data-donation/', DataDonationViewGPT.as_view(), name='data-donation-gpt'),
]
