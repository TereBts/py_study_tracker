from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages
from django.http import HttpResponse

from .models import Goal
from .forms import GoalForm
from .services import last_week_range, freeze_weekly_outcomes
from achievements.services import evaluate_achievements_for_user


# Create your views here.

def manual_freeze(request):
    ws, we = last_week_range()
    freeze_weekly_outcomes(week_start=ws, week_end=we, dry_run=False)

    # run achievements for this user after outcomes are generated
    if request.user.is_authenticated:
        new_awards = evaluate_achievements_for_user(request.user)
        for ua in new_awards:
            messages.success(
                request,
                f"Unlocked achievement: {ua.achievement.title} ✨"
            )

    return redirect("goals:list")


class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = "goals/goal_list.html"

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = "goals/goal_form.html"
    success_url = reverse_lazy("goals:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Goal created successfully.")
        return super().form_valid(form)


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    template_name = "goals/goal_form.html"
    success_url = reverse_lazy("goals:list")

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Goal updated successfully.")
        return super().form_valid(form)


class GoalDetailView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = "goals/goal_detail.html"
    context_object_name = "goal"

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ensure last week is frozen
        ws, we = last_week_range()
        freeze_weekly_outcomes(week_start=ws, week_end=we, dry_run=False)

        # check for achievements
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
            int(o.lessons_completed) if o.lessons_completed is not None else None
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
    model = Goal
    template_name = "goals/goal_confirm_delete.html"
    success_url = reverse_lazy("goals:list")

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Goal deleted.")
        return super().delete(request, *args, **kwargs)
