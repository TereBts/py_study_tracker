from django.urls import path
from .views import achievement_list

app_name = "achievements"

urlpatterns = [
    path("", achievement_list, name="list"),
]
