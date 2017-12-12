from projects.models import DataSource, Project, Repository
from rest_framework import serializers


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'data_sources')


class DataSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataSource
        fields = ('params', 'rep')


class RepositorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Repository
        fields = ('name',)
