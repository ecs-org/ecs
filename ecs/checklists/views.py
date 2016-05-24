from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from ecs.checklists.models import Checklist
from ecs.documents.views import handle_download


def yesno(flag):
    return flag and "Ja" or "Nein"


def checklist_comments(request, checklist_pk=None, flavour='negative'):
    checklist = get_object_or_404(Checklist, pk=checklist_pk)
    answer = flavour == 'positive'
    answers = checklist.get_answers_with_comments(answer).select_related('question')
    return HttpResponse("\n\n".join("%s\n%s: %s" % (a.question.text, yesno(a.answer), a.comment) for a in answers), content_type="text/plain")


def checklist_pdf(request, checklist_pk=None):
    checklist = get_object_or_404(Checklist, pk=checklist_pk)
    return handle_download(request, checklist.pdf_document)
