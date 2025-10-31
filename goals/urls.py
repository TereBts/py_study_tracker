# apps/goals/urls.py
from django.urls import path
from .views import GoalListView, GoalCreateView, GoalUpdateView, GoalDetailView

app_name = "goals"

urlpatterns = [
    path("", GoalListView.as_view(), name="list"),
    path("new/", GoalCreateView.as_view(), name="create"),
    path("<int:pk>/", GoalDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", GoalUpdateView.as_view(), name="edit"),
]
