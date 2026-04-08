from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import RedirectView


def _redirect_en_prefix_to_unprefixed(request, path=""):
    """
    With prefix_default_language=False, English URLs live at /lms/... not /en/lms/...
    Browsers, bookmarks, and docs often use /en/... — forward them so those links work.
    """
    if not path:
        return redirect("/")
    return redirect("/" + path)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("en/", RedirectView.as_view(url="/", permanent=False)),
    path("en/<path:path>", _redirect_en_prefix_to_unprefixed),
]

urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("academics/", include("academics.urls")),
    path("lms/", include("lms.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "JW Higher Institute — LMS"
admin.site.site_title = "LMS Admin"
