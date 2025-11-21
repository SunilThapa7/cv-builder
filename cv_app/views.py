from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import formset_factory
import json

from .models import CV, CVTemplate
from .forms import CVForm, ExperienceItemForm, EducationItemForm, ProjectItemForm


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
    ExperienceFormSet = formset_factory(ExperienceItemForm, extra=1, can_delete=True)
    EducationFormSet = formset_factory(EducationItemForm, extra=1, can_delete=True)
    ProjectFormSet = formset_factory(ProjectItemForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = CVForm(request.POST)
        exp_fs = ExperienceFormSet(request.POST, prefix='exp')
        edu_fs = EducationFormSet(request.POST, prefix='edu')
        proj_fs = ProjectFormSet(request.POST, prefix='proj')

        if form.is_valid() and exp_fs.is_valid() and edu_fs.is_valid() and proj_fs.is_valid():
            # Build JSON payloads from non-empty rows
            def non_empty(forms, keys):
                items = []
                for f in forms:
                    if getattr(f, 'cleaned_data', None) and not f.cleaned_data.get('DELETE'):
                        if any(f.cleaned_data.get(k, '').strip() for k in keys):
                            items.append({k: f.cleaned_data.get(k, '').strip() for k in keys})
                return items

            exp_items = non_empty(exp_fs.forms, ['company', 'position', 'duration', 'description'])
            edu_items = non_empty(edu_fs.forms, ['institution', 'degree', 'duration', 'status'])
            proj_items = non_empty(proj_fs.forms, ['name', 'description', 'technologies', 'status'])

            form.instance.experience = json.dumps(exp_items, ensure_ascii=False)
            form.instance.education = json.dumps(edu_items, ensure_ascii=False)
            form.instance.projects = json.dumps(proj_items, ensure_ascii=False)

n            cv = form.save(commit=False)
            cv.owner = request.user
            cv.save()
            messages.success(request, 'CV created successfully!')
            return redirect('dashboard')
    else:
        template_slug = request.GET.get('template')
        initial = {}
        if template_slug:
            try:
                tmpl = CVTemplate.objects.get(slug=template_slug, active=True)
                initial = {'template': tmpl}
            except CVTemplate.DoesNotExist:
                initial = {}
        form = CVForm(initial=initial)
        exp_fs = ExperienceFormSet(prefix='exp')
        edu_fs = EducationFormSet(prefix='edu')
        proj_fs = ProjectFormSet(prefix='proj')

    return render(request, 'cv/create.html', {
        'form': form,
        'exp_formset': exp_fs,
        'edu_formset': edu_fs,
        'proj_formset': proj_fs,
    })


@login_required
def cv_edit(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, owner=request.user)
    ExperienceFormSet = formset_factory(ExperienceItemForm, extra=1, can_delete=True)
    EducationFormSet = formset_factory(EducationItemForm, extra=1, can_delete=True)
    ProjectFormSet = formset_factory(ProjectItemForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = CVForm(request.POST, instance=cv)
        exp_fs = ExperienceFormSet(request.POST, prefix='exp')
        edu_fs = EducationFormSet(request.POST, prefix='edu')
        proj_fs = ProjectFormSet(request.POST, prefix='proj')

        if form.is_valid() and exp_fs.is_valid() and edu_fs.is_valid() and proj_fs.is_valid():
            def non_empty(forms, keys):
                items = []
                for f in forms:
                    if getattr(f, 'cleaned_data', None) and not f.cleaned_data.get('DELETE'):
                        if any(f.cleaned_data.get(k, '').strip() for k in keys):
                            items.append({k: f.cleaned_data.get(k, '').strip() for k in keys})
                return items

            exp_items = non_empty(exp_fs.forms, ['company', 'position', 'duration', 'description'])
            edu_items = non_empty(edu_fs.forms, ['institution', 'degree', 'duration', 'status'])
            proj_items = non_empty(proj_fs.forms, ['name', 'description', 'technologies', 'status'])

            form.instance.experience = json.dumps(exp_items, ensure_ascii=False)
            form.instance.education = json.dumps(edu_items, ensure_ascii=False)
            form.instance.projects = json.dumps(proj_items, ensure_ascii=False)

            form.save()
            messages.success(request, 'CV updated successfully!')
            return redirect('dashboard')
    else:
        form = CVForm(instance=cv)
        try:
            exp_initial = json.loads(cv.experience) if cv.experience else []
        except json.JSONDecodeError:
            exp_initial = []
        try:
            edu_initial = json.loads(cv.education) if cv.education else []
        except json.JSONDecodeError:
            edu_initial = []
        try:
            proj_initial = json.loads(cv.projects) if cv.projects else []
        except json.JSONDecodeError:
            proj_initial = []

        # Normalize keys to match form fields
        exp_initial = [{
            'company': item.get('company', ''),
            'position': item.get('position', ''),
            'duration': item.get('duration', ''),
            'description': item.get('description', ''),
        } for item in exp_initial]

        edu_initial = [{
            'institution': item.get('institution', ''),
            'degree': item.get('degree', ''),
            'duration': item.get('duration', item.get('year', '')),
            'status': item.get('status', ''),
        } for item in edu_initial]

        proj_initial = [{
            'name': item.get('name', ''),
            'description': item.get('description', ''),
            'technologies': item.get('technologies', ''),
            'status': item.get('status', ''),
        } for item in proj_initial]

        exp_fs = ExperienceFormSet(initial=exp_initial or [{}], prefix='exp')
        edu_fs = EducationFormSet(initial=edu_initial or [{}], prefix='edu')
        proj_fs = ProjectFormSet(initial=proj_initial or [{}], prefix='proj')

    return render(request, 'cv/edit.html', {
        'form': form,
        'cv': cv,
        'exp_formset': exp_fs,
        'edu_formset': edu_fs,
        'proj_formset': proj_fs,
    })


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
