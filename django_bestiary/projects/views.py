from django.http import HttpResponse
from django.template import loader

from rest_framework import viewsets

from projects.models import DataSource, Ecosystem, Project, Repository
from projects.serializers import ProjectSerializer, DataSourceSerializer, RepositorySerializer


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

#
# REST views
#


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer


class DataSourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows data sources to be viewed or edited.
    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer


class RepositoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows repositories to be viewed or edited.
    """
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
