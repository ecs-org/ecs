# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse
from django.template import Context, loader
import settings

def index(request):
    t = loader.get_template('index.html')
    c = Context(dict())
    return HttpResponse(t.render(c))



