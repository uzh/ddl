from django.urls import path

from reports.views import ChatGPTReport
from .views import BriefingViewGPT, DataDonationViewGPT

urlpatterns = [
    path('datadonation/<slug:slug>/briefing/', BriefingViewGPT.as_view(), name='briefing-gpt'),
    path('datadonation/<slug:slug>/data-donation/', DataDonationViewGPT.as_view(), name='data-donation-gpt'),
    path('datadonation/report/<slug:participant_id>/', ChatGPTReport.as_view(), name='gpt-report'),
]
