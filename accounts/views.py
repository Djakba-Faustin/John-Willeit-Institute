from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import InstituteRegistrationForm
from .models import User


class InstituteLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect("lms:index")
    if request.method == "POST":
        form = InstituteRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == User.Role.LECTURER:
                messages.success(
                    request,
                    _(
                        "Welcome — your lecturer account is ready. "
                        "An administrator must add you as an instructor on each course you teach."
                    ),
                )
            else:
                messages.success(
                    request,
                    _(
                        "Welcome — your student account is ready. "
                        "Browse programs and enroll in courses."
                    ),
                )
            return redirect("lms:index")
    else:
        form = InstituteRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})
