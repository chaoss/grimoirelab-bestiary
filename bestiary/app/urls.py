"""Bestiary URL Configuration"""


from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView

from graphene_django.views import GraphQLView

from .schema import schema

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html")),
    path('graphql/', GraphQLView.as_view(graphiql=settings.DEBUG, schema=schema))
]
