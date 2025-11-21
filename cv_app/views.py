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
            },
            {
                'name': 'Advanced',
                'slug': 'advanced',
                'description': 'Distinct, ATS-friendly with optional photo',
                'preview': 'img/template_previews/advanced.png'
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
        form = CVForm(request.POST, request.FILES)
        exp_fs = ExperienceFormSet(request.POST, prefix='exp')
        edu_fs = EducationFormSet(request.POST, prefix='edu')
        proj_fs = ProjectFormSet(request.POST, prefix='proj')
        # Determine selected template for conditional UI
        is_advanced_template = False
        tmpl_id = (request.POST.get('template') or '').strip()
        if tmpl_id:
            try:
                sel = CVTemplate.objects.get(id=tmpl_id)
                is_advanced_template = (sel.slug == 'advanced')
            except CVTemplate.DoesNotExist:
                is_advanced_template = False

        if form.is_valid() and exp_fs.is_valid() and edu_fs.is_valid() and proj_fs.is_valid():
            # Build JSON payloads from non-empty rows
            def non_empty(forms, keys):
                items = []
                for f in forms:
                    if getattr(f, 'cleaned_data', None) and not f.cleaned_data.get('DELETE'):
                        if any(f.cleaned_data.get(k, '').strip() for k in keys):
                            items.append({k: f.cleaned_data.get(k, '').strip() for k in keys})
                return items
            # Build experience with website and responsibilities as list
            exp_items = []
            for f in exp_fs.forms:
                cd = getattr(f, 'cleaned_data', {}) or {}
                if cd and not cd.get('DELETE'):
                    if any((cd.get('company') or cd.get('position') or cd.get('duration') or cd.get('website') or cd.get('description') or cd.get('responsibilities'))):
                        resp_raw = cd.get('responsibilities') or ''
                        responsibilities = [ln.strip() for ln in resp_raw.splitlines() if ln.strip()]
                        exp_items.append({
                            'company': (cd.get('company') or '').strip(),
                            'position': (cd.get('position') or '').strip(),
                            'duration': (cd.get('duration') or '').strip(),
                            'website': (cd.get('website') or '').strip(),
                            'responsibilities': responsibilities,
                            'description': (cd.get('description') or '').strip(),
                        })
            edu_items = non_empty(edu_fs.forms, ['institution', 'degree', 'duration', 'status'])
            proj_items = non_empty(proj_fs.forms, ['name', 'description', 'technologies', 'status'])

            form.instance.experience = json.dumps(exp_items, ensure_ascii=False)
            form.instance.education = json.dumps(edu_items, ensure_ascii=False)
            form.instance.projects = json.dumps(proj_items, ensure_ascii=False)

            cv = form.save(commit=False)
            cv.owner = request.user
            cv.save()
            messages.success(request, 'CV created successfully!')
            return redirect('dashboard')
    else:
        template_slug = request.GET.get('template')
        initial = {}
        is_advanced_template = False
        if template_slug:
            try:
                tmpl = CVTemplate.objects.get(slug=template_slug, active=True)
                initial = {'template': tmpl}
                is_advanced_template = (tmpl.slug == 'advanced')
            except CVTemplate.DoesNotExist:
                initial = {}
        else:
            # No template chosen yet: show selection page first
            templates = CVTemplate.objects.filter(active=True).order_by('name')
            return render(request, 'cv/select_template.html', {'templates': templates})
        form = CVForm(initial=initial)
        exp_fs = ExperienceFormSet(prefix='exp')
        edu_fs = EducationFormSet(prefix='edu')
        proj_fs = ProjectFormSet(prefix='proj')

    return render(request, 'cv/create.html', {
        'form': form,
        'exp_formset': exp_fs,
        'edu_formset': edu_fs,
        'proj_formset': proj_fs,
        'is_advanced_template': is_advanced_template,
    })


@login_required
def cv_edit(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, owner=request.user)
    ExperienceFormSet = formset_factory(ExperienceItemForm, extra=1, can_delete=True)
    EducationFormSet = formset_factory(EducationItemForm, extra=1, can_delete=True)
    ProjectFormSet = formset_factory(ProjectItemForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = CVForm(request.POST, request.FILES, instance=cv)
        exp_fs = ExperienceFormSet(request.POST, prefix='exp')
        edu_fs = EducationFormSet(request.POST, prefix='edu')
        proj_fs = ProjectFormSet(request.POST, prefix='proj')
        # Determine selected template from POST
        is_advanced_template = False
        tmpl_id = (request.POST.get('template') or '').strip()
        if tmpl_id:
            try:
                sel = CVTemplate.objects.get(id=tmpl_id)
                is_advanced_template = (sel.slug == 'advanced')
            except CVTemplate.DoesNotExist:
                is_advanced_template = False

        if form.is_valid() and exp_fs.is_valid() and edu_fs.is_valid() and proj_fs.is_valid():
            def non_empty(forms, keys):
                items = []
                for f in forms:
                    if getattr(f, 'cleaned_data', None) and not f.cleaned_data.get('DELETE'):
                        if any(f.cleaned_data.get(k, '').strip() for k in keys):
                            items.append({k: f.cleaned_data.get(k, '').strip() for k in keys})
                return items
            # Build experience with website and responsibilities as list
            exp_items = []
            for f in exp_fs.forms:
                cd = getattr(f, 'cleaned_data', {}) or {}
                if cd and not cd.get('DELETE'):
                    if any((cd.get('company') or cd.get('position') or cd.get('duration') or cd.get('website') or cd.get('description') or cd.get('responsibilities'))):
                        resp_raw = cd.get('responsibilities') or ''
                        responsibilities = [ln.strip() for ln in resp_raw.splitlines() if ln.strip()]
                        exp_items.append({
                            'company': (cd.get('company') or '').strip(),
                            'position': (cd.get('position') or '').strip(),
                            'duration': (cd.get('duration') or '').strip(),
                            'website': (cd.get('website') or '').strip(),
                            'responsibilities': responsibilities,
                            'description': (cd.get('description') or '').strip(),
                        })
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
        is_advanced_template = (cv.template.slug == 'advanced') if cv.template else False
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

        # Normalize keys to match form fields and keep all fields
        exp_initial = [{
            'company': item.get('company', ''),
            'position': item.get('position', ''),
            'duration': item.get('duration', ''),
            'website': item.get('website', ''),
            # responsibilities stored as list -> show as newline-separated in textarea
            'responsibilities': '\n'.join(item.get('responsibilities', []) if isinstance(item.get('responsibilities'), list) else [item.get('responsibilities', '')]).strip(),
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
        'is_advanced_template': is_advanced_template,
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
    # Allow saving the selected preview template or saving as a new CV
    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()
        sel_slug = (request.POST.get('template') or '').strip()
        try:
            sel_template = CVTemplate.objects.get(slug=sel_slug, active=True) if sel_slug else cv.template
        except CVTemplate.DoesNotExist:
            sel_template = cv.template
        if action == 'save_template':
            cv.template = sel_template
            cv.save(update_fields=['template', 'updated_at'])
            messages.success(request, 'Template updated for this CV.')
            return redirect('cv_preview', cv_id=cv.id)
        elif action == 'save_as_new':
            new_cv = CV(
                owner=request.user,
                title=f"{cv.title} (Copy)",
                template=sel_template,
                full_name=cv.full_name,
                job_title=cv.job_title,
                email=cv.email,
                phone=cv.phone,
                location=cv.location,
                links=cv.links,
                summary=cv.summary,
                skills=cv.skills,
                experience=cv.experience,
                education=cv.education,
                projects=cv.projects,
                photo=cv.photo,
            )
            new_cv.save()
            messages.success(request, 'Saved as a new CV with the selected template.')
            return redirect('cv_preview', cv_id=new_cv.id)

    # Optional override to preview as another template without saving (GET)
    override_slug = (request.GET.get('template') or '').strip()
    print_compact = (request.GET.get('compact') == '1')
    if override_slug:
        try:
            tmpl = CVTemplate.objects.get(slug=override_slug, active=True)
            template_slug = tmpl.slug
        except CVTemplate.DoesNotExist:
            template_slug = cv.template.slug
    else:
        template_slug = cv.template.slug

    template_name = f'cv/preview_{template_slug}.html'
    templates = CVTemplate.objects.filter(active=True).order_by('name')
    return render(request, template_name, {
        'cv': cv,
        'templates': templates,
        'current_template_slug': template_slug,
        'print_compact': print_compact,
    })

# Create your views here.
