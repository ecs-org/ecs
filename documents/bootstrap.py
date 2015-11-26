# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ecs import bootstrap
from ecs.documents.models import DocumentType
from ecs.bootstrap.utils import update_instance
from ecs.utils import Args, gpgutils

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
        Args(_(u"Statement on a review"), u"reviewstatement", _(u" ")),
        Args(_(u"other"), u"other", _(u"Patient diaries, patient card, technical information, questionnaires, etc.")),

        # internal document types; not user visible
        Args(_(u"Submission Form"), u"submissionform", _(u"Submission Form"), is_hidden=True),
        Args(_(u"Checklist"), u"checklist", _(u"Checklist"), is_hidden=True),
        Args(_(u"vote"), u"votes", _(u"Vote"), is_hidden=True),
        Args(_(u"Notification"), u"notification", _(u"Notification"), is_hidden=True),
        Args(_(u"Notification Answer"), u"notification_answer", _(u"Notification Answer"), is_hidden=True),
        Args(_(u"Invoice"), u"invoice", _(u"Invoice"), is_hidden=True),
        Args(_(u"Checklist Payment"), u"checklist_payment", _(u"Checklist Payment"), is_hidden=True),
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

@bootstrap.register()
def import_encryption_sign_keys():
    if not hasattr(settings, 'STORAGE_ENCRYPT'):
        raise ImproperlyConfigured("no STORAGE_ENCRYPT setting")
    for a in "gpghome", "encrypt_key", "signing_key":
        if not settings.STORAGE_ENCRYPT.has_key(a):
            raise ImproperlyConfigured("missing parameter {0} in settings.STORAGE_ENCRYPT".format(a))

    gpgutils.reset_keystore(settings.STORAGE_ENCRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_ENCRYPT ["encrypt_key"], settings.STORAGE_ENCRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_ENCRYPT ["signing_key"], settings.STORAGE_ENCRYPT ["gpghome"])

@bootstrap.register()
def import_decryption_verify_keys():
    if not hasattr(settings, 'STORAGE_DECRYPT'):
        raise ImproperlyConfigured("no STORAGE_DECRYPT setting")
    for a in "gpghome", "decrypt_key", "verify_key":
        if not settings.STORAGE_DECRYPT.has_key(a):
            raise ImproperlyConfigured("missing parameter {0} in settings.STORAGE_DECRYPT".format(a))

    gpgutils.reset_keystore(settings.STORAGE_DECRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_DECRYPT ["decrypt_key"], settings.STORAGE_DECRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_DECRYPT ["verify_key"], settings.STORAGE_DECRYPT ["gpghome"])

@bootstrap.register()
def create_local_storage_vault():
    workdir = settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir']
    if workdir:
        if not os.path.isdir(workdir):
            os.makedirs(workdir)
