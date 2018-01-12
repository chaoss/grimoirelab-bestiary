from django import forms

from projects.models import DataSource, DataSourceType, Ecosystem, Project

SELECT_LINES = 20

class EcosystemForm(forms.Form):

    widget = forms.Select(attrs={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        self.eco_name = None
        if 'eco_name' in kwargs:
            self.eco_name = kwargs.pop('eco_name')
        super(EcosystemForm, self).__init__(*args, **kwargs)

        choices = ()

        for eco in Ecosystem.objects.all():
            choices += ((eco.name, eco.name),)

        self.fields['name'] = forms.ChoiceField(label='Ecosystems',
                                                widget=self.widget, choices=choices)


class ProjectsForm(forms.Form):
    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        self.eco_name = None
        if 'eco_name' in kwargs:
            self.eco_name = kwargs.pop('eco_name')
        super(ProjectsForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.eco_name:
            for project in Project.objects.all():
                choices += ((project.name, project.name),)
        else:
            ecosystem_orm = Ecosystem.objects.get(name=self.eco_name)
            for project in ecosystem_orm.projects.all():
                choices += ((project.name, project.name),)

        self.fields['name'] = forms.ChoiceField(label='Projects',
                                                widget=self.widget, choices=choices)


class DataSourceTypeForm(forms.Form):
    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    CHOICES = ()

    for ds_type in DataSourceType.objects.all():
        CHOICES += ((ds_type.name, ds_type.name),)

    name = forms.ChoiceField(label='DataSourceTypes', widget=widget, choices=CHOICES)


class DataSourcesForm(forms.Form):
    widget = forms.Select(attrs={'size': SELECT_LINES, 'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        self.project_names = None
        if 'project_names' in kwargs:
            self.project_names = kwargs.pop('project_names')
        super(DataSourcesForm, self).__init__(*args, **kwargs)

        choices = ()

        if not self.project_names:
            for ds in DataSource.objects.all():
                choices += ((ds.rep.name, ds.rep.name),)
        else:
            for pname in self.project_names:
                project_orm = Project.objects.get(name=pname)
                for ds in project_orm.data_sources.all():
                    choices += ((ds.rep.name, ds.rep.name),)


        self.fields['name'] = forms.ChoiceField(label='DataSource',
                                                widget=self.widget, choices=choices)
