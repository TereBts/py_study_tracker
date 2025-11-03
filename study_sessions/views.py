from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import StudySession
from .forms import StudySessionForm
from django.utils import timezone


# Create your views here.
class StudySessionCreateView(LoginRequiredMixin, CreateView):
    model = StudySession
    form_class = StudySessionForm
    template_name = "study_sessions/session_form.html"
    success_url = reverse_lazy("study_sessions:my_sessions")

    def get_initial(self):
        # prefill the datetime field with the current time
        return {"started_at": timezone.localtime().replace(second=0, microsecond=0)}

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Study session logged.")
        return super().form_valid(form)

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