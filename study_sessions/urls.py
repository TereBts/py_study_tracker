from django.urls import path
from .views import StudySessionCreateView, MyStudySessionsView

app_name = "study_sessions"
urlpatterns = [
    path("new/", StudySessionCreateView.as_view(), name="new"),
    path("mine/", MyStudySessionsView.as_view(), name="my_sessions"),
]
