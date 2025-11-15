from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import CV, CVTemplate
from .forms import CVForm


def home(request):
    context = {
        'templates': [
            {
                'name': 'Classic',
                'slug': 'classic',
                'description': 'Conservative, two-column layout',
                'preview': 'img/template_previews/classic.png'
            },
            {
                'name': 'Modern',
                'slug': 'modern',
                'description': 'Color accents, clean headings',
                'preview': 'img/template_previews/modern.png'
            },
            {
                'name': 'Minimal',
                'slug': 'minimal',
                'description': 'Single-column, ATS-friendly',
                'preview': 'img/template_previews/minimal.png'
            }
        ]
    }
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    cvs = CV.objects.filter(owner=request.user).order_by('-updated_at')
    context = {'cvs': cvs}
    return render(request, 'dashboard.html', context)


@login_required
def cv_create(request):
    if request.method == 'POST':
        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.owner = request.user
            cv.save()
            messages.success(request, 'CV created successfully!')
            return redirect('dashboard')
    else:
        template_slug = request.GET.get('template')
        if template_slug:
            try:
                tmpl = CVTemplate.objects.get(slug=template_slug, active=True)
                form = CVForm(initial={'template': tmpl})
            except CVTemplate.DoesNotExist:
                form = CVForm()
        else:
            form = CVForm()
    return render(request, 'cv/create.html', {'form': form})


@login_required
def cv_edit(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, owner=request.user)
    if request.method == 'POST':
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            messages.success(request, 'CV updated successfully!')
            return redirect('dashboard')
    else:
        form = CVForm(instance=cv)
    return render(request, 'cv/edit.html', {'form': form, 'cv': cv})


@login_required
def cv_delete(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, owner=request.user)
    if request.method == 'POST':
        cv.delete()
        messages.success(request, 'CV deleted successfully!')
        return redirect('dashboard')
    return render(request, 'cv/delete_confirm.html', {'cv': cv})


@login_required
def cv_preview(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, owner=request.user)
    template_name = f'cv/preview_{cv.template.slug}.html'
    return render(request, template_name, {'cv': cv})

# Create your views here.
