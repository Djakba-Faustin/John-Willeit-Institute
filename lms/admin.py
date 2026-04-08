from django.contrib import admin

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


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 0
    fields = ("title", "resource_category", "kind", "file", "external_url", "order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "published")
    list_filter = ("course", "published")
    inlines = [MaterialInline]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order", "points")
    inlines = [ChoiceInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "published")
    inlines = [QuestionInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_at", "published", "max_score")
    list_filter = ("course", "published")


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "user", "submitted_at", "score")
    list_filter = ("assignment__course",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "enrolled_at")
    list_filter = ("status", "course")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score_percent", "started_at", "finished_at")


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "author", "created_at", "pinned")


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ("thread", "author", "created_at")


admin.site.register(LessonCompletion)
admin.site.register(QuizAnswer)
