from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.CourseList.as_view(), name="list"),
    path("new/", views.CourseCreate.as_view(), name="create"),
    path("<slug:slug>/", views.CourseDetail.as_view(), name="detail"),
    path("<slug:slug>/edit/", views.CourseUpdate.as_view(), name="update"),
    path("<slug:slug>/delete/", views.CourseDelete.as_view(), name="delete"),
]
