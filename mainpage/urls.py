from django.urls import path, include

from mainpage import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='main'),
]
