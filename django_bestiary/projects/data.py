from projects.models import DataSource, Ecosystem, Project, Repository, RepositoryView
from grimoire_elk import utils as gelk_utils


class DataSourcesData():

    def __init__(self, state):
        self.state = state

    def __fetch_from_repository_views(self, views):
        already_fetched = []

        for view in views:
            data_source_name = view.repository.data_source.name
            if data_source_name not in already_fetched:
                already_fetched.append(data_source_name)
                data_source = DataSource.objects.get(name=data_source_name)
                yield data_source

    def __fetch_from_projects(self, projects):

        for project in projects:
            views = project.repository_views.all()
            for data_source in self.__fetch_from_repository_views(views):
                yield data_source

    def fetch(self):

        if not self.state or self.state.is_empty():
            supported_data_sources = list(gelk_utils.get_connectors())
            for data_source_name in supported_data_sources:
                data_source = DataSource(name=data_source_name)
                yield data_source
        elif self.state.data_sources:
            data_sources = DataSource.objects.filter(name__in=self.state.data_sources)
            for data_source in data_sources:
                yield data_source
        elif self.state.repository_views:
            views = RepositoryView.objects.filter(id__in=self.state.repository_views)
            for data_source in self.__fetch_from_repository_views(views):
                yield data_source
        elif self.state.projects:
            projects = Project.objects.filter(name__in=self.state.projects)
            for data_source in self.__fetch_from_projects(projects):
                yield data_source
        elif self.state.eco_name:
            ecosystem = Ecosystem.objects.get(name=self.state.eco_name)
            projects = ecosystem.projects.all()
            for data_source in self.__fetch_from_projects(projects):
                yield data_source


class EcosystemsData():

    def __init__(self, state=None):
        self.state = state

    def fetch(self):
        for ecosystem in Ecosystem.objects.all():
            yield ecosystem


class ProjectsData():

    def __init__(self, state):
        self.state = state

    def fetch(self):
        if not self.state or self.state.is_empty():
            for project in Project.objects.all():
                yield project
        elif self.state.projects:
            projects = Project.objects.filter(name__in=self.state.projects)
            for project in projects:
                yield project
        elif self.state.repository_views:
            repository_views_idata_source = RepositoryView.objects.filter(id__in=self.state.repository_views).values_list("id")
            projects = Project.objects.filter(repository_views__in=list(repository_views_idata_source))
            for project in projects:
                yield project
        elif self.state.data_sources:
            data_source_idata_source = DataSource.objects.filter(name__in=self.state.data_sources).values_list("id")
            repos_idata_source = Repository.objects.filter(data_source__in=list(data_source_idata_source)).values_list("id")
            repository_views_idata_source = RepositoryView.objects.filter(repository__in=list(repos_idata_source)).values_list("id")
            projects = Project.objects.filter(repository_views__in=list(repository_views_idata_source))
            for project in projects:
                yield project
        elif self.state.eco_name:
            ecosystem = Ecosystem.objects.get(name=self.state.eco_name)
            projects = ecosystem.projects.all()
            for project in projects:
                yield project


class RepositoryViewsData():

    def __init__(self, state=None):
        self.state = state

    def fetch(self):
        if not self.state or self.state.is_empty():
            for view in RepositoryView.objects.all():
                yield view
        elif self.state.repository_views:
            repository_views = RepositoryView.objects.filter(id__in=self.state.repository_views)
            for view in repository_views:
                yield view
        elif self.state.projects:
            projects = Project.objects.filter(name__in=self.state.projects)
            for project in projects:
                for view in project.repository_views.all():
                    if self.state.data_sources:
                        if view.repository.data_source.name not in self.state.data_sources:
                            continue
                    yield view
        elif self.state.data_sources:
            for view in RepositoryView.objects.all():
                if view.repository.data_source.name in self.state.data_sources:
                    yield view
        elif self.state.eco_name:
            ecosystem = Ecosystem.objects.get(name=self.state.eco_name)
            for project in ecosystem.projects.all():
                for view in project.repository_views.all():
                    yield view
