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

from projects.bestiary_import import load_projects
from projects.models import DataSource, Ecosystem, Project, Repository

from . import forms


def index(request):

    template = loader.get_template('projects/project.html')
    project = 'grimoire'  # debug value just during testing
    if (request.GET.get('project')):
        project = request.GET.get('project')
    context = find_project_views(project)
    context.update(find_projects())
    context.update(find_project_data_sources(project))
    context['project_selected'] = project
    render_index = template.render(context, request)
    return HttpResponse(render_index)


def build_forms_context(eco_name=None, project_name=None,
                        data_source_type=None, data_source_id=None):
    """ Get all forms to be shown in the editor """

    projects = [project_name] if project_name else None
    data_source_types = [data_source_type] if data_source_type else None
    data_sources = [data_source_id] if data_source_id else None

    context = {"ecosystem_form": forms.EcosystemForm(initial={'name': eco_name}),
               "projects_form": forms.ProjectsForm(eco_name=eco_name, projects=projects,
                                                   data_source_types=data_source_types,
                                                   data_sources=data_sources,
                                                   initial={'name': project_name}),
               "data_source_types_form": forms.DataSourceTypeForm(eco_name=eco_name,
                                                                  data_source_types=data_source_types,
                                                                  projects=projects,
                                                                  data_sources=data_sources,
                                                                  initial={'name': data_source_type}),
               "data_sources_form": forms.DataSourcesForm(eco_name=eco_name, projects=projects,
                                                          data_source_types=data_source_types,
                                                          data_sources=data_sources),
               "data_source_form": forms.DataSourceForm(data_source_id=data_source_id)
               }

    return context


def update_data_source(request):
    if request.method == 'POST':
        form = forms.DataSourceForm(request.POST)
        if form.is_valid():
            data_source_id = form.cleaned_data['data_source_id']
            repository = form.cleaned_data['repository']
            params = form.cleaned_data['params']
            filters = form.cleaned_data['filters']
            ds_orm = DataSource.objects.get(id=data_source_id)
            ds_orm.repo = Repository.objects.get(name=repository)
            ds_orm.params = params
            # TODO: filters not yet in the data models
            ds_orm.save()
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(data_source_id=data_source_id))
        else:
            # TODO: Show error
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def edit_data_source(request):
    if request.method == 'POST':
        form = forms.DataSourcesForm(request.POST)
        if form.is_valid():
            data_source_id = int(form.cleaned_data['id'])
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(data_source_id=data_source_id))
        else:
            # TODO: Show error
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def edit_data_source_type(request):
    if request.method == 'POST':
        form = forms.DataSourceTypeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(data_source_type=name))
        else:
            # TODO: Show error
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def edit_project(request):
    if request.method == 'POST':
        form = forms.ProjectsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(project_name=name))
        else:
            # TODO: Show error
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def edit_ecosystem(request):
    if request.method == 'POST':
        form = forms.EcosystemForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(eco_name=name))
        else:
            # TODO: Show error
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def editor(request):
    """ Shows the Bestiary Editor """

    context = build_forms_context()

    return shortcuts.render(request, 'projects/editor.html', context)


def find_project_views(project):

    data = {"repo_views": []}

    try:
        project_orm = Project.objects.get(name=project)
        repo_views_orm = project_orm.repo_views.all()
        for view in repo_views_orm:
            data['repo_views'].append({
                "id": view.id,
                "name": view.rep.name,
                "params": view.params,
                "type": view.rep.data_source.name
            })
    except Project.DoesNotExist:
        print('Can not find project', project)

    return data


def find_project_data_sources(project):
    data = {"data_sources": []}
    already_added_data_sources = []

    try:
        project_orm = Project.objects.get(name=project)
        repo_views_orm = project_orm.repo_views.all()
        for view in repo_views_orm:
            if view.rep.data_source.id in already_added_data_sources:
                continue
            already_added_data_sources.append(view.rep.data_source.id)
            data['data_sources'].append({
                "id": view.rep.data_source.id,
                "name": view.rep.data_source.name
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
