from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import GalleryComment, GalleryLike, GalleryPost

User = get_user_model()


class GalleryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.lecturer = User.objects.create_user(
            username="gallery_lecturer",
            password="pass12345",
            role=User.Role.LECTURER,
        )
        self.student = User.objects.create_user(
            username="gallery_student",
            password="pass12345",
            role=User.Role.STUDENT,
        )
        self.post = GalleryPost.objects.create(
            title="School clean-up day",
            body="Students and lecturers cleaned the campus.",
            media_type=GalleryPost.MediaType.VIDEO,
            video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            published=True,
            created_by=self.lecturer,
        )

    def test_gallery_list_200(self):
        r = self.client.get(reverse("core:gallery"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "School clean-up day")

    def test_lecturer_can_create_gallery_post(self):
        self.client.login(username="gallery_lecturer", password="pass12345")
        r = self.client.post(
            reverse("core:gallery_new"),
            {
                "title": "Sports day",
                "body": "Inter-class football competition.",
                "media_type": GalleryPost.MediaType.VIDEO,
                "video_url": "https://www.youtube.com/embed/abc123xyz",
                "published": "on",
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(GalleryPost.objects.filter(title="Sports day").exists())

    def test_student_cannot_create_gallery_post(self):
        self.client.login(username="gallery_student", password="pass12345")
        r = self.client.get(reverse("core:gallery_new"))
        self.assertEqual(r.status_code, 403)

    def test_authenticated_user_can_like_and_comment(self):
        self.client.login(username="gallery_student", password="pass12345")
        like_r = self.client.post(reverse("core:gallery_like", kwargs={"post_id": self.post.pk}))
        self.assertEqual(like_r.status_code, 302)
        self.assertTrue(
            GalleryLike.objects.filter(post=self.post, user=self.student).exists()
        )

        comment_r = self.client.post(
            reverse("core:gallery_comment", kwargs={"post_id": self.post.pk}),
            {"body": "Great activity!"},
        )
        self.assertEqual(comment_r.status_code, 302)
        self.assertTrue(
            GalleryComment.objects.filter(post=self.post, user=self.student).exists()
        )
