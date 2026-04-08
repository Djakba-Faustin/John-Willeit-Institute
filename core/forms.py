from django import forms

from .models import GalleryComment, GalleryPost


class GalleryPostForm(forms.ModelForm):
    class Meta:
        model = GalleryPost
        fields = ("title", "body", "media_type", "image", "video_url", "published")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "media_type": forms.Select(attrs={"class": "form-select"}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "video_url": forms.URLInput(attrs={"class": "form-control"}),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class GalleryCommentForm(forms.ModelForm):
    class Meta:
        model = GalleryComment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write your comment...",
                }
            )
        }
