import json
import os

from datetime import datetime
from time import time

from django import forms

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from projects.bestiary_export import fetch_projects

from django import shortcuts

from projects.bestiary_import import load_projects
from projects.models import DataSource, DataSourceType, Ecosystem, Project

SELECT_LINES = 20


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


class EcosystemForm(forms.Form):
    widget = forms.Select(attrs={'class': 'form-control'})

    CHOICES = ()

    for eco in Ecosystem.objects.all():
        CHOICES += ((eco.name, eco.name),)

    name = forms.ChoiceField(label='Ecosystems', widget=widget, choices=CHOICES)


class ProjectsForm(forms.Form):
    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    CHOICES = ()

    for project in Project.objects.all():
        CHOICES += ((project.name, project.name),)

    name = forms.ChoiceField(label='Projects', widget=widget, choices=CHOICES)


class DataSourceTypeForm(forms.Form):
    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    CHOICES = ()

    for ds_type in DataSourceType.objects.all():
        CHOICES += ((ds_type.name, ds_type.name),)

    name = forms.ChoiceField(label='DataSourceTypes', widget=widget, choices=CHOICES)


class DataSourcesForm(forms.Form):
    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    CHOICES = ()

    for ds in DataSource.objects.all():
        CHOICES += ((ds.rep.name, ds.rep.name),)

    name = forms.ChoiceField(label='DataSources', widget=widget, choices=CHOICES)


def edit_ecosystem(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EcosystemForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EcosystemForm()

    return shortcuts.render(request, 'projects/editor.html', {'form': form})


def editor(request):
    """ Shows the Bestiary Editor """

    template = loader.get_template('projects/editor.html')
    context = {"ecosystem_form": EcosystemForm(),
               "projects_form": ProjectsForm(),
               "data_source_types_form": DataSourceTypeForm(),
               "data_sources_form": DataSourcesForm()
               }
    render_index = template.render(context, request)
    return HttpResponse(render_index)


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
