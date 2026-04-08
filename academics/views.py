from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from lms.models import Enrollment

from .models import Course, Department


class DepartmentListView(ListView):
    context_object_name = "departments"
    template_name = "academics/department_list.html"

    def get_queryset(self):
        return Department.objects.annotate(course_count=Count("courses")).order_by(
            "order", "name"
        )


class DepartmentDetailView(DetailView):
    model = Department
    context_object_name = "department"
    template_name = "academics/department_detail.html"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Department.objects.prefetch_related("courses")


class CourseDetailView(DetailView):
    model = Course
    context_object_name = "course"
    template_name = "academics/course_detail.html"

    def get_queryset(self):
        return Course.objects.select_related("department").prefetch_related("instructors")

    def get_object(self, queryset=None):
        dept_slug = self.kwargs["dept_slug"]
        slug = self.kwargs["slug"]
        return get_object_or_404(
            Course.objects.select_related("department"),
            department__slug=dept_slug,
            slug=slug,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["is_enrolled"] = False
        if user.is_authenticated:
            ctx["is_enrolled"] = Enrollment.objects.filter(
                user=user,
                course=self.object,
                status=Enrollment.Status.ACTIVE,
            ).exists()
        return ctx
