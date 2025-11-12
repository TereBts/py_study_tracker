from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import CourseForm
from .models import Course


class CourseList(LoginRequiredMixin, ListView):
    """
    Display a list of courses owned by the currently logged-in user.

    Inherits from Django’s ListView and automatically passes the user's
    course list to the 'courses/course_list.html' template.

    Attributes:
        model (Course): The model being listed.
        template_name (str): Path to the template used for rendering.
        context_object_name (str): The variable name used in the template context.
    """

    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        """
        Retrieve only the courses belonging to the current user.

        Returns:
            QuerySet: Courses filtered by the logged-in user.
        """
        return Course.objects.filter(owner=self.request.user)


class CourseDetail(LoginRequiredMixin, DetailView):
    """
    Display details for a single course owned by the logged-in user.

    Ensures that users cannot access other users’ course detail pages.

    Attributes:
        model (Course): The model being displayed.
        template_name (str): Template for rendering course details.
        context_object_name (str): The variable name for the course in the context.
        slug_field (str): The field used for lookups in the URL.
        slug_url_kwarg (str): The URL parameter name that holds the slug.
    """

    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self):
        """
        Retrieve a course instance owned by the logged-in user.

        Prevents users from viewing courses that don’t belong to them.

        Returns:
            Course: The matching course object if found.
        Raises:
            Http404: If no course exists for this user and slug.
        """
        return get_object_or_404(
            Course, owner=self.request.user, slug=self.kwargs["slug"]
        )


class CourseCreate(LoginRequiredMixin, CreateView):
    """
    Create a new course for the logged-in user.

    Uses the CourseForm for validation and automatically assigns ownership
    to the current user. Upon success, redirects to the course detail page.

    Attributes:
        model (Course): The model being created.
        form_class (CourseForm): The form class used for validation.
        template_name (str): The template used for rendering the creation form.
    """

    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def get_form_kwargs(self):
        """
        Inject the current user into the form's initialization parameters.

        Allows user-specific validation (e.g., unique course titles).

        Returns:
            dict: Form keyword arguments including 'user'.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Assign ownership and display success message when the form is valid.

        Returns:
            HttpResponseRedirect: Redirect to the new course’s detail page.
        """
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Course created successfully.")
        return response


class CourseUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """
    Edit an existing course owned by the logged-in user.

    Reuses the CourseForm and enforces per-user ownership. A success message
    is displayed upon successful update.

    Attributes:
        model (Course): The model being updated.
        form_class (CourseForm): The form used for editing.
        template_name (str): The template used for rendering.
        slug_field (str): The field used for lookups in the URL.
        slug_url_kwarg (str): The URL parameter name that holds the slug.
        success_message (str): The message shown after successful update.
    """

    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_message = "Course updated successfully."

    def get_queryset(self):
        """
        Limit edit access to the logged-in user's courses.

        Returns:
            QuerySet: The user's courses only.
        """
        return Course.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        """
        Pass the current user into the form to enable per-user validation.

        Returns:
            dict: Form keyword arguments including 'user'.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class CourseDelete(LoginRequiredMixin, DeleteView):
    """
    Delete a course owned by the logged-in user.

    Ensures only the owner can delete a course, and displays a success message
    upon completion.

    Attributes:
        template_name (str): The confirmation template for deletion.
        slug_field (str): The field used for lookups in the URL.
        slug_url_kwarg (str): The URL parameter name that holds the slug.
        success_url (str): The URL to redirect to after deletion.
    """

    template_name = "courses/course_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("courses:list")

    def get_object(self):
        """
        Retrieve the course to delete, ensuring it belongs to the user.

        Returns:
            Course: The course instance to delete.
        Raises:
            Http404: If the course does not belong to the user.
        """
        return get_object_or_404(Course, owner=self.request.user, slug=self.kwargs["slug"])

    def get_success_url(self):
        """
        Add a success message and redirect to the course list after deletion.

        Returns:
            str: The URL to redirect to after successful deletion.
        """
        messages.success(self.request, "Course deleted.")
        return self.success_url
