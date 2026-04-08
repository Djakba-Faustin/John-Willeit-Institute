import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def forwards_material_course(apps, schema_editor):
    Material = apps.get_model("lms", "Material")
    for m in Material.objects.all():
        m.course_id = m.lesson.course_id
        m.save(update_fields=["course_id"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0002_initial"),
        ("lms", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="course",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="materials",
                to="academics.course",
            ),
        ),
        migrations.AddField(
            model_name="material",
            name="resource_category",
            field=models.CharField(
                choices=[
                    ("lecture_notes", "Lecture notes"),
                    ("practical_guide", "Practical guide"),
                    ("academic_resource", "Academic resource"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=32,
            ),
        ),
        migrations.RunPython(forwards_material_course, noop),
        migrations.AlterField(
            model_name="material",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="materials",
                to="academics.course",
            ),
        ),
        migrations.AlterField(
            model_name="material",
            name="lesson",
            field=models.ForeignKey(
                blank=True,
                help_text="Leave empty for course-wide resources.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="materials",
                to="lms.lesson",
            ),
        ),
        migrations.AlterModelOptions(
            name="material",
            options={"ordering": ["course", "lesson", "order", "id"]},
        ),
        migrations.CreateModel(
            name="Assignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "due_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Optional deadline for students.",
                        null=True,
                    ),
                ),
                ("published", models.BooleanField(default=True)),
                ("max_score", models.PositiveSmallIntegerField(default=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="academics.course",
                    ),
                ),
            ],
            options={
                "ordering": ["course", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AssignmentSubmission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(blank=True)),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="assignment_submissions/%Y/%m/",
                    ),
                ),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=6,
                        null=True,
                    ),
                ),
                ("feedback", models.TextField(blank=True)),
                ("graded_at", models.DateTimeField(blank=True, null=True)),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="lms.assignment",
                    ),
                ),
                (
                    "graded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="graded_assignment_submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignment_submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-submitted_at"],
                "unique_together": {("assignment", "user")},
            },
        ),
    ]
