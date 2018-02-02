from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.status, name='index'),
    url(r'^status_select_ecosystem$', views.status_select_ecosystem),
    url(r'^status_select_project$', views.status_select_project),
]
#     url(r'^import/$', views.import_from_file),
#     url(r'^export/ecosystem=(?P<ecosystem>[\w ]+)', views.export_to_file),
# ]
