# -*- coding: utf-8 -*-
#from reversion import revision
#from reversion.models import Revision

from django.http import HttpResponse

def trail(request):
    #revisions = Revision.objects.order_by('date_created')
    revisions = []
    return HttpResponse('\n'.join([str(x) for x in revisions]))
