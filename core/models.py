from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class GalleryPost(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    image = models.ImageField(upload_to="gallery/images/%Y/%m/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gallery_posts_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.media_type == self.MediaType.IMAGE and not self.image:
            raise ValidationError("Please upload an image for image posts.")
        if self.media_type == self.MediaType.VIDEO and not self.video_url:
            raise ValidationError("Please provide a video URL for video posts.")
        if self.media_type == self.MediaType.IMAGE and self.video_url:
            raise ValidationError("Video URL must be empty for image posts.")
        if self.media_type == self.MediaType.VIDEO and self.image:
            raise ValidationError("Image must be empty for video posts.")

    def get_absolute_url(self):
        return reverse("core:gallery_detail", kwargs={"post_id": self.pk})

    def __str__(self):
        return self.title


class GalleryComment(models.Model):
    post = models.ForeignKey(
        GalleryPost,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gallery_comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class GalleryLike(models.Model):
    post = models.ForeignKey(
        GalleryPost,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gallery_likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["post", "user"]]
