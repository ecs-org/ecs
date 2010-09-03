# -*- coding: utf-8 -*-
from ecs import bootstrap
from ecs.documents.models import DocumentType

@bootstrap.register()
def document_types():
    names = (
        (u"Covering Letter", u"coveringletter", u"Anschreiben / Begleitschreiben an die Ethikkommission"),
        (u"Patienteninformation", u"patientinformation", 
            u"Patienten / Probanden / Kinder / Jugendliche / Eltern / Genetische- Information, Information für nicht einwilligungsfähige Patienten"),
        (u"Versicherungsbestätigung", u"insurancecertificate", u""),
        (u"Protokoll", u"protocol", u"Studienprotokoll"),
        (u"Investigator's Brochure", u"investigatorsbrochure", u""),
        (u"Amendment", u"amendment", u"Protokolländerungen"),
        (u"Curriculum Vitae (CV)", u"cv", u"Lebenslauf"),
        (u"Conflict of Interest", u"conflictofinterest", u"kann auch ein Financial Disclosure Form sein"),
        (u"Case Report Form (CRF)", u"crf", ""),
        (u"EudraCT Formular", u"eudract", u"Request for Authorisation, Notification of Amendment Form, Declaration of the end of the clinical trial"),
        (u"Nebenwirkungsmeldung", u"adversereaction", u"Med Watch-Bericht, CIOMS-Formular etc."),
        (u"Sonstige", u"other", u"Patiententagebuch, Patientenkarte, Fachinformation, Fragebögen etc."),
    )
    for name, identifier, helptext in names:
        d, created = DocumentType.objects.get_or_create(name=name, identifier=identifier)
        d.helptext= helptext
        d.save()