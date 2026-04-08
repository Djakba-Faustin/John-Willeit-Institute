from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import (
    Assignment,
    AssignmentSubmission,
    ForumPost,
    ForumThread,
    Lesson,
    Material,
    Quiz,
)


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ("title", "order", "content", "published")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "content": forms.Textarea(attrs={"rows": 14, "class": "form-control"}),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = (
            "lesson",
            "resource_category",
            "title",
            "kind",
            "file",
            "external_url",
            "order",
        )
        widgets = {
            "lesson": forms.Select(attrs={"class": "form-select"}),
            "resource_category": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "kind": forms.Select(attrs={"class": "form-select"}),
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,application/pdf",
                }
            ),
            "external_url": forms.URLInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].help_text = _(
            "Upload a PDF file (lecture notes, guides, or other documents). "
            "Use “External link” for non-PDF resources."
        )
        if course is not None:
            self.fields["lesson"].queryset = Lesson.objects.filter(course=course).order_by(
                "order", "id"
            )
            self.fields["lesson"].empty_label = "— Course-wide (not tied to a lesson) —"
            self.fields["lesson"].required = False

    def clean(self):
        data = super().clean()
        kind = data.get("kind")
        f = data.get("file")
        url = (data.get("external_url") or "").strip()
        if kind == Material.Kind.FILE:
            if not f and not (self.instance.pk and self.instance.file):
                raise ValidationError(
                    "Upload a file, or switch the type to “External link”."
                )
            if f and not f.name.lower().endswith(".pdf"):
                raise ValidationError("Uploaded files must be in PDF format.")
        elif kind == Material.Kind.LINK:
            if not url:
                raise ValidationError("Enter a URL for external links.")
        return data


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ("title", "description", "due_at", "published", "max_score")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "due_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "max_score": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["due_at"].required = False
        self.fields["due_at"].help_text = _(
            "Optional. Students see this due date on their assignment page (with date and time)."
        )
        f = self.fields["due_at"]
        f.widget.format = "%Y-%m-%dT%H:%M"
        f.input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ("text", "file")
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Type your answer here…",
                }
            ),
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,application/pdf",
                }
            ),
        }
        labels = {
            "text": _("Written response"),
            "file": _("Upload your work (PDF)"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].required = False
        self.fields["file"].required = False
        self.fields["file"].help_text = _(
            "Submit your assignment as a PDF. You can add text above and/or attach one PDF."
        )

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if f and not f.name.lower().endswith(".pdf"):
            raise ValidationError("Please upload a PDF file (.pdf).")
        return f


class GradeSubmissionForm(forms.Form):
    score = forms.DecimalField(
        min_value=0,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = (
            "title",
            "description",
            "time_limit_minutes",
            "pass_score",
            "published",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "time_limit_minutes": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 240}
            ),
            "pass_score": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100}
            ),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class QuizQuestionForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Question",
    )
    points = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )
    choice_1 = forms.CharField(
        label="Choice A",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    choice_2 = forms.CharField(
        label="Choice B",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    choice_3 = forms.CharField(
        label="Choice C",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    choice_4 = forms.CharField(
        label="Choice D",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    correct = forms.ChoiceField(
        label="Correct answer",
        choices=[("1", "A"), ("2", "B"), ("3", "C"), ("4", "D")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean(self):
        data = super().clean()
        cidx = data.get("correct")
        if cidx:
            key = f"choice_{cidx}"
            if not (data.get(key) or "").strip():
                raise ValidationError(
                    "Fill in the answer choice that you marked as correct, or change the correct answer."
                )
        return data


class ForumThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ("title",)
        widgets = {"title": forms.TextInput(attrs={"class": "form-control"})}


class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 5, "class": "form-control"})}
