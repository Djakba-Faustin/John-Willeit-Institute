from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class InstituteRegistrationForm(UserCreationForm):
    """Self-service sign-up for students and lecturers (staff accounts remain admin-only)."""

    role = forms.ChoiceField(
        choices=[
            (
                User.Role.STUDENT,
                _("Student — enroll in courses, access materials, and submit work"),
            ),
            (
                User.Role.LECTURER,
                _("Lecturer — manage courses once an administrator assigns you as instructor"),
            ),
        ],
        initial=User.Role.STUDENT,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label=_("I am registering as"),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "role",
            "username",
            "first_name",
            "last_name",
            "email",
        )
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user
