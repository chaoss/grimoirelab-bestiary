from django.conf.urls import url

from . import views

urlpatterns = [
     url(r'^$', views.index, name='index')
]
#     url(r'^import/$', views.import_from_file),
#     url(r'^export/ecosystem=(?P<ecosystem>[\w ]+)', views.export_to_file),
# ]
