from django.urls import path

from digital_meal import views as dm_views


urlpatterns = [
    path('report/youtube/<slug:external_participant_id>', dm_views.IndividualReport.as_view(), name='individual-report'),
    # path('report/fitbit/<slug:external_participant_id>', dm_views.IndividualFitbitReport.as_view(), name='individual-fitbit-report'),
    # path('', dm_views.ScientificaLandingView.as_view(), name='scientifica')
]
