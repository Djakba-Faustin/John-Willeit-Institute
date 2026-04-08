from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    path(
        "departments/<slug:slug>/",
        views.DepartmentDetailView.as_view(),
        name="department_detail",
    ),
    path(
        "departments/<slug:dept_slug>/courses/<slug:slug>/",
        views.CourseDetailView.as_view(),
        name="course_detail",
    ),
]
