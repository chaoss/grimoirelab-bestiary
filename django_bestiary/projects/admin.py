from django.contrib import admin
from . import models


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_source_type',)
    list_filter = ('data_source_type',)

# Register your models here.


admin.site.register(models.Organization)
admin.site.register(models.Project)
admin.site.register(models.Repository, RepositoryAdmin)
admin.site.register(models.DataSource)
admin.site.register(models.DataSourceType)
