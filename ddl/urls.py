from django.urls import path
from ddl.views import VPStudyLandingPage, VPStudyLandingPageInvited


urlpatterns = [
    path('vp-studie', VPStudyLandingPage.as_view(), name='vp-study'),
    path('vp-studie-inv', VPStudyLandingPageInvited.as_view(), name='vp-study-invited')
]
