# -*- coding: utf-8 -*-
from django.conf import settings

from ecs import bootstrap
from ecs.documents.models import DocumentType

_ = lambda s: s     # dummy gettext for marking strings

@bootstrap.register()
def document_types():
    names = (
        (_(u"Covering Letter"), u"coveringletter", _(u"Cover letter / covering letter to the Ethics Commission")),
        (_(u"patient information"), u"patientinformation", 
            _(u"Patients / subjects / children / youths / parents / genetic information, information for non competent patients")),
        (_(u"insurancecertificate"), u"insurancecertificate", _(u" ")),
        (_(u"study protocol"), u"protocol", _(u"study protocol")),
        (_(u"Investigator's Brochure"), u"investigatorsbrochure", _(u" ")),
        (_(u"Amendment"), u"amendment", _(u"Protocol changes")),
        (_(u"Curriculum Vitae (CV)"), u"cv", _(u"CV")),
        (_(u"Conflict of Interest"), u"conflictofinterest", _(u"can also be a Financial Disclosure Form")),
        (_(u"Case Report Form (CRF)"), u"crf", _(u" ")),
        (_(u"EudraCT Form"), u"eudract", _(u"Request for Authorisation, Notification of Amendment Form, Declaration of the end of the clinical trial")),
        (_(u"adverse reaction report"), u"adversereaction", _(u"Med Watch report, CIOMS form etc.")),
        (_(u"Submission Form"), u"submissionform", _(u"Submission Form")),
        (_(u"other"), u"other", _(u"Patient diaries, patient card, technical information, questionnaires, etc.")),
    )
    hidden = ('submissionform',)

    for name, identifier, helptext in names:
        d, created = DocumentType.objects.get_or_create(identifier=identifier)
        d.name = name
        d.helptext = helptext
        if identifier in hidden:
            d.hidden = True
        else:
            d.hidden = False
        d.save()

