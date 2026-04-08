from django.core.management.base import BaseCommand
from django.utils.text import slugify

from academics.models import Course, Department


# Data from project brief (Rose.txt) — departments and courses
STRUCTURE = [
    {
        "name": "Health Sciences Programs",
        "order": 1,
        "description": "Clinical and allied health training aligned with national standards.",
        "courses": [
            ("Nursing", "HS-NUR"),
            ("Midwifery", "HS-MID"),
            ("Medical Laboratory Technology", "HS-MLT"),
        ],
    },
    {
        "name": "Technology Programs",
        "order": 2,
        "description": "Software, networks, and modern web technologies.",
        "courses": [
            ("Software Engineering", "TECH-SE"),
            ("Networking & System Administration", "TECH-NSA"),
            ("Web Development", "TECH-WD"),
        ],
    },
    {
        "name": "Management & Business Programs",
        "order": 3,
        "description": "Business administration, finance, and marketing.",
        "courses": [
            ("Accounting", "MB-ACC"),
            ("Banking & Finance", "MB-BF"),
            ("Marketing & Business Administration", "MB-MBA"),
        ],
    },
    {
        "name": "Professional Certification Programs",
        "order": 4,
        "description": "Short professional pathways and assistant-level certifications.",
        "courses": [
            ("Assistant Nursing", "PC-AN"),
            ("Assistant Laboratory Technician", "PC-ALT"),
            ("Assistant Pharmacist", "PC-AP"),
            ("Professional Secretary", "PC-PS"),
        ],
    },
    {
        "name": "Language Programs",
        "order": 5,
        "description": "Intensive English language tracks.",
        "courses": [
            ("Intensive English (3 Months)", "LANG-IE3"),
            ("Intensive English (6 Months)", "LANG-IE6"),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed departments and courses for John Willeit Higher Institute (Nkongsamba)."

    def handle(self, *args, **options):
        for block in STRUCTURE:
            dept_slug = slugify(block["name"])[:280]
            dept, created = Department.objects.update_or_create(
                slug=dept_slug,
                defaults={
                    "name": block["name"],
                    "order": block["order"],
                    "description": block["description"],
                },
            )
            self.stdout.write(
                f"Department {'created' if created else 'updated'}: {dept.name}"
            )
            for title, code in block["courses"]:
                cslug = slugify(title)[:280]
                course, c_created = Course.objects.update_or_create(
                    department=dept,
                    slug=cslug,
                    defaults={
                        "name": title,
                        "code": code,
                        "description": "",
                    },
                )
                self.stdout.write(
                    f"  Course {'created' if c_created else 'updated'}: {course.code} {course.name}"
                )
        self.stdout.write(self.style.SUCCESS("Done."))
