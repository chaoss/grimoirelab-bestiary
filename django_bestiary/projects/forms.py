from django import forms

from projects.models import DataSource, DataSourceType, Ecosystem, Project

SELECT_LINES = 20


class BestiaryForm(forms.Form):

    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    def populate_state(self, kwargs):
        self.eco_name = kwargs.pop('eco_name') if 'eco_name' in kwargs else None
        self.projects = kwargs.pop('projects') if 'projects' in kwargs else None
        self.data_sources = kwargs.pop('data_sources') if 'data_sources' in kwargs else None
        self.data_source_types = kwargs.pop('data_source_types') if 'data_source_types' in kwargs else None

    def is_empty_state(self):
        return not (self.eco_name or self.projects or self.data_source_types or
                    self.data_sources)

    def __init__(self, *args, **kwargs):
        self.populate_state(kwargs)
        super(BestiaryForm, self).__init__(*args, **kwargs)


class EcosystemForm(BestiaryForm):

    widget = forms.Select(attrs={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        super(EcosystemForm, self).__init__(*args, **kwargs)

        choices = ()

        for eco in Ecosystem.objects.all():
            choices += ((eco.name, eco.name),)

        self.fields['name'] = forms.ChoiceField(label='Ecosystems',
                                                widget=self.widget, choices=choices)


class ProjectsForm(BestiaryForm):

    def __init__(self, *args, **kwargs):
        super(ProjectsForm, self).__init__(*args, **kwargs)

        choices = ()

        if self.is_empty_state():
            for project in Project.objects.all():
                choices += ((project.name, project.name),)
        else:
            if self.eco_name:
                ecosystem_orm = Ecosystem.objects.get(name=self.eco_name)
                for project in ecosystem_orm.projects.all():
                    choices += ((project.name, project.name),)
            if self.projects:
                for project in Project.objects.all():
                    if project.name in self.projects:
                        choices += ((project.name, project.name),)
            if self.data_sources:
                for project_orm in Project.objects.all():
                    for ds in project_orm.data_sources.all():
                        if ds.id in self.data_sources:
                            if (project_orm.name, project_orm.name) not in choices:
                                choices += ((project_orm.name, project_orm.name),)
                            break
            if self.data_source_types:
                for project_orm in Project.objects.all():
                    for ds in project_orm.data_sources.all():
                        ds_type = ds.rep.data_source_type.name
                        if ds_type in self.data_source_types:
                            if (project_orm.name, project_orm.name) not in choices:
                                choices += ((project_orm.name, project_orm.name),)
                            break

        choices = sorted(choices, key=lambda x: x[1])
        self.fields['name'] = forms.ChoiceField(label='Projects',
                                                widget=self.widget, choices=choices)


class DataSourceTypeForm(BestiaryForm):

    def __init__(self, *args, **kwargs):
        super(DataSourceTypeForm, self).__init__(*args, **kwargs)

        choices = ()

        if self.is_empty_state():
            for ds_type in DataSourceType.objects.all():
                choices += ((ds_type.name, ds_type.name),)
        else:
            if self.eco_name:
                eco_orm = Ecosystem.objects.get(name=self.eco_name)
                for project_orm in eco_orm.projects.all():
                    for ds in project_orm.data_sources.all():
                        ds_type = ds.rep.data_source_type.name
                        if (ds_type, ds_type) not in choices:
                            choices += ((ds_type, ds_type),)
            if self.projects:
                for pname in self.projects:
                    project_orm = Project.objects.get(name=pname)
                    for ds in project_orm.data_sources.all():
                        ds_type = ds.rep.data_source_type.name
                        if (ds_type, ds_type) not in choices:
                            choices += ((ds_type, ds_type),)
            if self.data_source_types:
                for ds_type in self.data_source_types:
                    choices += ((ds_type, ds_type),)
            if self.data_sources:
                for ds_id in self.data_sources:
                    ds_orm = DataSource.objects.get(id=ds_id)
                    ds_type = ds_orm.rep.data_source_type.name
                    if (ds_type, ds_type) not in choices:
                        choices += ((ds_type, ds_type),)

        choices = sorted(choices, key=lambda x: x[1])
        self.fields['name'] = forms.ChoiceField(label='DataSourceTypes',
                                                widget=self.widget, choices=choices)


class DataSourcesForm(BestiaryForm):
    def __init__(self, *args, **kwargs):
        super(DataSourcesForm, self).__init__(*args, **kwargs)

        choices = ()

        if self.is_empty_state():
            for ds in DataSource.objects.all():
                choices += ((ds.id, ds),)
        else:
            if self.eco_name:
                eco_orm = Ecosystem.objects.get(name=self.eco_name)
                for project_orm in eco_orm.projects.all():
                    for ds in project_orm.data_sources.all():
                        choices += ((ds.id, ds),)
            if self.projects is not None and self.projects:
                for pname in self.projects:
                    project_orm = Project.objects.get(name=pname)
                    for ds_orm in project_orm.data_sources.all():
                        choices += ((ds_orm.id, ds_orm),)
            if self.data_source_types is not None and self.data_source_types:
                for ds_orm in DataSource.objects.all():
                    if ds_orm.rep.data_source_type.name in self.data_source_types:
                        choices += ((ds_orm.id, ds_orm),)
            if self.data_sources:
                for ds_id in self.data_sources:
                    ds_orm = DataSource.objects.get(id=ds_id)
                    choices += ((ds_orm.id, ds_orm),)

        self.fields['id'] = forms.ChoiceField(label='DataSource',
                                              widget=self.widget, choices=choices)


class DataSourceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.data_source_id = None
        self.ds_orm = None
        if 'data_source_id' in kwargs:
            self.data_source_id = kwargs.pop('data_source_id')

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
