from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "lms"

urlpatterns = [
    path("", views.lms_entry, name="index"),
    # With and without trailing slash (both must work; teach/<id>/ is registered below)
    path("teach", views.teach_entry, name="teach_index"),
    path("teach/", views.teach_entry),
    path("learn", views.learn_entry, name="learn_index"),
    path("learn/", views.learn_entry),
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    # With and without trailing slash (both must resolve)
    path("lecturer", views.lecturer_dashboard),
    path("lecturer/", views.lecturer_dashboard, name="lecturer_dashboard"),
    # Common mistake: URL name vs path — redirect to /lms/lecturer/
    path(
        "lecturer_dashboard",
        RedirectView.as_view(
            pattern_name="lms:lecturer_dashboard",
            permanent=False,
        ),
    ),
    path(
        "lecturer_dashboard/",
        RedirectView.as_view(
            pattern_name="lms:lecturer_dashboard",
            permanent=False,
        ),
    ),
    path("course/<int:course_id>/enroll/", views.enroll_course, name="enroll"),
    path("learn/<int:course_id>/", views.student_course, name="student_course"),
    path(
        "learn/<int:course_id>/lesson/<int:lesson_id>/",
        views.lesson_detail,
        name="lesson_detail",
    ),
    path(
        "learn/<int:course_id>/lesson/<int:lesson_id>/complete/",
        views.mark_lesson_complete,
        name="lesson_complete",
    ),
    path("quiz/<int:quiz_id>/", views.quiz_take, name="quiz_take"),
    path("quiz/result/<int:attempt_id>/", views.quiz_result, name="quiz_result"),
    path("course/<int:course_id>/forum/", views.forum_list, name="forum_list"),
    path("forum/thread/<int:thread_id>/", views.forum_thread, name="forum_thread"),
    path(
        "course/<int:course_id>/forum/new/",
        views.forum_new_thread,
        name="forum_new",
    ),
    path(
        "teach/<int:course_id>/",
        views.lecturer_course,
        name="lecturer_course",
    ),
    path(
        "teach/<int:course_id>/lessons/new/",
        views.lesson_create,
        name="lesson_create",
    ),
    path(
        "teach/<int:course_id>/lessons/<int:lesson_id>/edit/",
        views.lesson_edit,
        name="lesson_edit",
    ),
    path(
        "teach/<int:course_id>/materials/add/",
        views.lecturer_material_add,
        name="material_add",
    ),
    path(
        "teach/<int:course_id>/materials/<int:material_id>/delete/",
        views.lecturer_material_delete,
        name="material_delete",
    ),
    path(
        "teach/<int:course_id>/assignments/add/",
        views.assignment_create,
        name="assignment_create",
    ),
    path(
        "teach/<int:course_id>/assignments/<int:assignment_id>/edit/",
        views.assignment_edit,
        name="assignment_edit",
    ),
    path(
        "teach/<int:course_id>/assignments/<int:assignment_id>/submissions/",
        views.assignment_submissions,
        name="assignment_submissions",
    ),
    path(
        "teach/<int:course_id>/submissions/<int:submission_id>/grade/",
        views.submission_grade,
        name="submission_grade",
    ),
    path(
        "teach/<int:course_id>/quizzes/add/",
        views.lecturer_quiz_create,
        name="quiz_create",
    ),
    path(
        "teach/<int:course_id>/quizzes/<int:quiz_id>/edit/",
        views.lecturer_quiz_edit,
        name="quiz_edit",
    ),
    path(
        "teach/<int:course_id>/quizzes/<int:quiz_id>/questions/add/",
        views.lecturer_quiz_question_add,
        name="quiz_question_add",
    ),
    path(
        "teach/<int:course_id>/quizzes/<int:quiz_id>/attempts/",
        views.lecturer_quiz_attempts,
        name="quiz_attempts",
    ),
    path(
        "learn/<int:course_id>/assignments/<int:assignment_id>/",
        views.student_assignment,
        name="student_assignment",
    ),
]
