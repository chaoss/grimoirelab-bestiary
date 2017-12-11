from django.http import HttpResponse
from django.template import loader

from projects.models import Project

# from django.shortcuts import render


def index(request):

    template = loader.get_template('projects/project.html')
    context = find_data_sources("grimoire")
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
