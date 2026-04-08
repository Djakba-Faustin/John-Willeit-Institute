from django.contrib import admin

from .models import GalleryComment, GalleryLike, GalleryPost


@admin.register(GalleryPost)
class GalleryPostAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "published", "created_by", "created_at")
    list_filter = ("media_type", "published", "created_at")
    search_fields = ("title", "body")


@admin.register(GalleryComment)
class GalleryCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    search_fields = ("post__title", "user__username", "body")


@admin.register(GalleryLike)
class GalleryLikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
