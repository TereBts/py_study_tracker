"""Goal views for StudyStar.

Contains class-based views for CRUD operations on Goal objects and
utility views for freezing weekly outcomes and triggering achievements.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
    )
from django.contrib import messages
from django.shortcuts import redirect

from .models import Goal
from .forms import GoalForm
from .services import last_week_range, freeze_weekly_outcomes
from achievements.services import evaluate_achievements_for_user


def manual_freeze(request):
    """
    Manually freeze last week's outcomes and evaluate achievements.

    This view:
      1) Computes the previous ISO week (Mon–Sun).
      2) Freezes weekly outcomes for all active goals.
      3) Evaluates and awards any new achievements for the current user,
         displaying a success message for each one.
      4) Redirects back to the goals list.

    Args:
        request (HttpRequest): The incoming request.

    Returns:
        HttpResponseRedirect: Redirect to the 'goals:list' page.
    """
    ws, we = last_week_range()
    freeze_weekly_outcomes(week_start=ws, week_end=we, dry_run=False)

    if request.user.is_authenticated:
        new_awards = evaluate_achievements_for_user(request.user)
        for ua in new_awards:
            messages.success(
                request, f"Unlocked achievement: {ua.achievement.title} ✨")

    return redirect("goals:list")


class GoalListView(LoginRequiredMixin, ListView):
    """
    List the logged-in user's goals.

    Uses the 'goals/goal_list.html' template and ensures that only
    the requesting user's goals are included.
    """

    model = Goal
    template_name = "goals/goal_list.html"

    def get_queryset(self):
        """
        Return only the current user's goals.

        Returns:
            QuerySet[Goal]: Goals filtered by the requesting user.
        """
        return Goal.objects.filter(user=self.request.user)


class GoalCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new goal for the logged-in user.

    Uses GoalForm for validation, injects the user for per-user
    course filtering, and sets ownership on save.
    """

    model = Goal
    form_class = GoalForm
    template_name = "goals/goal_form.html"
    success_url = reverse_lazy("goals:list")

    def get_form_kwargs(self):
        """
        Inject the current user into the form for queryset scoping.

        Returns:
            dict: Keyword args including 'user' for GoalForm.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Assign ownership, show a success message, and proceed with save.

        Args:
            form (GoalForm): The validated form instance.

        Returns:
            HttpResponseRedirect: Redirect to success_url.
        """
        form.instance.user = self.request.user
        messages.success(self.request, "Goal created successfully.")
        return super().form_valid(form)


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing goal owned by the logged-in user.

    Reuses GoalForm and limits edits to the user's own goals.
    """

    model = Goal
    form_class = GoalForm
    template_name = "goals/goal_form.html"
    success_url = reverse_lazy("goals:list")

    def get_queryset(self):
        """
        Limit updates to goals belonging to the current user.

        Returns:
            QuerySet[Goal]: The user's goals.
        """
        return Goal.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        """
        Provide the current user to the form for course scoping.

        Returns:
            dict: Keyword args including 'user' for GoalForm.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Show a success message and proceed with saving the changes.

        Args:
            form (GoalForm): The validated form instance.

        Returns:
            HttpResponseRedirect: Redirect to success_url.
        """
        messages.success(self.request, "Goal updated successfully.")
        return super().form_valid(form)


class GoalDetailView(LoginRequiredMixin, DetailView):
    """
    Show details of a single goal owned by the logged-in user.

    Augments context with:
      - A recent weekly outcomes slice for charts (up to 26 weeks).
      - Pre-built arrays for chart labels/series.
      - On access, freezes the previous week and evaluates achievements.
    """

    model = Goal
    template_name = "goals/goal_detail.html"
    context_object_name = "goal"

    def get_queryset(self):
        """
        Restrict access to the current user's own goals.

        Returns:
            QuerySet[Goal]: The user's goals.
        """
        return Goal.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Add weekly outcomes and chart data to the template context.

        Also ensures the previous week is frozen and runs achievement
        evaluation for the current user, surfacing any new unlocks.

        Returns:
            dict: Extended context including:
                - outcomes: recent GoalOutcome objects (ascending by week).
                - chart_* arrays for labels and series values.
        """
        context = super().get_context_data(**kwargs)

        # Ensure last week is frozen
        ws, we = last_week_range()
        freeze_weekly_outcomes(week_start=ws, week_end=we, dry_run=False)

        # Evaluate achievements
        new_awards = evaluate_achievements_for_user(self.request.user)
        for ua in new_awards:
            messages.success(
                self.request,
                f"Unlocked achievement: {ua.achievement.title} ✨"
            )

        # Pull recent history (ascending by week for chart)
        qs = self.object.outcomes.order_by("week_start")
        context["outcomes"] = qs.reverse()[:26][::-1]

        # Build chart data
        labels = [o.week_start.isoformat() for o in qs]
        hours_completed = [
            float(o.hours_completed) if o.hours_completed is not None else None
            for o in qs
        ]
        hours_target = [
            float(o.hours_target) if o.hours_target is not None else None
            for o in qs
        ]
        lessons_completed = [
            (
                int(o.lessons_completed)
                if o.lessons_completed is not None
                else None
            )
            for o in qs
        ]
        lessons_target = [
            int(o.lessons_target) if o.lessons_target is not None else None
            for o in qs
        ]

        context["chart_labels"] = labels
        context["chart_hours_completed"] = hours_completed
        context["chart_hours_target"] = hours_target
        context["chart_lessons_completed"] = lessons_completed
        context["chart_lessons_target"] = lessons_target

        return context


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a goal owned by the logged-in user.

    Shows a success message and redirects to the goal list.
    """

    model = Goal
    template_name = "goals/goal_confirm_delete.html"
    success_url = reverse_lazy("goals:list")

    def get_queryset(self):
        """
        Restrict deletions to the current user's goals.

        Returns:
            QuerySet[Goal]: The user's goals.
        """
        return Goal.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Add a success message before performing the delete.

        Returns:
            HttpResponseRedirect: Redirect to success_url after deletion.
        """
        messages.success(self.request, "Goal deleted.")
        return super().delete(request, *args, **kwargs)
