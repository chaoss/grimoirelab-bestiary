from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^import/$', views.import_from_file),
    url(r'^$', views.index, name='index'),
]
