import pickle

import requests

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import redis
from rq import Queue, Worker, use_connection
from rq.job import Job, JobStatus
from arthur.common import Q_STORAGE_ITEMS, Q_CREATION_JOBS, Q_UPDATING_JOBS

from projects import data, forms
from projects.views import build_forms_context, EditorState, select_ecosystem, select_project

from grimoirelab.toolkit.datetime import unixtime_to_datetime


class ServicesState():
    def __init__(self):
        self.arthur_tasks = None
        self.queued_tasks = None
        self.running_tasks = None
        self.waiting_tasks = None
        self.redis_items = None

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
    template = loader.get_template('custodian/status.html')
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


def index(request):
    context = {}
    template = loader.get_template('custodian/status.html')
    render_status = template.render(context, request)
    return HttpResponse(render_status)
