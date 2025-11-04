from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages

from .models import Goal
from .forms import GoalForm
from .services import last_week_range, freeze_weekly_outcomes


# Create your views here.

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
        ws, we = last_week_range()
        # idempotent: creates/updates last week only if due
        freeze_weekly_outcomes(week_start=ws, week_end=we, dry_run=False)
        context["outcomes"] = self.object.outcomes.all()[:26]
        return context
    
class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = "goals/goal_confirm_delete.html"  # create this template
    success_url = reverse_lazy("goals:list")

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Goal deleted.")
        return super().delete(request, *args, **kwargs)