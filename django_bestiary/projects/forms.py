import functools

from time import time

from django import forms

from projects.models import DataSource, Ecosystem, Project, Repository, RepositoryView

SELECT_LINES = 20
MAX_ITEMS = 1000  # Implement pagination if there are more items


def perfdata(func):
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):
        task_init = time()
        data = func(self, *args, **kwargs)
        print("%s: Total data collecting time ... %0.3f sec" %
              (self.__class__.__name__, time() - task_init))
        return data
    return decorator


class BestiaryEditorForm(forms.Form):

    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    # Hidden widgets to store the state of the BestiaryEditorForm
    eco_name_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    projects_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    data_sources_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    data_repository_views = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())

    def is_empty_state(self):
        return self.state.is_empty() if self.state else True

    def __init__(self, *args, **kwargs):
        self.state = kwargs.pop('state') if 'state' in kwargs else None
        if self.state:
            kwargs['initial'] = self.state.initial_state()
        super(BestiaryEditorForm, self).__init__(*args, **kwargs)

        # The state includes the names of objects except for repository_views
        # in which ids are included because there is no name
        self.state_fields = [self['eco_name_state'],
                             self['projects_state'],
                             self['data_sources_state'],
                             self['data_repository_views']
                             ]


class EcosystemForm(BestiaryEditorForm):

    widget = forms.Select(attrs={'class': 'form-control'})

    @perfdata
    def __init__(self, *args, **kwargs):
        super(EcosystemForm, self).__init__(*args, **kwargs)

        choices = ()

        for eco in Ecosystem.objects.all():
            choices += ((eco.name, eco.name),)

        self.fields['name'] = forms.ChoiceField(label='Ecosystems',
                                                widget=self.widget, choices=choices)


class ProjectsForm(BestiaryEditorForm):

    @perfdata
    def __init__(self, *args, **kwargs):
        super(ProjectsForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.state or self.state.is_empty():
            for project in Project.objects.all():
                choices += ((project.name, project.name),)
        elif self.state.projects:
            projects = Project.objects.filter(name__in=self.state.projects)
            for project in projects:
                choices += ((project.name, project.name),)
        elif self.state.data_sources:
            ds_ids = DataSource.objects.filter(name__in=self.state.data_sources).values_list("id")
            repos_ids = Repository.objects.filter(data_source__in=list(ds_ids)).values_list("id")
            repository_views_ids = RepositoryView.objects.filter(repository__in=list(repos_ids)).values_list("id")
            projects = Project.objects.filter(repository_views__in=list(repository_views_ids))
            for project_orm in projects:
                if (project_orm.name, project_orm.name) not in choices:
                    choices += ((project_orm.name, project_orm.name),)
        else:
            if self.state.eco_name:
                ecosystem_orm = Ecosystem.objects.get(name=self.state.eco_name)
                projects = ecosystem_orm.projects.all()
                for project in projects:
                    choices += ((project.name, project.name),)
            if self.state.repository_views:
                repository_views_ids = RepositoryView.objects.filter(id__in=self.state.repository_views).values_list("id")
                projects = Project.objects.filter(repository_views__in=list(repository_views_ids))
                for project_orm in projects:
                    if (project_orm.name, project_orm.name) not in choices:
                        choices += ((project_orm.name, project_orm.name),)

        choices = sorted(choices, key=lambda x: x[1])
        self.fields['name'] = forms.ChoiceField(label='Projects',
                                                widget=self.widget, choices=choices)


class DataSourcesForm(BestiaryEditorForm):

    @perfdata
    def __init__(self, *args, **kwargs):
        super(DataSourcesForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.state or self.state.is_empty():
            for ds in DataSource.objects.all():
                choices += ((ds.name, ds.name),)
        elif self.state.data_sources:
            for ds_name in self.state.data_sources:
                choices += ((ds_name, ds_name),)
        else:
            if self.state.eco_name and not self.state.projects:
                eco_orm = Ecosystem.objects.get(name=self.state.eco_name)
                for project_orm in eco_orm.projects.all():
                    for repository_view in project_orm.repository_views.all():
                        ds_name = repository_view.repository.data_source.name
                        if (ds_name, ds_name) not in choices:
                            choices += ((ds_name, ds_name),)
            if self.state.projects:
                projects = Project.objects.filter(name__in=self.state.projects)
                for project_orm in projects:
                    for repository_view in project_orm.repository_views.all():
                        ds_name = repository_view.repository.data_source.name
                        if (ds_name, ds_name) not in choices:
                            choices += ((ds_name, ds_name),)
            if self.state.repository_views:
                repository_views = RepositoryView.objects.filter(id__in=self.state.repository_views)
                for repository_view_orm in repository_views:
                    ds_name = repository_view_orm.repository.data_source.name
                    if (ds_name, ds_name) not in choices:
                        choices += ((ds_name, ds_name),)

        choices = sorted(choices, key=lambda x: x[1])
        self.fields['name'] = forms.ChoiceField(label='DataSources',
                                                widget=self.widget, choices=choices)


class RepositoryViewsForm(BestiaryEditorForm):

    @perfdata
    def __init__(self, *args, **kwargs):
        super(RepositoryViewsForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.state or self.state.is_empty():
            for view in RepositoryView.objects.all():
                choices += ((view.id, view),)
                if len(choices) > MAX_ITEMS:
                    break

        else:
            if self.state.eco_name and not self.state.projects:
                eco_orm = Ecosystem.objects.get(name=self.state.eco_name)
                for project_orm in eco_orm.projects.all():
                    if len(choices) > MAX_ITEMS:
                        break
                    for repository_view_orm in project_orm.repository_views.all():
                        choices += ((repository_view_orm.id, repository_view_orm),)
                        if len(choices) > MAX_ITEMS:
                            break
            if self.state.projects:
                projects = Project.objects.filter(name__in=self.state.projects)
                for project_orm in projects:
                    for repository_view_orm in project_orm.repository_views.all():
                        choices += ((repository_view_orm.id, repository_view_orm),)
            if self.state.data_sources:
                for repository_view_orm in RepositoryView.objects.all():
                    if repository_view_orm.repository.data_source.name in self.state.data_sources:
                        choices += ((repository_view_orm.id, repository_view_orm),)
                        if len(choices) > MAX_ITEMS:
                            break
            if self.state.repository_views:
                repository_views = RepositoryView.objects.filter(id__in=self.state.repository_views)
                for repository_view_orm in repository_views:
                    choices += ((repository_view_orm.id, repository_view_orm),)

        print("Choices len", len(choices))
        self.fields['id'] = forms.ChoiceField(label='DataSource',
                                              widget=self.widget, choices=choices)


class RepositoryViewForm(BestiaryEditorForm):

    @perfdata
    def __init__(self, *args, **kwargs):
        task_init = time()

        self.repository_view_id = None
        self.repository_view_orm = None

        # Process the state here because we need it for other initial values
        self.state = kwargs.pop('state') if 'state' in kwargs else None
        if self.state:
            kwargs['initial'] = self.state.initial_state()

        if self.state and self.state.repository_views:
            self.repository_view_id = self.state.repository_views[0]

        if self.repository_view_id:
            repository_view_orm = RepositoryView.objects.get(id=self.repository_view_id)
            kwargs['initial'] = {
                'repository_view_id': self.repository_view_id,
                'repository': repository_view_orm.repository.name,
                'params': repository_view_orm.params,
                'filters': ''
            }
        super(RepositoryViewForm, self).__init__(*args, **kwargs)

        self.fields['repository_view_id'] = forms.CharField(label='repository_view_id', max_length=100)

        self.fields['repository'] = forms.CharField(label='repository', max_length=100, required=False)
        self.fields['repository'].widget = forms.TextInput(attrs={'class': 'form-control'})

        self.fields['params'] = forms.CharField(label='params', max_length=100, required=False)
        self.fields['params'].widget = forms.TextInput(attrs={'class': 'form-control'})

        self.fields['filters'] = forms.CharField(label='filters', max_length=100, required=False)
        self.fields['filters'].widget = forms.TextInput(attrs={'class': 'form-control'})
