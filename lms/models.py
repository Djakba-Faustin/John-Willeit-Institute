import os

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        WITHDRAWN = "withdrawn", "Withdrawn"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "course"]]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user} → {self.course}"


class Lesson(models.Model):
    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)
    content = models.TextField(
        help_text="HTML allowed; staff should paste safe markup.",
        blank=True,
    )
    published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course", "order", "id"]

    def __str__(self):
        return self.title


class Material(models.Model):
    class Kind(models.TextChoices):
        FILE = "file", "File"
        LINK = "link", "External link"

    class ResourceCategory(models.TextChoices):
        LECTURE_NOTES = "lecture_notes", "Lecture notes"
        PRACTICAL_GUIDE = "practical_guide", "Practical guide"
        ACADEMIC_RESOURCE = "academic_resource", "Academic resource"
        OTHER = "other", "Other"

    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="materials",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="materials",
        null=True,
        blank=True,
        help_text="Leave empty for course-wide resources.",
    )
    title = models.CharField(max_length=255)
    resource_category = models.CharField(
        max_length=32,
        choices=ResourceCategory.choices,
        default=ResourceCategory.OTHER,
    )
    kind = models.CharField(
        max_length=10,
        choices=Kind.choices,
        default=Kind.FILE,
    )
    file = models.FileField(upload_to="materials/%Y/%m/", blank=True, null=True)
    external_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["course", "lesson", "order", "id"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.lesson_id:
            self.course = self.lesson.course
        if self.lesson_id and self.course_id and self.lesson.course_id != self.course_id:
            raise ValidationError("Lesson must belong to the same course as the material.")

    def save(self, *args, **kwargs):
        if self.lesson_id:
            self.course_id = self.lesson.course_id
        super().save(*args, **kwargs)

    @property
    def is_pdf(self):
        if not self.file:
            return False
        return os.path.basename(self.file.name).lower().endswith(".pdf")


class LessonCompletion(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="lesson_completions",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["enrollment", "lesson"]]


class Assignment(models.Model):
    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional deadline for students.",
    )
    published = models.BooleanField(default=True)
    max_score = models.PositiveSmallIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course", "-created_at"]

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )
    text = models.TextField(blank=True)
    file = models.FileField(
        upload_to="assignment_submissions/%Y/%m/",
        blank=True,
        null=True,
    )
    submitted_at = models.DateTimeField(
        auto_now=True,
        help_text="Updated each time the student saves their submission.",
    )
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="graded_assignment_submissions",
    )

    class Meta:
        unique_together = [["assignment", "user"]]
        ordering = ["-submitted_at"]

    @property
    def is_pdf(self):
        if not self.file:
            return False
        return os.path.basename(self.file.name).lower().endswith(".pdf")

    def __str__(self):
        return f"{self.user} → {self.assignment}"


class Quiz(models.Model):
    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_limit_minutes = models.PositiveSmallIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(240)],
    )
    pass_score = models.PositiveSmallIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage required to pass.",
    )
    published = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ["course", "id"]

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["quiz", "order", "id"]


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["question", "id"]


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-started_at"]

    def is_passed(self):
        if self.score_percent is None or self.quiz.pass_score is None:
            return False
        return float(self.score_percent) >= self.quiz.pass_score


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = [["attempt", "question"]]


class ForumThread(models.Model):
    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="forum_threads",
    )
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_threads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-pinned", "-created_at"]


class ForumPost(models.Model):
    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_posts",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
