import functools
import json

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
from projects.models import DataSource, Ecosystem, Project, Repository, RepositoryView

from . import forms
from . import data


class EditorState():

    def __init__(self, eco_name=None, eco_id=None, projects=[], project_id=None,
                 data_sources=[], repository_views=[], form=None, msg=None):
        self.eco_name = eco_name
        self.eco_id = eco_id
        self.projects = projects
        self.project_id = project_id
        self.data_sources = data_sources
        self.repository_views = repository_views
        self.msg = msg

        if form:
            # The form includes the state not chnaged to be propagated
            projects_state = form.cleaned_data['projects_state']
            data_sources = form.cleaned_data['data_sources_state']
            repository_views = form.cleaned_data['repository_views_state']

            if not self.eco_name:
                self.eco_name = form.cleaned_data['eco_name_state']
            if not self.eco_id:
                self.eco_id = form.cleaned_data['eco_id_state']
            if not self.projects:
                self.projects = [projects_state] if projects_state else []
            if not self.project_id:
                self.project_id = form.cleaned_data['project_id_state']
            if not self.data_sources:
                self.data_sources = [data_sources] if data_sources else []
            if not self.repository_views:
                self.repository_views = [repository_views] if repository_views else []

    def is_empty(self):
        return not (self.eco_name or self.eco_id or self.projects or self.project_id or
                    self.data_sources or self.repository_views)

    def initial_state(self):
        """ State to be filled in the forms so it is propagated

        The state needs to be serialized so it can be used in
        forms fields.
        """

        initial = {
            'eco_name_state': self.eco_name,
            'eco_id_state': self.eco_id,
            'projects_state': ";".join(self.projects),
            'project_id_state': self.project_id,
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


def return_error(message):

    template = loader.get_template('projects/error.html')
    context = {"alert_message": message}
    render_error = template.render(context)
    return HttpResponse(render_error)


def select_project(request, template, context=None):
    if request.method == 'POST':
        form = forms.ProjectsForm(request.POST)
        if form.is_valid():
            project_name = form.cleaned_data['name']
            try:
                project_orm = Project.objects.get(name=project_name)
            except Project.DoesNotExist:
                # TODO: Show error
                return shortcuts.render(request, template, build_forms_context())
            projects = [project_name]
            state = EditorState(projects=projects, project_id=project_orm.id, form=form)
            if context:
                context.update(build_forms_context(state))
            else:
                context = build_forms_context(state)
            return shortcuts.render(request, template, context)
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, template, build_forms_context())


@perfdata
def select_ecosystem(request, template, context=None):
    if request.method == 'POST':
        form = forms.EcosystemsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']

            if not name:
                # TODO: Show error when ecosystem name is empty
                return shortcuts.render(request, template, build_forms_context())
            # Select and ecosystem reset the state. Don't pass form=form
            try:
                eco_orm = Ecosystem.objects.get(name=name)
            except Ecosystem.DoesNotExist:
                # TODO: Show error
                return shortcuts.render(request, template, build_forms_context())

            state = build_forms_context(EditorState(eco_name=name, eco_id=eco_orm.id))
            if context:
                context.update(state)
            else:
                context = build_forms_context(EditorState(eco_name=name, eco_id=eco_orm.id))
            return shortcuts.render(request, template, context)
        else:
            # Ignore when the empty option is selected
            return shortcuts.render(request, template, build_forms_context())
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, template, build_forms_context())


@perfdata
def build_forms_context(state=None):
    """ Get all forms to be shown in the editor """
    eco_form = forms.EcosystemsForm(state=state)
    add_eco_form = forms.EcosystemForm(state=state)
    projects_form = forms.ProjectsForm(state=state)
    project_form = forms.ProjectForm(state=state)
    data_source_form = forms.DataSourceForm(state=state)
    data_sources_form = forms.DataSourcesForm(state=state)
    repository_views_form = forms.RepositoryViewsForm(state=state)
    repository_view_form = forms.RepositoryViewForm(state=state)
    msg = None

    if state:
        eco_form.initial['name'] = state.eco_name
        add_eco_form.initial['id'] = state.eco_id
        add_eco_form.initial['ecosystem_name'] = state.eco_name
        if state.projects:
            projects_form.initial['name'] = state.projects[0]
            project_form.initial['project_name'] = state.projects[0]
        if state.data_sources:
            data_sources_form.initial['name'] = state.data_sources[0]
            data_source_form.initial['data_source_name'] = state.data_sources[0]
        msg = state.msg

    context = {"ecosystems_form": eco_form,
               "ecosystem_form": add_eco_form,
               "projects_form": projects_form,
               "project_form": project_form,
               "data_source_form": data_source_form,
               "data_sources_form": data_sources_form,
               "repository_views_form": repository_views_form,
               "repository_view_form": repository_view_form,
               "msg": msg
               }
    return context

##
# status page methods
##


def fetch_status_repository_views(state=None):
    views = data.RepositoryViewsData(state).fetch()
    views_status = []
    for view in views:
        view_str = " ".join([view.repository.name, view.params])
        views_status.append({"id": view.id,
                             "name": view_str,
                             "status": "",
                             "last_updated": "",
                             "creation_date": "",
                             "results": ""})
    return views_status


def status(request):
    # Get the repository views
    state = None
    views_status = fetch_status_repository_views(state)
    context = {"views": views_status}
    # Adding more forms than needed. To be optimized.
    context.update(build_forms_context())
    template = loader.get_template('projects/status.html')
    render_status = template.render(context, request)
    return HttpResponse(render_status)


def status_select_ecosystem(request):
    state = None
    if request.method == 'POST':
        form = forms.EcosystemsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            state = EditorState(eco_name=name)

    views_status = fetch_status_repository_views(state)
    context = {"views": views_status}
    return select_ecosystem(request, "projects/status.html", context)


def status_select_project(request):
    state = None
    if request.method == 'POST':
        form = forms.ProjectsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            state = EditorState(projects=[name])

    views_status = fetch_status_repository_views(state)
    context = {"views": views_status}
    return select_project(request, "projects/status.html", context)


##
# editor page methods
##

@perfdata
def editor(request):
    """ Shows the Bestiary Editor """

    context = build_forms_context()

    return shortcuts.render(request, 'projects/editor.html', context)


def editor_select_ecosystem(request):
    return select_ecosystem(request, "projects/editor.html")


def add_ecosystem(request):

    if request.method == 'POST':
        form = forms.EcosystemForm(request.POST)
        if form.is_valid():
            ecosystem_name = form.cleaned_data['ecosystem_name']

            try:
                eco_orm = Ecosystem.objects.get(name=ecosystem_name)
                msg = 'Ecosystem \"%s\" already exists' % ecosystem_name
            except Ecosystem.DoesNotExist:
                eco_orm = Ecosystem(name=ecosystem_name)
                eco_orm.save()
                msg = 'Ecosystem \"%s\" has been added' % ecosystem_name

            # Select and ecosystem reset the state. Don't pass form=form
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(eco_name=ecosystem_name, eco_id=eco_orm.id, msg=msg)))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def update_ecosystem(request):
    if request.method == 'POST':
        form = forms.EcosystemForm(request.POST)
        if form.is_valid():
            eco_id = form.cleaned_data['eco_id_state']
            ecosystem_name = form.cleaned_data['ecosystem_name']

            try:
                eco_orm = Ecosystem.objects.get(id=eco_id)
            except Ecosystem.DoesNotExist:
                msg = 'Ecosystem does not exist'
                return shortcuts.render(request, 'projects/editor.html', build_forms_context(EditorState(msg=msg)))

            eco_orm.name = ecosystem_name
            eco_orm.save()

            msg = 'Ecosystem \"%s\" has been updated' % ecosystem_name
            state = EditorState(eco_name=ecosystem_name, eco_id=eco_id, form=form, msg=msg)
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(state))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def remove_ecosystem(request):
    if request.method == 'POST':
        form = forms.EcosystemForm(request.POST)
        if form.is_valid():
            ecosystem_name = form.cleaned_data['ecosystem_name']
            Ecosystem.objects.get(name=ecosystem_name).delete()
            msg = 'Ecosystem \"%s\" has been deleted' % ecosystem_name
            state = EditorState(msg=msg)
            return shortcuts.render(request, 'projects/editor.html', build_forms_context(state))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def add_repository_view(request):
    if request.method == 'POST':
        form = forms.RepositoryViewForm(request.POST)
        if form.is_valid():
            repository = form.cleaned_data['repository']
            params = form.cleaned_data['params']
            data_source = form.cleaned_data['data_source']
            # Don't support multiselect in projects yet
            project = form.cleaned_data['projects_state']
            # Adding a new repository view
            try:
                data_source_orm = DataSource.objects.get(name=data_source)
            except DataSource.DoesNotExist:
                data_source_orm = DataSource(name=data_source)
                data_source_orm.save()

            # Try to find a repository already created
            try:
                repository_orm = Repository.objects.get(name=repository, data_source=data_source_orm)
            except Repository.DoesNotExist:
                # Create a new repository
                repository_orm = Repository(name=repository, data_source=data_source_orm)
                repository_orm.save()
            # Try to find a repository view already created
            try:
                repository_view_orm = RepositoryView.objects.get(params=params, repository=repository_orm)
            except RepositoryView.DoesNotExist:
                repository_view_orm = RepositoryView(params=params,
                                                     repository=repository_orm)
                repository_view_orm.save()
            # If there is a project defined, add the repository view to the project
            if project:
                project_orm = Project.objects.get(name=project)
                project_orm.repository_views.add(repository_view_orm)
                project_orm.save()

            repository_view_orm.save()

            form.cleaned_data['repository_views_state'] = []
            msg = 'Data source has been added'
            state = EditorState(form=form, msg=msg)
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(state))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def update_repository_view(request):
    if request.method == 'POST':
        form = forms.RepositoryViewForm(request.POST)

        if form.is_valid():
            repository_view_id = form.cleaned_data['repository_view_id']
            repository = form.cleaned_data['repository']
            params = form.cleaned_data['params']
            data_source = form.cleaned_data['data_source']

            repository_view_orm = RepositoryView.objects.get(id=repository_view_id)

            try:
                repository_orm = Repository.objects.get(name=repository)
                repository_view_orm.repository = repository_orm
            except Repository.DoesNotExist:
                # Create a new repository
                data_source_orm = DataSource.objects.get(name=data_source)
                repository_orm = Repository(name=repository, data_source=data_source_orm)
                repository_orm.save()

            repository_view_orm.repository = repository_orm
            repository_view_orm.params = params

            repository_view_orm.save()

            msg = 'Data source has been updated'
            state = EditorState(repository_views=[repository_view_id], form=form, msg=msg)
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(state))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def remove_repository_view(request):
    if request.method == 'POST':
        form = forms.RepositoryViewForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['repository_view_id']:
                repository_view_id = int(form.cleaned_data['repository_view_id'])
                RepositoryView.objects.get(id=repository_view_id).delete()
            # Clean from the state the removed repository view
            form.cleaned_data['repository_views_state'] = []
            msg = 'Data source has been removed'
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(form=form, msg=msg)))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def select_repository_view(request):
    if request.method == 'POST':
        form = forms.RepositoryViewsForm(request.POST)
        if form.is_valid():
            repository_view_id = int(form.cleaned_data['id'])
            state = EditorState(form=form, repository_views=[repository_view_id])
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(state))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def add_data_source(request):

    if request.method == 'POST':
        form = forms.DataSourceForm(request.POST)
        if form.is_valid():
            eco_name = form.cleaned_data['eco_name_state']
            eco_orm = None
            project_name = form.cleaned_data['projects_state']
            project_orm = None
            if eco_name:
                eco_orm = Ecosystem.objects.get(name=eco_name)
                projects_orm = eco_orm.projects.all()
                eco_orm.save()

            data_source_name = form.cleaned_data['data_source_name']
            data_source_orm = DataSource(name=data_source_name)
            data_source_orm.save()

            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(form=form)))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def select_data_source(request):
    if request.method == 'POST':
        form = forms.DataSourcesForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            data_sources = [name] if name else []

            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(form=form, data_sources=data_sources)))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


def editor_select_project(request):
    return select_project(request, "projects/editor.html")


def update_project(request):
    if request.method == 'POST':
        form = forms.ProjectForm(request.POST)
        if form.is_valid():
            project_id = form.cleaned_data["project_id_state"]
            project_name = form.cleaned_data["project_name"]
            eco_name = form.cleaned_data['eco_name_state']
            eco_orm = None
            try:
                project_orm = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                msg = 'Project \"%s\" does not exist' % project_name
                state = EditorState(eco_name=eco_name, msg=msg)
                return shortcuts.render(request, 'projects/editor.html',
                                        build_forms_context(state))

            project_orm.name = project_name
            project_orm.save()
            msg = 'Project \"%s\" has been updated' % project_name
            state = EditorState(eco_name=eco_name, projects=[project_name],
                                project_id=project_id, form=form, msg=msg)
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(state))
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
            msg = 'Project \"%s\" has been removed' % project_name
            return shortcuts.render(request, 'projects/editor.html', build_forms_context(EditorState(msg=msg)))
        else:
            # TODO: Show error
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
            try:
                project_orm = Project.objects.get(name=project_name)
                msg = 'Project \"%s\" already exists' % project_name
            except Project.DoesNotExist:
                project_orm = Project(name=project_name)
                project_orm.save()
                msg = 'Project \"%s\" has been added' % project_name

            if eco_name:
                eco_orm = Ecosystem.objects.get(name=eco_name)
                eco_orm.projects.add(project_orm)
                eco_orm.save()

            context = EditorState(projects=[project_name], project_id=project_orm.id, form=form, msg=msg)
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(context))
        else:
            # TODO: Show error
            raise Http404
    # if a GET (or any other method) we'll create a blank form
    else:
        # TODO: Show error
        return shortcuts.render(request, 'projects/editor.html', build_forms_context())


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
        ecosystem = request.POST["name"]
        cur_dt = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_name = "%s_%s.json" % (ecosystem, cur_dt)
        fpath = '.imported/' + file_name  # FIXME Define path where all these files must be saved
        save_path = default_storage.save(fpath, ContentFile(myfile.read()))

        task_init = time()
        try:
            (nprojects, nrepos) = load_projects(save_path, ecosystem)
        except Exception:
            error_msg = "File %s couldn't be imported." % myfile.name
            return return_error(error_msg)

        print("Total loading time ... %.2f sec", time() - task_init)
        print("Projects loaded", nprojects)
        print("Repositories loaded", nrepos)

    return editor_select_ecosystem(request)


def export_to_file(request, ecosystem=None):

    if (request.method == "GET") and (not ecosystem):
        return editor(request)

    if request.method == "POST":
        ecosystem = request.POST["name"]

    file_name = "projects_%s.json" % ecosystem
    task_init = time()
    try:
        projects = fetch_projects(ecosystem)
    except (Ecosystem.DoesNotExist, Exception):
        error_msg = "Projects from ecosystem \"%s\" couldn't be exported." % ecosystem
        if request.method == "POST":
            # If request comes from web UI and fails, return error page
            return return_error(error_msg)
        else:
            # If request comes as a GET request, return HTTP 404: Not Found
            return HttpResponse(status=404)

    print("Total loading time ... %.2f sec", time() - task_init)
    if projects:
        projects_json = json.dumps(projects, indent=True, sort_keys=True)
        response = HttpResponse(projects_json, content_type="application/json")
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        return response
    else:
        error_msg = "There are no projects to export"
        return return_error(error_msg)

    return editor(request)
