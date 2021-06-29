from django.urls import path, include

from mainpage import views


urlpatterns = [
    path('mainpage', views.MainView.as_view(), name='main'),
]
