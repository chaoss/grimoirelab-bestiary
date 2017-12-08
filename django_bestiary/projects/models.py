from django.db import models


# Create your models here.
class DataSource(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Repository(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200)
    # Relations
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'data_source')

    def __str__(self):
        return "%s (%s)" % (self.name, self.data_source)


class RepositoryView(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    filters = models.CharField(max_length=400)  # A View is a Filter
    # Relations
    # Base Repository from which to create the View
    rep = models.ForeignKey(Repository, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('rep', 'filters')

    def __str__(self):
        return self.rep.name + " " + self.filters


class Project(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200)
    meta_title = models.CharField(max_length=200)
    # Relations
    rep_views = models.ManyToManyField(RepositoryView)
    # https://docs.djangoproject.com/en/1.11/ref/models/fields/#foreignkey
    subprojects = models.ManyToManyField("Project")
    org = models.ForeignKey("Organization", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'org')

    def __str__(self):
        return self.name


class Organization(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200, unique=True)
    # Relations
    projects = models.ManyToManyField(Project)
    suborgs = models.ManyToManyField("Organization")

    def __str__(self):
        return self.name
