from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("home/", views.home, name="home"),                 # public
    path("dashboard/", views.dashboard, name="dashboard"), # private
]
