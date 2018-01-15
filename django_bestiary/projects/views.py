import functools
import json
import os

from datetime import datetime
from time import time

from django.http import HttpResponse
from django.template import loader

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from projects.bestiary_export import fetch_projects

from django import shortcuts
from django.http import Http404

from projects.bestiary_import import load_projects
from projects.models import Ecosystem, Project, Repository, RepositoryView

from . import forms


def index(request):

    template = loader.get_template('projects/project.html')
    project = 'grimoire'  # debug value just during testing
    if (request.GET.get('project')):
        project = request.GET.get('project')
    context = find_project_repository_views(project)
    context.update(find_projects())
    context.update(find_project_data_sources(project))
    context['project_selected'] = project
    render_index = template.render(context, request)
    return HttpResponse(render_index)


class EditorState():

    def __init__(self, eco_name=None, projects=[], data_sources=[],
                 repository_views=[]):
        self.eco_name = eco_name
        self.projects = projects
        self.data_sources = data_sources
        self.repository_views = repository_views

    def is_empty(self):
        return not (self.eco_name or self.projects or self.data_sources or
                    self.repository_views)

    def initial_state(self):
        """ State to be filled in the forms so it is propagated

        The state needs to be serialized so it can be used in
        forms fields.
        """
        initial = {
            'eco_name_state': self.eco_name,
            'projects_state': ";".join(self.projects),
            'data_sources_state': ";".join(self.data_sources),
            "repository_views_state": ";".join([str(repo_view_id) for repo_view_id in self.repository_views])
        }

        return initial


def perfdata(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        task_init = time()
        data = func(*args, **kwargs)
        print("%s: %0.3f sec" % (func, time() - task_init))
        return data
    return decorator


@perfdata
def build_forms_context(state=None):
    """ Get all forms to be shown in the editor """
    eco_form = forms.EcosystemForm(state=state)
    projects_form = forms.ProjectsForm(state=state)
    project_form = forms.ProjectForm(state=state)
    project_remove_form = None
    data_sources_form = forms.DataSourcesForm(state=state)
    repository_views_form = forms.RepositoryViewsForm(state=state)
    repository_view_form = forms.RepositoryViewForm(state=state)

    if state:
        eco_form.initial['name'] = state.eco_name
        if state.projects:
            projects_form.initial['name'] = state.projects[0]
            project_remove_form = forms.ProjectForm(state=state)
            project_remove_form.initial['project_name'] = state.projects[0]
        if state.data_sources:
            data_sources_form.initial['name'] = state.data_sources[0]

    context = {"ecosystem_form": eco_form,
               "projects_form": projects_form,
               "project_form": project_form,
               "project_remove_form": project_remove_form,
               "data_sources_form": data_sources_form,
               "repository_views_form": repository_views_form,
               "repository_view_form": repository_view_form
               }
    return context


def update_repository_view(request):
    if request.method == 'POST':
        form = forms.RepositoryViewForm(request.POST)
        if form.is_valid():
            repository_view_id = form.cleaned_data['repository_view_id']
            repository = form.cleaned_data['repository']
            params = form.cleaned_data['params']
            filters = form.cleaned_data['filters']
            repository_view_orm = RepositoryView.objects.get(id=repository_view_id)
            repository_view_orm.repo = Repository.objects.get(name=repository)
            repository_view_orm.params = params
            # TODO: filters not yet in the data models
            repository_view_orm.save()
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(repository_views=[repository_view_id])))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def edit_repository_view(request):
    if request.method == 'POST':
        form = forms.RepositoryViewsForm(request.POST)
        if form.is_valid():
            repository_view_id = int(form.cleaned_data['id'])
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(repository_views=[repository_view_id])))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def edit_data_source(request):
    if request.method == 'POST':
        form = forms.DataSourcesForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            projects_state = form.cleaned_data['projects_state']
            state = {
                "eco_name": form.cleaned_data['eco_name_state'],
                "projects": [projects_state] if projects_state else [],
                "data_sources": [name] if name else []
            }

            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(**state)))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def remove_project(request):
    if request.method == 'POST':
        form = forms.ProjectForm(request.POST)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            Project.objects.get(name=project_name).delete()
            return shortcuts.render(request, 'projects/editor.html', build_forms_context())
        else:
            # TODO: Show error
            print("remove_project", form.errors)
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def add_project(request):
    if request.method == 'POST':
        form = forms.ProjectForm(request.POST)
        if form.is_valid():
            eco_name = form.cleaned_data['eco_name_state']
            eco_orm = None
            project_name = form.cleaned_data['project_name']
            project_orm = Project(name=project_name)
            project_orm.save()
            if eco_name:
                eco_orm = Ecosystem.objects.get(name=eco_name)
                eco_orm.projects.add(project_orm)
                eco_orm.save()
            state = {
                "eco_name": eco_name,
                "projects": [project_name],
            }
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(**state)))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def edit_project(request):
    if request.method == 'POST':
        form = forms.ProjectsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            state = {
                "eco_name": form.cleaned_data['eco_name_state'],
                "projects": [name],
            }
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(**state)))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


@perfdata
def edit_ecosystem(request):
    if request.method == 'POST':
        form = forms.EcosystemForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(eco_name=name)))
        else:
            # TODO: Show error
            print("FORM errors", form.errors)
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


@perfdata
def editor(request):
    """ Shows the Bestiary Editor """

    context = build_forms_context()

    return shortcuts.render(request, 'projects/editor.html', context)


def find_project_repository_views(project):

    data = {"repository_views": []}

    try:
        project_orm = Project.objects.get(name=project)
        repository_views_orm = project_orm.repository_views.all()
        for view in repository_views_orm:
            data['repository_views'].append({
                "id": view.id,
                "name": view.repository.name,
                "params": view.params,
                "type": view.repository.data_source.name
            })
    except Project.DoesNotExist:
        print('Can not find project', project)

    return data


def find_project_data_sources(project):
    data = {"data_sources": []}
    already_added_data_sources = []

    try:
        project_orm = Project.objects.get(name=project)
        repository_views = project_orm.repository_views.all()
        for repository_view_orm in repository_views:
            if repository_view_orm.repository.data_source.id in already_added_data_sources:
                continue
            already_added_data_sources.append(repository_view_orm.repository.data_source.id)
            data['data_sources'].append({
                "id": repository_view_orm.repository.data_source.id,
                "name": repository_view_orm.repository.data_source.name
            })
    except Project.DoesNotExist:
        print('Can not find project', project)

    return data


def find_projects(ecosystem=None):
    data = {"projects": []}

    try:
        if ecosystem:
            ecosystem_orm = Ecosystem.objects.get(name=ecosystem)
            projects_orm = ecosystem_orm.projects.all()
        else:
            projects_orm = Project.objects.all()
        for project in projects_orm:
            data['projects'].append({
                "id": project.id,
                "name": project.name
            })
    except Ecosystem.DoesNotExist:
        print('Can not find ecosystem', ecosystem)

    return data


def import_from_file(request):

    if request.method == "POST":
        myfile = request.FILES["imported_file"]
        ecosystem = request.POST["ecosystem"]
        cur_dt = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_name = "%s_%s.json" % (ecosystem, cur_dt)
        fpath = '.imported/' + file_name  # FIXME Define path where all these files must be saved
        save_path = default_storage.save(fpath, ContentFile(myfile.read()))

        task_init = time()
        (nprojects, nrepos) = load_projects(save_path, ecosystem)

        print("Total loading time ... %.2f sec", time() - task_init)
        print("Projects loaded", nprojects)
        print("Repositories loaded", nrepos)

    return index(request)


def export_to_file(request):

    if not os.path.exists('.exported'):
        os.mkdir(".exported")

    if request.method == "POST":
        ecosystem = request.POST["ecosystem"]
        task_init = time()
        projects = fetch_projects(ecosystem)

        print("Total loading time ... %.2f sec", time() - task_init)

        if projects:
            projects_json = json.dumps(projects, indent=True, sort_keys=True)
            file_name = "projects_%s.json" % ecosystem
            response = HttpResponse(projects_json, content_type="application/json")
            response['Content-Disposition'] = 'attachment; filename=' + file_name
            return response
        return HttpResponse(status=503)

    return index(request)
