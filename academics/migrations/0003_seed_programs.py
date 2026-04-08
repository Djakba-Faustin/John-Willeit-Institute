# Programs and courses (see Rose.txt / institute catalog).

from django.db import migrations
from django.utils.text import slugify

SEED_SLUGS = frozenset(
    {
        "health-sciences-programs",
        "technology-programs",
        "management-business-programs",
        "professional-certification-programs",
        "language-programs",
    }
)


def seed_programs(apps, schema_editor):
    Department = apps.get_model("academics", "Department")
    Course = apps.get_model("academics", "Course")

    programs = [
        {
            "name": "Health Sciences Programs",
            "order": 10,
            "description": "Nursing, midwifery, medical laboratory technology, and related health professions.",
            "courses": [
                ("Nursing", "HS-NUR-101"),
                ("Midwifery", "HS-MID-102"),
                ("Medical Laboratory Technology", "HS-MLT-103"),
            ],
        },
        {
            "name": "Technology Programs",
            "order": 20,
            "description": "Software engineering, networking, systems administration, and web development.",
            "courses": [
                ("Software Engineering", "TECH-SE-201"),
                ("Networking & System Administration", "TECH-NSA-202"),
                ("Web Development", "TECH-WD-203"),
            ],
        },
        {
            "name": "Management & Business Programs",
            "order": 30,
            "description": "Accounting, banking, finance, marketing, and business administration.",
            "courses": [
                ("Accounting", "MB-ACC-301"),
                ("Banking & Finance", "MB-BF-302"),
                ("Marketing & Business Administration", "MB-MBA-303"),
            ],
        },
        {
            "name": "Professional Certification Programs",
            "order": 40,
            "description": "Assistant nursing, laboratory, pharmacy, and professional secretary certifications.",
            "courses": [
                ("Assistant Nursing", "CERT-AN-401"),
                ("Assistant Laboratory Technician", "CERT-ALT-402"),
                ("Assistant Pharmacist", "CERT-AP-403"),
                ("Professional Secretary", "CERT-PS-404"),
            ],
        },
        {
            "name": "Language Programs",
            "order": 50,
            "description": "Intensive English short courses.",
            "courses": [
                ("Intensive English (3 Months)", "LANG-IE3-501"),
                ("Intensive English (6 Months)", "LANG-IE6-502"),
            ],
        },
    ]

    for prog in programs:
        dslug = slugify(prog["name"])[:280]
        dept, _ = Department.objects.update_or_create(
            slug=dslug,
            defaults={
                "name": prog["name"],
                "order": prog["order"],
                "description": prog["description"],
            },
        )
        for course_name, code in prog["courses"]:
            cslug = slugify(course_name)[:280]
            Course.objects.update_or_create(
                department=dept,
                slug=cslug,
                defaults={
                    "name": course_name,
                    "code": code,
                    "description": "",
                },
            )


def unseed_programs(apps, schema_editor):
    Department = apps.get_model("academics", "Department")
    Department.objects.filter(slug__in=SEED_SLUGS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(seed_programs, unseed_programs),
    ]
