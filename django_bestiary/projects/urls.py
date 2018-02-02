from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^import/$', views.import_from_file),
    url(r'^export/ecosystem=(?P<ecosystem>[\w ]+)', views.export_to_file),
    url(r'^export/$', views.export_to_file),
    url(r'^add_ecosystem$', views.add_ecosystem),
    url(r'^editor_select_ecosystem$', views.editor_select_ecosystem),
    url(r'^add_project$', views.add_project),
    url(r'^remove_project$', views.remove_project),
    url(r'^editor_select_project$', views.editor_select_project),
    url(r'^add_data_source$', views.add_data_source),
    url(r'^select_data_source$', views.select_data_source),
    url(r'^add_repository_view$', views.add_repository_view),
    url(r'^remove_repository_view$', views.remove_repository_view),
    url(r'^select_repository_view$', views.select_repository_view),
    url(r'^update_repository_view$', views.update_repository_view),
    url(r'^$', views.editor, name='index'),
]
