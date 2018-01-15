from django.db import models
from django.contrib.auth.models import User


class BeastModel(models.Model):
    """ Basic metadata for Bestiary objects """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True


# Create your models here.
class DataSource(BeastModel):
    """ The type of data source: git, github ... """
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Repository(BeastModel):
    name = models.CharField(max_length=200)
    # Relations
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'data_source')

    def __str__(self):
        return "%s (%s)" % (self.name, self.data_source)


class RepositoryView(BeastModel):
    """ A repository wit the extra params needed to collect it """
    params = models.CharField(max_length=400)
    # Relations
    # Base Repository from which to create the View
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('repository', 'params')

    def __str__(self):
        return self.repository.name + " " + self.params


class Project(BeastModel):
    name = models.CharField(max_length=200, unique=True)
    meta_title = models.CharField(max_length=200)
    # Relations
    repository_views = models.ManyToManyField(RepositoryView)
    # https://docs.djangoproject.com/en/1.11/ref/models/fields/#foreignkey
    subprojects = models.ManyToManyField("Project")

    def __str__(self):
        return self.name


class Ecosystem(BeastModel):
    name = models.CharField(max_length=200, unique=True)
    # Relations
    projects = models.ManyToManyField(Project)
    subecos = models.ManyToManyField("Ecosystem")

    def __str__(self):
        return self.name
