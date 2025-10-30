from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import CourseForm
from .models import Course

# Create your views here.
class CourseList(LoginRequiredMixin, ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        # Only show the logged-in user's courses
        return Course.objects.filter(owner=self.request.user)


class CourseDetail(LoginRequiredMixin, DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self):
        # Prevent access to other users' courses
        return get_object_or_404(
            Course, owner=self.request.user, slug=self.kwargs["slug"]
        )


class CourseCreate(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass user so the form can enforce per-user title uniqueness
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Attach ownership to the current user
        form.instance.owner = self.request.user
        response = super().form_valid(form)  # redirects to get_absolute_url()
        messages.success(self.request, "Course created successfully.")
        return response


class CourseUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_message = "Course updated successfully."

    def get_queryset(self):
        # Only allow editing of the logged-in user's courses
        return Course.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class CourseDelete(LoginRequiredMixin, DeleteView):
    template_name = "courses/course_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("courses:list")

    def get_object(self):
        return get_object_or_404(Course, owner=self.request.user, slug=self.kwargs["slug"])

    def get_success_url(self):
        messages.success(self.request, "Course deleted.")
        return self.success_url