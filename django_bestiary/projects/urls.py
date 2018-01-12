from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^import/$', views.import_from_file),
    url(r'^export/$', views.export_to_file),
    url(r'^editor/$', views.editor, name='editor'),
    url(r'^edit_ecosystem$', views.edit_ecosystem),
    url(r'^edit_project$', views.edit_project),
    url(r'^edit_data_source_type$', views.edit_data_source_type),
    url(r'^edit_data_source$', views.edit_data_source),
    url(r'^update_data_source$', views.update_data_source),
    url(r'^$', views.index, name='index'),
]
