import functools
import json
import pickle

from datetime import datetime
from time import time

import requests

import redis
from rq import Queue, Worker, use_connection
from rq.job import Job, JobStatus
from arthur.common import Q_STORAGE_ITEMS, Q_CREATION_JOBS, Q_UPDATING_JOBS

from django.http import HttpResponse
from django.template import loader

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from projects.bestiary_export import fetch_projects

from django import shortcuts
from django.http import Http404

from projects.bestiary_import import load_projects
from projects.models import DataSource, Ecosystem, Project, Repository, RepositoryView

from grimoirelab.toolkit.datetime import unixtime_to_datetime

from . import forms
from . import data


class EditorState():

    def __init__(self, eco_name=None, projects=[], data_sources=[],
                 repository_views=[], form=None):
        self.eco_name = eco_name
        self.projects = projects
        self.data_sources = data_sources
        self.repository_views = repository_views

        if form:
            # The form includes the state not chnaged to be propagated
            projects_state = form.cleaned_data['projects_state']
            data_sources = form.cleaned_data['data_sources_state']
            repository_views = form.cleaned_data['repository_views_state']

            if not self.eco_name:
                self.eco_name = form.cleaned_data['eco_name_state']
            if not self.projects:
                self.projects = [projects_state] if projects_state else []
            if not self.data_sources:
                self.data_sources = [data_sources] if data_sources else []
            if not self.repository_views:
                self.repository_views = [repository_views] if repository_views else []

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

class ServicesState():
    def __init__(self):
        self.arthur_tasks=None
        self.queued_tasks=None
        self.running_tasks=None
        self.waiting_tasks=None
        self.redis_items=None

        self.redis_con = redis.StrictRedis.from_url(REDIS_URL)

    def collect_arthur_tasks(self):
        arthur_tasks = []
        try:
            res = requests.get(ARTHUR_URL + "/tasks")
            res.raise_for_status()
            arthur_tasks = res.json()['tasks']
        except requests.exceptions.ConnectionError:
            print("Can not connect to arthur")

        return len(arthur_tasks)

    def collect_rq_tasks(self):
        tasks = 0
        use_connection(self.redis_con)
        for queue in Queue.all():
            # Let's try to find the repository_view in the queues
            for job in queue.get_jobs():
                print(job)
                tasks += 1
        return tasks

    def list_rq_queues(self):
        queues = []
        use_connection(self.redis_con)
        for queue in Queue.all():
            queues.append(queue.name)
        print(queues)
        return queues

    def list_rq_workers(self):
        workers = []
        use_connection(self.redis_con)
        for worker in Worker.all():
            workers.append(worker.name)
        return workers

    def list_rq_workers_state(self):
        states = []
        use_connection(self.redis_con)
        for worker in Worker.all():
            states.append(worker.get_state())
        return states

    def collect_redis_items(self):
        pipe = self.redis_con.pipeline()
        pipe.lrange(Q_UPDATING_JOBS, 0, -1)
        update_jobs = pipe.execute()[0]
        print(" ** update_jobs", len(update_jobs))
        for rq_job in update_jobs:
            job = pickle.loads(rq_job)
            print(job)
        pipe = self.redis_con.pipeline()
        pipe.lrange(Q_CREATION_JOBS, 0, -1)
        creation_jobs = pipe.execute()[0]
        print(" ** creation_jobs", len(creation_jobs))
        pipe = self.redis_con.pipeline()
        pipe.lrange(Q_STORAGE_ITEMS, 0, -1)
        items = pipe.execute()[0]
        print(" ** items", len(items))

        return len(items)

    def collect(self):
        arthur_tasks = self.collect_arthur_tasks()
        rq_tasks = self.collect_rq_tasks()
        running_tasks = 0  # number of workers active
        waiting_tasks = arthur_tasks - rq_tasks - running_tasks
        return {
           "arthur_tasks": arthur_tasks,
           "queues_list": ",".join(self.list_rq_queues()),
           "workers_list": self.list_rq_workers(),
           "workers_status": self.list_rq_workers_state(),
           "queued_tasks": rq_tasks,
           "running_tasks": running_tasks,
           "waiting_tasks": waiting_tasks,
           "redis_items": self.collect_redis_items()
           }


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
            name = form.cleaned_data['name']
            projects = [name]
            state = EditorState(projects=projects, form=form)
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
            state = build_forms_context(EditorState(eco_name=name))
            if context:
                context.update(state)
            else:
                context = build_forms_context(EditorState(eco_name=name))
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
    project_remove_form = forms.ProjectForm(state=state)
    data_source_form = forms.DataSourceForm(state=state)
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

    context = {"ecosystems_form": eco_form,
               "ecosystem_form": add_eco_form,
               "projects_form": projects_form,
               "project_form": project_form,
               "project_remove_form": project_remove_form,
               "data_source_form": data_source_form,
               "data_sources_form": data_sources_form,
               "repository_views_form": repository_views_form,
               "repository_view_form": repository_view_form
               }
    return context

##
# status page methods
##

REDIS_URL = 'redis://redis/8'
ARTHUR_URL = 'http://arthur:8080'

def check_status(repository_views):
    from random import random

    views_status = {}

    status = ['Running', 'Waiting', 'Failed', 'Creating Queue', 'Updating Queue']
    queues = ['create', 'update', 'failed']

    # The task list information comes from arthur
    arthur_tasks = []
    try:
        res = requests.get(ARTHUR_URL + "/tasks")
        res.raise_for_status()
        arthur_tasks = res.json()['tasks']
    except requests.exceptions.ConnectionError:
        print("Can not connect to arthur")

    for view in repository_views:
        views_status[view.id] = {}
        views_status[view.id]['status'] = 'N/A'
        views_status[view.id]['creation_date'] = 'N/A'
        for task in arthur_tasks:
            print(task)
            if view.repository.name == task['backend_args']['uri']:
                # views_status[view.id]['status'] = status[int(len(status)*random())]
                views_status[view.id]['status'] = 'arthur'
                views_status[view.id]['creation_date'] = unixtime_to_datetime(task['created_on'])
                break

    return views_status

def fetch_status_repository_views(state=None):
    views_status = []
    views = data.RepositoryViewsData(state).fetch()
    views_data = check_status(views)
    views = data.RepositoryViewsData(state).fetch()
    for view in views:
        view_str = " ".join([view.repository.name, view.params])
        views_status.append({"id": view.id,
                             "name": view_str,
                             "status": views_data[view.id]['status'],
                             "last_updated": "",
                             "creation_date": views_data[view.id]['creation_date'],
                             "results": ""})
    return views_status


def status(request):
    # Get the repository views
    state = None
    views_status = fetch_status_repository_views(state)
    context = {"views": views_status}
    context.update(ServicesState().collect())
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
    context.update(ServicesState().collect())
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
    context.update(ServicesState().collect())
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
            except Ecosystem.DoesNotExist:
                eco_orm = Ecosystem(name=ecosystem_name)
                eco_orm.save()

            # Select and ecosystem reset the state. Don't pass form=form
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(eco_name=ecosystem_name)))
        else:
            # TODO: Show error
            print("FORM errors", form.errors)
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
            state = EditorState(form=form)
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(state))
        else:
            # TODO: Show error
            print(form.errors)
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

            state = EditorState(repository_views=[repository_view_id], form=form)
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(state))
        else:
            # TODO: Show error
            print(form.errors)
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
            return shortcuts.render(request, 'projects/editor.html',
                                    build_forms_context(EditorState(form=form)))
        else:
            # TODO: Show error
            print(form.errors)
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
            context = EditorState(projects=[project_name], form=form)
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
