# -*- coding: utf-8 -*-

from ecs import bootstrap
from ecs.documents.models import DocumentType
from ecs.bootstrap.utils import update_instance
from ecs.utils import Args

_ = lambda s: s     # dummy gettext for marking strings

@bootstrap.register()
def document_types():
    names = (
        Args(_(u"Covering Letter"), u"coveringletter", _(u"Cover letter / covering letter to the Ethics Commission")),
        Args(_(u"patient information"), u"patientinformation", 
            _(u"Patients / subjects / children / youths / parents / genetic information, information for non competent patients")),
        Args(_(u"insurancecertificate"), u"insurancecertificate", _(u" ")),
        Args(_(u"study protocol"), u"protocol", _(u"study protocol")),
        Args(_(u"Investigator's Brochure"), u"investigatorsbrochure", _(u" "), is_downloadable=False),
        Args(_(u"Amendment"), u"amendment", _(u"Protocol changes")),
        Args(_(u"Curriculum Vitae (CV)"), u"cv", _(u"CV")),
        Args(_(u"Conflict of Interest"), u"conflictofinterest",_(u"can also be a Financial Disclosure Form")),
        Args(_(u"Case Report Form (CRF)"), u"crf", _(u" ")),
        Args(_(u"EudraCT Form"), u"eudract",
            _(u"Request for Authorisation, Notification of Amendment Form, Declaration of the end of the clinical trial")),
        Args(_(u"adverse reaction report"), u"adversereaction", _(u"Med Watch report, CIOMS form etc.")),
        Args(_(u"other"), u"other", _(u"Patient diaries, patient card, technical information, questionnaires, etc.")),

        # internal document types; not user visible
        Args(_(u"Submission Form"), u"submissionform", _(u"Submission Form"), is_hidden=True),
        Args(_(u"Checklist"), u"checklist", _(u"Checklist"), is_hidden=True),
        Args(_(u"vote"), u"votes", _(u"Vote"), is_hidden=True),
        Args(_(u"Notification"), u"notification", _(u"Notification"), is_hidden=True),
        Args(_(u"Notification Answer"), u"notification_answer", _(u"Notification Answer"), is_hidden=True),
    )

    for args in names:
        name, identifier, helptext = args
        data = {
            'name': name,
            'helptext': helptext,
            'is_hidden': args.get('is_hidden', False),
            'is_downloadable': args.get('is_downloadable', True),
        }
        d, created = DocumentType.objects.get_or_create(identifier=identifier, defaults=data)
        update_instance(d, data)
