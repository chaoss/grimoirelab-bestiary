from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^import/$', views.import_from_file),
    url(r'^export/$', views.export_to_file),
    url(r'^editor/$', views.editor, name='editor'),
    url(r'^select_ecosystem$', views.select_ecosystem),
    url(r'^add_project$', views.add_project),
    url(r'^remove_project$', views.remove_project),
    url(r'^select_project$', views.select_project),
    url(r'^select_data_source$', views.select_data_source),
    url(r'^select_repository_view$', views.select_repository_view),
    url(r'^update_repository_view$', views.update_repository_view),
    url(r'^$', views.index, name='index'),
]
