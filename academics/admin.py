from django.contrib import admin

from .models import Course, Department


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CourseInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "department")
    list_filter = ("department",)
    search_fields = ("name", "code")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("instructors",)
