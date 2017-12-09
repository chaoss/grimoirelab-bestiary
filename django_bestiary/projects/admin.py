from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Organization)
admin.site.register(models.Project)
admin.site.register(models.Repository)
admin.site.register(models.DataSource)
admin.site.register(models.DataSourceType)
