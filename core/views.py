from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from .forms import GalleryCommentForm, GalleryPostForm
from .models import GalleryComment, GalleryLike, GalleryPost


class HomeView(TemplateView):
    template_name = "core/home.html"


class AboutView(TemplateView):
    template_name = "core/about.html"


def _can_publish_gallery_post(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return getattr(user, "role", None) in ("lecturer", "staff")


def gallery_list(request):
    posts = (
        GalleryPost.objects.filter(published=True)
        .select_related("created_by")
        .prefetch_related("likes", "comments__user")
    )
    user_liked_ids = set()
    if request.user.is_authenticated:
        user_liked_ids = set(
            GalleryLike.objects.filter(user=request.user, post__in=posts).values_list(
                "post_id", flat=True
            )
        )
    return render(
        request,
        "core/gallery_list.html",
        {
            "posts": posts,
            "user_liked_ids": user_liked_ids,
            "can_publish": _can_publish_gallery_post(request.user),
        },
    )


def gallery_detail(request, post_id):
    post = get_object_or_404(
        GalleryPost.objects.select_related("created_by").prefetch_related("comments__user"),
        pk=post_id,
        published=True,
    )
    comments = post.comments.select_related("user")
    user_liked = False
    if request.user.is_authenticated:
        user_liked = GalleryLike.objects.filter(post=post, user=request.user).exists()
    return render(
        request,
        "core/gallery_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": GalleryCommentForm(),
            "user_liked": user_liked,
            "can_publish": _can_publish_gallery_post(request.user),
        },
    )


@login_required
def gallery_post_create(request):
    if not _can_publish_gallery_post(request.user):
        return HttpResponseForbidden()
    if request.method == "POST":
        form = GalleryPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()
            messages.success(request, "Gallery post published.")
            return redirect("core:gallery_detail", post_id=post.pk)
    else:
        form = GalleryPostForm()
    return render(request, "core/gallery_form.html", {"form": form})


@login_required
def gallery_toggle_like(request, post_id):
    post = get_object_or_404(GalleryPost, pk=post_id, published=True)
    obj, created = GalleryLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        obj.delete()
    return redirect("core:gallery_detail", post_id=post.pk)


@login_required
def gallery_add_comment(request, post_id):
    post = get_object_or_404(GalleryPost, pk=post_id, published=True)
    form = GalleryCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Comment cannot be empty.")
    return redirect("core:gallery_detail", post_id=post.pk)
