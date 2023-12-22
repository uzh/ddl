from django.urls import path
from ddl.views import VPStudyLandingPage, VPStudyLandingPageInvited, ProjectDataAPIAlt


urlpatterns = [
    path('vp-studie', VPStudyLandingPage.as_view(), name='vp-study'),
    path('vp-studie-inv', VPStudyLandingPageInvited.as_view(), name='vp-study-invited'),
    path('project/<int:pk>/data-alt', ProjectDataAPIAlt.as_view(), name='ddm-data-api'),
]
