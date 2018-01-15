import os

from datetime import datetime
from time import time

from django.http import HttpResponse
from django.template import loader

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from projects.bestiary_export import export_projects
from projects.bestiary_import import load_projects
from projects.models import Ecosystem, Project


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
        file_name = "projects_%s.json" % ecosystem
        file_path = os.path.abspath(os.path.curdir) + "/.exported/" + file_name

        task_init = time()
        (nprojects, nrepos) = export_projects(file_path, ecosystem)

        print("Total loading time ... %.2f sec", time() - task_init)
        print("Projects loaded", nprojects)
        print("Repositories loaded", nrepos)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as fexport:
                response = HttpResponse(fexport.read(), content_type="application/json")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                return response
        return HttpResponse(status=503)

    return index(request)
