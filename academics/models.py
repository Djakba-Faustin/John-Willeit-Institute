from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Department(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=280)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:280]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("academics:department_detail", kwargs={"slug": self.slug})


class Course(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280)
    code = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    instructors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="courses_teaching",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["department", "name"]
        unique_together = [["department", "slug"]]

    def __str__(self):
        return f"{self.code} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:280]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "academics:course_detail",
            kwargs={"dept_slug": self.department.slug, "slug": self.slug},
        )
