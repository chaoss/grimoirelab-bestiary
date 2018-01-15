from django.contrib import admin
from . import models


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_source',)
    list_filter = ('data_source',)

# Register your models here.


admin.site.register(models.Ecosystem)
admin.site.register(models.Project)
admin.site.register(models.Repository, RepositoryAdmin)
admin.site.register(models.RepositoryView)
admin.site.register(models.DataSource)
