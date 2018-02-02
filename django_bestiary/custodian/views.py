from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


# Create your views here.

def index(request):
    context = {}
    template = loader.get_template('custodian/status.html')
    render_status = template.render(context, request)
    return HttpResponse(render_status)
