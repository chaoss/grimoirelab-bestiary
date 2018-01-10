from datetime import datetime
from time import time


from django.http import HttpResponse
from django.template import loader

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from projects.bestiary_import import load_projects
from projects.models import Ecosystem, Project


def index(request):

    template = loader.get_template('projects/project.html')
    project = 'grimoire'  # debug value just during testing
    if (request.GET.get('project')):
        project = request.GET.get('project')
    context = find_data_sources(project)
    context.update(find_projects())
    context.update(find_data_sources_types(project))
    context['project_selected'] = project
    render_index = template.render(context, request)
    return HttpResponse(render_index)


def find_data_sources(project):

    data = {"data_sources": []}

    try:
        project_orm = Project.objects.get(name=project)
        data_sources_orm = project_orm.data_sources.all()
        for ds in data_sources_orm:
            data['data_sources'].append({
                "id": ds.id,
                "name": ds.rep.name,
                "params": ds.params,
                "type": ds.rep.data_source_type.name
            })
    except Project.DoesNotExist:
        print('Can not find project', project)

    return data


def find_data_sources_types(project):
    data = {"data_sources_types": []}
    already_add_ds_tpes = []

    try:
        project_orm = Project.objects.get(name=project)
        data_sources_orm = project_orm.data_sources.all()
        for ds in data_sources_orm:
            if ds.rep.data_source_type.id in already_add_ds_tpes:
                continue
            already_add_ds_tpes.append(ds.rep.data_source_type.id)
            data['data_sources_types'].append({
                "id": ds.rep.data_source_type.id,
                "name": ds.rep.data_source_type.name
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
