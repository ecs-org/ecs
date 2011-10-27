from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from ecs.checklists.models import Checklist
from ecs.utils.security import readonly


def yesno(flag):
    return flag and "Ja" or "Nein"


@readonly()
def checklist_comments(request, checklist_pk=None, flavour='negative'):
    checklist = get_object_or_404(Checklist, pk=checklist_pk)
    answer = flavour == 'positive'
    answers = checklist.get_answers_with_comments(answer).select_related('question')
    return HttpResponse("\n\n".join("%s\n%s: %s" % (a.question.text, yesno(answer), a.comment) for a in answers), content_type="text/plain")


@readonly()
def checklist_pdf(request, checklist_pk=None):
    checklist = get_object_or_404(Checklist, pk=checklist_pk, pdf_document__isnull=False)
    url = checklist.pdf_document.get_downloadurl()
    if not url:
        raise Http404()
    return HttpResponseRedirect(url)
