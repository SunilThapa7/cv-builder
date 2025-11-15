from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm
from cv_app.models import CV


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile(request):
    cv_count = CV.objects.filter(owner=request.user).count()
    context = {
        'user': request.user,
        'cv_count': cv_count
    }
    return render(request, 'accounts/profile.html', context)
