from django.contrib.staticfiles import finders
from django.templatetags.static import static


def site_branding(request):
    branding_logo = None
    if finders.find("images/logo.png"):
        branding_logo = static("images/logo.png")
    return {
        "SITE_NAME": "John Willeit Higher Institute of Nkongsamba",
        "SITE_NAME_FULL": (
            "John Willeit's Higher Institute of Health, Management and Technology"
        ),
        "SITE_TAGLINE": "Quality Education and Humanising Health Care",
        "SITE_TAGLINE_FR": "Éducation de Qualité et les soins de Santé Humanisant",
        "branding_logo": branding_logo,
    }
