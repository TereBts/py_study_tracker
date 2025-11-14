from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.utils import timezone
from .models import StudySession
from .forms import StudySessionForm
from achievements.services import evaluate_achievements_for_user
from django.views.generic import DeleteView


class StudySessionCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new StudySession record for the logged-in user.

    Allows users to log the details of their study sessions,
    automatically linking the record to their account and filtering
    course and goal options to those they own.

    On successful submission:
        - Saves the session to the database.
        - Displays a success message.
        - Evaluates and announces any newly unlocked achievements.

    Template:
        study_sessions/session_form.html

    Redirects to:
        study_sessions:my_sessions
    """

    model = StudySession
    form_class = StudySessionForm
    template_name = "study_sessions/session_form.html"
    success_url = reverse_lazy("study_sessions:my_sessions")

    def get_initial(self):
        """
        Prepopulate the 'started_at' field with the current local time.

        Returns:
            dict: Default initial form values.
        """
        return {
            "started_at": timezone.localtime().replace(
                second=0,
                microsecond=0
            )
        }

    def get_form_kwargs(self):
        """
        Inject the current user into the form for queryset filtering.

        Ensures that:
            - Course dropdown only shows the user’s courses.
            - Goal dropdown only shows the user’s active goals.

        Returns:
            dict: Form keyword arguments, including 'user'.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Handle successful form submission.

        Attaches the current user to the StudySession instance, saves it,
        and checks for any newly unlocked achievements.

        Args:
            form (StudySessionForm): The validated form instance.

        Returns:
            HttpResponseRedirect: Redirect to the success URL.
        """
        form.instance.user = self.request.user

        # Save the study session
        response = super().form_valid(form)

        # Notify user
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
    """
    Display a paginated list of the logged-in user's study sessions.

    Each entry includes details about the course, goal, start time,
    and duration. Uses select_related() for efficient foreign-key
    lookups and sorts sessions from newest to oldest.

    Template:
        study_sessions/my_sessions.html

    Context:
        sessions (QuerySet[StudySession]): The user’s session list.
    """

    model = StudySession
    template_name = "study_sessions/my_sessions.html"
    context_object_name = "sessions"
    paginate_by = 10

    def get_queryset(self):
        """
        Return only the logged-in user's sessions, with related data preloaded.

        Returns:
            QuerySet[StudySession]: User's sessions ordered by newest first.
        """
        return (
            StudySession.objects
            .filter(user=self.request.user)
            .select_related("course", "goal")
            .order_by("-started_at")
        )

class StudySessionDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete view for a StudySession.

    Only sessions belonging to the current user can be deleted.
    After deletion, user is redirected to the 'My Sessions' page.
    """

    model = StudySession
    template_name = "study_sessions/session_confirm_delete.html"
    success_url = reverse_lazy("study_sessions:my_sessions")

    def get_queryset(self):
        """
        Limit queryset to sessions owned by the logged-in user.
        This avoids 403s and means other users' sessions 404.
        """
        return StudySession.objects.filter(user=self.request.user)