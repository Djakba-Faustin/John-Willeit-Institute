"""Smoke and integration tests for the LMS app."""

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import NoReverseMatch, reverse

from academics.models import Course, Department
from lms.models import Assignment, Enrollment, Lesson, Material, Quiz

User = get_user_model()


class LMSURLReverseTests(TestCase):
    """Every named route should reverse without error."""

    def test_all_lms_named_urls_reverse(self):
        cases = [
            ("index", {}),
            ("teach_index", {}),
            ("learn_index", {}),
            ("dashboard_redirect", {}),
            ("student_dashboard", {}),
            ("lecturer_dashboard", {}),
            ("enroll", {"course_id": 1}),
            ("student_course", {"course_id": 1}),
            ("lesson_detail", {"course_id": 1, "lesson_id": 1}),
            ("lesson_complete", {"course_id": 1, "lesson_id": 1}),
            ("quiz_take", {"quiz_id": 1}),
            ("quiz_result", {"attempt_id": 1}),
            ("forum_list", {"course_id": 1}),
            ("forum_thread", {"thread_id": 1}),
            ("forum_new", {"course_id": 1}),
            ("lecturer_course", {"course_id": 1}),
            ("lesson_create", {"course_id": 1}),
            ("lesson_edit", {"course_id": 1, "lesson_id": 1}),
            ("material_add", {"course_id": 1}),
            ("material_delete", {"course_id": 1, "material_id": 1}),
            ("assignment_create", {"course_id": 1}),
            ("assignment_edit", {"course_id": 1, "assignment_id": 1}),
            ("assignment_submissions", {"course_id": 1, "assignment_id": 1}),
            ("submission_grade", {"course_id": 1, "submission_id": 1}),
            ("quiz_create", {"course_id": 1}),
            ("quiz_edit", {"course_id": 1, "quiz_id": 1}),
            ("quiz_question_add", {"course_id": 1, "quiz_id": 1}),
            ("quiz_attempts", {"course_id": 1, "quiz_id": 1}),
            ("student_assignment", {"course_id": 1, "assignment_id": 1}),
        ]
        for name, kwargs in cases:
            try:
                reverse(f"lms:{name}", kwargs=kwargs)
            except NoReverseMatch as e:
                self.fail(f"lms:{name} {kwargs!r}: {e}")


class LMSEntryRedirectTests(TestCase):
    """``/lms/`` should redirect instead of 404."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username="entry_student",
            password="pass12345",
            role=User.Role.STUDENT,
        )

    def test_anonymous_redirects_to_home(self):
        r = self.client.get(reverse("lms:index"))
        self.assertRedirects(r, reverse("core:home"), fetch_redirect_response=False)

    def test_logged_in_redirects_to_dashboard(self):
        self.client.login(username="entry_student", password="pass12345")
        r = self.client.get(reverse("lms:index"))
        self.assertRedirects(r, reverse("lms:student_dashboard"), fetch_redirect_response=False)


class LMSTeachLearnRedirectTests(TestCase):
    """``/lms/teach/`` and ``/lms/learn/`` resolve; teach shows a page for lecturers."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username="tl_student",
            password="pass12345",
            role=User.Role.STUDENT,
        )
        self.lecturer = User.objects.create_user(
            username="tl_lecturer",
            password="pass12345",
            role=User.Role.LECTURER,
        )

    def test_teach_anonymous_redirects_to_login(self):
        r = self.client.get(reverse("lms:teach_index"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_teach_lecturer_sees_teaching_page(self):
        self.client.login(username="tl_lecturer", password="pass12345")
        r = self.client.get(reverse("lms:teach_index"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Courses you teach")

    def test_teach_student_goes_to_student_dashboard(self):
        self.client.login(username="tl_student", password="pass12345")
        r = self.client.get(reverse("lms:teach_index"))
        self.assertRedirects(r, reverse("lms:student_dashboard"), fetch_redirect_response=False)

    def test_lecturer_dashboard_typo_path_redirects(self):
        """``/lms/lecturer_dashboard`` is a common mistake for ``/lms/lecturer/``."""
        self.client.login(username="tl_lecturer", password="pass12345")
        r = self.client.get("/lms/lecturer_dashboard/")
        self.assertRedirects(
            r,
            reverse("lms:lecturer_dashboard"),
            fetch_redirect_response=False,
        )

    def test_learn_anonymous_redirects_to_login(self):
        r = self.client.get(reverse("lms:learn_index"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_learn_student_goes_to_student_dashboard(self):
        self.client.login(username="tl_student", password="pass12345")
        r = self.client.get(reverse("lms:learn_index"))
        self.assertRedirects(r, reverse("lms:student_dashboard"), fetch_redirect_response=False)

    def test_learn_lecturer_goes_to_lecturer_dashboard(self):
        self.client.login(username="tl_lecturer", password="pass12345")
        r = self.client.get(reverse("lms:learn_index"))
        self.assertRedirects(r, reverse("lms:lecturer_dashboard"), fetch_redirect_response=False)


class LecturerDashboardViewTests(TestCase):
    """``/lms/lecturer`` and ``/lms/lecturer/`` — auth, roles, and course list."""

    def setUp(self):
        self.client = Client()
        self.lecturer = User.objects.create_user(
            username="ld_lecturer",
            password="pass12345",
            role=User.Role.LECTURER,
        )
        self.staff = User.objects.create_user(
            username="ld_staff",
            password="pass12345",
            role=User.Role.STAFF,
        )
        self.student = User.objects.create_user(
            username="ld_student",
            password="pass12345",
            role=User.Role.STUDENT,
        )
        self.dept = Department.objects.create(name="LD Dept", slug="ld-dept", order=0)
        self.course = Course.objects.create(
            department=self.dept,
            name="LD Course",
            slug="ld-course",
            code="LD-101",
        )
        self.course.instructors.add(self.lecturer)

    def test_anonymous_redirects_to_login(self):
        r = self.client.get(reverse("lms:lecturer_dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_student_redirects_to_student_dashboard(self):
        self.client.login(username="ld_student", password="pass12345")
        r = self.client.get(reverse("lms:lecturer_dashboard"))
        self.assertRedirects(r, reverse("lms:student_dashboard"), fetch_redirect_response=False)

    def test_lecturer_sees_dashboard_200(self):
        self.client.login(username="ld_lecturer", password="pass12345")
        r = self.client.get(reverse("lms:lecturer_dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Courses you teach")
        self.assertContains(r, "LD-101")

    def test_staff_sees_assigned_courses(self):
        self.course.instructors.add(self.staff)
        self.client.login(username="ld_staff", password="pass12345")
        r = self.client.get(reverse("lms:lecturer_dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "LD-101")

    def test_path_without_trailing_slash_200(self):
        self.client.login(username="ld_lecturer", password="pass12345")
        r = self.client.get("/lms/lecturer")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "LD-101")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    def test_dashboard_shows_email_notifications_disabled_message(self):
        self.client.login(username="ld_lecturer", password="pass12345")
        r = self.client.get(reverse("lms:lecturer_dashboard"))
        self.assertContains(r, "Email notifications:")
        self.assertContains(r, "console mode")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST="smtp.example.com",
        EMAIL_HOST_USER="mailer@example.com",
        EMAIL_HOST_PASSWORD="secret",
    )
    def test_dashboard_shows_email_notifications_enabled_message(self):
        self.client.login(username="ld_lecturer", password="pass12345")
        r = self.client.get(reverse("lms:lecturer_dashboard"))
        self.assertContains(r, "Email notifications:")
        self.assertContains(r, "enabled and ready to deliver")

    def test_en_prefixed_url_redirects_to_unprefixed(self):
        """Default language has no /en/ prefix; /en/lms/... must not 404."""
        r = self.client.get("/en/lms/lecturer/")
        self.assertRedirects(
            r,
            "/lms/lecturer/",
            status_code=302,
            fetch_redirect_response=False,
        )


class LMSIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="Test Dept", slug="test-dept", order=0)
        self.course = Course.objects.create(
            department=self.dept,
            name="Test Course",
            slug="test-course",
            code="TC-101",
        )
        self.lecturer = User.objects.create_user(
            username="lecturer1",
            password="pass12345",
            role=User.Role.LECTURER,
        )
        self.student = User.objects.create_user(
            username="student1",
            password="pass12345",
            role=User.Role.STUDENT,
        )
        self.course.instructors.add(self.lecturer)
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Lesson 1",
            order=1,
            content="Hello",
            published=True,
        )
        Material.objects.create(
            course=self.course,
            lesson=None,
            title="Sample resource",
            resource_category=Material.ResourceCategory.LECTURE_NOTES,
            kind=Material.Kind.LINK,
            external_url="https://example.com/sample.pdf",
            order=0,
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Homework 1",
            description="Do the thing",
            published=True,
            max_score=10,
        )
        self.quiz = Quiz.objects.create(
            course=self.course,
            title="Quiz 1",
            published=True,
        )
        Enrollment.objects.create(user=self.student, course=self.course)

    def test_lecturer_course_200(self):
        self.client.login(username="lecturer1", password="pass12345")
        url = reverse("lms:lecturer_course", kwargs={"course_id": self.course.pk})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_student_course_200(self):
        self.client.login(username="student1", password="pass12345")
        url = reverse("lms:student_course", kwargs={"course_id": self.course.pk})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_student_assignment_200(self):
        self.client.login(username="student1", password="pass12345")
        url = reverse(
            "lms:student_assignment",
            kwargs={"course_id": self.course.pk, "assignment_id": self.assignment.pk},
        )
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_material_add_get_200(self):
        self.client.login(username="lecturer1", password="pass12345")
        url = reverse("lms:material_add", kwargs={"course_id": self.course.pk})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_quiz_create_get_200(self):
        self.client.login(username="lecturer1", password="pass12345")
        url = reverse("lms:quiz_create", kwargs={"course_id": self.course.pk})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_quiz_edit_get_200(self):
        self.client.login(username="lecturer1", password="pass12345")
        url = reverse(
            "lms:quiz_edit",
            kwargs={"course_id": self.course.pk, "quiz_id": self.quiz.pk},
        )
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.com",
)
class LMSNotificationEmailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="Mail Dept", slug="mail-dept", order=0)
        self.course = Course.objects.create(
            department=self.dept,
            name="Mail Course",
            slug="mail-course",
            code="ML-101",
        )
        self.lecturer = User.objects.create_user(
            username="mail_lecturer",
            password="pass12345",
            role=User.Role.LECTURER,
            email="lecturer@example.com",
        )
        self.student = User.objects.create_user(
            username="mail_student",
            password="pass12345",
            role=User.Role.STUDENT,
            email="student@example.com",
        )
        self.course.instructors.add(self.lecturer)
        Enrollment.objects.create(user=self.student, course=self.course)
        self.client.login(username="mail_lecturer", password="pass12345")

    def test_material_upload_sends_email_to_enrolled_students(self):
        response = self.client.post(
            reverse("lms:material_add", kwargs={"course_id": self.course.pk}),
            {
                "lesson": "",
                "resource_category": Material.ResourceCategory.LECTURE_NOTES,
                "title": "Week 1 notes",
                "kind": Material.Kind.LINK,
                "external_url": "https://example.com/w1.pdf",
                "order": 0,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("New material", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["student@example.com"])

    def test_published_assignment_sends_email(self):
        response = self.client.post(
            reverse("lms:assignment_create", kwargs={"course_id": self.course.pk}),
            {
                "title": "Assignment 1",
                "description": "Do task A",
                "due_at": "",
                "published": "on",
                "max_score": 100,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("New assignment", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["student@example.com"])

    def test_published_quiz_sends_email(self):
        response = self.client.post(
            reverse("lms:quiz_create", kwargs={"course_id": self.course.pk}),
            {
                "title": "Quiz 1",
                "description": "Chapters 1-2",
                "time_limit_minutes": 20,
                "pass_score": 50,
                "published": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("New quiz", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["student@example.com"])
