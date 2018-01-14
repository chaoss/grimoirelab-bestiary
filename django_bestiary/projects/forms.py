from time import time

from django import forms

from projects.models import DataSource, DataSourceType, Ecosystem, Project, Repository

SELECT_LINES = 20


class BestiaryEditorForm(forms.Form):

    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    # Hidden widgets to store the state of the BestiaryEditorForm
    eco_name_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    projects_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    data_source_types_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
    data_sources_state = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())

    def is_empty_state(self):
        return self.state.is_empty() if self.state else True

    def __init__(self, *args, **kwargs):
        self.state = kwargs.pop('state') if 'state' in kwargs else None
        if self.state:
            kwargs['initial'] = self.state.initial_state()
        super(BestiaryEditorForm, self).__init__(*args, **kwargs)

        self.state_fields = [self['eco_name_state'],
                             self['projects_state'],
                             self['data_source_types_state'],
                             self['data_sources_state']
                             ]



class EcosystemForm(BestiaryEditorForm):

    widget = forms.Select(attrs={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        super(EcosystemForm, self).__init__(*args, **kwargs)

        choices = ()

        for eco in Ecosystem.objects.all():
            choices += ((eco.name, eco.name),)

        self.fields['name'] = forms.ChoiceField(label='Ecosystems',
                                                widget=self.widget, choices=choices)


class ProjectsForm(BestiaryEditorForm):

    def __init__(self, *args, **kwargs):
        super(ProjectsForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.state or self.state.is_empty():
            for project in Project.objects.all():
                choices += ((project.name, project.name),)
        elif self.state.projects:
            for project in Project.objects.all():
                if project.name in self.state.projects:
                    choices += ((project.name, project.name),)
        else:
            if self.state.eco_name:
                ecosystem_orm = Ecosystem.objects.get(name=self.state.eco_name)
                for project in ecosystem_orm.projects.all():
                    choices += ((project.name, project.name),)
            if self.state.data_sources:
                for project_orm in Project.objects.all():
                    for ds in project_orm.data_sources.all():
                        if ds.id in self.state.data_sources:
                            if (project_orm.name, project_orm.name) not in choices:
                                choices += ((project_orm.name, project_orm.name),)
                            break
            if self.state.data_source_types:
                task_init = time()
                ds_types_ids = DataSourceType.objects.filter(name__in=self.state.data_source_types).values_list("id")
                repos_ids = Repository.objects.filter(data_source_type__in=list(ds_types_ids)).values_list("id")
                ds_ids = DataSource.objects.filter(rep__in=list(repos_ids)).values_list("id")
                projects = Project.objects.filter(data_sources__in=list(ds_ids))
                for project_orm in projects:
                    if (project_orm.name, project_orm.name) not in choices:
                        choices += ((project_orm.name, project_orm.name),)
                print("Total QUERY time for finding projects for data sources %.3f sec"
                      % (time() - task_init))

        choices = sorted(choices, key=lambda x: x[1])
        self.fields['name'] = forms.ChoiceField(label='Projects',
                                                widget=self.widget, choices=choices)


class DataSourceTypeForm(BestiaryEditorForm):

    def __init__(self, *args, **kwargs):
        super(DataSourceTypeForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.state or self.state.is_empty():
            for ds_type in DataSourceType.objects.all():
                choices += ((ds_type.name, ds_type.name),)
        else:
            if self.state.eco_name:
                eco_orm = Ecosystem.objects.get(name=self.state.eco_name)
                for project_orm in eco_orm.projects.all():
                    for ds in project_orm.data_sources.all():
                        ds_type = ds.rep.data_source_type.name
                        if (ds_type, ds_type) not in choices:
                            choices += ((ds_type, ds_type),)
            if self.state.projects:
                for pname in self.state.projects:
                    project_orm = Project.objects.get(name=pname)
                    for ds in project_orm.data_sources.all():
                        ds_type = ds.rep.data_source_type.name
                        if (ds_type, ds_type) not in choices:
                            choices += ((ds_type, ds_type),)
            if self.state.data_source_types:
                for ds_type in self.state.data_source_types:
                    choices += ((ds_type, ds_type),)
            if self.state.data_sources:
                for ds_id in self.state.data_sources:
                    ds_orm = DataSource.objects.get(id=ds_id)
                    ds_type = ds_orm.rep.data_source_type.name
                    if (ds_type, ds_type) not in choices:
                        choices += ((ds_type, ds_type),)

        choices = sorted(choices, key=lambda x: x[1])
        self.fields['name'] = forms.ChoiceField(label='DataSourceTypes',
                                                widget=self.widget, choices=choices)


class DataSourcesForm(BestiaryEditorForm):
    def __init__(self, *args, **kwargs):
        super(DataSourcesForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.state or self.state.is_empty():
            for ds in DataSource.objects.all():
                choices += ((ds.id, ds),)
        else:
            if self.state.eco_name:
                eco_orm = Ecosystem.objects.get(name=self.state.eco_name)
                for project_orm in eco_orm.projects.all():
                    for ds in project_orm.data_sources.all():
                        choices += ((ds.id, ds),)
            if self.state.projects:
                for pname in self.state.projects:
                    project_orm = Project.objects.get(name=pname)
                    for ds_orm in project_orm.data_sources.all():
                        choices += ((ds_orm.id, ds_orm),)
            if self.state.data_source_types:
                for ds_orm in DataSource.objects.all():
                    if ds_orm.rep.data_source_type.name in self.state.data_source_types:
                        choices += ((ds_orm.id, ds_orm),)
            if self.state.data_sources:
                for ds_id in self.state.data_sources:
                    ds_orm = DataSource.objects.get(id=ds_id)
                    choices += ((ds_orm.id, ds_orm),)

        self.fields['id'] = forms.ChoiceField(label='DataSource',
                                              widget=self.widget, choices=choices)


class DataSourceForm(BestiaryEditorForm):
    def __init__(self, *args, **kwargs):
        self.data_source_id = None
        self.ds_orm = None

        # Process the state here because we need it for other initial values
        self.state = kwargs.pop('state') if 'state' in kwargs else None
        if self.state:
            kwargs['initial'] = self.state.initial_state()

        if self.state and self.state.data_sources:
            self.data_source_id = self.state.data_sources[0]

        if self.data_source_id:
            ds_orm = DataSource.objects.get(id=self.data_source_id)
            kwargs['initial'] = {
                'data_source_id': self.data_source_id,
                'repository': ds_orm.rep.name,
                'params': ds_orm.params,
                'filters': ''
            }
        super(DataSourceForm, self).__init__(*args, **kwargs)

        self.fields['data_source_id'] = forms.CharField(label='repository', max_length=100)

        self.fields['repository'] = forms.CharField(label='repository', max_length=100, required=False)
        self.fields['repository'].widget = forms.TextInput(attrs={'class': 'form-control'})

        self.fields['params'] = forms.CharField(label='params', max_length=100, required=False)
        self.fields['params'].widget = forms.TextInput(attrs={'class': 'form-control'})

        self.fields['filters'] = forms.CharField(label='filters', max_length=100, required=False)
        self.fields['filters'].widget = forms.TextInput(attrs={'class': 'form-control'})
