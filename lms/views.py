from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg, Count, Max, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from academics.models import Course

from .forms import (
    AssignmentForm,
    AssignmentSubmissionForm,
    ForumReplyForm,
    ForumThreadForm,
    GradeSubmissionForm,
    LessonForm,
    MaterialForm,
    QuizForm,
    QuizQuestionForm,
)
from .models import (
    Assignment,
    AssignmentSubmission,
    Choice,
    Enrollment,
    ForumPost,
    ForumThread,
    Lesson,
    LessonCompletion,
    Material,
    Question,
    Quiz,
    QuizAnswer,
    QuizAttempt,
)


def redirect_user_to_role_dashboard(request):
    """
    Send the current user to the correct LMS home in one step (no redirect chains).
    Lecturers/staff/superuser → lecturer dashboard; everyone else → student dashboard.
    """
    u = request.user
    if u.is_superuser or getattr(u, "role", None) in ("lecturer", "staff"):
        return redirect("lms:lecturer_dashboard")
    return redirect("lms:student_dashboard")


def lms_entry(request):
    """Bare ``/lms/`` — role dashboard if logged in, site home otherwise."""
    if request.user.is_authenticated:
        return redirect_user_to_role_dashboard(request)
    return redirect("core:home")


def _courses_for_lecturer(user):
    """Courses a lecturer can manage (same rules as the lecturer dashboard)."""
    base = Course.objects.select_related("department")
    if user.is_superuser:
        return base.all()
    return base.filter(instructors=user).distinct()


def teach_entry(request):
    """
    Teaching hub at ``/lms/teach`` — real page for lecturers (not only a redirect).
    Students are sent to their dashboard.
    """
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    u = request.user
    if u.is_superuser or getattr(u, "role", None) in ("lecturer", "staff"):
        email_notifications_enabled, email_notifications_message = (
            _email_notifications_status()
        )
        return render(
            request,
            "lms/lecturer_dashboard.html",
            {
                "courses": _courses_for_lecturer(u),
                "is_teach_hub": True,
                "email_notifications_enabled": email_notifications_enabled,
                "email_notifications_message": email_notifications_message,
            },
        )
    return redirect("lms:student_dashboard")


def learn_entry(request):
    """``/lms/learn/`` — same role-based dashboard (entry point for learning)."""
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    return redirect_user_to_role_dashboard(request)


def _enrollment(user, course):
    return Enrollment.objects.filter(
        user=user,
        course=course,
        status=Enrollment.Status.ACTIVE,
    ).first()


def _is_instructor(user, course):
    if not user.is_authenticated:
        return False
    if user.is_superuser or getattr(user, "role", None) == "staff":
        return True
    return course.instructors.filter(pk=user.pk).exists()


def _student_emails_for_course(course):
    return list(
        Enrollment.objects.filter(
            course=course,
            status=Enrollment.Status.ACTIVE,
            user__email__isnull=False,
        )
        .exclude(user__email="")
        .values_list("user__email", flat=True)
        .distinct()
    )


def _notify_students_about_course_update(course, subject, body):
    recipients = _student_emails_for_course(course)
    if not recipients:
        return
    send_mail(
        subject=subject,
        message=body,
        from_email=None,
        recipient_list=recipients,
        fail_silently=True,
    )


def _email_notifications_status():
    backend = getattr(settings, "EMAIL_BACKEND", "")
    if backend == "django.core.mail.backends.console.EmailBackend":
        return (
            False,
            "Email notifications are in console mode. Configure SMTP in .env for real delivery.",
        )
    if not all(
        [
            getattr(settings, "EMAIL_HOST", ""),
            getattr(settings, "EMAIL_HOST_USER", ""),
            getattr(settings, "EMAIL_HOST_PASSWORD", ""),
        ]
    ):
        return (
            False,
            "Email notifications are not fully configured. Set EMAIL_HOST, EMAIL_HOST_USER, and EMAIL_HOST_PASSWORD.",
        )
    return (True, "Email notifications are enabled and ready to deliver.")


@login_required
def dashboard_redirect(request):
    return redirect_user_to_role_dashboard(request)


@login_required
def student_dashboard(request):
    if request.user.role not in ("student",):
        return redirect("lms:lecturer_dashboard")
    enrollments = (
        Enrollment.objects.filter(user=request.user, status=Enrollment.Status.ACTIVE)
        .select_related("course", "course__department")
        .order_by("-enrolled_at")
    )
    return render(
        request,
        "lms/student_dashboard.html",
        {"enrollments": enrollments},
    )


@login_required
def lecturer_dashboard(request):
    if not (
        request.user.role in ("lecturer", "staff") or request.user.is_superuser
    ):
        return redirect("lms:student_dashboard")
    email_notifications_enabled, email_notifications_message = (
        _email_notifications_status()
    )
    return render(
        request,
        "lms/lecturer_dashboard.html",
        {
            "courses": _courses_for_lecturer(request.user),
            "is_teach_hub": False,
            "email_notifications_enabled": email_notifications_enabled,
            "email_notifications_message": email_notifications_message,
        },
    )


@login_required
@require_http_methods(["POST"])
def enroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.role != "student":
        messages.error(request, "Only student accounts can self-enroll.")
        return redirect(course.get_absolute_url())
    obj, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={"status": Enrollment.Status.ACTIVE},
    )
    if not created and obj.status != Enrollment.Status.ACTIVE:
        obj.status = Enrollment.Status.ACTIVE
        obj.save()
    messages.success(request, f"You are now enrolled in {course.name}.")
    return redirect(
        "academics:course_detail",
        dept_slug=course.department.slug,
        slug=course.slug,
    )


@login_required
def student_course(request, course_id):
    course = get_object_or_404(
        Course.objects.select_related("department"),
        pk=course_id,
    )
    en = _enrollment(request.user, course)
    if not en:
        messages.warning(request, "Enroll in this course to access lessons and tools.")
        return redirect(
            "academics:course_detail",
            dept_slug=course.department.slug,
            slug=course.slug,
        )
    lessons = course.lessons.filter(published=True).prefetch_related("materials")
    completed_ids = set(
        LessonCompletion.objects.filter(enrollment=en).values_list(
            "lesson_id", flat=True
        )
    )
    quiz_avg = (
        QuizAttempt.objects.filter(user=request.user, quiz__course=course)
        .exclude(score_percent__isnull=True)
        .aggregate(avg=Avg("score_percent"))["avg"]
    )
    lecturer_materials = (
        course.materials.filter(Q(lesson__isnull=True) | Q(lesson__published=True))
        .select_related("lesson")
        .order_by("lesson__order", "lesson_id", "resource_category", "order", "id")
    )
    assignments = course.assignments.filter(published=True).order_by("-created_at")
    submission_by_assignment = {
        s.assignment_id: s
        for s in AssignmentSubmission.objects.filter(
            user=request.user,
            assignment__in=assignments,
        )
    }
    assignment_rows = [(a, submission_by_assignment.get(a.id)) for a in assignments]
    return render(
        request,
        "lms/student_course.html",
        {
            "course": course,
            "enrollment": en,
            "lessons": lessons,
            "completed_ids": completed_ids,
            "completed_count": len(completed_ids),
            "lesson_count": lessons.count(),
            "quiz_avg": quiz_avg,
            "quizzes": course.quizzes.filter(published=True),
            "lecturer_materials": lecturer_materials,
            "assignments": assignments,
            "assignment_rows": assignment_rows,
            "now": timezone.now(),
        },
    )


@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, pk=course_id)
    en = _enrollment(request.user, course)
    if not en:
        messages.error(request, "Enrollment required.")
        return redirect(
            "academics:course_detail",
            dept_slug=course.department.slug,
            slug=course.slug,
        )
    lesson = get_object_or_404(
        Lesson.objects.prefetch_related("materials"),
        pk=lesson_id,
        course=course,
        published=True,
    )
    completed = LessonCompletion.objects.filter(
        enrollment=en,
        lesson=lesson,
    ).exists()
    return render(
        request,
        "lms/lesson_detail.html",
        {
            "course": course,
            "lesson": lesson,
            "completed": completed,
            "enrollment": en,
        },
    )


@login_required
@require_http_methods(["POST"])
def mark_lesson_complete(request, course_id, lesson_id):
    course = get_object_or_404(Course, pk=course_id)
    en = _enrollment(request.user, course)
    if not en:
        return HttpResponseForbidden()
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course, published=True)
    LessonCompletion.objects.get_or_create(enrollment=en, lesson=lesson)
    messages.success(request, "Lesson marked complete.")
    return redirect("lms:lesson_detail", course_id=course_id, lesson_id=lesson_id)


@login_required
def quiz_take(request, quiz_id):
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__choices"),
        pk=quiz_id,
        published=True,
    )
    course = quiz.course
    en = _enrollment(request.user, course)
    if not en:
        messages.error(request, "You must be enrolled to take this quiz.")
        return redirect(
            "academics:course_detail",
            dept_slug=course.department.slug,
            slug=course.slug,
        )
    questions = list(quiz.questions.all().prefetch_related("choices"))
    if request.method == "POST":
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)
        total_points = 0
        earned = 0
        for q in questions:
            total_points += q.points
            raw = request.POST.get(f"q_{q.id}")
            selected = None
            if raw:
                try:
                    selected = Choice.objects.get(pk=int(raw), question=q)
                except (ValueError, Choice.DoesNotExist):
                    selected = None
                if selected and selected.is_correct:
                    earned += q.points
            QuizAnswer.objects.create(
                attempt=attempt,
                question=q,
                selected=selected,
            )
        if total_points > 0:
            score = round(earned / total_points * 100, 2)
        else:
            score = 0
        attempt.score_percent = score
        attempt.finished_at = timezone.now()
        attempt.save()
        messages.success(
            request,
            f"Quiz submitted. Score: {score}% (pass: {quiz.pass_score}%).",
        )
        return redirect("lms:quiz_result", attempt_id=attempt.pk)
    return render(
        request,
        "lms/quiz_take.html",
        {"quiz": quiz, "questions": questions, "course": course},
    )


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz", "quiz__course"),
        pk=attempt_id,
        user=request.user,
    )
    answers = attempt.answers.select_related("question", "selected")
    return render(
        request,
        "lms/quiz_result.html",
        {"attempt": attempt, "answers": answers},
    )


@login_required
def forum_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    en = _enrollment(request.user, course)
    if not en:
        messages.error(request, "Enrollment required.")
        return redirect(
            "academics:course_detail",
            dept_slug=course.department.slug,
            slug=course.slug,
        )
    threads = course.forum_threads.annotate(post_count=Count("posts")).order_by(
        "-pinned", "-created_at"
    )
    return render(
        request,
        "lms/forum_list.html",
        {"course": course, "threads": threads},
    )


@login_required
def forum_thread(request, thread_id):
    thread = get_object_or_404(
        ForumThread.objects.select_related("course", "course__department"),
        pk=thread_id,
    )
    en = _enrollment(request.user, thread.course)
    if not en:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            ForumPost.objects.create(
                thread=thread,
                author=request.user,
                body=form.cleaned_data["body"],
            )
            return redirect("lms:forum_thread", thread_id=thread.pk)
    else:
        form = ForumReplyForm()
    posts = thread.posts.select_related("author")
    return render(
        request,
        "lms/forum_thread.html",
        {"thread": thread, "posts": posts, "form": form},
    )


@login_required
def forum_new_thread(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    en = _enrollment(request.user, course)
    if not en:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ForumThreadForm(request.POST)
        reply = ForumReplyForm(request.POST, prefix="p")
        if form.is_valid() and reply.is_valid():
            thread = form.save(commit=False)
            thread.course = course
            thread.author = request.user
            thread.save()
            ForumPost.objects.create(
                thread=thread,
                author=request.user,
                body=reply.cleaned_data["body"],
            )
            messages.success(request, "Discussion started.")
            return redirect("lms:forum_thread", thread_id=thread.pk)
    else:
        form = ForumThreadForm()
        reply = ForumReplyForm(prefix="p")
    return render(
        request,
        "lms/forum_new_thread.html",
        {"course": course, "form": form, "reply": reply},
    )


@login_required
def lecturer_course(request, course_id):
    course = get_object_or_404(Course.objects.select_related("department"), pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    lessons = course.lessons.all().order_by("order", "id")
    course_resources = (
        course.materials.filter(lesson__isnull=True)
        .order_by("resource_category", "order", "id")
    )
    assignments = course.assignments.all().order_by("-created_at")
    quizzes = course.quizzes.all().order_by("id")
    return render(
        request,
        "lms/lecturer_course.html",
        {
            "course": course,
            "lessons": lessons,
            "course_resources": course_resources,
            "assignments": assignments,
            "quizzes": quizzes,
        },
    )


@login_required
def lesson_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "Lesson created.")
            return redirect("lms:lecturer_course", course_id=course.pk)
    else:
        form = LessonForm()
    return render(
        request,
        "lms/lesson_form.html",
        {"form": form, "course": course, "title": "New lesson"},
    )


@login_required
def lesson_edit(request, course_id, lesson_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated.")
            return redirect("lms:lecturer_course", course_id=course.pk)
    else:
        form = LessonForm(instance=lesson)
    return render(
        request,
        "lms/lesson_form.html",
        {"form": form, "course": course, "title": "Edit lesson"},
    )


@login_required
def lecturer_material_add(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    if request.method == "POST":
        form = MaterialForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            mat = form.save(commit=False)
            mat.course = course
            mat.save()
            _notify_students_about_course_update(
                course=course,
                subject=f"[{course.code}] New material: {mat.title}",
                body=(
                    f"A new learning material has been uploaded in {course.code} - {course.name}.\n\n"
                    f"Title: {mat.title}\n"
                    f"Open course: {reverse('lms:student_course', kwargs={'course_id': course.pk})}"
                ),
            )
            messages.success(request, "Resource uploaded.")
            return redirect("lms:lecturer_course", course_id=course.pk)
    else:
        form = MaterialForm(course=course)
    return render(
        request,
        "lms/material_form.html",
        {"form": form, "course": course},
    )


@login_required
@require_http_methods(["POST"])
def lecturer_material_delete(request, course_id, material_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    mat = get_object_or_404(Material, pk=material_id, course=course)
    mat.delete()
    messages.success(request, "Resource removed.")
    return redirect("lms:lecturer_course", course_id=course.pk)


@login_required
def assignment_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.course = course
            a.save()
            if a.published:
                _notify_students_about_course_update(
                    course=course,
                    subject=f"[{course.code}] New assignment: {a.title}",
                    body=(
                        f"A new assignment has been posted in {course.code} - {course.name}.\n\n"
                        f"Title: {a.title}\n"
                        f"Due: {a.due_at or 'No deadline'}\n"
                        f"Open course: {reverse('lms:student_course', kwargs={'course_id': course.pk})}"
                    ),
                )
            messages.success(request, "Assignment created.")
            return redirect("lms:lecturer_course", course_id=course.pk)
    else:
        form = AssignmentForm()
    return render(
        request,
        "lms/assignment_form.html",
        {"form": form, "course": course, "title": "New assignment"},
    )


@login_required
def assignment_edit(request, course_id, assignment_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    assignment = get_object_or_404(Assignment, pk=assignment_id, course=course)
    was_published = assignment.published
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            if assignment.published and not was_published:
                _notify_students_about_course_update(
                    course=course,
                    subject=f"[{course.code}] New assignment: {assignment.title}",
                    body=(
                        f"A new assignment is now available in {course.code} - {course.name}.\n\n"
                        f"Title: {assignment.title}\n"
                        f"Due: {assignment.due_at or 'No deadline'}\n"
                        f"Open course: {reverse('lms:student_course', kwargs={'course_id': course.pk})}"
                    ),
                )
            messages.success(request, "Assignment updated.")
            return redirect("lms:lecturer_course", course_id=course.pk)
    else:
        form = AssignmentForm(instance=assignment)
    return render(
        request,
        "lms/assignment_form.html",
        {"form": form, "course": course, "title": "Edit assignment", "assignment": assignment},
    )


@login_required
def assignment_submissions(request, course_id, assignment_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    assignment = get_object_or_404(Assignment, pk=assignment_id, course=course)
    subs = assignment.submissions.select_related("user").order_by("-submitted_at")
    return render(
        request,
        "lms/assignment_submissions.html",
        {"course": course, "assignment": assignment, "submissions": subs},
    )


@login_required
def submission_grade(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    sub = get_object_or_404(
        AssignmentSubmission.objects.select_related("assignment", "assignment__course"),
        pk=submission_id,
    )
    if sub.assignment.course_id != course.id:
        return HttpResponseForbidden()
    assignment = sub.assignment
    if request.method == "POST":
        form = GradeSubmissionForm(request.POST)
        if form.is_valid():
            score = form.cleaned_data["score"]
            if score > assignment.max_score:
                messages.error(request, f"Score cannot exceed {assignment.max_score}.")
            else:
                sub.score = score
                sub.feedback = form.cleaned_data.get("feedback") or ""
                sub.graded_at = timezone.now()
                sub.graded_by = request.user
                sub.save()
                messages.success(request, "Submission graded.")
                return redirect(
                    "lms:assignment_submissions",
                    course_id=course.pk,
                    assignment_id=assignment.pk,
                )
    else:
        initial = {}
        if sub.score is not None:
            initial["score"] = sub.score
        if sub.feedback:
            initial["feedback"] = sub.feedback
        form = GradeSubmissionForm(initial=initial)
    return render(
        request,
        "lms/submission_grade.html",
        {
            "course": course,
            "assignment": assignment,
            "submission": sub,
            "form": form,
        },
    )


@login_required
def student_assignment(request, course_id, assignment_id):
    course = get_object_or_404(Course.objects.select_related("department"), pk=course_id)
    en = _enrollment(request.user, course)
    assignment = get_object_or_404(
        Assignment.objects.filter(published=True),
        pk=assignment_id,
        course=course,
    )
    if not en:
        messages.error(request, "Enroll in this course to access assignments.")
        return redirect(
            "academics:course_detail",
            dept_slug=course.department.slug,
            slug=course.slug,
        )
    existing = AssignmentSubmission.objects.filter(
        assignment=assignment,
        user=request.user,
    ).first()
    if request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            text_ok = bool((form.cleaned_data.get("text") or "").strip())
            new_file = request.FILES.get("file")
            if not text_ok and not new_file and not (existing and existing.file):
                messages.error(request, "Add text or upload a PDF file.")
            else:
                sub = form.save(commit=False)
                sub.assignment = assignment
                sub.user = request.user
                sub.save()
                messages.success(
                    request,
                    "Your assignment was submitted online. The date and time below reflect your latest submission.",
                )
                return redirect("lms:student_assignment", course_id=course.pk, assignment_id=assignment.pk)
    else:
        form = (
            AssignmentSubmissionForm(instance=existing)
            if existing
            else AssignmentSubmissionForm()
        )
        sub = existing
    due_passed = bool(assignment.due_at and assignment.due_at < timezone.now())
    return render(
        request,
        "lms/student_assignment.html",
        {
            "course": course,
            "assignment": assignment,
            "submission": sub,
            "form": form,
            "due_passed": due_passed,
        },
    )


@login_required
def lecturer_quiz_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.course = course
            q.save()
            if q.published:
                _notify_students_about_course_update(
                    course=course,
                    subject=f"[{course.code}] New quiz: {q.title}",
                    body=(
                        f"A new quiz has been published in {course.code} - {course.name}.\n\n"
                        f"Title: {q.title}\n"
                        f"Pass score: {q.pass_score}%\n"
                        f"Time limit: {q.time_limit_minutes} minutes\n"
                        f"Open course: {reverse('lms:student_course', kwargs={'course_id': course.pk})}"
                    ),
                )
            messages.success(request, "Quiz created. Add questions next.")
            return redirect("lms:quiz_edit", course_id=course.pk, quiz_id=q.pk)
    else:
        form = QuizForm()
    return render(
        request,
        "lms/quiz_form.html",
        {"form": form, "course": course, "title": "New quiz"},
    )


@login_required
def lecturer_quiz_edit(request, course_id, quiz_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    quiz = get_object_or_404(Quiz, pk=quiz_id, course=course)
    was_published = quiz.published
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            quiz = form.save()
            if quiz.published and not was_published:
                _notify_students_about_course_update(
                    course=course,
                    subject=f"[{course.code}] New quiz: {quiz.title}",
                    body=(
                        f"A new quiz is now available in {course.code} - {course.name}.\n\n"
                        f"Title: {quiz.title}\n"
                        f"Pass score: {quiz.pass_score}%\n"
                        f"Time limit: {quiz.time_limit_minutes} minutes\n"
                        f"Open course: {reverse('lms:student_course', kwargs={'course_id': course.pk})}"
                    ),
                )
            messages.success(request, "Quiz saved.")
            return redirect("lms:lecturer_course", course_id=course.pk)
    else:
        form = QuizForm(instance=quiz)
    questions = quiz.questions.prefetch_related("choices").order_by("order", "id")
    return render(
        request,
        "lms/quiz_form.html",
        {
            "form": form,
            "course": course,
            "quiz": quiz,
            "title": "Edit quiz",
            "questions": questions,
        },
    )


@login_required
def lecturer_quiz_question_add(request, course_id, quiz_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    quiz = get_object_or_404(Quiz, pk=quiz_id, course=course)
    if request.method == "POST":
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            nxt = (quiz.questions.aggregate(m=Max("order"))["m"] or 0) + 1
            q = Question.objects.create(
                quiz=quiz,
                text=form.cleaned_data["text"],
                order=nxt,
                points=form.cleaned_data["points"],
            )
            correct = form.cleaned_data["correct"]
            for i in range(1, 5):
                txt = (form.cleaned_data.get(f"choice_{i}") or "").strip()
                if not txt:
                    continue
                Choice.objects.create(
                    question=q,
                    text=txt,
                    is_correct=(str(i) == correct),
                )
            if q.choices.count() < 2:
                q.delete()
                messages.error(request, "Provide at least two answer choices.")
            else:
                messages.success(request, "Question added.")
                return redirect("lms:quiz_edit", course_id=course.pk, quiz_id=quiz.pk)
    else:
        form = QuizQuestionForm()
    return render(
        request,
        "lms/quiz_question_form.html",
        {"form": form, "course": course, "quiz": quiz},
    )


@login_required
def lecturer_quiz_attempts(request, course_id, quiz_id):
    course = get_object_or_404(Course, pk=course_id)
    if not _is_instructor(request.user, course):
        return HttpResponseForbidden()
    quiz = get_object_or_404(Quiz, pk=quiz_id, course=course)
    attempts = (
        QuizAttempt.objects.filter(quiz=quiz)
        .select_related("user")
        .order_by("-started_at")
    )
    return render(
        request,
        "lms/quiz_attempts_lecturer.html",
        {"course": course, "quiz": quiz, "attempts": attempts},
    )
