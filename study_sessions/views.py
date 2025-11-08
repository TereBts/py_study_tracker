from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.utils import timezone

from .models import StudySession
from .forms import StudySessionForm
from achievements.services import evaluate_achievements_for_user


class StudySessionCreateView(LoginRequiredMixin, CreateView):
    model = StudySession
    form_class = StudySessionForm
    template_name = "study_sessions/session_form.html"
    success_url = reverse_lazy("study_sessions:my_sessions")

    def get_initial(self):
        # prefill the datetime field with the current time
        return {"started_at": timezone.localtime().replace(second=0, microsecond=0)}

    def get_form_kwargs(self):
        """
        Inject the current user into the form so it can filter
        courses and goals to this user's objects only.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Save the study session first
        response = super().form_valid(form)

        # Base success message
        messages.success(self.request, "Study session logged.")

        # Check for newly unlocked achievements
        new_awards = evaluate_achievements_for_user(self.request.user)
        for ua in new_awards:
            messages.success(
                self.request,
                f"Unlocked achievement: {ua.achievement.title} ✨"
            )

        return response


class MyStudySessionsView(LoginRequiredMixin, ListView):
    model = StudySession
    template_name = "study_sessions/my_sessions.html"
    context_object_name = "sessions"
    paginate_by = 10

    def get_queryset(self):
        return (
            StudySession.objects
            .filter(user=self.request.user)
            .select_related("course", "goal")
            .order_by("-started_at")
        )
