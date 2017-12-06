from django.db import models


# Create your models here.
class DataSource(models.Model):
    name = models.CharField(max_length=200, unique=True)
    # creation_date = models.DateTimeField('date creation')

    def __str__(self):
        return self.name


class Repository(models.Model):
    name = models.CharField(max_length=200)
    # creation_date = models.DateTimeField('date creation')
    # Relations
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'data_source')

    def __str__(self):
        return "%s (%s)" % (self.name, self.data_source)


class RepositoryView(models.Model):
    # creation_date = models.DateTimeField('date creation')
    # update_date = models.DateTimeField('date update')
    filters = models.CharField(max_length=400)  # A View is a Filter
    # Relations
    # Base Repository from which to create the View
    rep = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return self.rep.name + " " + self.filters


class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    meta = models.CharField(max_length=200, default='')
    # creation_date = models.DateTimeField('date creation')
    # update_date = models.DateTimeField('date update')
    # Relations
    rep_views = models.ManyToManyField(RepositoryView)
    # https://docs.djangoproject.com/en/1.11/ref/models/fields/#foreignkey
    subprojects = models.ManyToManyField("Project")

    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    # creation_date = models.DateTimeField('date creation')
    # update_date = models.DateTimeField('date update')
    # Relations
    projects = models.ManyToManyField(Project)
    suborgs = models.ManyToManyField("Organization")

    def __str__(self):
        return self.name
