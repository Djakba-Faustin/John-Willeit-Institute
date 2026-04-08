from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("gallery/", views.gallery_list, name="gallery"),
    path("gallery/new/", views.gallery_post_create, name="gallery_new"),
    path("gallery/<int:post_id>/", views.gallery_detail, name="gallery_detail"),
    path("gallery/<int:post_id>/like/", views.gallery_toggle_like, name="gallery_like"),
    path(
        "gallery/<int:post_id>/comment/",
        views.gallery_add_comment,
        name="gallery_comment",
    ),
]
