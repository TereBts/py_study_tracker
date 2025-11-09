from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("home/", views.home, name="home"),                 # public
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/", views.dashboard, name="dashboard"), # private
]
